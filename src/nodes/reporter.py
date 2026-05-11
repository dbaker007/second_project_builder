import os
from nodes.base import BaseNode


class ReporterNode(BaseNode):
    def execute(self, state: dict):
        target = state.get("target_path")
        critique = state.get("surgical_critique", "No critique provided.")
        fulfilled = state.get("requirements_fulfilled", False)

        # 1. Build the Status Header based on Cycle Detection
        if fulfilled:
            status = "✅ MISSION COMPLETE: All phases verified and delivered."
        elif critique.startswith("LOOP FAILURE"):
            history = state.get("violation_history", [])
            status = f"🛑 LOOP DETECTED: Agent halted after oscillating on protocols: {history[-1] if history else 'Unknown'}"
        else:
            status = "⚠️ MISSION INTERRUPTED: Manual review required."

        logs = state.get("execution_logs", [])
        last_entry = logs[-1] if logs else "[UNKNOWN]"
        v_history = state.get("violation_history", [])
        protocol_trace = (
            " -> ".join([str(v) for v in v_history])
            if v_history
            else "No violations recorded."
        )

        protocol_trace = (
            " -> ".join([str(v) for v in v_history])
            if v_history
            else "No violations recorded."
        )

        # 2. Extract Token Telemetry
        usage = state.get("usage", {}).get("total_tokens", 0)

        # 3. Construct the Summary
        execution_history = state.get("execution_logs", [])
        audit_trail = "\n        ".join(execution_history)
        report = f"""
        {"=" * 60}
        {status}
        {"=" * 60}
        
        PROJECT: {state.get("repo_url")}
        TOTAL COST: {usage} tokens
        PROTOCOL TRAIL: {protocol_trace}
        
        TERMINAL NODE: {last_entry}
        
        CRITICAL IMPEDIMENT:
        {critique[:1000]}
        
        {"=" * 60}
        AGENT AUDIT TRAIL:
        {audit_trail}        
        {"=" * 60}
        """

        # 4. Persistence
        report_path = (
            os.path.join(target, "MISSION_REPORT.md") if target else "MISSION_REPORT.md"
        )
        with open(report_path, "w") as f:
            f.write(report)

        self.log(f"📄 Report generated at: {report_path}")
        print(report)

        return {"next_step": "end"}
