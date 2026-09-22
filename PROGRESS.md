# Progress

## Week 1 - Session 1 (done)
- FastAPI + Postgres 16 via Docker Compose in Codespaces
- Split liveness (/health) from readiness (/health/db)
- Learned: containers, DNS service discovery, volumes, stateless vs stateful

## Gotchas
- Codespaces: legacy iptables FORWARD policy is sometimes DROP, so new
  container-to-container connections are silently dropped (only
  RELATED,ESTABLISHED allowed). Symptom: DNS resolves, TCP times out.
  Check: sudo iptables-legacy -L FORWARD -n | head -1
  Fix:   sudo iptables-legacy -P FORWARD ACCEPT
- .env is gitignored, so recreate it in a fresh Codespace before compose up.
- Don't add a custom .devcontainer image; it broke Docker (landed on Alpine).
