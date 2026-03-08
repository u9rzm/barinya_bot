import json
with open('/tmp/tmp-220197-6cpGYrQwrl9B/stats.json') as f:
    data = json.load(f)

# Find all leaf nodes with sizes
leaves = []
def find_leaves(node, path=""):
    current_path = f"{path}/{node.get('name', '')}" if path else node.get('name', '')
    if "uid" in node:
        leaves.append({"path": current_path, "node": node})
    elif "children" in node:
        for child in node["children"]:
            find_leaves(child, current_path)

find_leaves(data["tree"])

# Sort by value
leaves_with_size = [(l["path"], l["node"].get("value", 0) or l["node"].get("size", 0)) for l in leaves]
leaves_with_size = [(p, s) for p, s in leaves_with_size if s > 0]
leaves_with_size.sort(key=lambda x: x[1], reverse=True)

print("Top 30 largest files:")
for path, size in leaves_with_size[:30]:
    print(f"{size:>10}  {path}")

# Group by package
print("\n\nBy package:")
packages = {}
for path, size in leaves_with_size:
    parts = path.split('/')
    for i, part in enumerate(parts):
        if part == 'node_modules' and i+1 < len(parts):
            pkg = parts[i+1]
            if pkg.startswith('@') and i+2 < len(parts):
                pkg = '/'.join(parts[i+1:i+3])
            packages[pkg] = packages.get(pkg, 0) + size
            break

sorted_pkgs = sorted(packages.items(), key=lambda x: x[1], reverse=True)
total = sum(packages.values())
for pkg, size in sorted_pkgs[:20]:
    pct = (size/total*100) if total else 0
    print(f"{size:>10} bytes  ({pct:5.1f}%)  {pkg}")
print(f"{total:>10} bytes  (100%)  TOTAL")
