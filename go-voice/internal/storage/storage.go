package storage

import (
	"context"
	"fmt"
	"time"

	"singhji-voice-go/internal/config"

	"github.com/supabase-community/supabase-go"
	"go.uber.org/zap"
)

type Client struct {
	cfg    *config.Config
	logger *zap.Logger
	client *supabase.Client
}

type VoiceRecord struct {
	ID        string    `json:"id"`
	UserID    string    `json:"user_id"`
	Type      string    `json:"type"`
	Text      string    `json:"text"`
	AudioURL  string    `json:"audio_url"`
	Language  string    `json:"language"`
	Provider  string    `json:"provider"`
	Duration  float64   `json:"duration_ms"`
	CreatedAt time.Time `json:"created_at"`
}

func NewClient(cfg *config.Config, logger *zap.Logger) *Client {
	var client *supabase.Client
	if cfg.SupabaseURL != "" && cfg.SupabaseKey != "" {
		var err error
		client, err = supabase.NewClient(cfg.SupabaseURL, cfg.SupabaseKey, nil)
		if err != nil {
			logger.Warn("Supabase init failed", zap.Error(err))
		}
	}

	return &Client{
		cfg:    cfg,
		logger: logger,
		client: client,
	}
}

func (c *Client) SaveVoice(ctx context.Context, record *VoiceRecord) error {
	if c.client == nil {
		c.logger.Warn("Supabase not configured, skipping save")
		return nil
	}

	record.ID = fmt.Sprintf("voice_%d", time.Now().UnixNano())
	record.CreatedAt = time.Now()

	_, _, err := c.client.From("voice_history").Insert(record, false, "", "representation", "minimal").Execute()
	if err != nil {
		c.logger.Error("Failed to save voice record", zap.Error(err))
		return err
	}

	c.logger.Info("Voice saved", zap.String("id", record.ID), zap.String("user_id", record.UserID))
	return nil
}

func (c *Client) GetVoiceHistory(ctx context.Context, userID string) ([]VoiceRecord, error) {
	if c.client == nil {
		return []VoiceRecord{}, nil
	}

	var records []VoiceRecord
	_, err := c.client.From("voice_history").
		Select("*", "exact", false).
		Eq("user_id", userID).
		Order("created_at", &supabase.OrderOpts{Ascending: false}).
		Limit(100, "").
		ExecuteTo(&records)

	if err != nil {
		c.logger.Error("Failed to fetch voice history", zap.Error(err))
		return nil, err
	}

	return records, nil
}

func (c *Client) UploadAudio(ctx context.Context, userID string, audio []byte, filename string) (string, error) {
	if c.client == nil {
		return "", fmt.Errorf("supabase not configured")
	}

	path := fmt.Sprintf("%s/%s", userID, filename)

	_, err := c.client.Storage.UploadFile(c.cfg.SupabaseBucket, path, audio)
	if err != nil {
		return "", err
	}

	url := fmt.Sprintf("%s/storage/v1/object/public/%s/%s", c.cfg.SupabaseURL, c.cfg.SupabaseBucket, path)
	return url, nil
}
