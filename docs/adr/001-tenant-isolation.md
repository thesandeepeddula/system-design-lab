# ADR 001: Tenant Isolation Model

## Status
Accepted — 2026-09-23

## Context
Multiple customer organizations share one deployment. Data must never
leak across tenants. ~100 tenants expected, each small.

## Options Considered

### A. Shared tables with tenant_id column
+ Cheapest; one migration for all; instant tenant creation
- One forgotten WHERE clause leaks data across customers
- Noisy neighbours share resources

### B. Schema per tenant
+ Stronger separation; per-tenant backup is easy
- Migrations must run N times; connection pooling gets complex

### C. Database per tenant
+ Strongest isolation; per-tenant performance and compliance
- Expensive; slow provisioning; heavy operations
  (this is roughly the ServiceNow instance model)

## Decision
Option A, plus Postgres Row-Level Security.

RLS moves the isolation guarantee out of application code and into the
database. Even a query with no WHERE clause returns zero foreign rows.
The app filters AND the database enforces: defense in depth.

## Consequences
- Every tenant-scoped table carries tenant_id and has an RLS policy
- Each request sets app.tenant_id inside its transaction
- The app must connect as a NON-owner role, because table owners bypass RLS
- Noisy neighbours must be handled separately (rate limits, week 7)
- Tests must include a cross-tenant leakage test

## When we would revisit
- A customer contractually requires physical isolation → Option C for them
- A single tenant exceeds ~20% of total load → dedicated shard (week 10)
- Tenant count exceeds ~10,000 → revisit indexing and partitioning strategy