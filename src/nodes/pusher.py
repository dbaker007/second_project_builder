import logging
import os
import subprocess
import re
from github import Github
from nodes.base import BaseNode


class PusherNode(BaseNode):
    def execute(self, state: dict):
        target = state["target_path"]
        plan_file = os.path.join(target, "IMPLEMENTATION_PLAN.md")
        success_file = os.path.join(target, ".sentinel_success")

        self.log("📝 Pusher: Finalizing phase and creating local save point.")

        # 1. Update the Checklist
        if os.path.exists(plan_file):
            with open(plan_file, "r") as f:
                content = f.read()
            updated_content = re.sub(r"-\s*\[\s*\]", "- [x]", content, count=1)
            with open(plan_file, "w") as f:
                f.write(updated_content)

        # 2. Drop the Success Marker
        with open(success_file, "w") as f:
            f.write("PHASE_VERIFIED")

        # 3. Local Git Save Point
        branch = state.get("feature_branch", "agent/implementation")
        try:
            self._create_local_commit(
                target, branch, state.get("tech_spec", "Phase Completion")
            )
            self.log("🔄 Phase archived.")
        except Exception as e:
            self.log(f"⚠️ Local commit failed: {e}", logging.ERROR)
            return {
                "next_step": "reporter",
                "surgical_critique": f"GIT FAILURE: Could not create local commit on {branch}. Error: {e}",
                "requirements_fulfilled": False,
            }

        # 4. Check for finalization
        with open(plan_file, "r") as f:
            remaining_plan = f.read()

        phases_remain = "- [ ]" in remaining_plan

        if not phases_remain:
            self.log("🚀 All phases complete. Pushing to remote and creating PR.")
            try:
                self._push_to_remote(state)
                self._create_github_pr(state)
                return {"next_step": "reporter", "requirements_fulfilled": True}
            except Exception as e:
                self.log(f"⚠️ Remote delivery failed: {e}", logging.ERROR)
                return {"next_step": "reporter"}

        return {
            "next_step": "monitor",
            "requirements_fulfilled": False,
            "qa_passed": False,
        }

    def _create_local_commit(self, target, branch, tech_spec):
        """Ensures the correct branch and creates a local commit."""
        # Ensure branch alignment
        current = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=target
            )
            .decode()
            .strip()
        )
        if current != branch:
            self.log(
                f"🚨 ENVIRONMENT DESYNC: Expected {branch}, found {current}.", level=40
            )
            return {
                "next_step": "reporter",
                "surgical_critique": f"CRITICAL ENVIRONMENT FAILURE: The workspace branch shifted from '{branch}' to '{current}'. To prevent repository corruption, autonomous execution has been halted. Manual reconciliation is required.",
                "requirements_fulfilled": False,
            }

        # Stage and Commit
        subprocess.run(["git", "add", "."], cwd=target, check=True)
        msg = f"🤖 Sentinel: Phase Verified - {tech_spec[:50]}..."
        subprocess.run(
            [
                "git",
                "-c",
                "user.name='Sentinel'",
                "-c",
                "user.email='a@b.com'",
                "commit",
                "-m",
                msg,
            ],
            cwd=target,
            capture_output=True,
        )

    def _push_to_remote(self, state):
        """Pushes the local feature branch to the remote origin."""
        target = state["target_path"]
        repo_url = state.get("repo_url", "").rstrip("/")
        token = os.getenv("GITHUB_TOKEN")
        branch = state.get("feature_branch")

        auth_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
        subprocess.run(["git", "push", "-u", auth_url, branch], cwd=target, check=True)

    def _create_github_pr(self, state):
        """Opens the Pull Request on GitHub."""
        token = os.getenv("GITHUB_TOKEN")
        repo_url = state.get("repo_url", "").rstrip("/")
        branch = state.get("feature_branch")

        repo_path = repo_url.split("://github.com")[-1].replace(".git", "").strip("/")
        g = Github(token)
        repo = g.get_repo(repo_path)

        pr = repo.create_pull(
            title="🤖 Sentinel: Project Implementation Complete",
            body="Autonomous phased implementation verified through local TDD cycles.",
            head=branch,
            base="main",
        )
        self.log(f"✅ PR Created: {pr.html_url}")
