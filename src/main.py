import os
import sys
import time
import logging
from dotenv import load_dotenv
from engine import build_graph

# Setup Logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)-18s | %(message)s", datefmt="%H:%M:%S")
for logger_name in ["gitingest", "httpx", "httpcore", "openai", "langchain", "urllib3"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logger = logging.getLogger("sentinel")
load_dotenv()

def main():
    target = os.getenv("TARGET_PATH", "./targets/active_repo")
    app = build_graph()
    
    cycles = 0
    max_cycles = 2
    
    logger.info(f"🚀 Starting Sentinel (Limit: {max_cycles} cycles)...")
    
    while cycles < max_cycles:
        cycles += 1
        logger.info(f"🔄 --- STARTING CYCLE {cycles} ---")
        
        # Check if we should skip the wipe (Only wipe on Cycle 1)
        skip_wipe = True if cycles > 1 and os.path.exists(os.path.join(target, ".git")) else False
        
        state = {
            "repo_url": os.getenv("REPO_URL"),
            "target_path": target,
            "feature_branch": f"agent/fix-{int(time.time())}",
            "iteration_count": 0,
            "circuit_breaker": False,
            "usage": {"total_tokens": 0},
            "execution_logs": [f"Monitor: Cycle {cycles} starting."],
            "skip_init_wipe": skip_wipe # Node can check this
        }
        
        try:
            app.invoke(state)
            break # Exit loop if graph finishes (it handles its own inner loops)
        except Exception as e:
            logger.error(f"💥 Graph Crash: {e}")
            if cycles < max_cycles:
                logger.info("😴 Retrying in 5s...")
                time.sleep(5)

    logger.info("🏁 Sentinel shutting down.")

if __name__ == "__main__":
    main()
