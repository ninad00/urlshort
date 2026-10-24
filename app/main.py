import os
import secrets

import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl


class MemoryStore:
    def __init__(self) -> None:
        self._d: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._d.get(key)

    def set(self, key: str, value: str) -> None:
        self._d[key] = value


def make_store():
    url = os.environ.get("REDIS_URL")
    return redis.Redis.from_url(url, decode_responses=True) if url else MemoryStore()


store = make_store()
app = FastAPI(title="shortlink")


class ShortenRequest(BaseModel):
    url: HttpUrl


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/shorten", status_code=201)
def shorten(req: ShortenRequest):
    code = secrets.token_urlsafe(4)
    store.set(code, str(req.url))
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def resolve(code: str):
    url = store.get(code)
    if url is None:
        raise HTTPException(status_code=404, detail="not found")
    return RedirectResponse(url, status_code=307)
