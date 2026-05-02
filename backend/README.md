# Backend

FastAPI backend for the Thats Nuts MVP.

## Current endpoints

- `GET /health`
- `POST /check-ingredients`
- `POST /lookup-product`
- `POST /enrich-product`
- `GET /scan-history`
- `GET /test-ui`

## Reliable local run flow

The recommended entry point is the shared helper script:

```bash
./scripts/run_backend.sh
```

What it does:

- loads `backend/.env` if it exists
- creates `backend/.venv` if missing
- installs dependencies only when `requirements.txt` changes
- starts the backend on `APP_HOST` / `APP_PORT`
- defaults to port `8002`
- runs without `--reload` unless `APP_RELOAD=true`

For local development with code reload:

```bash
APP_RELOAD=true ./scripts/run_backend.sh
```

## Oracle Linux 9 run steps

From the repository root on Oracle Linux 9:

```bash
sudo dnf install -y python3 python3-pip git
cp backend/.env.example backend/.env
./scripts/run_backend.sh
```

Then verify:

```bash
curl http://127.0.0.1:8002/health
```

If you want the backend bound only to localhost for a single-machine deployment, set this in `backend/.env`:

```bash
APP_HOST=127.0.0.1
```

## Environment file

Use [backend/.env.example](/mnt/apps/ThatsNuts/backend/.env.example) as the reference configuration.

Recommended stable local defaults:

```bash
APP_HOST=0.0.0.0
APP_PORT=8002
APP_RELOAD=false
APP_LOG_LEVEL=info
INSTALL_DEPS=true
DATABASE_URL=sqlite:///./thatsnuts.db
DATABASE_AUTO_CREATE=true
DATABASE_SEED_DATA=true
PRODUCT_LOOKUP_PROVIDER=food_then_beauty
PRODUCT_LOOKUP_BEAUTY_BASE_URL=https://world.openbeautyfacts.org
PRODUCT_LOOKUP_FOOD_BASE_URL=https://world.openfoodfacts.org
PRODUCT_LOOKUP_BASE_URL=https://world.openfoodfacts.org
PRODUCT_LOOKUP_API_KEY=
PRODUCT_LOOKUP_USER_AGENT="thats-nuts-backend/0.1 (contact@example.com)"
PRODUCT_LOOKUP_TIMEOUT_SECONDS=5.0
```

The app itself does not load dotenv files automatically. The helper script does.

## Systemd example

For a long-running local service, create `/etc/systemd/system/thats-nuts-backend.service`:

```ini
[Unit]
Description=Thats Nuts backend
After=network.target

[Service]
Type=simple
User=opc
Group=opc
WorkingDirectory=/mnt/apps/ThatsNuts
Environment=APP_ENV_FILE=/mnt/apps/ThatsNuts/backend/.env
Environment=INSTALL_DEPS=false
ExecStart=/mnt/apps/ThatsNuts/scripts/run_backend.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now thats-nuts-backend
sudo systemctl status thats-nuts-backend
```

Recommended service settings in `backend/.env`:

```bash
APP_HOST=0.0.0.0
APP_PORT=8002
APP_RELOAD=false
APP_LOG_LEVEL=info
DATABASE_URL=sqlite:///./thatsnuts.db
DATABASE_AUTO_CREATE=true
DATABASE_SEED_DATA=true
PRODUCT_LOOKUP_PROVIDER=beauty_then_food
PRODUCT_LOOKUP_BEAUTY_BASE_URL=https://world.openbeautyfacts.org
PRODUCT_LOOKUP_FOOD_BASE_URL=https://world.openfoodfacts.org
```

For service operation, leave `APP_RELOAD=false`. Set `INSTALL_DEPS=false` in the unit once the environment is installed and stable.

## Internal test UI

For manual backend testing without the mobile app, open:

```bash
http://127.0.0.1:8002/test-ui
```

The page is intentionally minimal and uses the live backend routes directly:

- refresh `/health` and confirm the active provider mode shown from backend config
- paste an ingredient list and submit `/check-ingredients`
- submit a barcode to test `/lookup-product`
- refresh recent `/scan-history`
- inspect persisted products through `/saved-products`, including filterable barcode/brand/product search
- inspect both human-readable summaries and raw JSON responses for each tool

No separate frontend build step is required.

## Database setup

The backend uses `SQLModel` and includes persistence for:

- `products`
- `ingredients`
- `ingredient_aliases`
- `ingredient_nut_mappings`
- `ingredient_mappings`
- `allergy_profiles`
- `scan_history`

By default, the app uses a local SQLite database:

```bash
DATABASE_URL=sqlite:///./thatsnuts.db
```

To run against PostgreSQL instead, update `backend/.env`:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5432/thatsnuts
```

When `DATABASE_AUTO_CREATE=true`, the app attempts to create tables on startup. When `DATABASE_SEED_DATA=true`, the seed ingredient rules are mirrored into the database tables on startup. If the database is unavailable, startup continues so the health endpoint and current ingredient checking flow still run.

The live ingredient rules engine still reads from the JSON seed file at runtime, so persistence does not change the current matching contract.

## Product lookup abstraction

The backend includes a small provider abstraction for barcode-based product lookup.

- `ProductLookupProvider` defines the lookup interface
- `StubProductLookupProvider` returns placeholder normalized product data
- `MockApiProductLookupProvider` shows the normalization seam for a future external provider
- `OpenFoodFactsProductLookupProvider` integrates with a real external barcode data source
- `ProductLookupService` wraps the provider and returns a stable response shape

Provider configuration is environment-variable based so secrets stay out of source control:

```bash
PRODUCT_LOOKUP_PROVIDER=beauty_then_food
PRODUCT_LOOKUP_BEAUTY_BASE_URL=https://world.openbeautyfacts.org
PRODUCT_LOOKUP_FOOD_BASE_URL=https://world.openfoodfacts.org
# Legacy alias for the food provider base URL:
# PRODUCT_LOOKUP_BASE_URL=https://world.openfoodfacts.org
PRODUCT_LOOKUP_API_KEY=
PRODUCT_LOOKUP_USER_AGENT="thats-nuts-backend/0.1 (contact@example.com)"
PRODUCT_LOOKUP_TIMEOUT_SECONDS=5.0
```

Current provider options:

- `stub`
- `mock_api`
- `open_beauty_facts`
- `open_food_facts`
- `food_then_beauty`
- `beauty_then_food` (legacy alias for `food_then_beauty`)

Production default behavior:

- normalize the submitted barcode
- Open Food Facts first
- Open Beauty Facts second
- saved manual/text-scan enrichment data only as the final fallback

The chained provider returns the first provider result with usable ingredient data. If Open Food Facts does not return usable ingredients, the service falls through to Open Beauty Facts before considering saved enrichment data.

## Demo barcodes

For reliable local demos, the repository includes a small checked-in dataset at
[demo_barcodes.json](/mnt/apps/ThatsNuts/backend/app/data/demo_barcodes.json).

The current `/lookup-product` flow checks the local product cache before calling the configured provider, so preloading this dataset gives deterministic demo results without changing runtime lookup behavior.

Each dataset entry is intentionally lightweight and includes:

- `barcode`
- `product_name`
- `expected_status`
- `reason`

It covers one known barcode for each current assessment outcome:

- `contains_nut_ingredient`
- `possible_nut_derived_ingredient`
- `no_nut_ingredient_found`
- `cannot_verify`

The recommended flow is:

```bash
cp backend/.env.example backend/.env
./scripts/run_backend.sh
backend/.venv/bin/python scripts/load_demo_barcodes.py
```

Why this works:

- the helper writes the demo products into the existing local `products` cache
- `/lookup-product` already checks that cache before calling the configured provider
- runtime provider behavior stays unchanged

To print the known barcodes without writing to the database:

```bash
backend/.venv/bin/python scripts/load_demo_barcodes.py --list-only
```

You can then test them through the API or the internal test UI:

```bash
curl -X POST http://127.0.0.1:8002/lookup-product \
  -H "Content-Type: application/json" \
  -d '{"barcode":"9900000000001"}'
```

Known demo outcomes in the shipped dataset:

- `9900000000001` -> `contains_nut_ingredient`
- `9900000000002` -> `possible_nut_derived_ingredient`
- `9900000000003` -> `no_nut_ingredient_found`
- `9900000000004` -> `cannot_verify`

For a quick reference without loading anything into the database:

```bash
backend/.venv/bin/python scripts/load_demo_barcodes.py --list-only
```
