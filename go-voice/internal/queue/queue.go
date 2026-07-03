package queue

import (
	"context"
	"fmt"
	"sync"
	"time"

	"singhji-voice-go/internal/config"

	"go.uber.org/zap"
)

type System struct {
	cfg      *config.Config
	logger   *zap.Logger
	workers  int
	jobs     chan Job
	wg       sync.WaitGroup
	ctx      context.Context
	cancel   context.CancelFunc
}

type Job struct {
	ID        string
	Type      string
	Data      interface{}
	Result    chan Result
	CreatedAt time.Time
}

type Result struct {
	Data  interface{}
	Error error
}

func NewSystem(cfg *config.Config, logger *zap.Logger) *System {
	ctx, cancel := context.WithCancel(context.Background())

	s := &System{
		cfg:     cfg,
		logger:  logger,
		workers: cfg.QueueWorkers,
		jobs:    make(chan Job, cfg.QueueSize),
		ctx:     ctx,
		cancel:  cancel,
	}

	for i := 0; i < s.workers; i++ {
		s.wg.Add(1)
		go s.worker(i)
	}

	logger.Info("Queue system started", zap.Int("workers", s.workers), zap.Int("size", cfg.QueueSize))
	return s
}

func (s *System) worker(id int) {
	defer s.wg.Done()

	for {
		select {
		case <-s.ctx.Done():
			s.logger.Info("Worker stopped", zap.Int("id", id))
			return
		case job := <-s.jobs:
			s.logger.Info("Processing job",
				zap.Int("worker", id),
				zap.String("job_id", job.ID),
				zap.String("type", job.Type))

			result := s.processJob(job)

			select {
			case job.Result <- result:
			case <-time.After(10 * time.Second):
				s.logger.Warn("Job result timeout", zap.String("job_id", job.ID))
			}
		}
	}
}

func (s *System) processJob(job Job) Result {
	switch job.Type {
	case "stt":
		return s.processSTT(job)
	case "tts":
		return s.processTTS(job)
	case "translate":
		return s.processTranslate(job)
	case "voice_clone":
		return s.processVoiceClone(job)
	default:
		return Result{Error: fmt.Errorf("unknown job type: %s", job.Type)}
	}
}

func (s *System) processSTT(job Job) Result {
	return Result{Data: "STT processed"}
}

func (s *System) processTTS(job Job) Result {
	return Result{Data: "TTS processed"}
}

func (s *System) processTranslate(job Job) Result {
	return Result{Data: "Translation processed"}
}

func (s *System) processVoiceClone(job Job) Result {
	return Result{Data: "Voice clone processed"}
}

func (s *System) Submit(job Job) (chan Result, error) {
	select {
	case s.jobs <- job:
		resultChan := make(chan Result, 1)
		job.Result = resultChan
		return resultChan, nil
	case <-time.After(5 * time.Second):
		return nil, fmt.Errorf("queue full, job rejected")
	}
}

func (s *System) Stop() {
	s.cancel()
	s.wg.Wait()
	close(s.jobs)
	s.logger.Info("Queue system stopped")
}
