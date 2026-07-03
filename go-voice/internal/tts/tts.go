package tts

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

type TTSRequest struct {
	Text     string `json:"text"`
	Language string `json:"language"`
	Voice    string `json:"voice,omitempty"`
}

func HandleTTS(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	
	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(map[string]bool{"success": false})
		return
	}
	
	var req TTSRequest
	json.NewDecoder(r.Body).Decode(&req)
	
	if req.Text == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "Text required"})
		return
	}
	
	voiceMap := map[string]string{
		"hi": "hi-IN-SwaraNeural",
		"en": "en-US-AriaNeural",
		"pa": "pa-IN",
		"ta": "ta-IN",
		"te": "te-IN",
		"bn": "bn-IN",
		"mr": "mr-IN",
		"gu": "gu-IN",
		"kn": "kn-IN",
		"ml": "ml-IN",
	}
	
	voice := voiceMap[req.Language]
	if voice == "" {
		voice = "hi-IN-SwaraNeural"
	}
	
	tmpDir := os.TempDir()
	outputFile := filepath.Join(tmpDir, fmt.Sprintf("tts_%d.mp3", os.Getpid()))
	
	cmd := exec.Command("edge-tts",
		"--text", req.Text,
		"--voice", voice,
		"--write-media", outputFile,
	)
	
	if err := cmd.Run(); err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}
	
	audioData, err := os.ReadFile(outputFile)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": "Read failed"})
		return
	}
	
	os.Remove(outputFile)
	
	w.Header().Set("Content-Type", "audio/mpeg")
	w.Write(audioData)
}
