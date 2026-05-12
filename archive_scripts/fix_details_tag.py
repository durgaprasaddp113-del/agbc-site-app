APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

# L3772 (0-based: 3771): </div>}  → need to find the correct closing
# The <details> was opened inside activeSection==="manpower" div
# We need to close </details> before </div>}

# Strategy: find the <details> opening, then find its matching </div>} and add </details>
def s(x): return x.encode('ascii',errors='replace').decode('ascii')

changes = 0

# Find the details opening
details_line = -1
for i,l in enumerate(lines):
    if "<details" in l and "activeSection" in "".join(lines[max(0,i-3):i+1]):
        details_line = i
        print(f"Found <details at L{i+1}: {s(l.rstrip())[:80]}")
        break

if details_line != -1:
    # Find the closing </div>} after the details block
    # Count braces to find where the conditional ends
    for j in range(details_line+1, min(details_line+80, len(lines))):
        l = lines[j].strip()
        if l == "</div>}" or l == "      </div>}":
            # Insert </details> before this line
            indent = lines[j][:len(lines[j])-len(lines[j].lstrip())]
            lines.insert(j, indent + "</details>}\n")
            # Remove the old } from the </div> line (now shifted by 1)
            lines[j+1] = lines[j+1].replace("</div>}", "</div>")
            # But wait - the outer div still needs to close
            # Actually the structure is:
            # {activeSection==="manpower"&&<details>..content..</div>}
            # We need: {activeSection==="manpower"&&<details>..content..</details>}
            # The </div> inside closes the inner content div, </details> closes the details
            changes += 1
            print(f"FIX: </details> inserted at L{j+1}")
            break
        # Also check the actual error line
        if "Total Workers" in l or "reduce" in l:
            # We're in the right area
            pass

# Write
out = "".join(lines)
with open(APP,"w",encoding="utf-8") as f:
    f.write(out)
print(f"Saved. Lines: {len(lines)}")
print(f"Changes: {changes}")
print("\nRun: set CI=false && npm run build")
input("Press Enter...")
