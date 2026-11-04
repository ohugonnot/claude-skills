#!/usr/bin/env bash
set -euo pipefail
CASE="$(cd "$(dirname "$0")" && pwd)"
git init -q -b main . && cp -r "$CASE/fixture/." .
git add -A && git -c user.name=dev -c user.email=dev@example.com commit -qm "base"
cp -r "$CASE/buggy/." .
