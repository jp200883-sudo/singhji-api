package tts

import (
	"bytes"
	"context"
	"encoding/base64"
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

type SynthesisResult struct {
	Audio      []byte  `json:"audio"`
	Format     string  `json:"format"`
	Duration   float64 `json:"duration_ms"`
	Provider   string  `json:"provider"`
	SampleRate int     `json:"sample_rate"`
}

func NewEngine(cfg *config.Config, logger *zap.Logger) *Engine {
	return &Engine{
		cfg:    cfg,
		logger: logger,
		client: resty.New().SetTimeout(30 * time.Second),
	}
}

func (e *Engine) Synthesize(ctx context.Context, text, language, voice, cloneID string) ([]byte, error) {
	start := time.Now()

	audio, err := e.minimaxSynthesize(ctx, text, language, voice, cloneID)
	if err == nil {
		e.logger.Info("TTS: Minimax success",
			zap.String("language", language),
			zap.Int("audio_size", len(audio)),
			zap.Duration("duration", time.Since(start)))
		return audio, nil
	}
	e.logger.Warn("TTS: Minimax failed, trying Edge", zap.Error(err))

	audio, err = e.edgeTTSSynthesize(ctx, text, language, voice)
	if err == nil {
		e.logger.Info("TTS: Edge success", zap.Duration("duration", time.Since(start)))
		return audio, nil
	}
	e.logger.Warn("TTS: Edge failed, trying Piper", zap.Error(err))

	audio, err = e.piperSynthesize(ctx, text, language)
	if err == nil {
		e.logger.Info("TTS: Piper success", zap.Duration("duration", time.Since(start)))
		return audio, nil
	}
	e.logger.Warn("TTS: Piper failed, trying Kokoro", zap.Error(err))

	audio, err = e.kokoroSynthesize(ctx, text, language)
	if err == nil {
		e.logger.Info("TTS: Kokoro success", zap.Duration("duration", time.Since(start)))
		return audio, nil
	}

	return nil, fmt.Errorf("all TTS providers failed: %w", err)
}

func (e *Engine) minimaxSynthesize(ctx context.Context, text, language, voice, cloneID string) ([]byte, error) {
	if e.cfg.MinimaxAPIKey == "" {
		return nil, fmt.Errorf("minimax API key not configured")
	}

	reqBody := map[string]interface{}{
		"text": text,
		"voice_id": voice,
		"language": language,
		"speed": 1.0,
		"volume": 1.0,
		"sample_rate": e.cfg.SampleRate,
		"bitrate": e.cfg.Bitrate,
		"format": "opus",
	}

	if cloneID != "" {
		reqBody["voice_id"] = cloneID
		reqBody["voice_type"] = "cloned"
	}

	resp, err := e.client.R().
		SetContext(ctx).
		SetHeader("Authorization", "Bearer "+e.cfg.MinimaxAPIKey).
		SetHeader("Content-Type", "application/json").
		SetBody(reqBody).
		Post("https://api.minimax.chat/v1/t2a_v2")

	if err != nil {
		return nil, err
	}

	var result struct {
		Data struct {
			Audio string `json:"audio"`
		} `json:"data"`
		BaseResp struct {
			StatusMsg string `json:"status_msg"`
		} `json:"base_resp"`
	}

	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}

	if result.BaseResp.StatusMsg != "" && result.BaseResp.StatusMsg != "success" {
		return nil, fmt.Errorf("minimax error: %s", result.BaseResp.StatusMsg)
	}

	return base64.StdEncoding.DecodeString(result.Data.Audio)
}

func (e *Engine) edgeTTSSynthesize(ctx context.Context, text, language, voice string) ([]byte, error) {
	voiceMap := map[string]string{
		"en": "en-US-AriaNeural",
		"hi": "hi-IN-MadhurNeural",
		"bn": "bn-IN-BashkarNeural",
		"ta": "ta-IN-PallaviNeural",
		"te": "te-IN-MohanNeural",
		"mr": "mr-IN-AarohiNeural",
		"gu": "gu-IN-DhwaniNeural",
		"kn": "kn-IN-GaganNeural",
		"ml": "ml-IN-MidhunNeural",
		"pa": "pa-IN-GulshanNeural",
		"ur": "ur-IN-GulNeural",
		"es": "es-ES-ElviraNeural",
		"fr": "fr-FR-DeniseNeural",
		"de": "de-DE-KatjaNeural",
		"ja": "ja-JP-NanamiNeural",
		"ko": "ko-KR-SunHiNeural",
		"zh": "zh-CN-XiaoxiaoNeural",
		"ar": "ar-SA-ZariyahNeural",
		"ru": "ru-RU-SvetlanaNeural",
		"pt": "pt-BR-FranciscaNeural",
	}

	edgeVoice := voiceMap[language]
	if edgeVoice == "" {
		edgeVoice = "en-US-AriaNeural"
	}
	if voice != "" && voice != "default" {
		edgeVoice = voice
	}

	cmd := exec.CommandContext(ctx, e.cfg.EdgeTTSPath,
		"--voice", edgeVoice,
		"--text", text,
		"--write-media", "-",
		"--format", "opus",
	)

	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("edge-tts failed: %w", err)
	}

	return output, nil
}

func (e *Engine) piperSynthesize(ctx context.Context, text, language string) ([]byte, error) {
	modelPath := fmt.Sprintf("%s/%s.onnx", e.cfg.PiperModelPath, language)
	configPath := fmt.Sprintf("%s/%s.onnx.json", e.cfg.PiperModelPath, language)

	cmd := exec.CommandContext(ctx, "piper",
		"--model", modelPath,
		"--config", configPath,
		"--output_file", "-",
		"--quality", fmt.Sprintf("%d", e.cfg.Bitrate),
	)
	cmd.Stdin = bytes.NewReader([]byte(text))

	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("piper failed: %w", err)
	}

	return output, nil
}

func (e *Engine) kokoroSynthesize(ctx context.Context, text, language string) ([]byte, error) {
	cmd := exec.CommandContext(ctx, "python3",
		"-c",
		fmt.Sprintf(`
import sys
sys.path.insert(0, "%s")
from kokoro import KPipeline
pipeline = KPipeline(lang_code="%s")
generator = pipeline(text, voice="af")
for _, (_, _, audio) in enumerate(generator):
    sys.stdout.buffer.write(audio.tobytes())
`, e.cfg.KokoroModelPath, language),
	)

	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("kokoro failed: %w", err)
	}

	return output, nil
}

func (e *Engine) StreamSynthesize(ctx context.Context, text, language, voice string, callback func([]byte) error) error {
	audio, err := e.edgeTTSSynthesize(ctx, text, language, voice)
	if err != nil {
		audio, err = e.piperSynthesize(ctx, text, language)
		if err != nil {
			return err
		}
	}

	chunkSize := 32 * 1024
	for i := 0; i < len(audio); i += chunkSize {
		end := i + chunkSize
		if end > len(audio) {
			end = len(audio)
		}
		if err := callback(audio[i:end]); err != nil {
			return err
		}
	}

	return nil
}
