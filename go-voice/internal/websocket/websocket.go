package websocket

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"singhji-voice-go/internal/ai"
	"singhji-voice-go/internal/config"
	"singhji-voice-go/internal/queue"
	"singhji-voice-go/internal/storage"
	"singhji-voice-go/internal/stt"
	"singhji-voice-go/internal/tts"
	"singhji-voice-go/internal/translate"
	"singhji-voice-go/internal/voiceclone"

	"github.com/gorilla/websocket"
	"go.uber.org/zap"
)

type Hub struct {
	clients    map[*Client]bool
	broadcast  chan []byte
	register   chan *Client
	unregister chan *Client
	sttEngine     *stt.Engine
	transEngine   *translate.Engine
	aiBrain       *ai.Brain
	ttsEngine     *tts.Engine
	cloneEngine   *voiceclone.Engine
	storageClient *storage.Client
	queueSystem   *queue.System
	logger *zap.Logger
}

type Client struct {
	hub  *Hub
	conn *websocket.Conn
	send chan []byte
	userID      string
	language    string
	voice       string
	cloneID     string
	isStreaming bool
	streamCtx   context.Context
	streamCancel context.CancelFunc
}

type VoiceMessage struct {
	Type     string `json:"type"`
	Text     string `json:"text,omitempty"`
	Audio    []byte `json:"audio,omitempty"`
	Language string `json:"language,omitempty"`
	Voice    string `json:"voice,omitempty"`
	CloneID  string `json:"clone_id,omitempty"`
	From     string `json:"from,omitempty"`
	To       string `json:"to,omitempty"`
}

type VoiceResponse struct {
	Type       string  `json:"type"`
	Text       string  `json:"text,omitempty"`
	Audio      []byte  `json:"audio,omitempty"`
	Language   string  `json:"language,omitempty"`
	Provider   string  `json:"provider,omitempty"`
	Confidence float64 `json:"confidence,omitempty"`
	Error      string  `json:"error,omitempty"`
	Latency    int64   `json:"latency_ms,omitempty"`
}

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func NewHub(logger *zap.Logger, stt *stt.Engine, trans *translate.Engine, brain *ai.Brain, 
	tts *tts.Engine, clone *voiceclone.Engine, storage *storage.Client, queue *queue.System) *Hub {
	return &Hub{
		clients:       make(map[*Client]bool),
		broadcast:     make(chan []byte),
		register:      make(chan *Client),
		unregister:    make(chan *Client),
		sttEngine:     stt,
		transEngine:   trans,
		aiBrain:       brain,
		ttsEngine:     tts,
		cloneEngine:   clone,
		storageClient: storage,
		queueSystem:   queue,
		logger:        logger,
	}
}

func (h *Hub) Run() {
	for {
		select {
		case client := <-h.register:
			h.clients[client] = true
			h.logger.Info("Client connected", zap.String("user_id", client.userID))

		case client := <-h.unregister:
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
				if client.streamCancel != nil {
					client.streamCancel()
				}
				h.logger.Info("Client disconnected", zap.String("user_id", client.userID))
			}

		case message := <-h.broadcast:
			for client := range h.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(h.clients, client)
				}
			}
		}
	}
}

func ServeWs(hub *Hub, w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		return
	}

	client := &Client{
		hub:      hub,
		conn:     conn,
		send:     make(chan []byte, 256),
		userID:   r.URL.Query().Get("user_id"),
		language: r.URL.Query().Get("lang"),
		voice:    r.URL.Query().Get("voice"),
		cloneID:  r.URL.Query().Get("clone_id"),
	}

	if client.language == "" {
		client.language = "en"
	}
	if client.voice == "" {
		client.voice = "default"
	}

	client.hub.register <- client

	go client.writePump()
	go client.readPump()
}

func (c *Client) readPump() {
	defer func() {
		c.hub.unregister <- c
		c.conn.Close()
	}()

	c.conn.SetReadLimit(10 * 1024 * 1024)
	c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				c.hub.logger.Warn("WebSocket error", zap.Error(err))
			}
			break
		}

		var msg VoiceMessage
		if err := json.Unmarshal(message, &msg); err != nil {
			c.sendError("Invalid message format")
			continue
		}

		c.handleMessage(msg)
	}
}

func (c *Client) writePump() {
	ticker := time.NewTicker(30 * time.Second)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			c.conn.WriteMessage(websocket.BinaryMessage, message)

		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

func (c *Client) handleMessage(msg VoiceMessage) {
	start := time.Now()
	ctx := context.Background()

	switch msg.Type {
	case "stt":
		if len(msg.Audio) == 0 {
			c.sendError("No audio data provided")
			return
		}

		result, err := c.hub.sttEngine.Transcribe(ctx, bytes.NewReader(msg.Audio), msg.Language)
		if err != nil {
			c.sendError(fmt.Sprintf("STT failed: %v", err))
			return
		}

		c.sendResponse(VoiceResponse{
			Type:       "stt_result",
			Text:       result.Text,
			Language:   result.Language,
			Provider:   result.Provider,
			Confidence: result.Confidence,
			Latency:    time.Since(start).Milliseconds(),
		})

	case "tts":
		if msg.Text == "" {
			c.sendError("No text provided")
			return
		}

		c.isStreaming = true
		c.streamCtx, c.streamCancel = context.WithCancel(ctx)

		err := c.hub.ttsEngine.StreamSynthesize(c.streamCtx, msg.Text, msg.Language, msg.Voice, 
			func(chunk []byte) error {
				if !c.isStreaming {
					return fmt.Errorf("streaming cancelled")
				}
				c.sendResponse(VoiceResponse{
					Type:     "tts_chunk",
					Audio:    chunk,
					Language: msg.Language,
					Latency:  time.Since(start).Milliseconds(),
				})
				return nil
			})

		if err != nil {
			c.sendError(fmt.Sprintf("TTS failed: %v", err))
			return
		}

		c.sendResponse(VoiceResponse{
			Type:    "tts_complete",
			Latency: time.Since(start).Milliseconds(),
		})
		c.isStreaming = false

	case "chat":
		if msg.Text == "" {
			c.sendError("No text provided")
			return
		}

		response, err := c.hub.aiBrain.Chat(ctx, msg.Text, nil, msg.Language)
		if err != nil {
			c.sendError(fmt.Sprintf("AI failed: %v", err))
			return
		}

		audio, err := c.hub.ttsEngine.Synthesize(ctx, response, msg.Language, msg.Voice, msg.CloneID)
		if err != nil {
			c.sendError(fmt.Sprintf("TTS failed: %v", err))
			return
		}

		c.sendResponse(VoiceResponse{
			Type:     "chat_response",
			Text:     response,
			Audio:    audio,
			Language: msg.Language,
			Latency:  time.Since(start).Milliseconds(),
		})

	case "translate":
		if msg.Text == "" {
			c.sendError("No text provided")
			return
		}

		result, err := c.hub.transEngine.Translate(ctx, msg.Text, msg.From, msg.To)
		if err != nil {
			c.sendError(fmt.Sprintf("Translation failed: %v", err))
			return
		}

		c.sendResponse(VoiceResponse{
			Type:     "translate_result",
			Text:     result.Text,
			Language: result.To,
			Latency:  time.Since(start).Milliseconds(),
		})

	case "clone":
		if msg.Text == "" {
			c.sendError("No sample URL provided")
			return
		}

		cloneID, err := c.hub.cloneEngine.CreateClone(ctx, msg.Text, msg.Voice)
		if err != nil {
			c.sendError(fmt.Sprintf("Clone failed: %v", err))
			return
		}

		c.sendResponse(VoiceResponse{
			Type: "clone_ready",
			Text: cloneID,
		})

	case "ping":
		c.sendResponse(VoiceResponse{
			Type: "pong",
		})

	default:
		c.sendError(fmt.Sprintf("Unknown message type: %s", msg.Type))
	}
}

func (c *Client) sendResponse(resp VoiceResponse) {
	data, _ := json.Marshal(resp)
	select {
	case c.send <- data:
	default:
		c.hub.logger.Warn("Client send buffer full")
	}
}

func (c *Client) sendError(err string) {
	c.sendResponse(VoiceResponse{
		Type:  "error",
		Error: err,
	})
}
