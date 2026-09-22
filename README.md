# system-design-lab
# Progress

## Week 1 - Session 1 (done)
- FastAPI + Postgres 16 via Docker Compose in Codespaces
- Split liveness (/health) from readiness (/health/db)
- Learned: containers, DNS service discovery, volumes, stateless vs stateful

## Gotchas
- Codespaces: legacy iptables FORWARD policy is DROP, so container-to-container
  SYN packets are dropped (only RELATED,ESTABLISHED allowed). Symptom: DNS
  resolves, TCP times out silently.
  Fix: sudo iptables-legacy -P FORWARD ACCEPT
  Automated in .devcontainer/devcontainer.json postStartCommand.