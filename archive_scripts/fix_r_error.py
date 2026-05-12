import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup: " + bk)

with open(APP, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# ─────────────────────────────────────────────────────────────────────────────
# FIX: Find broken pid lines where "r.project_id" was inserted incorrectly
# ─────────────────────────────────────────────────────────────────────────────
print("Searching for broken pid lines...")

# Find all lines with broken "r.project_id" that should use actual variable
broken_pattern = re.compile(r'pid:\s*String\(r\.project_id\|\|["\']["\'\]]\)\.toLowerCase\(\),')

# Find all occurrences and show context
for match in broken_pattern.finditer(content):
    pos = match.start()
    # Get context around this line
    line_start = content.rfind('\n', 0, pos) + 1
    line_end = content.find('\n', pos)
    print("Found broken line: " + content[line_start:line_end].strip()[:80])

    # Look backwards for the .map( variable name
    context_before = content[max(0, pos-500):pos]
    # Find the map variable — pattern like ".map(n =>" or ".map(item =>"
    map_match = re.findall(r'\.map\(([a-zA-Z_]+)\s*=>', context_before)
    if map_match:
        var_name = map_match[-1]  # Last .map variable before this line
        print("  Map variable: " + var_name)
        old_line = match.group(0)
        new_line = 'pid: String(' + var_name + '.project_id||"").toLowerCase(),'
        content = content[:pos] + new_line + content[pos+len(old_line):]
        changes += 1
        print("  FIXED: " + old_line + " -> " + new_line)
    else:
        # Try another approach - look for the data variable in select statement
        select_match = re.search(r'supabase\s*\.\s*from\(["\']([^"\']+)["\']\)\s*\.\s*select', context_before)
        if select_match:
            table = select_match.group(1)
            print("  Table: " + table)

        # Default fix - use 'n' as variable
        old_line = match.group(0)
        new_line = 'pid: String(n.project_id||"").toLowerCase(),'
        content = content[:pos] + new_line + content[pos+len(old_line):]
        changes += 1
        print("  FIXED (default n): " + new_line)

# ─────────────────────────────────────────────────────────────────────────────
# Also check for any remaining broken patterns
# ─────────────────────────────────────────────────────────────────────────────
broken_simple = re.compile(r"pid:\s*String\(r\.")
for match in broken_simple.finditer(content):
    pos = match.start()
    line_end = content.find('\n', pos)
    print("Still broken: " + content[pos:line_end].strip()[:80])

    # Find map variable
    context_before = content[max(0, pos-300):pos]
    map_match = re.findall(r'\.map\(([a-zA-Z_]+)\s*=>', context_before)
    if map_match:
        var_name = map_match[-1]
        line_content = content[pos:line_end]
        new_line_content = re.sub(r'String\(r\.', 'String(' + var_name + '.', line_content)
        content = content[:pos] + new_line_content + content[line_end:]
        changes += 1
        print("  FIXED with var: " + var_name)

# ─────────────────────────────────────────────────────────────────────────────
# Verify no more broken references
# ─────────────────────────────────────────────────────────────────────────────
remaining = len(re.findall(r'pid:\s*String\(r\.project_id', content))
print("\nRemaining broken 'r.project_id': " + str(remaining))

if remaining > 0:
    print("Still found issues — showing contexts:")
    for m in re.finditer(r'pid:\s*String\(r\.project_id', content):
        pos = m.start()
        ctx = content[max(0,pos-200):pos+100]
        # Find last map variable
        map_vars = re.findall(r'\.map\(([a-zA-Z_]+)\s*=>', ctx)
        print("  At pos " + str(pos) + ", last map var: " + (map_vars[-1] if map_vars else "NOT FOUND"))
        print("  Context: " + content[pos:pos+60])

with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 55)
print("Done — " + str(changes) + " fixes")
print("Backup: " + bk)
print()
print("Run: set CI=false && npm run build")
print("     npx vercel --prod --force")
print("=" * 55)
input("Press Enter...")
