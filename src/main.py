import os
import time
import sys
import subprocess
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("sentinel")

load_dotenv()

def validate_env():
    required = ["REASONING_KEY", "FAST_KEY", "GITHUB_TOKEN", "REPO_URL"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    os.makedirs("logs", exist_ok=True)
    # Ensure targets parent directory exists
    target_path = os.getenv("TARGET_PATH", "./targets/active_repo")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

def get_surgical_delta(target_path):
    """
    Fetches origin/main and diffs the local requirements.md.
    If the repo doesn't exist, it signals a need for Init.
    """
    # Safety: If .git doesn't exist, we can't fetch. 
    # We return a dummy delta to trigger the InitNode to perform the clone.
    if not os.path.exists(os.path.join(target_path, ".git")):
        logger.info("🆕 Target repo not found. Triggering initial clone...")
        return "INITIAL_CLONE_REQUIRED"

    try:
        subprocess.run(["git", "-C", target_path, "fetch", "origin", "main"], 
                       capture_output=True, check=True)
        
        diff_cmd = ["git", "-C", target_path, "diff", "origin/main", "HEAD", "--", "requirements.md"]
        result = subprocess.run(diff_cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Failed to check watermark: {e}")
        return ""

def main():
    validate_env()
    
    # Delayed import of engine to prevent circular dependencies or init errors
    from engine import build_graph
    
    repo_url = os.getenv("REPO_URL")
    target = os.getenv("TARGET_PATH", "./targets/active_repo")
    interval = int(os.getenv("HEARTBEAT_INTERVAL", 30))
    
    app = build_graph()
    logger.info(f"📡 Sentinel V2 Active: Monitoring {repo_url}")
    
    while True:
        delta = get_surgical_delta(target)
        
        if delta:
            logger.info("🎯 Requirements change detected. Starting healing cycle...")
            
            initial_state = {
                "repo_url": repo_url,
                "target_path": target,
                "feature_branch": f"agent/heal-{int(time.time())}",
                "iteration_count": 0,
                "circuit_breaker": False,
                "usage": {"total_tokens": 0},
                "execution_logs": ["Monitor: Requirements delta detected."]
            }
            
            try:
                final_state = app.invoke(initial_state)
                if final_state.get("circuit_breaker"):
                    logger.error("🛑 Circuit Breaker Tripped.")
                else:
                    logger.info("✅ Cycle complete.")
            except Exception as e:
                logger.error(f"💥 Graph Crash: {e}")
        
        else:
            sys.stdout.write(f"\r😴 No changes. Sleeping {interval}s...   ")
            sys.stdout.flush()
        
        time.sleep(interval)

if __name__ == "__main__":
    main()
