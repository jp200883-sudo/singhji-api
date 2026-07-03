package stt

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os/exec"
	"time"

	"singhji-voice-go/internal/config"

	"github.com/go-resty/resty/v2"
	"go.uber.org/zap"
)

type Engine struct {
	cfg    *config.Config
	logger *zap.Logger
	client *resty.Client
}

type TranscriptionResult struct {
	Text       string  `json:"text"`
	Confidence float64 `json:"confidence"`
	Language   string  `json:"language"`
	Provider   string  `json:"provider"`
	Duration   float64 `json:"duration_ms"`
}

func NewEngine(cfg *config.Config, logger *zap.Logger) *Engine {
	return &Engine{
		cfg:    cfg,
		logger: logger,
		client: resty.New().SetTimeout(30 * time.Second),
	}
}

func (e *Engine) Transcribe(ctx context.Context, audio io.Reader, language string) (*TranscriptionResult, error) {
	start := time.Now()

	result, err := e.whisperTranscribe(ctx, audio, language)
	if err == nil {
		e.logger.Info("STT: Whisper success", 
			zap.String("text", result.Text[:min(50, len(result.Text))]),
			zap.Duration("duration", time.Since(start)))
		return result, nil
	}
	e.logger.Warn("STT: Whisper failed, trying Vosk", zap.Error(err))

	result, err = e.voskTranscribe(ctx, audio, language)
	if err == nil {
		e.logger.Info("STT: Vosk success", zap.Duration("duration", time.Since(start)))
		return result, nil
	}
	e.logger.Warn("STT: Vosk failed, trying Google", zap.Error(err))

	result, err = e.googleTranscribe(ctx, audio, language)
	if err == nil {
		e.logger.Info("STT: Google success", zap.Duration("duration", time.Since(start)))
		return result, nil
	}

	return nil, fmt.Errorf("all STT providers failed: %w", err)
}

func (e *Engine) whisperTranscribe(ctx context.Context, audio io.Reader, language string) (*TranscriptionResult, error) {
	data, err := io.ReadAll(audio)
	if err != nil {
		return nil, err
	}

	cmd := exec.CommandContext(ctx, "whisper",
		"--model", e.cfg.WhisperModelPath,
		"--language", language,
		"--output_format", "json",
		"--no_speech_threshold", "0.3",
		"-",
	)
	cmd.Stdin = bytes.NewReader(data)

	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("whisper failed: %w", err)
	}

	var whisperResult struct {
		Text     string  `json:"text"`
		Language string  `json:"language"`
		Segments []struct {
			Text       string  `json:"text"`
			Confidence float64 `json:"avg_logprob"`
		} `json:"segments"`
	}

	if err := json.Unmarshal(output, &whisperResult); err != nil {
		return nil, err
	}

	confidence := 0.95
	if len(whisperResult.Segments) > 0 {
		confidence = whisperResult.Segments[0].Confidence
	}

	return &TranscriptionResult{
		Text:       whisperResult.Text,
		Confidence: confidence,
		Language:   whisperResult.Language,
		Provider:   "whisper",
		Duration:   float64(time.Since(time.Now())) / float64(time.Millisecond),
	}, nil
}

func (e *Engine) voskTranscribe(ctx context.Context, audio io.Reader, language string) (*TranscriptionResult, error) {
	data, err := io.ReadAll(audio)
	if err != nil {
		return nil, err
	}

	cmd := exec.CommandContext(ctx, "vosk-transcriber",
		"--model", e.cfg.VoskModelPath,
		"--input", "-",
		"--output", "-",
	)
	cmd.Stdin = bytes.NewReader(data)

	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("vosk failed: %w", err)
	}

	return &TranscriptionResult{
		Text:       string(output),
		Confidence: 0.85,
		Language:   language,
		Provider:   "vosk",
		Duration:   0,
	}, nil
}

func (e *Engine) googleTranscribe(ctx context.Context, audio io.Reader, language string) (*TranscriptionResult, error) {
	if e.cfg.GoogleSTTKey == "" {
		return nil, fmt.Errorf("google STT key not configured")
	}

	data, err := io.ReadAll(audio)
	if err != nil {
		return nil, err
	}

	reqBody := map[string]interface{}{
		"config": map[string]interface{}{
			"encoding":        "OGG_OPUS",
			"sampleRateHertz": e.cfg.SampleRate,
			"languageCode":    language,
			"enableAutomaticPunctuation": true,
		},
		"audio": map[string]interface{}{
			"content": data,
		},
	}

	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Authorization", "Bearer "+e.cfg.GoogleSTTKey).
		SetHeader("Content-Type", "application/json").
		SetBody(reqBody).
		Post("https://speech.googleapis.com/v1/speech:recognize")

	if err != nil {
		return nil, err
	}

	var result struct {
		Results []struct {
			Alternatives []struct {
				Transcript string  `json:"transcript"`
				Confidence float64 `json:"confidence"`
			} `json:"alternatives"`
		} `json:"results"`
	}

	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	if len(result.Results) == 0 || len(result.Results[0].Alternatives) == 0 {
		return nil, fmt.Errorf("no transcription results")
	}

	alt := result.Results[0].Alternatives[0]
	return &TranscriptionResult{
		Text:       alt.Transcript,
		Confidence: alt.Confidence,
		Language:   language,
		Provider:   "google",
		Duration:   0,
	}, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
