import re

with open('templates/index.html', encoding='utf-8') as f:
    html = f.read()

with open('static/js/dashboard.js', encoding='utf-8') as f:
    js = f.read()

matches = re.findall(r"const\s+(\w+)\s*=\s*document\.getElementById\(['\"]([^'\"]+)['\"]\)", js)

missing = []
for var_name, el_id in matches:
    if f'id="{el_id}"' not in html and f"id='{el_id}'" not in html:
        # Check if var_name has addEventListener called on it
        has_listener = bool(re.search(rf"\b{var_name}\.addEventListener", js))
        missing.append((var_name, el_id, has_listener))

print(f"Total element references checked: {len(matches)}")
print(f"Missing in HTML: {len(missing)}")
for var_name, el_id, has_listener in missing:
    print(f"  Var: {var_name:30} ID: {el_id:30} Direct addEventListener: {has_listener}")
