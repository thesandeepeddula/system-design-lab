# Design: Multi-tenant Document Q&A Platform

## 1. Functional Requirements

### Must have (v1)
- A user can register and log in
- A user can create a tenant and invite others to it
- A user can belong to multiple tenants and switch between them
- A member can upload a PDF to their tenant
- Uploaded documents are processed into searchable chunks
- A user can search their tenant's documents (keyword + semantic)
- A user can ask a question and get an answer with citations
- A user can see the processing status of their documents

### Nice to have (later)
- Document deletion and re-processing
- Usage analytics per tenant

## 2. Non-Goals (explicitly out of scope)
- Real-time collaborative editing
- Formats other than PDF
- Mobile apps
- Billing and payments
- SSO / SAML


## 3. Non-Functional Requirements

| Property | Target | Why it matters |
|---|---|---|
| Search latency | p95 < 500ms | Drives caching + index choice |
| Upload response | p95 < 200ms | Forces async processing |
| Doc processing | < 2 min for a 50-page PDF | Sets worker count |
| Availability | 99.5% (~3.6h downtime/month) | Learning project, not banking |
| Isolation | A tenant must never read another's data | Drives RLS |
| Durability | No uploaded document is ever lost | Drives object storage + retries |
| Consistency | Search may lag uploads by seconds | Eventual consistency is acceptable |


## 4. Capacity Estimation

### Assumptions
- 100 tenants
- 50 users per tenant → 5,000 users
- 1,000 documents per tenant → 100,000 documents
- Average document: 2 MB, 20 pages
- ~40 chunks per document (500 tokens each)
- Each user: 20 searches/day, 2 uploads/week

### Storage
- Raw PDFs: 100,000 × 2 MB = 200 GB
- Chunks: 100,000 × 40 = 4,000,000 chunks
- Chunk text: 4M × 2 KB = 8 GB
- Vectors (384-dim float32 = 1,536 bytes): 4M × 1.5 KB = 6 GB
- Metadata + indexes: ~2 GB
- Total DB: ~16 GB; Object storage: 200 GB

### Throughput
- Searches: 5,000 users × 20 = 100,000/day
  → 100,000 / 86,400 ≈ 1.2 QPS average
  → peak 10× = 12 QPS
- Uploads: 5,000 × 2 / 7 ≈ 1,430/day ≈ 0.02 QPS average
  → but bursty: a tenant may upload 500 docs at once

### Derived decisions
- 6 GB of vectors fits in RAM on one machine → pgvector is fine, no dedicated vector DB
- 12 QPS is low → a single well-indexed Postgres handles reads; caching is for latency, not capacity
- 200 GB of PDFs does NOT belong in Postgres → object storage (week 2)
- Upload bursts are the real risk → queue with backpressure (week 4)
- One worker at ~30s/doc handles ~2,800 docs/day → enough on average, too slow for bursts → scale workers horizontally


## 5. High-Level Architecture

Client
  │
  ▼
Load Balancer (nginx)         [week 2]
  │
  ▼
API (FastAPI, N replicas — stateless)
  │
  ├──> Postgres (users, tenants, docs, chunks, vectors)   [stateful]
  ├──> Redis (cache, rate limits, job status)             [week 3, 7]
  ├──> Object Storage / MinIO (raw PDFs)                  [week 2]
  └──> Queue ──> Workers (parse → chunk → embed)          [week 4]

Observability: Prometheus + Grafana + traces               [week 8]

## 6. Data Model (sketch)

users(id, email UNIQUE, password_hash, created_at)
tenants(id, name, plan, created_at)
memberships(user_id, tenant_id, role, PRIMARY KEY (user_id, tenant_id))
documents(id, tenant_id, filename, s3_key, status, created_at)
chunks(id, document_id, tenant_id, text, embedding, chunk_index)
refresh_tokens(id, user_id, token_hash, expires_at, revoked_at)

Document status: PENDING_UPLOAD → UPLOADED → QUEUED → PROCESSING → READY | FAILED

Notes:
- tenant_id is denormalized onto chunks (it's derivable via documents)
  so RLS and filtering work without a join
- memberships has a composite PK: a user joins a tenant at most once

