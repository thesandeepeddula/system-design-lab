import os
import asyncpg
from fastapi import FastAPI, HTTPException

app = FastAPI(title="System Design Lab")
DATABASE_URL = os.environ["DATABASE_URL"]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/db")
async def health_db():
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=3)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        return {"database": "ok", "version": version}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"database unavailable: {type(e).__name__}: {e!r}",
        )