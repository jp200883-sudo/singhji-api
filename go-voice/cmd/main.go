package main

import (
	"log"
	"net/http"
	"os"
	
	"singhji-ai/go-voice/internal/ai"
	"singhji-ai/go-voice/internal/stt"
	"singhji-ai/go-voice/internal/tts"
)

func healthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"status":"ok","version":"7.0","service":"singhji-voice"}`))
}

func main() {
	http.HandleFunc("/health", healthCheck)
	http.HandleFunc("/go-voice/tts", tts.HandleTTS)
	http.HandleFunc("/go-voice/stt", stt.HandleSTT)
	http.HandleFunc("/go-voice/ai-brain", ai.HandleAIBrain)
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	
	log.Printf("🎙️ Singh Ji Voice Server v7.0 starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
