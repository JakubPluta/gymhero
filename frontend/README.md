# gymhero — frontend

React SPA for the gymhero API. Vite, TypeScript, Tailwind + shadcn/ui, TanStack Router/Query.

## Run

Needs the backend on `:8000` (`mise run dev` from the repo root).

```bash
cd frontend
npm install
npm run gen:api   # generate the typed API client from the running backend
npm run dev       # http://localhost:5173
```

Or, from the repo root: `mise run dev-full`.

## Scripts

- `dev` / `build` / `preview`
- `gen:api` — regenerate `src/api/schema.d.ts` after the API changes
- `test` · `lint` · `typecheck`

## Notes

- Dev hits the API through a Vite proxy (`/api` → `:8000`), so there's no CORS to set up.
- Auth: access token in memory, refresh token in `localStorage`, silent refresh on `401`.
- For production set `VITE_API_URL` (see `.env.example`).
