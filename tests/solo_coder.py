import os
import sys
import logging
from dotenv import load_dotenv

# 🏗️ Path Fix
sys.path.append(os.path.join(os.getcwd(), "src"))
from factory import NodeFactory
from utils.debug import load_snapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)-18s | %(message)s")

def run_coder():
    load_dotenv()
    factory = NodeFactory()
    
    # 📂 Load the state from the successful Planner run
    try:
        state = load_snapshot("planner")
    except FileNotFoundError:
        print("❌ Error: snapshots/planner.json not found. Run the Monitor/Planner test first.")
        return

    print("\n--- [STEP 4] CODING (Aider) ---")
    coder = factory.get_node("coder")
    result = coder(state)
    
    print("\n--- [RESULT] ---")
    print(f"🏁 Next Step: {result.get('next_step')}")
    print("👉 Check targets/active_repo/src/project_manager/main.py")

if __name__ == "__main__":
    run_coder()
