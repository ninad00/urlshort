import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="shortlink")
_store: dict[str, str] = {}


class ShortenRequest(BaseModel):
    url: HttpUrl


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/shorten", status_code=201)
def shorten(req: ShortenRequest):
    code = secrets.token_urlsafe(4)
    _store[code] = str(req.url)
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def resolve(code: str):
    if code not in _store:
        raise HTTPException(status_code=404, detail="not found")
    return RedirectResponse(_store[code], status_code=307)
