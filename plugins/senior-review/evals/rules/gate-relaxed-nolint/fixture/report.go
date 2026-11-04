package report

import "os"

func Save(path string, body []byte) error {
	return os.WriteFile(path, body, 0o600)
}
