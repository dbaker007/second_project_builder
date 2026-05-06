import os
import ast

def get_signatures(directory):
    """Walks the repo and extracts classes/functions while ignoring .git and noise."""
    signatures = []
    exclude = {'.git', '__pycache__', '.pytest_cache', 'venv', 'node_modules', '.repo_map_structure.json'}
    
    for root, dirs, files in os.walk(directory):
        # In-place directory filtering to prevent walking into excluded folders
        dirs[:] = [d for d in dirs if d not in exclude]
        
        for file in files:
            if file.endswith(".py"):
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                signatures.append(f"\nFILE: {rel_path}")
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            signatures.append(f"  CLASS: {node.name}")
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            args = [a.arg for a in node.args.args]
                            signatures.append(f"    DEF: {node.name}({', '.join(args)})")
                except Exception as e:
                    signatures.append(f"  [Parse Error: {e}]")
    return "\n".join(signatures)
