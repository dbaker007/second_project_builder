import os
import sys
import logging
from dotenv import load_dotenv

# 🏗️ Path Fix
sys.path.append(os.path.join(os.getcwd(), "src"))
from factory import NodeFactory

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)-18s | %(message)s")

def main():
    load_dotenv()
    factory = NodeFactory()
    
    state = {
        "repo_url": os.getenv("REPO_URL"),
        "target_path": os.path.abspath("targets/active_repo"),
        "feature_branch": "agent/surgical-graft",
        "requirements_delta": "",
        "iteration_count": 0,
        "usage": {},
        "execution_logs": [],
        "circuit_breaker": False,
        "env_context": {"package_name": "project_manager"},
        "next_step": "cloner"
    }

    # 🔗 Execution Chain
    for node_type in ["cloner", "monitor", "planner", "coder"]:
        print(f"\n--- [RUNNING: {node_type.upper()}] ---")
        node = factory.get_node(node_type)
        result = node(state)
        state.update(result)
        
        if state.get("circuit_breaker"):
            print(f"🛑 Failure in {node_type}. Check logs.")
            return

    print("\n✅ Sequence complete.")
    print("👉 Check targets/active_repo/src/project_manager/main.py")

if __name__ == "__main__":
    main()
