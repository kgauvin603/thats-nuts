from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.config import settings

router = APIRouter()


HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Thats Nuts Internal Test UI</title>
    <style>
      :root {
        color-scheme: light;
        --page-bg: #f5f1e8;
        --card-bg: #ffffff;
        --card-border: #ddd6c8;
        --card-shadow: rgba(40, 33, 24, 0.08);
        --text-main: #231f18;
        --text-muted: #685f53;
        --surface-muted: #f7f4ee;
        --status-red: #c53b33;
        --status-red-bg: #fde8e6;
        --status-amber: #b87500;
        --status-amber-bg: #fff4dd;
        --status-green: #2f7d32;
        --status-green-bg: #e7f4e8;
        --status-gray: #6b7280;
        --status-gray-bg: #eef0f3;
      }
      * {
        box-sizing: border-box;
      }
      body {
        margin: 0;
        padding: 32px 16px 48px;
        background: linear-gradient(180deg, #f7f3eb 0%, var(--page-bg) 100%);
        color: var(--text-main);
        font-family: "Segoe UI", Helvetica, Arial, sans-serif;
        line-height: 1.45;
      }
      .page {
        max-width: 1120px;
        margin: 0 auto;
      }
      h1, h2, h3, h4, p {
        margin-top: 0;
      }
      .page-header {
        margin-bottom: 20px;
      }
      .page-header h1 {
        margin-bottom: 8px;
      }
      .page-header p {
        color: var(--text-muted);
        max-width: 780px;
      }
      .status-grid,
      .two-column {
        display: grid;
        gap: 16px;
      }
      .status-grid {
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        margin-bottom: 16px;
      }
      .two-column {
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      }
      .card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 10px 24px var(--card-shadow);
        margin-bottom: 16px;
      }
      .metric-label {
        display: block;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
      }
      .metric-value {
        font-size: 1.4rem;
        font-weight: 800;
      }
      .metric-note {
        margin-top: 10px;
        color: var(--text-muted);
        font-size: 0.95rem;
      }
      .toolbar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        margin-bottom: 12px;
      }
      textarea,
      input,
      button {
        font: inherit;
      }
      textarea,
      input {
        width: 100%;
        border: 1px solid #c9c1b3;
        border-radius: 12px;
        padding: 12px 14px;
        background: #fffdf9;
        color: var(--text-main);
      }
      textarea {
        min-height: 170px;
        resize: vertical;
      }
      button {
        border: 0;
        border-radius: 999px;
        padding: 10px 16px;
        cursor: pointer;
        background: #324438;
        color: white;
        font-weight: 700;
      }
      button.secondary {
        background: #e9e3d7;
        color: var(--text-main);
      }
      .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.86rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
      }
      .contains_nut_ingredient {
        background: var(--status-red-bg);
        color: var(--status-red);
      }
      .possible_nut_derived_ingredient {
        background: var(--status-amber-bg);
        color: var(--status-amber);
      }
      .no_nut_ingredient_found {
        background: var(--status-green-bg);
        color: var(--status-green);
      }
      .cannot_verify,
      .not_found,
      .unknown {
        background: var(--status-gray-bg);
        color: var(--status-gray);
      }
      .summary-panel {
        margin-top: 14px;
        border: 1px solid #e6dece;
        background: var(--surface-muted);
        border-radius: 14px;
        padding: 14px;
      }
      .summary-panel.empty {
        color: var(--text-muted);
      }
      .summary-grid {
        display: grid;
        grid-template-columns: 140px 1fr;
        gap: 8px 12px;
        margin-top: 12px;
      }
      .summary-grid div:nth-child(odd) {
        font-weight: 700;
        color: var(--text-muted);
      }
      .matched-list,
      .history-list,
      .saved-products-list {
        display: grid;
        gap: 12px;
        margin-top: 12px;
      }
      .matched-item,
      .history-item,
      .saved-product-item {
        border: 1px solid #e1d9cb;
        border-radius: 12px;
        padding: 12px;
        background: white;
      }
      .matched-item strong,
      .history-item strong,
      .saved-product-item strong {
        display: block;
        margin-bottom: 4px;
      }
      .matched-meta,
      .history-meta,
      .saved-product-meta {
        color: var(--text-muted);
        font-size: 0.94rem;
      }
      .saved-product-item details {
        margin-top: 10px;
      }
      .saved-product-toolbar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: flex-end;
      }
      .saved-product-toolbar .field {
        flex: 1 1 260px;
      }
      .saved-product-toolbar .field label {
        display: block;
        margin-bottom: 6px;
        font-weight: 700;
        color: var(--text-muted);
      }
      pre {
        margin: 14px 0 0;
        padding: 14px;
        border-radius: 14px;
        background: #1f1e1b;
        color: #f8f7f3;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-word;
      }
      details {
        margin-top: 12px;
      }
      summary {
        cursor: pointer;
        font-weight: 700;
        color: var(--text-muted);
      }
      .inline-note {
        color: var(--text-muted);
        font-size: 0.95rem;
      }
      @media (max-width: 720px) {
        .summary-grid {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <div class="page">
      <header class="page-header">
        <h1>Thats Nuts Internal Test UI</h1>
        <p>Operator page for exercising the live backend routes, checking provider behavior, and inspecting recent scan history without building a separate admin frontend.</p>
      </header>

      <section class="status-grid">
        <div class="card">
          <span class="metric-label">Backend Health</span>
          <div id="health-status" class="metric-value">Unknown</div>
          <div id="health-note" class="metric-note">Run the health check to confirm the API is reachable.</div>
          <div class="toolbar">
            <button id="health-submit" type="button">Refresh Health</button>
          </div>
        </div>
        <div class="card">
          <span class="metric-label">Environment</span>
          <div class="metric-value">__APP_ENVIRONMENT__</div>
          <div class="metric-note">Rendered from backend config for quick local verification.</div>
        </div>
        <div class="card">
          <span class="metric-label">Active Lookup Provider</span>
          <div class="metric-value">__PRODUCT_LOOKUP_PROVIDER__</div>
          <div class="metric-note">This is the configured provider mode currently loaded by the backend.</div>
        </div>
      </section>

      <div class="two-column">
        <section class="card">
          <h2>Manual Ingredient Check</h2>
          <p class="inline-note">Paste an ingredient list and submit it to the existing <code>/check-ingredients</code> route.</p>
          <label for="ingredient-text">Ingredient list</label>
          <textarea id="ingredient-text" placeholder="Water, Glycerin, Prunus Amygdalus Dulcis Oil"></textarea>
          <div class="toolbar">
            <button id="ingredient-submit" type="button">Check Ingredients</button>
            <button id="ingredient-reset" type="button" class="secondary">Clear</button>
          </div>
          <div id="ingredient-summary" class="summary-panel empty">No request yet.</div>
          <details>
            <summary>Raw JSON</summary>
            <pre id="ingredient-result">No request yet.</pre>
          </details>
        </section>

        <section class="card">
          <h2>Barcode Lookup Check</h2>
          <p class="inline-note">Submit a barcode to the existing <code>/lookup-product</code> route and inspect the normalized product payload plus assessment result.</p>
          <label for="barcode">Barcode</label>
          <input id="barcode" type="text" placeholder="0001234567890">
          <div class="toolbar">
            <button id="barcode-submit" type="button">Lookup Barcode</button>
            <button id="barcode-reset" type="button" class="secondary">Clear</button>
          </div>
          <div id="barcode-summary" class="summary-panel empty">No request yet.</div>
          <details>
            <summary>Raw JSON</summary>
            <pre id="barcode-result">No request yet.</pre>
          </details>
        </section>
      </div>

      <section class="card">
        <h2>Recent Scan History</h2>
        <p class="inline-note">Fetches the latest entries from <code>/scan-history</code>. Useful for verifying persistence after manual checks and barcode lookups.</p>
        <div class="toolbar">
          <button id="history-submit" type="button">Refresh History</button>
        </div>
        <div id="history-list" class="history-list">
          <div class="history-item">No history loaded yet.</div>
        </div>
      </section>

      <section class="card">
        <h2>Saved Products</h2>
        <p class="inline-note">Inspect products already persisted in the backend cache. Use the search box for a quick barcode, product, or brand filter.</p>
        <div class="saved-product-toolbar">
          <div class="field">
            <label for="saved-products-query">Filter</label>
            <input id="saved-products-query" type="text" placeholder="Search barcode, product, or brand">
          </div>
          <button id="saved-products-submit" type="button">Refresh Saved Products</button>
          <button id="saved-products-reset" type="button" class="secondary">Clear Filter</button>
        </div>
        <div id="saved-products-list" class="saved-products-list">
          <div class="saved-product-item">No saved products loaded yet.</div>
        </div>
      </section>
    </div>

    <script>
      async function requestJson(path, options) {
        const response = await fetch(path, options);
        let body;
        try {
          body = await response.json();
        } catch (error) {
          body = { error: "Response was not valid JSON." };
        }
        return { ok: response.ok, status: response.status, body };
      }

      function escapeHtml(value) {
        return String(value)
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#39;");
      }

      function showResult(elementId, result) {
        document.getElementById(elementId).textContent = JSON.stringify(result, null, 2);
      }

      function statusClass(status) {
        if (!status) {
          return "unknown";
        }
        return status;
      }

      function statusPill(status) {
        const safeStatus = status || "unknown";
        return `<div class="status-pill ${escapeHtml(statusClass(safeStatus))}">${escapeHtml(safeStatus)}</div>`;
      }

      function renderMatchedIngredients(items) {
        if (!items || !items.length) {
          return "<div class=\\"history-meta\\">No matched ingredients returned.</div>";
        }

        return `<div class="matched-list">${
          items.map((item) => `
            <div class="matched-item">
              <strong>${escapeHtml(item.original_text || item.normalized_name || "Unknown")}</strong>
              <div class="history-meta">Normalized: ${escapeHtml(item.normalized_name || "n/a")}</div>
              <div class="history-meta">Nut source: ${escapeHtml(item.nut_source || "unknown")} | Confidence: ${escapeHtml(item.confidence || "unknown")}</div>
              <div>${escapeHtml(item.reason || "No reason returned.")}</div>
            </div>
          `).join("")
        }</div>`;
      }

      function renderHealth(result) {
        const statusTarget = document.getElementById("health-status");
        const noteTarget = document.getElementById("health-note");

        if (!result.ok) {
          statusTarget.textContent = "Unavailable";
          noteTarget.textContent = `Health check failed with HTTP ${result.status}.`;
          return;
        }

        statusTarget.textContent = (result.body && result.body.status) || "Unknown";
        noteTarget.textContent = "Health route responded successfully.";
      }

      function renderIngredientSummary(result) {
        const target = document.getElementById("ingredient-summary");
        if (!result.ok) {
          target.className = "summary-panel";
          target.innerHTML = `<strong>Ingredient check failed.</strong><div class="history-meta">HTTP ${escapeHtml(result.status)}</div>`;
          return;
        }

        const body = result.body || {};
        target.className = "summary-panel";
        target.innerHTML = `
          <h3>Assessment Summary</h3>
          ${statusPill(body.status)}
          <div class="summary-grid">
            <div>Status</div><div>${escapeHtml(body.status || "unknown")}</div>
            <div>Explanation</div><div>${escapeHtml(body.explanation || "")}</div>
          </div>
          <h4>Matched Ingredients</h4>
          ${renderMatchedIngredients(body.matched_ingredients || [])}
        `;
      }

      function renderBarcodeSummary(result) {
        const target = document.getElementById("barcode-summary");
        if (!result.ok) {
          target.className = "summary-panel";
          target.innerHTML = `<strong>Barcode lookup failed.</strong><div class="history-meta">HTTP ${escapeHtml(result.status)}</div>`;
          return;
        }

        const body = result.body || {};
        const product = body.product || {};
        const status = body.assessment_result || (body.found ? "cannot_verify" : "not_found");
        target.className = "summary-panel";
        target.innerHTML = `
          <h3>Lookup Summary</h3>
          ${statusPill(status)}
          <div class="summary-grid">
            <div>Found</div><div>${escapeHtml(body.found ? "yes" : "no")}</div>
            <div>Product</div><div>${escapeHtml(product.product_name || "Not found")}</div>
            <div>Brand</div><div>${escapeHtml(product.brand_name || "Unknown")}</div>
            <div>Barcode</div><div>${escapeHtml(product.barcode || "")}</div>
            <div>Coverage</div><div>${escapeHtml(product.ingredient_coverage_status || "Unknown")}</div>
            <div>Source</div><div>${escapeHtml(product.source || "Unknown")}</div>
            <div>Ingredient Text</div><div>${escapeHtml(body.ingredient_text || "No ingredient text returned.")}</div>
            <div>Explanation</div><div>${escapeHtml(body.explanation || "")}</div>
          </div>
          <h4>Matched Ingredients</h4>
          ${renderMatchedIngredients(body.matched_ingredients || [])}
        `;
      }

      function renderHistory(result) {
        const historyList = document.getElementById("history-list");
        if (!result.ok) {
          historyList.innerHTML = `<div class="history-item">History request failed with HTTP ${escapeHtml(result.status)}.</div>`;
          return;
        }

        const items = (result.body && result.body.items) || [];
        if (!items.length) {
          historyList.innerHTML = '<div class="history-item">No scan history yet.</div>';
          return;
        }

        historyList.innerHTML = items.map((item) => {
          const title = item.product_name || "Manual ingredient check";
          const matched = item.matched_ingredient_summary
            ? `<div><strong>Matched Summary</strong><span>${escapeHtml(item.matched_ingredient_summary)}</span></div>`
            : "";
          return `
            <div class="history-item">
              <strong>${escapeHtml(title)}</strong>
              ${statusPill(item.assessment_status || "unknown")}
              <div class="summary-grid">
                <div>Barcode</div><div>${escapeHtml(item.barcode || "")}</div>
                <div>Scan Type</div><div>${escapeHtml(item.scan_type || "unknown")}</div>
                <div>Explanation</div><div>${escapeHtml(item.explanation || "")}</div>
                <div>Created</div><div>${escapeHtml(item.created_at || "Unknown")}</div>
              </div>
              ${matched}
            </div>
          `;
        }).join("");
      }

      function renderSavedProducts(result) {
        const target = document.getElementById("saved-products-list");
        if (!result.ok) {
          target.innerHTML = `<div class="saved-product-item">Saved products request failed with HTTP ${escapeHtml(result.status)}.</div>`;
          return;
        }

        const items = (result.body && result.body.items) || [];
        if (!items.length) {
          target.innerHTML = '<div class="saved-product-item">No saved products found.</div>';
          return;
        }

        target.innerHTML = items.map((item) => {
          const latestAssessment = item.latest_assessment_status
            ? `
              <div class="summary-grid">
                <div>Latest Assessment</div><div>${escapeHtml(item.latest_assessment_status)}</div>
                <div>Latest Scan</div><div>${escapeHtml(item.latest_scan_created_at || "Unknown")}</div>
                <div>Matched Summary</div><div>${escapeHtml(item.latest_matched_ingredient_summary || "None")}</div>
                <div>Assessment Note</div><div>${escapeHtml(item.latest_assessment_explanation || "")}</div>
              </div>
            `
            : '<div class="saved-product-meta">No saved scan result is linked to this product yet.</div>';

          return `
            <div class="saved-product-item">
              <strong>${escapeHtml(item.product_name || "Unnamed product")}</strong>
              <div class="saved-product-meta">${escapeHtml(item.brand_name || "Unknown brand")}</div>
              <div class="summary-grid">
                <div>Barcode</div><div>${escapeHtml(item.barcode || "")}</div>
                <div>Source</div><div>${escapeHtml(item.source || "Unknown")}</div>
                <div>Coverage</div><div>${escapeHtml(item.ingredient_coverage_status || "Unknown")}</div>
                <div>Created</div><div>${escapeHtml(item.created_at || "Unknown")}</div>
                <div>Updated</div><div>${escapeHtml(item.updated_at || "Unknown")}</div>
              </div>
              <details>
                <summary>Inspect Product Details</summary>
                <div class="summary-grid">
                  <div>Ingredient Text</div><div>${escapeHtml(item.ingredient_text || "No ingredient text stored.")}</div>
                </div>
                ${latestAssessment}
                <details>
                  <summary>Raw Product JSON</summary>
                  <pre>${escapeHtml(JSON.stringify(item, null, 2))}</pre>
                </details>
              </details>
            </div>
          `;
        }).join("");
      }

      async function refreshHealth() {
        const result = await requestJson("/health", { method: "GET" });
        renderHealth(result);
      }

      async function refreshHistory() {
        document.getElementById("history-list").innerHTML = '<div class="history-item">Loading...</div>';
        const result = await requestJson("/scan-history?limit=10", { method: "GET" });
        renderHistory(result);
      }

      async function refreshSavedProducts() {
        const query = document.getElementById("saved-products-query").value.trim();
        const path = query
          ? `/saved-products?limit=20&q=${encodeURIComponent(query)}`
          : "/saved-products?limit=20";
        document.getElementById("saved-products-list").innerHTML = '<div class="saved-product-item">Loading...</div>';
        const result = await requestJson(path, { method: "GET" });
        renderSavedProducts(result);
      }

      document.getElementById("health-submit").addEventListener("click", refreshHealth);

      document.getElementById("ingredient-submit").addEventListener("click", async () => {
        const ingredientText = document.getElementById("ingredient-text").value;
        showResult("ingredient-result", { loading: true });
        document.getElementById("ingredient-summary").className = "summary-panel";
        document.getElementById("ingredient-summary").textContent = "Loading...";
        const result = await requestJson("/check-ingredients", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ingredient_text: ingredientText })
        });
        showResult("ingredient-result", result);
        renderIngredientSummary(result);
        refreshHistory();
      });

      document.getElementById("barcode-submit").addEventListener("click", async () => {
        const barcode = document.getElementById("barcode").value;
        showResult("barcode-result", { loading: true });
        document.getElementById("barcode-summary").className = "summary-panel";
        document.getElementById("barcode-summary").textContent = "Loading...";
        const result = await requestJson("/lookup-product", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ barcode })
        });
        showResult("barcode-result", result);
        renderBarcodeSummary(result);
        refreshHistory();
        refreshSavedProducts();
      });

      document.getElementById("history-submit").addEventListener("click", refreshHistory);
      document.getElementById("saved-products-submit").addEventListener("click", refreshSavedProducts);

      document.getElementById("ingredient-reset").addEventListener("click", () => {
        document.getElementById("ingredient-text").value = "";
      });

      document.getElementById("barcode-reset").addEventListener("click", () => {
        document.getElementById("barcode").value = "";
      });

      document.getElementById("saved-products-reset").addEventListener("click", () => {
        document.getElementById("saved-products-query").value = "";
        refreshSavedProducts();
      });

      refreshHealth();
      refreshHistory();
      refreshSavedProducts();
    </script>
  </body>
</html>
"""


def build_test_ui_html() -> str:
    return (
        HTML.replace("__APP_ENVIRONMENT__", settings.environment)
        .replace("__PRODUCT_LOOKUP_PROVIDER__", settings.product_lookup_provider)
    )


@router.get("/test-ui", response_class=HTMLResponse)
def render_test_ui() -> HTMLResponse:
    return HTMLResponse(content=build_test_ui_html())
