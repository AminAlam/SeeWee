## Contributing to SeeWee

### Development (Docker)

```bash
docker compose up --build
```

### Project layout

- `apps/web`: Next.js UI
- `backend`: FastAPI + core modules + migrations
- `docker`: Dockerfiles

### How to contribute

- Open an issue first for larger changes.
- Keep PRs small and focused.
- Add/adjust API endpoints in `backend/api/routers`.
- Keep domain/export logic in `backend/core`.


