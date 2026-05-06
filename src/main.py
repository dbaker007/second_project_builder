import os
import time
import logging
from dotenv import load_dotenv
from src.engine import build_graph

# Setup Logging - Standard Professional Format
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-18s | %(message)s",
    datefmt="%H:%M:%S"
)

# Silence noisy external libraries
for logger_name in ["gitingest", "httpx", "httpcore", "openai", "langchain", "urllib3"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logger = logging.getLogger("sentinel")
load_dotenv()

def main():
    # 1. Configuration from .env
    repo_url = os.getenv("REPO_URL")
    # Resolve target_path relative to this project root
    target = os.path.abspath(os.path.join(os.getcwd(), "targets/active_repo"))
    
    if not repo_url:
        logger.error("❌ REPO_URL not found in .env")
        return

    # 2. Build the LangGraph
    app = build_graph()
    logger.info(f"🚀 Sentinel initializing for: {repo_url}")

    # 3. Initial State - Single Pass Contract
    state = {
        "repo_url": repo_url,
        "target_path": target,
        "feature_branch": f"agent/surgical-{int(time.time())}",
        "requirements_delta": "",
        "env_context": {"package_name": "project_manager"}, # Default pkg hint
        "tech_spec": "",
        "file_impact": [],
        "test_command": "",
        "surgical_critique": "",
        "iteration_count": 0,
        "circuit_breaker": False,
        "usage": {"total_tokens": 0},
        "execution_logs": ["Init: Watcher pass started."],
        "next_step": "cloner" 
    }

    # 4. Execution
    try:
        logger.info(f"📂 Targeting path: {target}")
        app.invoke(state)
    except Exception as e:
        logger.error(f"💥 Graph Execution Failed: {e}")

    logger.info("🏁 Watcher pass complete.")

if __name__ == "__main__":
    main()
