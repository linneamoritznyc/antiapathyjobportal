#!/usr/bin/env python3
"""
Live Supabase Database Inspector
Run this script to see your current database structure
"""
import requests
import json

# Your Supabase credentials
SUPABASE_URL = "https://apqrvyeujsetxdjkwupx.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwcXJ2eWV1anNldHhkamt3dXB4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDc1OTczOSwiZXhwIjoyMDg2MzM1NzM5fQ.J35GpamK_n-1mxr4tbw178fckdV6z8_Apbz04sTlG3M"

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

def get_tables():
    """Get list of all tables"""
    response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
    response.raise_for_status()
    spec = response.json()
    return list(spec.get("definitions", {}).keys())

def get_table_schema(table_name):
    """Get schema for a specific table"""
    # Query with limit 0 to get column info without data
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table_name}",
        headers={**headers, "Prefer": "count=exact"},
        params={"limit": 0}
    )
    response.raise_for_status()

    # Get column info from response headers or first row
    sample = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table_name}",
        headers=headers,
        params={"limit": 1}
    )

    if sample.json():
        columns = list(sample.json()[0].keys())
        return columns
    return []

def get_sample_data(table_name, limit=3):
    """Get sample rows from a table"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table_name}",
        headers=headers,
        params={"limit": limit}
    )
    response.raise_for_status()
    return response.json()

def get_row_count(table_name):
    """Get total row count for a table"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table_name}",
        headers={**headers, "Prefer": "count=exact"},
        params={"limit": 0}
    )
    response.raise_for_status()
    content_range = response.headers.get('Content-Range', '')
    if '/' in content_range:
        return content_range.split('/')[-1]
    return "unknown"

def main():
    print("=" * 80)
    print("🔍 LIVE SUPABASE DATABASE INSPECTION")
    print("=" * 80)
    print()

    try:
        # Get all tables
        tables = get_tables()
        print(f"📊 Found {len(tables)} tables\n")

        for table in tables:
            print("─" * 80)
            print(f"📋 TABLE: {table}")
            print("─" * 80)

            # Get row count
            count = get_row_count(table)
            print(f"   Rows: {count}")

            # Get schema
            columns = get_table_schema(table)
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                print(f"      • {col}")

            # Get sample data
            print(f"\n   Sample data (first 3 rows):")
            try:
                samples = get_sample_data(table, limit=3)
                if samples:
                    for i, row in enumerate(samples, 1):
                        print(f"\n   Row {i}:")
                        for key, value in row.items():
                            # Truncate long values
                            val_str = str(value)
                            if len(val_str) > 100:
                                val_str = val_str[:100] + "..."
                            print(f"      {key}: {val_str}")
                else:
                    print("      (empty table)")
            except Exception as e:
                print(f"      Error reading data: {e}")

            print()

        print("=" * 80)
        print("✅ INSPECTION COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
