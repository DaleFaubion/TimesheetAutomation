import re

with open('templates/index.html', encoding='utf-8') as f:
    html = f.read()

with open('static/js/dashboard.js', encoding='utf-8') as f:
    js = f.read()

# Find lines like: varName.addEventListener(
lines = js.splitlines()
unsafe_listeners = []
for idx, line in enumerate(lines, 1):
    m = re.search(r'^\s*([a-zA-Z0-9_$]+)\.addEventListener\(', line)
    if m:
        var = m.group(1)
        # Check if var was assigned via document.getElementById('...')
        id_match = re.search(rf'const\s+{var}\s*=\s*document\.getElementById\([\'\"]([^\'\"]+)[\'\"]\)', js)
        if id_match:
            el_id = id_match.group(1)
            in_html = f'id="{el_id}"' in html or f"id='{el_id}'" in html
            if not in_html:
                unsafe_listeners.append((idx, line.strip(), var, el_id))

print(f"Direct addEventListener on elements NOT in index.html: {len(unsafe_listeners)}")
for line_num, code, var, el_id in unsafe_listeners:
    print(f"Line {line_num}: {var} (id='{el_id}') is NOT in index.html! Code: {code}")
