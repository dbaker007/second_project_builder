import os
import sys
import logging
from dotenv import load_dotenv

# 🏗️ Path Fix: Inject 'src' directly so 'from factory import...' works
sys.path.append(os.path.join(os.getcwd(), "src"))

from factory import NodeFactory

# Setup Logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)-18s | %(message)s")

def run_test():
    load_dotenv()
    factory = NodeFactory()
    
    # 🎯 State configuration for Sandbox testing
    state = {
        "repo_url": os.getenv("REPO_URL"),
        "target_path": os.path.abspath("targets/active_repo"),
        "feature_branch": "agent/test-run",
        "requirements_delta": "",
        "iteration_count": 0,
        "usage": {},
        "execution_logs": [],
        "circuit_breaker": False,
        "env_context": {"package_name": "project_manager"},
        "next_step": "cloner"
    }

    print("\n--- [STEP 1] CLONING ---")
    cloner = factory.get_node("cloner")
    clone_result = cloner(state)
    state.update(clone_result)
    
    if state.get("circuit_breaker"):
        print("🛑 Cloner Failed. Check your REPO_URL and Git permissions.")
        return

    print("\n--- [STEP 2] MONITORING ---")
    monitor = factory.get_node("monitor")
    mon_result = monitor(state)
    state.update(mon_result)
    
    if state.get("circuit_breaker"):
        print("🛑 Monitor: No new tasks detected. Update requirements.md in the target repo.")
        return

    print("\n--- [STEP 3] PLANNING ---")
    planner = factory.get_node("planner")
    plan_result = planner(state)
    state.update(plan_result)

    print("\n" + "="*50)
    print("📍 RESULT SUMMARY")
    print(f"📂 Target: {state['target_path']}")
    print(f"📂 Files:  {state.get('file_impact')}")
    print(f"🧪 Test:   {state.get('test_command')}")
    print(f"📝 Goal:   {state.get('tech_spec')}")
    print("="*50)

if __name__ == "__main__":
    run_test()
