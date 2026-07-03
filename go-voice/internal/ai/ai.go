package ai

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"singhji-voice-go/internal/config"

	"github.com/go-resty/resty/v2"
	"go.uber.org/zap"
)

type Brain struct {
	cfg    *config.Config
	logger *zap.Logger
	client *resty.Client
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatResult struct {
	Response string `json:"response"`
	Provider string `json:"provider"`
	Tokens   int    `json:"tokens_used"`
	Latency  int64  `json:"latency_ms"`
}

func NewBrain(cfg *config.Config, logger *zap.Logger) *Brain {
	return &Brain{
		cfg:    cfg,
		logger: logger,
		client: resty.New().SetTimeout(30 * time.Second),
	}
}

func (b *Brain) Chat(ctx context.Context, text string, history []Message, language string) (string, error) {
	start := time.Now()

	result, err := b.groqChat(ctx, text, history, language)
	if err == nil {
		b.logger.Info("AI: Groq success",
			zap.Int("tokens", result.Tokens),
			zap.Int64("latency_ms", result.Latency),
			zap.Duration("duration", time.Since(start)))
		return result.Response, nil
	}
	b.logger.Warn("AI: Groq failed", zap.Error(err))

	result, err = b.geminiChat(ctx, text, history, language)
	if err == nil {
		b.logger.Info("AI: Gemini success", zap.Duration("duration", time.Since(start)))
		return result.Response, nil
	}
	b.logger.Warn("AI: Gemini failed", zap.Error(err))

	result, err = b.localLLMChat(ctx, text, history, language)
	if err == nil {
		b.logger.Info("AI: Local LLM success", zap.Duration("duration", time.Since(start)))
		return result.Response, nil
	}

	return "", fmt.Errorf("all AI providers failed: %w", err)
}

func (b *Brain) groqChat(ctx context.Context, text string, history []Message, language string) (*ChatResult, error) {
	if b.cfg.GroqAPIKey == "" {
		return nil, fmt.Errorf("groq API key not configured")
	}

	messages := []map[string]string{
		{
			"role": "system",
			"content": fmt.Sprintf("You are Singh Ji AI, a helpful Indian AI assistant. Respond in %s language. Be friendly, use Indian context when relevant.", language),
		},
	}

	for _, msg := range history {
		messages = append(messages, map[string]string{
			"role":    msg.Role,
			"content": msg.Content,
		})
	}

	messages = append(messages, map[string]string{
		"role":    "user",
		"content": text,
	})

	resp, err := b.client.R().
		SetContext(ctx).
		SetHeader("Authorization", "Bearer "+b.cfg.GroqAPIKey).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"model":       "llama3-70b-8192",
			"messages":    messages,
			"temperature": 0.7,
			"max_tokens":  1024,
		}).
		Post("https://api.groq.com/openai/v1/chat/completions")

	if err != nil {
		return nil, err
	}

	var result struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
		Usage struct {
			TotalTokens int `json:"total_tokens"`
		} `json:"usage"`
	}

	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	if len(result.Choices) == 0 {
		return nil, fmt.Errorf("no response from Groq")
	}

	return &ChatResult{
		Response: result.Choices[0].Message.Content,
		Provider: "groq",
		Tokens:   result.Usage.TotalTokens,
		Latency:  0,
	}, nil
}

func (b *Brain) geminiChat(ctx context.Context, text string, history []Message, language string) (*ChatResult, error) {
	if b.cfg.GeminiAPIKey == "" {
		return nil, fmt.Errorf("gemini API key not configured")
	}

	contents := []map[string]interface{}{
		{
			"role": "user",
			"parts": []map[string]string{
				{"text": fmt.Sprintf("You are Singh Ji AI. Respond in %s. User: %s", language, text)},
			},
		},
	}

	resp, err := b.client.R().
		SetContext(ctx).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"contents": contents,
			"generationConfig": map[string]interface{}{
				"temperature":     0.7,
				"maxOutputTokens": 1024,
			},
		}).
		Post(fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=%s", b.cfg.GeminiAPIKey))

	if err != nil {
		return nil, err
	}

	var result struct {
		Candidates []struct {
			Content struct {
				Parts []struct {
					Text string `json:"text"`
				} `json:"parts"`
			} `json:"content"`
		} `json:"candidates"`
	}

	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	if len(result.Candidates) == 0 || len(result.Candidates[0].Content.Parts) == 0 {
		return nil, fmt.Errorf("no response from Gemini")
	}

	return &ChatResult{
		Response: result.Candidates[0].Content.Parts[0].Text,
		Provider: "gemini",
		Tokens:   0,
		Latency:  0,
	}, nil
}

func (b *Brain) localLLMChat(ctx context.Context, text string, history []Message, language string) (*ChatResult, error) {
	messages := []map[string]string{
		{
			"role": "system",
			"content": fmt.Sprintf("You are Singh Ji AI. Respond in %s language.", language),
		},
	}

	for _, msg := range history {
		messages = append(messages, map[string]string{
			"role":    msg.Role,
			"content": msg.Content,
		})
	}

	messages = append(messages, map[string]string{
		"role":    "user",
		"content": text,
	})

	resp, err := b.client.R().
		SetContext(ctx).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"model":    "llama3",
			"messages": messages,
			"stream":   false,
		}).
		Post(b.cfg.LocalLLMURL + "/api/chat")

	if err != nil {
		return nil, err
	}

	var result struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	}

	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	return &ChatResult{
		Response: result.Message.Content,
		Provider: "local",
		Tokens:   0,
		Latency:  0,
	}, nil
}
