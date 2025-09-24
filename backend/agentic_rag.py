from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from workflow_nodes import AgenticRAGState, WorkflowNodes

class AgenticMathRAG:
    """Complete Agentic RAG system for Math Education with Proper Output Guardrails"""
    
    def __init__(self, workflow_nodes: WorkflowNodes):
        self.workflow_nodes = workflow_nodes
        self.workflow_app = self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        # Build the LangGraph workflow
        workflow = StateGraph(AgenticRAGState)

        # Add nodes
        workflow.add_node("input_guardrails", self.workflow_nodes.input_guardrails_node)
        workflow.add_node("vector_search", self.workflow_nodes.vector_search_node)
        workflow.add_node("web_search", self.workflow_nodes.web_search_node)
        workflow.add_node("solution_generation", self.workflow_nodes.solution_generation_node)
        workflow.add_node("output_guardrails", self.workflow_nodes.output_guardrails_node)
        workflow.add_node("feedback_collection", self.workflow_nodes.feedback_collection_node)

        # Add edges
        workflow.add_edge(START, "input_guardrails")
        workflow.add_edge("input_guardrails", "vector_search")
        workflow.add_edge("vector_search", "web_search")
        workflow.add_edge("web_search", "solution_generation")
        workflow.add_edge("solution_generation", "output_guardrails")
        workflow.add_edge("output_guardrails", "feedback_collection")
        workflow.add_edge("feedback_collection", END)

        # Compile the workflow
        return workflow.compile()
    
    def solve_math_problem(self, question: str) -> Dict[str, Any]:
        """Main method to solve math problems using the complete workflow"""
        
        # Initialize state
        initial_state = AgenticRAGState(
            user_question=question,
            input_guardrails_passed=False,
            output_guardrails_passed=False,
            knowledge_base_results=[],
            web_search_results=[],
            raw_solution="",
            final_solution="",
            feedback_rating=None,
            feedback_comments=None,
            error_message=None,
            guardrail_attempts=0
        )
        
        print(f"Processing question: {question}")
        print("=" * 80)
        
        # Run the workflow
        try:
            final_state = self.workflow_app.invoke(initial_state)
            
            # Display results
            self._display_results(final_state)
            
            return final_state
        
        except Exception as e:
            print(f"Workflow error: {str(e)}")
            return {"error": str(e)}
    
    async def solve_math_problem_async(self, question: str) -> Dict[str, Any]:
        """Async version of solve_math_problem"""
        # Initialize state
        initial_state = AgenticRAGState(
            user_question=question,
            input_guardrails_passed=False,
            output_guardrails_passed=False,
            knowledge_base_results=[],
            web_search_results=[],
            raw_solution="",
            final_solution="",
            feedback_rating=None,
            feedback_comments=None,
            error_message=None,
            guardrail_attempts=0
        )
        
        try:
            final_state = await self.workflow_app.ainvoke(initial_state)
            return final_state
        except Exception as e:
            return {"error": str(e)}
    
    def _display_results(self, state: AgenticRAGState):
        """Display the results of the workflow"""
        
        print("\n INPUT GUARDRAILS: ")
        if state["input_guardrails_passed"]:
            print("Input passed guardrails - Valid math question")
        else:
            print(f"Input failed guardrails - {state.get('error_message', 'Invalid input')}")
            return
        
        print("\n KNOWLEDGE BASE SEARCH: ")
        if state["knowledge_base_results"]:
            print(f"Found {len(state['knowledge_base_results'])} similar problems")
            for i, result in enumerate(state["knowledge_base_results"][:2], 1):
                print(f"{i}. Score: {result['score']:.3f} - Topic: {result['topic']}")
        else:
            print("No similar problems found in knowledge base")
        
        print("\n WEB SEARCH: ")
        if state["web_search_results"]:
            print(f"Found {len(state['web_search_results'])} web resources")
            for i, result in enumerate(state["web_search_results"][:2], 1):
                print(f"{i}. {result['title'][:50]}...")
        else:
            print("No web search performed (good knowledge base match found)")
        
        print("\nOUTPUT GUARDRAILS: ")
        if state.get("output_guardrails_passed", False):
            print(f"Output passed guardrails after {state.get('guardrail_attempts', 0)} attempts")
        else:
            print(f"Output guardrails failed after {state.get('guardrail_attempts', 0)} attempts - used fallback")
        
        print("\n FINAL SOLUTION: ")
        solution_preview = state['final_solution'][:300] + "..." if len(state['final_solution']) > 300 else state['final_solution']
        print(f"{solution_preview}")
        
        print("\n FEEDBACK: ")
        if state["feedback_rating"]:
            print(f"Rating: {state['feedback_rating']}/5")
            if state["feedback_comments"]:
                for aspect, comment in state["feedback_comments"].items():
                    print(f"   • {aspect.capitalize()}: {comment}")
        
        print("\n" + "=" * 80)