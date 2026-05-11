import logging
from abc import ABC, abstractmethod
from utils.debug import save_snapshot


class BaseNode(ABC):
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace("node", "")
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")

    def log(self, message: str, level: int = logging.INFO):
        self.logger.log(level, message)

    @abstractmethod
    def execute(self, state: dict) -> dict:
        pass

    def __call__(self, state: dict) -> dict:
        import hashlib
        import json
        import time
        import logging

        start_time = time.time()
        self.log("▶ START")

        # 1. Execute the actual node logic
        result = self.execute(state)

        # 2. Timing and Token Telemetry
        duration = time.time() - start_time
        tokens = result.get("usage", {}).get("total_tokens", 0)
        telemetry = f"[{self.name.upper()}] Time: {duration:.2f}s | Tokens: {tokens}"

        # 3. Create a stable state signature for Universal Loop Detection
        # We exclude noisy fields like 'usage', 'logs', or 'time' to focus on logical state
        signature_data = {
            "next_step": result.get("next_step"),
            "violated_protocols": sorted(result.get("violated_protocols", [])),
        }

        sig_str = json.dumps(signature_data, sort_keys=True)
        sig_hash = hashlib.md5(sig_str.encode()).hexdigest()

        # 4. Loop Detection Check
        current_v = sorted(
            result.get("violated_protocols") or state.get("violated_protocols", [])
        )

        if current_v:
            result["violation_history"] = [current_v]

        # We only track loops if there is an error/critique present
        history = state.get("turn_history", [])
        if result.get("surgical_critique") and sig_hash in history:
            self.log(f"🛑 LOOP DETECTED: {sig_hash}", level=logging.CRITICAL)
            result["next_step"] = "reporter"
            result["surgical_critique"] = (
                f"UNIVERSAL LOOP FAILURE: The agent repeated a previous logical state ({current_v})."
            )
        else:
            # Append this turn's signature to the history list
            result["turn_history"] = [sig_hash]

        # 5. Finalize execution_logs for the Reducer
        result["execution_logs"] = [telemetry]

        # 6. Logging and Persistence
        self.log(f"⏹ END ({duration:.2f}s)")
        count = state.get("node_counter", 0) + 1
        result["node_counter"] = count

        # Create the snapshot state
        snapshot_state = {**state, **result}

        # MANUALLY SIMULATE REDUCERS FOR THE SNAPSHOT
        # This fixes the visual 'overwrite' in the JSON file
        for key in ["turn_history", "violation_history", "execution_logs"]:
            if key in result:
                snapshot_state[key] = (state.get(key) or []) + (result.get(key) or [])

        save_snapshot(snapshot_state, f"{count:03d}_{self.name}")

        return result
