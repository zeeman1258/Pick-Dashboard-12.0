from flask import Flask, request, jsonify, render_template_string, session
import json, os, sqlite3, threading, webbrowser, time
from pathlib import Path
from datetime import date

app = Flask(__name__)
app.secret_key = 'analytics-secret-key-2026'
BASE_DIR = Path(__file__).parent
# Search for data folder - check all likely locations
_candidates = [
    BASE_DIR.parent / 'pick-dashboard-app-3.6.6' / 'pick-dashboard-app' / 'data',
    BASE_DIR.parent / 'pick-dashboard-app' / 'data',
    BASE_DIR.parent / 'data',
    BASE_DIR / 'data',
]
# Prefer existing folders with actual date subfolders, else use first existing, else default
DATA_DIR = None
for c in _candidates:
    if c.exists() and list(c.glob('20*')):
        DATA_DIR = c
        break
if DATA_DIR is None:
    DATA_DIR = next((c for c in _candidates if c.exists()), _candidates[0])
DATA_DIR.mkdir(parents=True, exist_ok=True)
print(f"[Analytics] Data dir: {DATA_DIR.absolute()}")

DB_PATH = BASE_DIR / 'analytics.db'

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
        item_id TEXT PRIMARY KEY, name TEXT, first_seen TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS daily_totals (
        item_id TEXT, date TEXT, warehouse TEXT, units INTEGER,
        PRIMARY KEY (item_id, date, warehouse))""")
    conn.commit()
    conn.close()

def update_db():
    conn = sqlite3.connect(str(DB_PATH))
    for date_dir in sorted(DATA_DIR.glob("20??-??-??")):
        d = date_dir.name
        for wh_file in date_dir.glob("*.json"):
            wh = wh_file.stem
            try:
                data = json.loads(wh_file.read_text())
                for item in data.get("items", []):
                    iid = str(item["item_id"])
                    name = item.get("description", "")
                    units = item.get("total_ordered", 0)
                    conn.execute("INSERT OR REPLACE INTO products VALUES (?,?,?)", (iid, name, d))
                    conn.execute("INSERT OR REPLACE INTO daily_totals VALUES (?,?,?,?)", (iid, d, wh, units))
            except Exception as e:
                print(f"Error: {e}")
    conn.commit()
    conn.close()

HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Analytics Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {theme: {extend: {colors: {
      bg: '#f7f6f2', surface: '#f9f8f5', text: '#28251d', muted: '#7a7974',
      primary: '#01696f', primary2: '#0c4e54', border: '#d4d1ca'
    }}}}
  </script>
  <style>
    body { font-family: ui-sans-serif, system-ui, sans-serif; background: var(--bg); color: var(--text); }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; }
    .metric { font-size: 2.5em; font-weight: 700; color: var(--primary); }
    .badge { background: var(--primary); color: white; padding: 4px 10px; border-radius: 999px; font-size: 13px; }
    canvas { max-height: 400px; }
  </style>
</head>
<body class="p-8 max-w-7xl mx-auto">
  <div class="mb-12">
    <h1 class="text-4xl font-bold mb-2">📊 Analytics Dashboard</h1>
    <p class="text-muted text-lg">Product performance across all saved routes</p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
    <div class="card text-center cursor-pointer p-8 hover:shadow-lg transition-all" onclick="showPanel('search')">
      <div class="text-3xl mb-2">🔍</div>
      <h3 class="font-bold text-xl mb-2">Product Search</h3>
      <p class="text-muted">Search & compare multiple products over time</p>
    </div>
    <div class="card text-center cursor-pointer p-8 hover:shadow-lg transition-all" onclick="showPanel('top')">
      <div class="text-3xl mb-2">🏆</div>
      <h3 class="font-bold text-xl mb-2">Top Products</h3>
      <p class="text-muted">Highest volume items by time range</p>
    </div>
    <div class="card text-center cursor-pointer p-8 hover:shadow-lg transition-all" onclick="showPanel('last')">
      <div class="text-3xl mb-2">📅</div>
      <h3 class="font-bold text-xl mb-2">Last Night</h3>
      <p class="text-muted">Yesterday's shipping summary</p>
    </div>
  </div>

  <div id="searchPanel" class="hidden">
    <div class="card">
      <div class="flex gap-4 items-end mb-6">
        <input id="productSearch" class="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Search products by name or ID...">
        <select id="searchRange" class="p-3 border border-gray-300 rounded-lg">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="365">Last year</option>
          <option value="9999">All time</option>
        </select>
        <button onclick="loadCompare()" class="btn px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Compare</button>
      </div>
      <div id="searchResults" class="max-h-64 overflow-y-auto mb-6"></div>
      <div id="selectedProducts" class="flex flex-wrap gap-2 mb-6"></div>
      <div id="compareChart"></div>
    </div>
  </div>

  <div id="topPanel" class="hidden">
    <div class="card">
      <div class="flex gap-4 items-end mb-6">
        <select id="topRange" class="p-3 border border-gray-300 rounded-lg">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="365">Last year</option>
          <option value="9999">All time</option>
        </select>
        <button onclick="loadTopProducts()" class="btn px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Load Top 25</button>
      </div>
      <canvas id="topChart" class="max-h-96"></canvas>
    </div>
  </div>

  <div id="lastPanel" class="hidden">
    <div class="card">
      <button onclick="loadLastNight()" class="btn mb-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Reload</button>
      <div id="lastNightContent"></div>
    </div>
  </div>

  <script>
    let products = {};
    let charts = {};
    let selected = {};

    function showPanel(id) {
      document.querySelectorAll('[id$="Panel"]').forEach(p => p.classList.add('hidden'));
      document.getElementById(id+'Panel').classList.remove('hidden');
    }

    async function loadProducts() {
      const r = await fetch('/api/products');
      products = await r.json();
    }

    async function searchProducts() {
      const q = document.getElementById('productSearch').value.toLowerCase();
      const results = document.getElementById('searchResults');
      if(q.length < 2) { results.innerHTML = ''; return; }
      await loadProducts();
      const matches = Object.entries(products)
        .filter(([id,name]) => id.includes(q) || name.toLowerCase().includes(q))
        .slice(0,20);
      results.innerHTML = matches.map(([id,name]) => 
        `<div class="p-3 border-b border-gray-200 hover:bg-gray-50 cursor-pointer" onclick="toggleProduct('${id}')">
          <div class="font-mono text-sm">${id}</div>
          <div>${name}</div>
        </div>`
      ).join('');
    }

    function toggleProduct(id) {
      if(selected[id]) delete selected[id];
      else selected[id] = products[id];
      renderSelected();
      document.getElementById('searchResults').innerHTML = '';
    }

    function renderSelected() {
      const el = document.getElementById('selectedProducts');
      el.innerHTML = Object.entries(selected).map(([id,name]) =>
        `<span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
          ${id}: ${name.slice(0,20)} 
          <button onclick="toggleProduct('${id}')" class="ml-2 font-bold">×</button>
        </span>`
      ).join('');
    }

    async function loadCompare() {
      const ids = Object.keys(selected);
      if(!ids.length) return alert('Select products first');
      const days = document.getElementById('searchRange').value;
      const r = await fetch(`/api/compare?ids=${ids.join(',')}&days=${days}`);
      // chart code here
      console.log('Compare:', ids, days);
    }

    async function loadTopProducts() {
      const days = document.getElementById('topRange').value;
      const r = await fetch(`/api/top-products?days=${days}`);
      const data = await r.json();
      // chart code here
      console.log('Top:', data);
    }

    async function loadLastNight() {
      const r = await fetch('/api/last-night');
      const data = await r.json();
      if(!data.date) {
        document.getElementById('lastNightContent').innerHTML = '<div class="text-gray-500 p-8 text-center">No saved routes yet</div>';
        return;
      }
      let total = 0;
      const table = data.items.map(item => {
        total += item.units;
        return `<tr><td class="font-mono">${item.id}</td><td>${item.name}</td><td class="text-right">${item.units.toLocaleString()}</td></tr>`;
      }).join('');
      document.getElementById('lastNightContent').innerHTML = `
        <div class="text-4xl font-bold mb-4">${total.toLocaleString()} units</div>
        <div class="text-muted mb-6">${data.date} across ${data.items.length} products</div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead><tr><th>Item ID</th><th>Name</th><th class="text-right">Units</th></tr></thead>
            <tbody>${table}</tbody>
          </table>
        </div>
      `;
    }

    document.getElementById('productSearch').addEventListener('input', (e) => {
      searchProducts(e.target.value);
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    print(f"[Analytics] Data dir: {DATA_DIR.absolute()}")
    print(f"[Analytics] Date folders found: {list(DATA_DIR.glob('20*'))}")
    update_db()
    return render_template_string(HTML)

@app.route("/api/products")
def api_products():
    update_db()
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("SELECT item_id, name FROM products ORDER BY name").fetchall()
    conn.close()
    return jsonify(dict(rows))

@app.route("/api/item/<item_id>")
def api_item(item_id):
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("SELECT date, warehouse, units FROM daily_totals WHERE item_id=? ORDER BY date", (item_id,)).fetchall()
    conn.close()
    return jsonify({"item_id": item_id, "records": [{"date":r[0],"warehouse":r[1],"units":r[2]} for r in rows]})

@app.route("/api/top-products")
def api_top():
    days = request.args.get("days", "7")
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("""
        SELECT p.item_id, p.name, SUM(dt.units) as total
        FROM products p JOIN daily_totals dt ON p.item_id=dt.item_id
        WHERE dt.date >= date('now', ? || ' days')
        GROUP BY p.item_id ORDER BY total DESC LIMIT 25
    """, ("-"+days,)).fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"units":r[2]} for r in rows])

@app.route("/api/last-night")
def api_last_night():
    conn = sqlite3.connect(str(DB_PATH))
    last = conn.execute("SELECT MAX(date) FROM daily_totals").fetchone()[0]
    if not last:
        conn.close()
        return jsonify({"date": None, "total_units": 0, "items": []})
    rows = conn.execute("""
        SELECT p.item_id, p.name, SUM(dt.units) as units
        FROM products p JOIN daily_totals dt ON p.item_id=dt.item_id
        WHERE dt.date=? GROUP BY p.item_id ORDER BY units DESC LIMIT 100
    """, (last,)).fetchall()
    conn.close()
    items = [{"id":r[0],"name":r[1],"units":r[2]} for r in rows]
    return jsonify({"date": last, "total_units": sum(i["units"] for i in items), "items": items})

if __name__ == "__main__":
    init_db()
    port = 5001
    print(f"Analytics Dashboard running on http://localhost:{port}")
    print(f"Reading data from: {DATA_DIR.absolute()}")
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    app.run(host="0.0.0.0", port=port, debug=False)
