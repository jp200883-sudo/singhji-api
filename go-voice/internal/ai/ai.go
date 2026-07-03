package ai

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type AIRequest struct {
	Message  string `json:"message"`
	Language string `json:"language,omitempty"`
	Model    string `json:"model,omitempty"`
}

type AIResponse struct {
	Success  bool   `json:"success"`
	Response string `json:"response,omitempty"`
	Error    string `json:"error,omitempty"`
}

func HandleAIBrain(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	
	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(AIResponse{Success: false, Error: "POST only"})
		return
	}
	
	var req AIRequest
	json.NewDecoder(r.Body).Decode(&req)
	
	if req.Message == "" {
		json.NewEncoder(w).Encode(AIResponse{Success: false, Error: "Message required"})
		return
	}
	
	model := req.Model
	if model == "" {
		model = "llama3-70b-8192"
	}
	
	groqKey := os.Getenv("GROQ_API_KEY")
	if groqKey == "" {
		json.NewEncoder(w).Encode(AIResponse{Success: false, Error: "GROQ key missing"})
		return
	}
	
	groqReq := map[string]interface{}{
		"model": model,
		"messages": []map[string]string{
			{"role": "system", "content": fmt.Sprintf("You are Singh Ji AI. Respond in %s.", req.Language)},
			{"role": "user", "content": req.Message},
		},
	}
	
	jsonData, _ := json.Marshal(groqReq)
	
	req2, _ := http.NewRequest("POST", "https://api.groq.com/openai/v1/chat/completions", bytes.NewBuffer(jsonData))
	req2.Header.Set("Authorization", "Bearer "+groqKey)
	req2.Header.Set("Content-Type", "application/json")
	
	client := &http.Client{}
	resp, err := client.Do(req2)
	if err != nil {
		json.NewEncoder(w).Encode(AIResponse{Success: false, Error: "Groq failed"})
		return
	}
	defer resp.Body.Close()
	
	var result struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}
	
	json.NewDecoder(resp.Body).Decode(&result)
	
	if len(result.Choices) == 0 {
		json.NewEncoder(w).Encode(AIResponse{Success: false, Error: "No response"})
		return
	}
	
	json.NewEncoder(w).Encode(AIResponse{
		Success:  true,
		Response: result.Choices[0].Message.Content,
	})
}
