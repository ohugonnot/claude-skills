#!/usr/bin/env bash
# A small uncommitted change, so the prompt has something to review.
set -euo pipefail
git init -q -b main .
cat > amount.go <<'GO'
package amount

func Cents(units int) int { return units * 100 }
GO
git add -A && git -c user.name=dev -c user.email=dev@example.com commit -qm "base"
cat > amount.go <<'GO'
package amount

func Cents(units int) int { return units * 100 }

func Split(total, parts int) int { return total / parts }
GO
