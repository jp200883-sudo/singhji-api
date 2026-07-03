package translate

import (
	"context"
	"encoding/json"
	"fmt"
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

type TranslationResult struct {
	Text     string `json:"translated_text"`
	From     string `json:"source_language"`
	To       string `json:"target_language"`
	Provider string `json:"provider"`
}

var indicLanguages = map[string]bool{
	"hi": true, "bn": true, "ta": true, "te": true, "mr": true,
	"gu": true, "kn": true, "ml": true, "pa": true, "ur": true,
	"or": true, "as": true, "ne": true, "si": true, "sd": true,
	"sa": true, "kok": true, "mni": true, "doi": true, "brx": true,
}

func NewEngine(cfg *config.Config, logger *zap.Logger) *Engine {
	return &Engine{
		cfg:    cfg,
		logger: logger,
		client: resty.New().SetTimeout(15 * time.Second),
	}
}

func (e *Engine) Translate(ctx context.Context, text, from, to string) (*TranslationResult, error) {
	start := time.Now()

	if indicLanguages[from] && indicLanguages[to] && e.cfg.IndicTrans2URL != "" {
		result, err := e.indicTrans2Translate(ctx, text, from, to)
		if err == nil {
			e.logger.Info("Translation: IndicTrans2 success",
				zap.String("from", from),
				zap.String("to", to),
				zap.Duration("duration", time.Since(start)))
			return result, nil
		}
		e.logger.Warn("Translation: IndicTrans2 failed", zap.Error(err))
	}

	result, err := e.seamlessM4TTranslate(ctx, text, from, to)
	if err == nil {
		e.logger.Info("Translation: SeamlessM4T success", zap.Duration("duration", time.Since(start)))
		return result, nil
	}
	e.logger.Warn("Translation: SeamlessM4T failed", zap.Error(err))

	result, err = e.googleTranslate(ctx, text, from, to)
	if err == nil {
		e.logger.Info("Translation: Google success", zap.Duration("duration", time.Since(start)))
		return result, nil
	}

	return nil, fmt.Errorf("all translation providers failed: %w", err)
}

func (e *Engine) indicTrans2Translate(ctx context.Context, text, from, to string) (*TranslationResult, error) {
	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"text": text,
			"source": from,
			"target": to,
		}).
		Post(e.cfg.IndicTrans2URL + "/translate")

	if err != nil {
		return nil, err
	}

	var result struct {
		Translation string `json:"translation"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	return &TranslationResult{
		Text:     result.Translation,
		From:     from,
		To:       to,
		Provider: "indictrans2",
	}, nil
}

func (e *Engine) seamlessM4TTranslate(ctx context.Context, text, from, to string) (*TranslationResult, error) {
	if e.cfg.SeamlessM4TURL == "" {
		return nil, fmt.Errorf("seamlessm4t not configured")
	}

	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]interface{}{
			"text": text,
			"source_lang": from,
			"target_lang": to,
		}).
		Post(e.cfg.SeamlessM4TURL + "/translate")

	if err != nil {
		return nil, err
	}

	var result struct {
		Text string `json:"text"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	return &TranslationResult{
		Text:     result.Text,
		From:     from,
		To:       to,
		Provider: "seamlessm4t",
	}, nil
}

func (e *Engine) googleTranslate(ctx context.Context, text, from, to string) (*TranslationResult, error) {
	if e.cfg.GoogleTranslateKey == "" {
		return nil, fmt.Errorf("google translate key not configured")
	}

	if from == "auto" {
		from = ""
	}

	resp, err := e.client.R().
		SetContext(ctx).
		SetQueryParams(map[string]string{
			"q":      text,
			"source": from,
			"target": to,
			"key":    e.cfg.GoogleTranslateKey,
			"format": "text",
		}).
		Get("https://translation.googleapis.com/language/translate/v2")

	if err != nil {
		return nil, err
	}

	var result struct {
		Data struct {
			Translations []struct {
				TranslatedText string `json:"translatedText"`
				DetectedSource string `json:"detectedSourceLanguage"`
			} `json:"translations"`
		} `json:"data"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	if len(result.Data.Translations) == 0 {
		return nil, fmt.Errorf("no translation results")
	}

	detectedFrom := from
	if detectedFrom == "" {
		detectedFrom = result.Data.Translations[0].DetectedSource
	}

	return &TranslationResult{
		Text:     result.Data.Translations[0].TranslatedText,
		From:     detectedFrom,
		To:       to,
		Provider: "google",
	}, nil
}

func (e *Engine) DetectLanguage(ctx context.Context, text string) (string, error) {
	if e.cfg.GoogleTranslateKey == "" {
		return "en", nil
	}

	resp, err := e.client.R().
		SetContext(ctx).
		SetQueryParams(map[string]string{
			"q":   text,
			"key": e.cfg.GoogleTranslateKey,
		}).
		Get("https://translation.googleapis.com/language/translate/v2/detect")

	if err != nil {
		return "en", nil
	}

	var result struct {
		Data struct {
			Detections [][]struct {
				Language   string  `json:"language"`
				Confidence float64 `json:"confidence"`
			} `json:"detections"`
		} `json:"data"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return "en", nil
	}

	if len(result.Data.Detections) > 0 && len(result.Data.Detections[0]) > 0 {
		return result.Data.Detections[0][0].Language, nil
	}

	return "en", nil
}
