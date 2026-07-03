package voiceclone

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"

	"singhji-voice-go/internal/config"

	"github.com/go-resty/resty/v2"
	"go.uber.org/zap"
)

type Engine struct {
	cfg    *config.Config
	logger *zap.Logger
	client *resty.Client
	clones map[string]*CloneVoice
}

type CloneVoice struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	SampleURL string    `json:"sample_url"`
	Provider  string    `json:"provider"`
	CreatedAt time.Time `json:"created_at"`
	Status    string    `json:"status"`
}

func NewEngine(cfg *config.Config, logger *zap.Logger) *Engine {
	return &Engine{
		cfg:    cfg,
		logger: logger,
		client: resty.New().SetTimeout(60 * time.Second),
		clones: make(map[string]*CloneVoice),
	}
}

func (e *Engine) CreateClone(ctx context.Context, sampleURL, name string) (string, error) {
	cloneID := fmt.Sprintf("clone_%d", time.Now().UnixNano())

	clone := &CloneVoice{
		ID:        cloneID,
		Name:      name,
		SampleURL: sampleURL,
		CreatedAt: time.Now(),
		Status:    "processing",
	}

	e.clones[cloneID] = clone

	var err error

	err = e.coquiClone(ctx, clone)
	if err == nil {
		clone.Provider = "coqui-xtts-v2"
		clone.Status = "ready"
		e.logger.Info("Voice clone: Coqui XTTS v2 success", zap.String("clone_id", cloneID))
		return cloneID, nil
	}
	e.logger.Warn("Voice clone: Coqui failed", zap.Error(err))

	err = e.fishAudioClone(ctx, clone)
	if err == nil {
		clone.Provider = "fish-audio"
		clone.Status = "ready"
		e.logger.Info("Voice clone: Fish Audio success", zap.String("clone_id", cloneID))
		return cloneID, nil
	}
	e.logger.Warn("Voice clone: Fish Audio failed", zap.Error(err))

	err = e.orpheusClone(ctx, clone)
	if err == nil {
		clone.Provider = "orpheus"
		clone.Status = "ready"
		e.logger.Info("Voice clone: Orpheus success", zap.String("clone_id", cloneID))
		return cloneID, nil
	}

	clone.Status = "failed"
	return "", fmt.Errorf("all voice clone providers failed: %w", err)
}

func (e *Engine) GetClone(cloneID string) (*CloneVoice, error) {
	clone, exists := e.clones[cloneID]
	if !exists {
		return nil, fmt.Errorf("clone not found: %s", cloneID)
	}
	return clone, nil
}

func (e *Engine) SynthesizeWithClone(ctx context.Context, cloneID, text string) ([]byte, error) {
	clone, err := e.GetClone(cloneID)
	if err != nil {
		return nil, err
	}

	if clone.Status != "ready" {
		return nil, fmt.Errorf("clone not ready: %s", clone.Status)
	}

	switch clone.Provider {
	case "coqui-xtts-v2":
		return e.coquiSynthesize(ctx, clone, text)
	case "fish-audio":
		return e.fishAudioSynthesize(ctx, clone, text)
	case "orpheus":
		return e.orpheusSynthesize(ctx, clone, text)
	default:
		return nil, fmt.Errorf("unknown clone provider: %s", clone.Provider)
	}
}

func (e *Engine) coquiClone(ctx context.Context, clone *CloneVoice) error {
	sampleData, err := e.downloadSample(ctx, clone.SampleURL)
	if err != nil {
		return err
	}

	tempDir := os.TempDir()
	samplePath := filepath.Join(tempDir, fmt.Sprintf("%s_sample.wav", clone.ID))
	if err := os.WriteFile(samplePath, sampleData, 0644); err != nil {
		return err
	}

	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"speaker_wav": samplePath,
			"clone_name":  clone.Name,
		}).
		Post("http://localhost:5002/clone_speaker")

	if err != nil {
		return err
	}

	var result struct {
		Status string `json:"status"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return err
	}

	if result.Status != "success" {
		return fmt.Errorf("coqui clone failed: %s", result.Status)
	}

	return nil
}

func (e *Engine) coquiSynthesize(ctx context.Context, clone *CloneVoice, text string) ([]byte, error) {
	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"text":        text,
			"speaker_id":  clone.ID,
			"language":    "en",
			"speed":       1.0,
		}).
		Post("http://localhost:5002/tts")

	if err != nil {
		return nil, err
	}

	return resp.Body(), nil
}

func (e *Engine) fishAudioClone(ctx context.Context, clone *CloneVoice) error {
	if e.cfg.FishAudioKey == "" {
		return fmt.Errorf("fish audio key not configured")
	}

	sampleData, err := e.downloadSample(ctx, clone.SampleURL)
	if err != nil {
		return err
	}

	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Authorization", "Bearer "+e.cfg.FishAudioKey).
		SetFileReader("sample", "sample.wav", io.NopCloser(io.Reader(bytes.NewReader(sampleData)))).
		SetFormData(map[string]string{
			"name": clone.Name,
		}).
		Post("https://api.fish.audio/v1/voices")

	if err != nil {
		return err
	}

	var result struct {
		ID string `json:"id"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return err
	}

	clone.ID = result.ID
	return nil
}

func (e *Engine) fishAudioSynthesize(ctx context.Context, clone *CloneVoice, text string) ([]byte, error) {
	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Authorization", "Bearer "+e.cfg.FishAudioKey).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"text":     text,
			"voice_id": clone.ID,
		}).
		Post("https://api.fish.audio/v1/tts")

	if err != nil {
		return nil, err
	}

	return resp.Body(), nil
}

func (e *Engine) orpheusClone(ctx context.Context, clone *CloneVoice) error {
	sampleData, err := e.downloadSample(ctx, clone.SampleURL)
	if err != nil {
		return err
	}

	tempDir := os.TempDir()
	samplePath := filepath.Join(tempDir, fmt.Sprintf("%s_orpheus.wav", clone.ID))
	if err := os.WriteFile(samplePath, sampleData, 0644); err != nil {
		return err
	}

	return nil
}

func (e *Engine) orpheusSynthesize(ctx context.Context, clone *CloneVoice, text string) ([]byte, error) {
	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"text":         text,
			"speaker_ref":  clone.ID,
			"language":     "auto",
		}).
		Post("http://localhost:8000/generate")

	if err != nil {
		return nil, err
	}

	return resp.Body(), nil
}

func (e *Engine) downloadSample(ctx context.Context, url string) ([]byte, error) {
	resp, err := e.client.R().
		SetContext(ctx).
		Get(url)

	if err != nil {
		return nil, err
	}

	return resp.Body(), nil
}
