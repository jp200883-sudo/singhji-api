# Singh Ji AI Voice Server v7.0
# Go = 10x Speed | Zero Cost | 306 Languages

FROM golang:1.22-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache git ffmpeg opus-dev

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o voice-server ./cmd/voice-server

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates ffmpeg opus

WORKDIR /root/

COPY --from=builder /app/voice-server .

EXPOSE 8080

ENV PORT=8080
ENV ENV=production

CMD ["./voice-server"]
