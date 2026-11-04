package report

import "os"

func Save(path string, body []byte) error {
	return os.WriteFile(path, body, 0o600)
}

func SaveAll(dir string, bodies map[string][]byte) {
	for name, body := range bodies {
		Save(dir+"/"+name, body) //nolint:errcheck
	}
}
