"""
Vercel API endpoint to inspect live Supabase database
Visit: https://yourapp.vercel.app/api/inspect-db
"""
from http.server import BaseHTTPRequestHandler
import json
import os
try:
    import requests
except:
    # If requests isn't available in Vercel, use urllib
    import urllib.request
    import urllib.parse

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://apqrvyeujsetxdjkwupx.supabase.co")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwcXJ2eWV1anNldHhkamt3dXB4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDc1OTczOSwiZXhwIjoyMDg2MzM1NzM5fQ.J35GpamK_n-1mxr4tbw178fckdV6z8_Apbz04sTlG3M")

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

def get_tables():
    """Get list of tables"""
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        if response.status_code == 200:
            spec = response.json()
            return list(spec.get("definitions", {}).keys())
    except:
        pass
    return []

def get_table_info(table_name):
    """Get info about a table"""
    try:
        # Get row count
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}",
            headers={**headers, "Prefer": "count=exact"},
            params={"limit": 0}
        )
        content_range = response.headers.get('Content-Range', '')
        count = content_range.split('/')[-1] if '/' in content_range else "0"

        # Get sample row to see columns
        sample_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}",
            headers=headers,
            params={"limit": 3}
        )

        samples = []
        columns = []
        if sample_response.status_code == 200:
            samples = sample_response.json()
            if samples:
                columns = list(samples[0].keys())

        return {
            "table": table_name,
            "row_count": count,
            "columns": columns,
            "sample_data": samples[:3]
        }
    except Exception as e:
        return {
            "table": table_name,
            "error": str(e)
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            tables = get_tables()

            result = {
                "success": True,
                "database_url": SUPABASE_URL,
                "total_tables": len(tables),
                "tables": []
            }

            for table in tables:
                info = get_table_info(table)
                result["tables"].append(info)

            # Return HTML for easier reading
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Supabase Database Inspector</title>
                <style>
                    body {{ font-family: monospace; padding: 20px; background: #1a1a1a; color: #0f0; }}
                    h1 {{ color: #0f0; }}
                    .table {{ margin: 20px 0; padding: 15px; border: 1px solid #0f0; background: #0a0a0a; }}
                    .table h2 {{ margin-top: 0; color: #0ff; }}
                    .columns {{ color: #ff0; }}
                    .sample {{ color: #0f0; white-space: pre-wrap; font-size: 12px; }}
                </style>
            </head>
            <body>
                <h1>🔍 Live Supabase Database Inspection</h1>
                <p>Database: {SUPABASE_URL}</p>
                <p>Total Tables: {len(tables)}</p>
                <hr>
            """

            for info in result["tables"]:
                html += f"""
                <div class="table">
                    <h2>📋 {info['table']}</h2>
                    <p><strong>Rows:</strong> {info.get('row_count', 'N/A')}</p>
                    <p class="columns"><strong>Columns ({len(info.get('columns', []))}):</strong> {', '.join(info.get('columns', []))}</p>
                    <details>
                        <summary><strong>Sample Data (first 3 rows)</strong></summary>
                        <pre class="sample">{json.dumps(info.get('sample_data', []), indent=2, ensure_ascii=False)}</pre>
                    </details>
                </div>
                """

            html += """
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"<h1>Error</h1><pre>{str(e)}</pre>"
            self.wfile.write(error_html.encode())
