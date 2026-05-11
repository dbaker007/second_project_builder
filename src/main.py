import os
import sys
import time
import logging
from dotenv import load_dotenv
from engine import build_graph

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)-18s | %(message)s"
)
logger = logging.getLogger("sentinel")
load_dotenv()


def main():
    repo_url = os.getenv("REPO_URL")
    target = os.path.abspath(os.path.join(os.getcwd(), "targets/active_repo"))
    app = build_graph()

    while True:
        state = {
            "repo_url": repo_url,
            "target_path": target,
            "feature_branch": f"agent/surgical-{int(time.time())}",
            "usage": {"total_tokens": 0},
            "env_context": {"package_name": "project_manager"},
            "requirements_delta": "",
            "tech_spec": "",
            "test_spec": "",
            "file_impact": [],
            "surgical_critique": "",
            "last_error": "",
            "stall_count": 0,
            "iteration_count": 0,
            "requirements_fulfilled": False,
            "execution_logs": ["Init: Watcher pass started."],
            "next_step": "cloner",
            "pr_url": "",
            "qa_passed": False,
            "dependencies": [],
            "violated_protocols": [],
            "violation_history": [],
            "node_counter": 0,
        }
        try:
            app.invoke(state)
            logger.info(
                "🛑 Checkpoint reached. State saved. Process terminating for manual review."
            )
            sys.exit(0)

        except Exception as e:
            logger.error(f"💥 Graph Execution Failed: {e}")
            # 1. Update state to signal the failure
            state["next_step"] = "reporter"
            state["surgical_critique"] = f"CRITICAL GRAPH FAILURE: {str(e)}"

            # 2. Run the reporter one last time to save the mission report
            try:
                from nodes.reporter import ReporterNode

                reporter = ReporterNode()
                state = reporter(state)
            except Exception as e1:
                logger.critical(f"🚨 Reporter failed during emergency shutdown: {e1}")

            # 3. Hard break the loop to prevent the Cloner restart
            break

        # time.sleep(30)


if __name__ == "__main__":
    main()
