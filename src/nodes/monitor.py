import logging
import os
import hashlib
import re
import subprocess
from nodes.base import BaseNode
from utils.scanner import get_signatures


class MonitorNode(BaseNode):
    def execute(self, state: dict):
        target = state["target_path"]
        req_file = os.path.join(target, "requirements.md")
        plan_file = os.path.join(target, "IMPLEMENTATION_PLAN.md")
        watermark_file = os.path.join(target, ".sentinel_watermark")

        # 1. Verify Intent Source
        if not os.path.exists(req_file):
            self.log("⚠️ No requirements.md found. Standing by...", logging.ERROR)
            return {"next_step": "reporter"}

        with open(req_file, "r") as f:
            current_reqs = f.read()

        # 2. Watermark / Intent Sync (The Gatekeeper)
        current_hash = hashlib.md5(current_reqs.encode()).hexdigest()
        old_hash = ""
        if os.path.exists(watermark_file):
            with open(watermark_file, "r") as f:
                old_hash = f.read().strip()

        # If requirements changed, we wipe the plan to prevent stale logic
        if current_hash != old_hash:
            self.log("🆕 Change detected. Updating watermark and clearing old plan.")
            if os.path.exists(plan_file):
                os.remove(plan_file)
            with open(watermark_file, "w") as f:
                f.write(current_hash)
            return {
                "next_step": "planner",
                "requirements_delta": current_reqs,
                "requirements_fulfilled": False,
            }

        # 3. Spatial Grounding (The Reality Check)
        # We gather the tree and signatures every time to ensure the Planner is grounded
        tree = subprocess.run(
            ["tree", "-L", "3", target], capture_output=True, text=True
        ).stdout
        signatures = get_signatures(target)

        # 4. Plan Analysis (Phase Discovery)
        if not os.path.exists(plan_file):
            self.log(
                "📂 No Implementation Plan found. Routing to Planner for Breakdown.",
                logging.ERROR,
            )
            return {
                "next_step": "planner",
                "requirements_delta": current_reqs,
                "project_tree": tree,
                "project_signatures": signatures,
                "turn_history": [],
            }

        with open(plan_file, "r") as f:
            plan_content = f.read()

        # Find the first unchecked task: - [ ]
        match = re.search(r"-\s*\[\s*\]\s*(.*)", plan_content)

        if match:
            phase_text = match.group(1).strip()
            self.log(f"📍 Next Phase: {phase_text[:60]}...")

            return {
                "tech_spec": phase_text,
                "requirements_delta": current_reqs,
                "project_tree": tree,
                "project_signatures": signatures,
                "next_step": "planner",  # Route back to Planner for Phase Detail
                "qa_passed": False,
                "iteration_count": 0,
                "turn_history": [],  # 🎯 Clear loop memory for the new task
                "violated_protocols": [],  # 🎯 Clear protocol memory
                "violation_history": [],
            }

        # 5. Mission Fulfillment
        self.log("🏁 IMPLEMENTATION_PLAN.md complete.")
        return {"requirements_fulfilled": True, "next_step": "pusher"}
