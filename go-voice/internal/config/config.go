package config

import (
	"os"
	"strconv"
	"time"
)

type Config struct {
	Port        string
	Environment string
	WhisperModelPath   string
	VoskModelPath      string
	GoogleSTTKey       string
	IndicTrans2URL     string
	SeamlessM4TURL     string
	GoogleTranslateKey string
	GroqAPIKey         string
	GeminiAPIKey       string
	LocalLLMURL        string
	MinimaxAPIKey      string
	EdgeTTSPath        string
	PiperModelPath     string
	KokoroModelPath    string
	CoquiXTTSPath      string
	FishAudioKey       string
	OrpheusModelPath   string
	SupabaseURL        string
	SupabaseKey        string
	SupabaseBucket     string
	SampleRate    int
	BitDepth      int
	Channels      int
	Bitrate       int
	MaxFileSize   int64
	MaxDuration   time.Duration
	QueueWorkers  int
	QueueSize     int
	WSReadBuffer  int
	WSWriteBuffer int
	WSMaxMessage  int64
}

func Load() *Config {
	return &Config{
		Port:        getEnv("PORT", "8080"),
		Environment: getEnv("ENV", "development"),
		WhisperModelPath:   getEnv("WHISPER_MODEL_PATH", "./models/whisper-base"),
		VoskModelPath:      getEnv("VOSK_MODEL_PATH", "./models/vosk-en"),
		GoogleSTTKey:       getEnv("GOOGLE_STT_KEY", ""),
		IndicTrans2URL:     getEnv("INDICTRANS2_URL", ""),
		SeamlessM4TURL:     getEnv("SEAMLESSM4T_URL", ""),
		GoogleTranslateKey: getEnv("GOOGLE_TRANSLATE_KEY", ""),
		GroqAPIKey:         getEnv("GROQ_API_KEY", ""),
		GeminiAPIKey:       getEnv("GEMINI_API_KEY", ""),
		LocalLLMURL:        getEnv("LOCAL_LLM_URL", "http://localhost:11434"),
		MinimaxAPIKey:      getEnv("MINIMAX_API_KEY", ""),
		EdgeTTSPath:        getEnv("EDGE_TTS_PATH", "edge-tts"),
		PiperModelPath:     getEnv("PIPER_MODEL_PATH", "./models/piper-en"),
		KokoroModelPath:    getEnv("KOKORO_MODEL_PATH", "./models/kokoro"),
		CoquiXTTSPath:      getEnv("COQUI_XTTS_PATH", "./models/coqui-xtts-v2"),
		FishAudioKey:       getEnv("FISH_AUDIO_KEY", ""),
		OrpheusModelPath:   getEnv("ORPHEUS_MODEL_PATH", "./models/orpheus"),
		SupabaseURL:        getEnv("SUPABASE_URL", ""),
		SupabaseKey:        getEnv("SUPABASE_KEY", ""),
		SupabaseBucket:     getEnv("SUPABASE_BUCKET", "voice-files"),
		SampleRate:  getIntEnv("SAMPLE_RATE", 16000),
		BitDepth:    getIntEnv("BIT_DEPTH", 16),
		Channels:    getIntEnv("CHANNELS", 1),
		Bitrate:     getIntEnv("BITRATE", 32),
		MaxFileSize: getInt64Env("MAX_FILE_SIZE", 10*1024*1024),
		MaxDuration: getDurationEnv("MAX_DURATION", "30s"),
		QueueWorkers: getIntEnv("QUEUE_WORKERS", 10),
		QueueSize:    getIntEnv("QUEUE_SIZE", 1000),
		WSReadBuffer:  getIntEnv("WS_READ_BUFFER", 1024),
		WSWriteBuffer: getIntEnv("WS_WRITE_BUFFER", 1024),
		WSMaxMessage:  getInt64Env("WS_MAX_MESSAGE", 10*1024*1024),
	}
}

func getEnv(key, defaultVal string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultVal
}

func getIntEnv(key string, defaultVal int) int {
	if val := os.Getenv(key); val != "" {
		if i, err := strconv.Atoi(val); err == nil {
			return i
		}
	}
	return defaultVal
}

func getInt64Env(key string, defaultVal int64) int64 {
	if val := os.Getenv(key); val != "" {
		if i, err := strconv.ParseInt(val, 10, 64); err == nil {
			return i
		}
	}
	return defaultVal
}

func getDurationEnv(key string, defaultVal string) time.Duration {
	if val := os.Getenv(key); val != "" {
		if d, err := time.ParseDuration(val); err == nil {
			return d
		}
	}
	d, _ := time.ParseDuration(defaultVal)
	return d
}
