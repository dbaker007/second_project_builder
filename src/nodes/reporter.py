from nodes.base import BaseNode

class ReporterNode(BaseNode):
    def execute(self, state: dict):
        self.log("🏁 Reporter: Generating final summary...")
        
        success = not state.get("circuit_breaker", False)
        status = "✅ SUCCESS" if success else "❌ FAILED"
        iters = state.get("iteration_count", 0)
        
        print("\n" + "="*50)
        print(f"🏁 RUN SUMMARY: {status}")
        print(f"🔄 TOTAL FIX-LOOPS: {iters}")
        print(f"💰 TOTAL TOKENS: {state.get('usage', {}).get('total_tokens', 0)}")
        
        if state.get("circuit_breaker"):
            print(f"⚠️ REASON: {state.get('surgical_critique', 'Iteration limit reached or Circuit Breaker tripped.')}")
        
        print("="*50 + "\n")

        return {"next_step": "end"}
