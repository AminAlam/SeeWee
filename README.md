## SeeWee

SeeWee is an open-source **CV manager**. You enter structured experiences, projects, publications, awards, and volunteering once, then generate multiple **CV variants** and export them to:

- **LaTeX** (`.tex` bundle)
- **HTML** (a small React-based static viewer)
- **LinkedIn-friendly** exports (copy blocks + CSV/JSON for manual entry)

### Architecture

- **Frontend**: Next.js (browser UI)
- **Backend**: FastAPI (Python) managing a **local SQLite DB file**
- **Install**: Docker Compose

### Quickstart (Docker)

```bash
docker compose up --build
```

- Web UI: `http://localhost:3000`
- API health: `http://localhost:8000/health`

SQLite lives in a Docker volume mounted at `/data/seewee.db` inside the API container.

### MVP Usage

1. Open `http://localhost:3000`
2. Go to **Entries** and create a few entries (type + JSON + tags)
3. Go to **Variants** and create a variant (sections + rules JSON)
4. Use **Preview** and export buttons:
   - Export **LaTeX**: downloads a zip with `main.tex`
   - Export **HTML**: downloads a zip with `index.html` + `app.js`
   - Export **LinkedIn**: downloads a zip with `linkedin_experience.csv` + `copy_blocks.txt`

### LLM integrations (foundation)

The backend exposes stubbed endpoints so we can plug in hosted providers and/or Ollama later:

- `POST /llm/rewrite_bullets`
- `POST /llm/suggest_keywords`
- `POST /llm/consistency_check`

Controlled by `SEEWEE_LLM_MODE=hosted|ollama|both` (default in `docker-compose.yml` is `both`).

### Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).


