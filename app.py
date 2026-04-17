"""Web wrapper around emailchk.py — turns the CLI into a FastAPI service."""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from emailchk import FreeSession, check_email_api

app = FastAPI(title="Email Validator API", version="1.0.0")

_free_session: Optional[FreeSession] = None


def _free() -> FreeSession:
    global _free_session
    if _free_session is None:
        s = FreeSession()
        s._init_session()
        _free_session = s
    return _free_session


class CheckRequest(BaseModel):
    email: str
    api_key: Optional[str] = None
    mode: str = "auto"


class BulkRequest(BaseModel):
    emails: list[str]
    api_key: Optional[str] = None
    mode: str = "auto"


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/check")
def check(req: CheckRequest) -> dict:
    if not req.email.strip():
        raise HTTPException(400, "email is required")
    if req.api_key:
        return check_email_api(req.email, api_key=req.api_key, mode=req.mode)
    return _free().check(req.email)


@app.post("/api/check-bulk")
def check_bulk(req: BulkRequest) -> dict:
    emails = [e.strip() for e in req.emails if e and e.strip()]
    if not emails:
        raise HTTPException(400, "emails is required")
    if len(emails) > 50:
        raise HTTPException(400, "max 50 emails per request")

    results = []
    sess = None if req.api_key else _free()
    for e in emails:
        try:
            if req.api_key:
                results.append(check_email_api(e, api_key=req.api_key, mode=req.mode))
            else:
                results.append(sess.check(e))
        except Exception as ex:  # noqa: BLE001
            results.append({"email": e, "status": "error", "_error": str(ex)})
    return {"count": len(results), "results": results}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return INDEX_HTML


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Email Validator</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
         background: #0b0f14; color: #e6edf3; min-height: 100vh; }
  .wrap { max-width: 760px; margin: 0 auto; padding: 48px 20px; }
  h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: -0.01em; }
  p.lead { margin: 0 0 28px; color: #8b949e; font-size: 15px; }
  .card { background: #0f1620; border: 1px solid #1f2a37; border-radius: 14px; padding: 22px; }
  label { display: block; font-size: 13px; color: #9aa4af; margin: 12px 0 6px; }
  input, textarea, select {
    width: 100%; padding: 11px 13px; background: #0b121b; color: #e6edf3;
    border: 1px solid #233044; border-radius: 9px; font-size: 14px; font-family: inherit;
    outline: none;
  }
  input:focus, textarea:focus, select:focus { border-color: #34d399; }
  textarea { min-height: 110px; resize: vertical; }
  .row { display: flex; gap: 10px; }
  .row > * { flex: 1; }
  button {
    margin-top: 16px; width: 100%; padding: 12px 16px; background: #34d399; color: #04221a;
    border: 0; border-radius: 9px; font-weight: 600; font-size: 14px; cursor: pointer;
  }
  button:disabled { opacity: 0.6; cursor: not-allowed; }
  .tabs { display: flex; gap: 6px; margin: 0 0 16px; }
  .tab { padding: 8px 14px; background: #0f1620; border: 1px solid #1f2a37; border-radius: 999px;
         font-size: 13px; color: #9aa4af; cursor: pointer; }
  .tab.active { background: #103024; color: #34d399; border-color: #1f5c41; }
  pre { background: #05090d; border: 1px solid #1f2a37; border-radius: 9px; padding: 14px;
        overflow: auto; font-size: 12.5px; margin-top: 16px; max-height: 360px; }
  .hint { color: #6b7681; font-size: 12px; margin-top: 6px; }
  .pill { display: inline-block; padding: 3px 8px; border-radius: 999px;
          font-size: 11px; margin-right: 6px; }
  .pill.ok { background: #103024; color: #34d399; }
  .pill.bad { background: #2b1013; color: #f87171; }
  .pill.warn { background: #2b2510; color: #fbbf24; }
  a { color: #34d399; }
</style>
</head>
<body>
  <div class="wrap">
    <h1>Email Validator</h1>
    <p class="lead">Bulk email checker. Free mode works out of the box (100/day/IP).
      For API mode, paste a <a href="https://sonjj.com" target="_blank" rel="noopener">sonjj.com</a> key.</p>

    <div class="card">
      <div class="tabs">
        <div class="tab active" data-tab="single">Single</div>
        <div class="tab" data-tab="bulk">Bulk</div>
        <div class="tab" data-tab="api">REST API</div>
      </div>

      <div id="tab-single">
        <label>Email</label>
        <input id="email" placeholder="someone@example.com" autocomplete="off" />
        <div class="row">
          <div>
            <label>Mode</label>
            <select id="mode-single">
              <option value="auto">auto</option>
              <option value="disposable">disposable</option>
            </select>
          </div>
          <div>
            <label>API key (optional)</label>
            <input id="key-single" placeholder="leave empty for free mode" autocomplete="off" />
          </div>
        </div>
        <button id="btn-single">Check</button>
        <pre id="out-single" hidden></pre>
      </div>

      <div id="tab-bulk" hidden>
        <label>Emails (one per line, max 50)</label>
        <textarea id="emails" placeholder="a@example.com&#10;b@example.com"></textarea>
        <div class="row">
          <div>
            <label>Mode</label>
            <select id="mode-bulk">
              <option value="auto">auto</option>
              <option value="disposable">disposable</option>
            </select>
          </div>
          <div>
            <label>API key (optional)</label>
            <input id="key-bulk" placeholder="leave empty for free mode" autocomplete="off" />
          </div>
        </div>
        <button id="btn-bulk">Check all</button>
        <pre id="out-bulk" hidden></pre>
      </div>

      <div id="tab-api" hidden>
        <p style="color:#9aa4af;font-size:14px;line-height:1.6;margin:8px 0 0">
          Hit these endpoints directly.
        </p>
        <pre style="max-height:none">POST /api/check
Content-Type: application/json

{ "email": "foo@gmail.com", "api_key": null, "mode": "auto" }


POST /api/check-bulk
Content-Type: application/json

{ "emails": ["a@example.com","b@example.com"], "api_key": null, "mode": "auto" }


GET /api/health  →  { "status": "ok" }</pre>
      </div>
    </div>
  </div>

<script>
  const $ = (id) => document.getElementById(id);
  document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    ['single','bulk','api'].forEach(n => $('tab-' + n).hidden = n !== t.dataset.tab);
  });

  async function post(path, body) {
    const r = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return r.json();
  }

  $('btn-single').onclick = async () => {
    const email = $('email').value.trim();
    if (!email) return;
    const btn = $('btn-single');
    btn.disabled = true; btn.textContent = 'Checking...';
    const data = await post('/api/check', {
      email,
      api_key: $('key-single').value.trim() || null,
      mode: $('mode-single').value,
    });
    $('out-single').hidden = false;
    $('out-single').textContent = JSON.stringify(data, null, 2);
    btn.disabled = false; btn.textContent = 'Check';
  };

  $('btn-bulk').onclick = async () => {
    const lines = $('emails').value.split(/\\n/).map(s => s.trim()).filter(Boolean);
    if (!lines.length) return;
    const btn = $('btn-bulk');
    btn.disabled = true; btn.textContent = 'Checking...';
    const data = await post('/api/check-bulk', {
      emails: lines,
      api_key: $('key-bulk').value.trim() || null,
      mode: $('mode-bulk').value,
    });
    $('out-bulk').hidden = false;
    $('out-bulk').textContent = JSON.stringify(data, null, 2);
    btn.disabled = false; btn.textContent = 'Check all';
  };
</script>
</body>
</html>"""


if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "3000")))
