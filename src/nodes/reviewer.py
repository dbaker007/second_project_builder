#!/bin/bash
# Step 15: Initialize the Reporter Node

echo "📝 Populating src/nodes/reporter.py..."
cat <<'EOF' > src/nodes/reporter.py
from typing import Dict, Any
from nodes.base import BaseNode

class ReporterNode(BaseNode):
    """
    The Communication Specialist.
    Finalizes the run by summarizing logs and token usage.
    """
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log("📊 Generating final execution report...")
        
        status = "❌ FAILED (Circuit Breaker)" if state.get("circuit_breaker") else "✅ SUCCESS"
        total_tokens = state.get("usage", {}).get("total_tokens", 0)
        
        print("\n" + "="*50)
        print(f"       SENTINEL HEALER RUN COMPLETE")
        print("="*50)
        print(f"STATUS: {status}")
        print(f"TOKENS USED: {total_tokens:,}")
        print("-" * 50)
        print("EXECUTION LOGS:")
        for entry in state.get("execution_logs", []):
            print(f" - {entry}")
        print("="*50 + "\n")

        return {"next_step": "end"}
EOF

echo "✅ Step 15 Complete: Reporter Node implemented."
