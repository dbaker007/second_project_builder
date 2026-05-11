import logging
import os
import subprocess
from nodes.base import BaseNode


class EnvironmentNode(BaseNode):
    def _heal_infrastructure(self, state: dict):
        target = state["target_path"]
        package_name = state.get("env_context", {}).get(
            "package_name", "project_manager"
        )

        # Now we only care if .gitignore or .env.example are missing/empty
        # Scaffolder has already anchored the pyproject.toml
        anchors = [".gitignore", ".env.example"]
        missing_or_empty = [
            f
            for f in anchors
            if not os.path.exists(os.path.join(target, f))
            or os.path.getsize(os.path.join(target, f)) == 0
        ]

        if not missing_or_empty:
            return

        self.log(f"🚑 Infrastructure: Healing empty files: {missing_or_empty}")

        from utils.safety import get_llm
        from utils.parser import parse_llm_json

        model = get_llm("FAST", self.name)

        # 🎯 Targeted Prompting
        prompt = f"""
        TASK: Generate specific infrastructure configuration files.
        PACKAGE: {package_name}
        TECH STACK: {state.get("tech_spec")}
        LIBRARIES: {state.get("dependencies", [])}

        FILES TO GENERATE: {missing_or_empty}

        SPECIFIC RULES:
        - If .gitignore: Include standard Python noise, .venv, and tech-specific patterns (like .db for SQLite).
        - If .env.example: Include keys mentioned in the TECH STACK or common for this type of project.

        FORMAT: JSON object where keys are filenames and values are the new file content.
        """

        response = model.invoke(prompt)
        healed_files = parse_llm_json(response.content)

        for filename, content in healed_files.items():
            # Double check we only write what we asked for
            if filename in missing_or_empty:
                with open(os.path.join(target, filename), "w") as f:
                    f.write(content)
                self.log(f"✅ Healed: {filename}", logging.DEBUG)

    def execute(self, state: dict):
        target = state["target_path"]

        # 🛡️ Step 1: Heal Infrastructure (Anchors the project)
        self._heal_infrastructure(state)

        # 📦 Step 2: Install Planned Dependencies
        planned_libs = state.get("dependencies", [])
        if planned_libs:
            self.log(f"📦 Environment: Installing planned libraries: {planned_libs}")
            for lib in planned_libs:
                # uv add handles both adding to toml and installing
                result = subprocess.run(
                    ["uv", "add", lib], cwd=target, capture_output=True, text=True
                )

                if result.returncode != 0:
                    self.log(
                        f"❌ Dependency Error: '{lib}' failed to install.",
                        logging.ERROR,
                    )
                    return {
                        "next_step": "reporter",
                        "surgical_critique": f"FATAL ENVIRONMENT ERROR: The library '{lib}' could not be installed via uv. This usually means the package name is misspelled or does not exist on PyPI. Implementation halted to prevent logic loops.",
                        "requirements_fulfilled": False,
                    }

        # 🔄 Step 3: Final Sync
        subprocess.run(["uv", "sync"], cwd=target, capture_output=True)
        self.log("✅ Environment synchronized with Planner intent.")

        return {"next_step": "qa"}
