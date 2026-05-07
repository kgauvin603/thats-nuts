# That’s Nuts Web Companion

Static React + Vite + TypeScript companion site for the That’s Nuts project. This app is intended to build into static files and be served directly by Nginx, not by a persistent Node service.

## Local development

Prerequisite: Node.js 18+ and npm available on your shell path.

```bash
cd web
npm install
npm run dev
```

The default Vite dev server is suitable for local testing only. Production should use the generated static files.

## Build for production

```bash
cd web
npm install
npm run build
```

The production output is written to `web/dist`.

You can preview the built app locally with:

```bash
cd web
npm run preview
```

## Test

```bash
cd web
npm test
```

Current tests cover:

- disclaimer gating before agreement
- disclaimer acceptance persistence
- default API base URL
- product image rendering and placeholder fallback

## API base URL

The app defaults to:

```text
https://api.thatsnuts.activeadvantage.co
```

Override it for local or staging use with:

```bash
VITE_API_BASE_URL=https://api.example.com npm run dev
```

or a `.env` file such as:

```bash
VITE_API_BASE_URL=https://api.example.com
```

## Backend routes used

- Barcode lookup: `POST /lookup-product`
- Manual ingredient review: `POST /check-ingredients`

These route names were discovered from the existing backend source under `backend/app/api/routes/`.

## Production deployment notes

Preferred production pattern:

```text
https://thatsnuts.activeadvantage.co
  -> Nginx 443
  -> /mnt/apps/ThatsNuts/web/dist static files
```

Suggested deployment flow on OEL9:

1. Build locally or on a build host with `npm install && npm run build`.
2. Copy the `web/` directory or at minimum `web/dist` and the deployment example into `/mnt/apps/ThatsNuts/web/`.
3. Install an Nginx server block based on `deploy/nginx-thatsnuts-site.conf.example`.
4. Point the `root` directive at `/mnt/apps/ThatsNuts/web/dist`.
5. Reload Nginx after validating the config with `nginx -t`.

This app does not require a new systemd unit, a public Node port, or a long-running frontend server.

## HTTPS / Certbot note

This repository only includes an example Nginx file. It does not modify live Nginx or certificates.

When you install the site on the server, add the HTTPS server block and Certbot-managed certificate directives separately as part of your normal production process.
