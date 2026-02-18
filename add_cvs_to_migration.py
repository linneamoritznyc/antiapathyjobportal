#!/usr/bin/env python3
"""Extract CV_VERSIONS from index.py and add INSERT statements to migration SQL"""
import re

# Read index.py and extract CV_VERSIONS
with open('v2/api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find CV_VERSIONS section
match = re.search(r'CV_VERSIONS = \[(.*?)\n    \]', content, re.DOTALL)
if not match:
    print("ERROR: Could not find CV_VERSIONS in index.py")
    exit(1)

cv_section = match.group(1)

# Extract each CV entry using regex
cv_pattern = r'\{"user_id": user_id, "vibe_id": "(\w+)", "vibe_name": "([^"]+)", "vibe_emoji": "([^"]*)", "cv_text": """(.*?)"""\}'
cvs = re.findall(cv_pattern, cv_section, re.DOTALL)

print(f"Found {len(cvs)} CVs")

# Generate SQL INSERT statements
sql_lines = []
sql_lines.append("\n    -- Insert CV Versions (8 full CVs)")
sql_lines.append("    INSERT INTO user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text) VALUES")

for i, (vibe_id, vibe_name, vibe_emoji, cv_text) in enumerate(cvs):
    # Escape single quotes in SQL
    cv_text_escaped = cv_text.replace("'", "''")

    comma = "," if i < len(cvs) - 1 else ";"
    sql_lines.append(f"    (v_user_id, '{vibe_id}', '{vibe_name}', '{vibe_emoji}', '{cv_text_escaped}'){comma}")

sql_output = "\n".join(sql_lines)

# Read current migration SQL
with open('v2/migrate_complete_data.sql', 'r', encoding='utf-8') as f:
    migration_sql = f.read()

# Find where to insert (before the final RAISE NOTICE)
insert_pos = migration_sql.rfind("    RAISE NOTICE '✅ Migration complete!';")
if insert_pos == -1:
    print("ERROR: Could not find insertion point in migration SQL")
    exit(1)

# Insert the CV SQL
new_migration_sql = migration_sql[:insert_pos] + sql_output + "\n\n" + migration_sql[insert_pos:]

# Update the row count notice
new_migration_sql = new_migration_sql.replace(
    "RAISE NOTICE '  - CV Branscher: 8';",
    "RAISE NOTICE '  - CV Branscher: 8';\n    RAISE NOTICE '  - CV Versions: 8';"
)

# Write updated migration SQL
with open('v2/migrate_complete_data.sql', 'w', encoding='utf-8') as f:
    f.write(new_migration_sql)

print(f"✅ Added {len(cvs)} CVs to migration SQL")
print("Updated: v2/migrate_complete_data.sql")
