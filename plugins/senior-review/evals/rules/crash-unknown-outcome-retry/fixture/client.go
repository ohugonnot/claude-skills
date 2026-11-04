package payout

import "context"

// Bank sends money to an external provider. Send has a side effect on the provider.
type Bank interface {
	Send(ctx context.Context, account string, cents int64) (transferID string, err error)
	Find(ctx context.Context, transferID string) (status string, err error)
}
