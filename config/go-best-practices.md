# Go Best Practices

> Référence — consulter lors de reviews ou en cas de doute.

## Simplicité d'abord
- Fonctions courtes (20-30 lignes max), 2-3 params max, sinon struct
- Early return + guard clauses, jamais de nesting profond
- Accept interfaces, return structs
- "A little copying is better than a little dependency" — ne pas abstraire pour 2 usages
- Make the zero value useful
- 1 fichier si < 500 lignes et cohésion forte
- Newspaper layout : publics en haut, helpers privés en bas

## Error Handling
```go
// ✅ Wrapper avec contexte
return fmt.Errorf("failed to process item %s: %w", itemID, err)
// ✅ errors.Is / errors.As — pas type assertions
// ❌ return err — perd le contexte
// ❌ panic(err) — sur erreurs normales
```

### Resilient Execution (partial success > total failure)
```go
for _, item := range items {
    if err := process(item); err != nil {
        slog.Error("Failed item, continuing", "item", item.ID, "error", err)
        continue
    }
    successCount++
}
```

## Concurrency
```go
// Goroutine avec exit propre
go func() {
    for {
        select {
        case val := <-ch: process(val)
        case <-ctx.Done(): return
        }
    }
}()

// Mutex pour shared data
type SafeCounter struct {
    mu    sync.Mutex
    count int
}
func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

## PostgreSQL
```go
// ✅ Prepared statements (jamais string concatenation)
err := db.GetContext(ctx, &user, "SELECT * FROM users WHERE email = $1", email)
// Transaction : defer tx.Rollback() avant les opérations, tx.Commit() à la fin
```

## Context
- Toujours propager `ctx` — jamais remplacer par `context.Background()`

## Testing
```go
// Stdlib testing uniquement — PAS testify — assertions manuelles
// Table-driven avec → dans les noms
tests := []struct {
    name    string
    input   string
    wantErr bool
}{
    {"valid → ok", "ok", false},
    {"empty → error", "", true},
}
```

## Anti-Patterns
- `file, _ := os.Open(...)` — ne jamais ignorer les erreurs
- Naked returns dans fonctions > 10 lignes
- `close(ch)` oublié → goroutine leak
- Interface avec 1 seule implémentation (YAGNI)
- God object / struct qui fait tout
- `map[string]string` non trié → non-déterministe, `sort.Strings` avant join
- Magic numbers → constantes nommées
- Code mort/commenté → supprimer (Git garde l'historique)
- Logging `log.Printf` → `slog.Info("msg", "key", val)`
