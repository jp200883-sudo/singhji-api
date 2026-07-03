package stt

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

type STTResponse struct {
	Success bool   `json:"success"`
	Text    string `json:"text,omitempty"`
	Error   string `json:"error,omitempty"`
}

func HandleSTT(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	
	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(STTResponse{Success: false, Error: "POST only"})
		return
	}
	
	if err := r.ParseMultipartForm(10 << 20); err != nil {
		json.NewEncoder(w).Encode(STTResponse{Success: false, Error: "Parse failed"})
		return
	}
	
	file, _, err := r.FormFile("audio")
	if err != nil {
		json.NewEncoder(w).Encode(STTResponse{Success: false, Error: "Audio required"})
		return
	}
	defer file.Close()
	
	lang := r.FormValue("language")
	if lang == "" {
		lang = "hi"
	}
	
	tmpDir := os.TempDir()
	inputFile := filepath.Join(tmpDir, fmt.Sprintf("stt_%d.wav", os.Getpid()))
	
	out, _ := os.Create(inputFile)
	io.Copy(out, file)
	out.Close()
	
	cmd := exec.Command("whisper",
		inputFile,
		"--model", "base",
		"--language", lang,
		"--output_format", "txt",
		"--output_dir", tmpDir,
	)
	
	cmd.Run()
	
	outputFile := inputFile + ".txt"
	textData, _ := os.ReadFile(outputFile)
	
	os.Remove(inputFile)
	os.Remove(outputFile)
	
	json.NewEncoder(w).Encode(STTResponse{
		Success: true,
		Text:    string(textData),
	})
}
