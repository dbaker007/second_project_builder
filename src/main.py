import os
import time
import sys
import subprocess
import logging
from dotenv import load_dotenv

# We will import the graph engine in Step 3
# from engine import build_graph

# Configure logging for the Orchestrator
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("sentinel")

load_dotenv()

def validate_env():
    """Ensure infrastructure keys exist before starting the loop."""
    required = ["REASONING_KEY", "FAST_KEY", "GITHUB_TOKEN"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    os.makedirs("logs", exist_ok=True)

def get_surgical_delta(target_path):
    """
    The Watermark Check:
    Fetches origin/main and diffs the local requirements.md.
    """
    try:
        # Fetch remote state without merging
        subprocess.run(["git", "-C", target_path, "fetch", "origin", "main"], 
                       capture_output=True, check=True)
        
        # Compare local requirements.md to the remote truth
        diff_cmd = ["git", "-C", target_path, "diff", "origin/main", "HEAD", "--", "requirements.md"]
        result = subprocess.run(diff_cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Failed to check watermark: {e}")
        return ""

def main():
    validate_env()
    
    repo_url = os.getenv("REPO_URL")
    target = os.getenv("TARGET_PATH", "./targets/active_repo")
    interval = int(os.getenv("HEARTBEAT_INTERVAL", 30))
    
    logger.info(f"📡 Sentinel V2 Active: Monitoring {repo_url}")
    
    while True:
        delta = get_surgical_delta(target)
        
        if delta:
            logger.info("🎯 Requirements change detected against origin/main.")
            logger.info(f"📉 Delta captured:\n{delta[:200]}...")
            
            # --- PHASE 2 PREVIEW ---
            # In Step 3, we will initialize the graph and invoke it here.
            # initial_state = { ... }
            # app.invoke(initial_state)
            
            logger.info("⏳ Graph execution skipped (Engine not yet implemented).")
        else:
            # Scannable status line
            sys.stdout.write(f"\r😴 No changes relative to origin/main. Sleeping {interval}s...   ")
            sys.stdout.flush()
        
        time.sleep(interval)

if __name__ == "__main__":
    main()
