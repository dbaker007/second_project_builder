import json
import os
import logging
from datetime import datetime

logger = logging.getLogger("agent.utils.debug")

def save_snapshot(state: dict, node_name: str):
    """Saves the current state to a JSON file for debugging."""
    snapshot_dir = "snapshots"
    os.makedirs(snapshot_dir, exist_ok=True)
    
    # Clean state for JSON serialization
    # Remove objects that cannot be serialized if any exist
    serializable_state = {}
    for k, v in state.items():
        try:
            json.dumps({k: v})
            serializable_state[k] = v
        except:
            serializable_state[k] = str(v)

    filename = os.path.join(snapshot_dir, f"{node_name}.json")
    
    try:
        with open(filename, "w") as f:
            json.dump(serializable_state, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Failed to save snapshot for {node_name}: {e}")

def load_snapshot(node_name: str) -> dict:
    """Loads a state snapshot from a JSON file."""
    filename = os.path.join("snapshots", f"{node_name}.json")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"No snapshot found for node: {node_name}")
        
    with open(filename, "r") as f:
        return json.load(f)
