import os
import sys
import logging
from dotenv import load_dotenv

# 🏗️ Path Fix: Point to the 'src' directory
sys.path.append(os.path.join(os.getcwd(), "src"))

from factory import NodeFactory
from utils.debug import load_snapshot

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)-18s | %(message)s")
logger = logging.getLogger("sentinel.qa_standalone")

def run_standalone_qa():
    load_dotenv()
    factory = NodeFactory()

    # 1. Load state from the last successful coder pass
    try:
        state = load_snapshot("coder")
    except FileNotFoundError:
        logger.error("❌ Error: snapshots/coder.json not found. Run the Coder pass first.")
        return

    logger.info("🧪 Executing Standalone QA Node...")

    # 2. Execute QA Node
    qa_node = factory.get_node("qa")
    result = qa_node(state)

    # 3. Summary
    print("\n" + "="*50)
    print(f"🏁 QA RESULT: {result.get('next_step').upper()}")
    if result.get("surgical_critique"):
        print("📝 FEEDBACK CAPTURED (Failures detected)")
    else:
        print("✅ CLEAN PASS (Ready for Pusher)")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_standalone_qa()
