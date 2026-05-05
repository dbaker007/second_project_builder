from typing import Dict, Any
from nodes.base import BaseNode

class ReporterNode(BaseNode):
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # A run is only truly successful if it pushed a PR
        pushed_pr = any("PR-Creator" in log for log in state.get("execution_logs", []))
        circuit_broken = state.get("circuit_breaker", False)
        
        status = "✅ SUCCESS" if pushed_pr and not circuit_broken else "❌ FAILED"
        
        # Token usage debug
        usage = state.get("usage", {})
        total = usage.get("total_tokens", 0)
        
        print("\n" + "═"*50)
        print(f"  🏁 RUN SUMMARY: {status}")
        print(f"  💰 TOTAL TOKENS: {total:,}")
        if not pushed_pr:
            print(f"  ⚠️ REASON: Iteration limit reached or Circuit Breaker tripped.")
        print("═"*50 + "\n")
        
        return {"next_step": "end"}
