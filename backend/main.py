import asyncio
from data_loader import load_jee_bench_data, prepare_documents_for_vector_store
from guardrails import setup_input_guardrails, setup_output_guardrails
from vector_store import VectorStoreManager
from web_search import WebSearchManager
from dspy_optimizer import DSPyMathOptimizer
from mcp_integration import MCPMathServer
from workflow_nodes import WorkflowNodes
from agentic_rag import AgenticMathRAG

async def initialize_system():
    """Initialize the complete Agentic RAG system"""
    print("INITIALIZING AGENTIC MATH RAG SYSTEM")
    print("=" * 80)
    
    # 1. Load knowledge base
    print("Loading JEE Bench dataset...")
    knowledge_base = load_jee_bench_data()
    
    # 2. Setup guardrails
    print("Setting up Portkey guardrails...")
    llm_input_guardrails = setup_input_guardrails()
    llm_output_guardrails = setup_output_guardrails()
    
    # 3. Initialize vector store
    print("Initializing Qdrant vector store...")
    vector_store_manager = VectorStoreManager()
    documents, metadatas = prepare_documents_for_vector_store(knowledge_base)
    vector_store_manager.add_documents(documents, metadatas)
    
    # 4. Initialize web search
    print("Setting up Tavily web search...")
    web_search_manager = WebSearchManager()
    
    # 5. Initialize DSPy optimizer
    print("Setting up DSPy optimizer...")
    dspy_optimizer = DSPyMathOptimizer()
    
    # 6. Initialize MCP server
    print("Initializing MCP math server...")
    mcp_server = MCPMathServer()
    await mcp_server.initialize()
    
    # 7. Create workflow nodes
    print("Creating workflow nodes...")
    workflow_nodes = WorkflowNodes(
        llm_input_guardrails=llm_input_guardrails,
        llm_output_guardrails=llm_output_guardrails,
        vector_store_manager=vector_store_manager,
        web_search_manager=web_search_manager,
        dspy_optimizer=dspy_optimizer
    )
    
    # 8. Initialize complete system
    print("Initializing Agentic RAG system...")
    math_rag_system = AgenticMathRAG(workflow_nodes)
    
    print("SYSTEM INITIALIZATION COMPLETE")
    print("=" * 80)
    
    return {
        'math_rag_system': math_rag_system,
        'knowledge_base': knowledge_base,
        'vector_store_manager': vector_store_manager,
        'web_search_manager': web_search_manager,
        'dspy_optimizer': dspy_optimizer,
        'mcp_server': mcp_server,
        'llm_input_guardrails': llm_input_guardrails,
        'llm_output_guardrails': llm_output_guardrails,
        'workflow_nodes': workflow_nodes
    }

def test_system(system_components):
    """Test the system with sample questions"""
    print("\n TESTING AGENTIC RAG SYSTEM")
    print("=" * 80)
    
    math_rag_system = system_components['math_rag_system']
    
    # Test cases
    test_questions = [
        "What is the derivative of x^2 + 3x + 2?",
        "Solve the equation 2x + 5 = 15",
        "Find the integral of sin(x) dx",
        "What is the area of a circle with radius 5?",
        "Explain the Pythagorean theorem with an example"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n TEST {i}")
        result = math_rag_system.solve_math_problem(question)
        print("\n" + "⭐" * 80)
    
    # Display feedback analytics
    dspy_optimizer = system_components['dspy_optimizer']
    analytics = dspy_optimizer.get_feedback_analytics()
    
    print("\nFEEDBACK ANALYSIS")
    print("=" * 80)
    print(f"Total feedback entries: {analytics['total_feedback']}")
    print(f"Average rating: {analytics['average_rating']}")
    print("Rating distribution:", analytics['rating_distribution'])

if __name__ == "__main__":
    async def main():
        # Initialize system
        system_components = await initialize_system()
        
        # Test system
        test_system(system_components)
        
        print("\n SYSTEM READY FOR FASTAPI DEPLOYMENT")
        print("Components available:")
        for component_name in system_components.keys():
            print(f"{component_name}")
    
    # Run the initialization
    asyncio.run(main())