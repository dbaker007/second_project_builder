import os
from nodes.base import BaseNode


class ScaffoldNode(BaseNode):
    def execute(self, state: dict):
        target = state["target_path"]
        package_name = state.get("env_context", {}).get(
            "package_name", "project_manager"
        )

        # 🛡️ Guard: Only scaffold if we haven't already anchored the structure
        if os.path.exists(os.path.join(target, "src")):
            self.log("📂 Structure already exists. Skipping scaffolding.")
            return {"next_step": "planner"}

        # ⚓ Anchor Content: Valid baseline to ground the AI's pathing logic
        pyproject_content = f"""[project]
name = "{package_name}"
version = "0.1.0"
description = "Sentinel Managed Project"
requires-python = ">=3.12"
dependencies = [
    "pytest>=8.0.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

        self.log(
            f"🏗️ Scaffolder: Anchoring project '{package_name}' with baseline config"
        )

        # Create directories
        os.makedirs(os.path.join(target, "src", package_name), exist_ok=True)
        os.makedirs(os.path.join(target, "tests"), exist_ok=True)

        # Write Anchor Files (pyproject.toml is now populated)
        files = {
            "pyproject.toml": pyproject_content,
            "README.md": f"# {package_name}",
            f"src/{package_name}/__init__.py": "",
            "tests/__init__.py": "",
        }

        for path, content in files.items():
            full_path = os.path.join(target, path)
            if not os.path.exists(full_path):
                with open(full_path, "w") as f:
                    f.write(content)

        return {"next_step": "monitor"}
