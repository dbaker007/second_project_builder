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
logger = logging.getLogger("sentinel.pusher_standalone")

def run_standalone_pusher():
    load_dotenv()
    factory = NodeFactory()

    # 1. Load state from the last successful pass (QA usually precedes Pusher)
    try:
        state = load_snapshot("qa")
    except FileNotFoundError:
        try:
            state = load_snapshot("coder")
        except FileNotFoundError:
            logger.error("❌ Error: No snapshot found. Run the Coder/QA pass first.")
            return

    logger.info("🚀 Executing Standalone Pusher Node...")

    # 2. Execute Pusher Node
    pusher_node = factory.get_node("pusher")
    result = pusher_node(state)

    # 3. Summary
    print("\n" + "="*50)
    print(f"🏁 PUSHER RESULT: {result.get('next_step').upper()}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_standalone_pusher()
