package payout

import (
	"context"
	"errors"
	"time"
)

func Pay(ctx context.Context, bank Bank, account string, cents int64) (string, error) {
	var lastErr error
	for attempt := 0; attempt < 3; attempt++ {
		callCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
		id, err := bank.Send(callCtx, account, cents)
		cancel()
		if err == nil {
			return id, nil
		}
		if !errors.Is(err, context.DeadlineExceeded) {
			return "", err
		}
		lastErr = err
	}
	return "", lastErr
}
