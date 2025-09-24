import re
from typing import Dict, List, Optional, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage

class AgenticRAGState(TypedDict):
    """State for the Agentic RAG workflow"""
    user_question: str
    input_guardrails_passed: bool
    output_guardrails_passed: bool
    knowledge_base_results: List[Dict]
    web_search_results: List[Dict]
    raw_solution: str
    final_solution: str
    feedback_rating: Optional[int]
    feedback_comments: Optional[Dict]
    error_message: Optional[str]
    guardrail_attempts: int

class WorkflowNodes:
    """Contains all workflow node implementations"""
    
    def __init__(self, llm_input_guardrails, llm_output_guardrails, vector_store_manager, 
                 web_search_manager, dspy_optimizer):
        self.llm_input_guardrails = llm_input_guardrails
        self.llm_output_guardrails = llm_output_guardrails
        self.vector_store_manager = vector_store_manager
        self.web_search_manager = web_search_manager
        self.dspy_optimizer = dspy_optimizer
    
    def input_guardrails_node(self, state: AgenticRAGState) -> AgenticRAGState:
        """Node 1: Apply INPUT guardrails using Portkey"""
        try:
            print("🛡️ Applying INPUT guardrails...")
            
            # Enhanced math keywords - more comprehensive list
            math_keywords = [
                # Basic operations
                'equation', 'solve', 'find', 'calculate', 'determine', 'evaluate', 'compute',
                # Algebra
                'algebra', 'polynomial', 'quadratic', 'linear', 'variable', 'coefficient',
                # Calculus
                'derivative', 'integral', 'limit', 'differential', 'antiderivative',
                # Geometry
                'geometry', 'area', 'perimeter', 'volume', 'radius', 'diameter', 'triangle', 
                'circle', 'rectangle', 'square', 'angle', 'pythagorean', 'theorem',
                # Trigonometry
                'trigonometry', 'sin', 'cos', 'tan', 'sine', 'cosine', 'tangent',
                # General math
                'mathematics', 'math', 'formula', 'function', 'graph', 'plot',
                # Statistics
                'statistics', 'probability', 'mean', 'median', 'mode', 'deviation',
                # Other math concepts
                'matrix', 'vector', 'logarithm', 'exponential', 'factorial', 'prime'
            ]
            
            # Math operation verbs
            math_verbs = ['explain', 'prove', 'show', 'demonstrate', 'derive', 'verify']
            
            question_lower = state["user_question"].lower()
            
            # Check for math keywords
            has_math_keyword = any(keyword in question_lower for keyword in math_keywords)
            
            # Check for math operation verbs with math context
            has_math_verb = any(verb in question_lower for verb in math_verbs)
            
            # Check for mathematical expressions (numbers, symbols)
            has_math_symbols = bool(re.search(r'[0-9+\-*/=^()x²³√∫∂∑π]', question_lower))
            
            # More lenient validation - pass if ANY condition is met
            is_math_question = has_math_keyword or (has_math_verb and has_math_symbols) or has_math_symbols
            
            # Additional Portkey validation
            try:
                test_message = [
                    SystemMessage(content="Respond 'VALID' if this is a math question, 'INVALID' otherwise."),
                    HumanMessage(content=state["user_question"])
                ]
                response = self.llm_input_guardrails.invoke(test_message)
                portkey_validation = "VALID" in response.content.upper()
            except:
                portkey_validation = True  # Default to true if Portkey fails
            
            # Final decision - pass if either validation method succeeds
            input_passed = is_math_question or portkey_validation
            
            print(f"   Math keywords: {has_math_keyword}")
            print(f"   Math symbols: {has_math_symbols}")
            print(f"   Portkey validation: {portkey_validation}")
            print(f"   Input guardrails: {'PASSED' if input_passed else 'FAILED'}")
            
            return {
                **state,
                "input_guardrails_passed": input_passed,
                "error_message": None if input_passed else "Question failed input validation - not a valid math question"
            }
        except Exception as e:
            print(f" Input guardrails error: {str(e)}")
            return {
                **state,
                "input_guardrails_passed": False,
                "error_message": f"Input guardrails error: {str(e)}"
            }

    def vector_search_node(self, state: AgenticRAGState) -> AgenticRAGState:
        """Node 2: Search in knowledge base using vector search"""
        if not state["input_guardrails_passed"]:
            return state
        
        try:
            print("Searching knowledge base...")
            
            # Search for similar problems in knowledge base
            results = self.vector_store_manager.similarity_search_with_score(state["user_question"], k=3)
            
            knowledge_results = []
            for doc, score in results:
                result = {
                    'question': doc.metadata['question'],
                    'answer': doc.metadata['answer'],
                    'topic': doc.metadata['topic'],
                    'score': float(score),
                    'content': doc.page_content
                }
                knowledge_results.append(result)
            
            print(f"   Found {len(knowledge_results)} similar problems")
            
            return {
                **state,
                "knowledge_base_results": knowledge_results
            }
        except Exception as e:
            print(f" Vector search error: {str(e)}")
            return {
                **state,
                "error_message": f"Vector search error: {str(e)}"
            }

    def web_search_node(self, state: AgenticRAGState) -> AgenticRAGState:
        """Node 3: Perform web search using Tavily"""
        if not state["input_guardrails_passed"]:
            return state
        
        try:
            print("Performing web search...")
            
            # Only do web search if no good knowledge base results found
            should_search = (not state["knowledge_base_results"] or 
                           state["knowledge_base_results"][0]["score"] > 0.7)
            
            if should_search:
                search_query = f"solve step by step math problem: {state['user_question']}"
                web_results = self.web_search_manager.search(search_query)
                processed_results = self.web_search_manager.process_results(web_results, max_results=3)
                
                print(f"   Found {len(processed_results)} web resources")
                
                return {
                    **state,
                    "web_search_results": processed_results
                }
            else:
                print("   Skipped web search - good knowledge base match found")
                return {
                    **state,
                    "web_search_results": []
                }
        except Exception as e:
            print(f" Web search error: {str(e)}")
            return {
                **state,
                "error_message": f"Web search error: {str(e)}"
            }

    def solution_generation_node(self, state: AgenticRAGState) -> AgenticRAGState:
        """Node 4: Generate raw solution using DSPy (before output guardrails)"""
        if not state["input_guardrails_passed"]:
            return state
        
        try:
            print("Generating initial solution...")
            
            # Prepare context from knowledge base and web results
            context = ""
            
            if state["knowledge_base_results"]:
                context += "Knowledge Base Results:\n"
                for i, result in enumerate(state["knowledge_base_results"][:2], 1):
                    context += f"{i}. Question: {result['question']}\n   Answer: {result['answer']}\n\n"
            
            if state["web_search_results"]:
                context += "Web Search Results:\n"
                for i, result in enumerate(state["web_search_results"][:2], 1):
                    context += f"{i}. {result['title']}\n   Content: {result['content']}\n\n"
            
            # Generate raw solution using DSPy
            if context:
                raw_solution = self.dspy_optimizer.solve_problem(state["user_question"], context)
            else:
                raw_solution = self.dspy_optimizer.solve_problem(state["user_question"])
            
            print(f"   Generated solution: {len(raw_solution)} characters")
            
            return {
                **state,
                "raw_solution": raw_solution,
                "guardrail_attempts": 0
            }
            
        except Exception as e:
            print(f" Solution generation error: {str(e)}")
            return {
                **state,
                "error_message": f"Solution generation error: {str(e)}"
            }

    def output_guardrails_node(self, state: AgenticRAGState) -> AgenticRAGState:
        """Node 5: Apply OUTPUT guardrails using Portkey"""
        if not state["input_guardrails_passed"] or not state["raw_solution"]:
            return state
        
        try:
            print("Applying OUTPUT guardrails...")
            
            # Import format_solution_manually function
            from guardrails import format_solution_manually
            
            # Create a proper solution prompt for guardrails
            solution_prompt = f"""
Please format this math solution properly with clear steps:

Original Question: {state["user_question"]}

Raw Solution: {state["raw_solution"]}

Requirements:
1. Start with "Solution:"
2. Break down into numbered steps
3. Show all calculations clearly
4. End with "Therefore, the final answer is..."
5. Use proper mathematical notation

Please provide a well-structured solution:
"""
            
            max_attempts = 3
            attempt = state.get("guardrail_attempts", 0)
            
            while attempt < max_attempts:
                try:
                    print(f"   Attempt {attempt + 1}/{max_attempts}")
                    
                    # This will trigger output guardrails
                    guardrailed_response = self.llm_output_guardrails.invoke([
                        SystemMessage(content="You are a math tutor providing step-by-step solutions. Always follow the formatting requirements."),
                        HumanMessage(content=solution_prompt)
                    ])
                    
                    final_solution = guardrailed_response.content
                    
                    # Additional manual validation
                    required_elements = ["step", "solution", "answer"]
                    has_elements = any(element.lower() in final_solution.lower() for element in required_elements)
                    is_long_enough = len(final_solution) >= 100
                    
                    if has_elements and is_long_enough:
                        print(" Output guardrails PASSED")
                        return {
                            **state,
                            "final_solution": final_solution,
                            "output_guardrails_passed": True,
                            "guardrail_attempts": attempt + 1
                        }
                    else:
                        attempt += 1
                        print(f" Output validation failed on attempt {attempt}")
                        
                except Exception as guardrail_error:
                    attempt += 1
                    print(f" Output guardrails triggered on attempt {attempt}: {str(guardrail_error)}")
            
            # Fallback: Use manual formatting if all attempts fail
            print(" Using fallback manual formatting")
            fallback_solution = format_solution_manually(state["raw_solution"], state["user_question"])
            
            return {
                **state,
                "final_solution": fallback_solution,
                "output_guardrails_passed": False,
                "guardrail_attempts": max_attempts,
                "error_message": "Output guardrails failed, used fallback formatting"
            }
            
        except Exception as e:
            print(f"Output guardrails error: {str(e)}")
            from guardrails import format_solution_manually
            fallback_solution = format_solution_manually(
                state.get("raw_solution", "No solution generated"), 
                state["user_question"]
            )
            return {
                **state,
                "final_solution": fallback_solution,
                "output_guardrails_passed": False,
                "error_message": f"Output guardrails error: {str(e)}"
            }

    def feedback_collection_node(self, state: AgenticRAGState) -> AgenticRAGState:
        """Node 6: Collect human feedback (simulated for demo)"""
        if not state["input_guardrails_passed"] or not state["final_solution"]:
            return state
        
        try:
            print(" Collecting feedback...")
            
            # In a real application, this would collect actual user feedback
            # For demo purposes, we'll simulate feedback based on output guardrails performance
            if state.get("output_guardrails_passed", False):
                simulated_feedback = {
                    "rating": 5,
                    "comments": {
                        "clarity": "Excellent step-by-step explanation",
                        "accuracy": "Mathematically correct and well-formatted",
                        "completeness": "Complete solution with proper structure"
                    }
                }
            else:
                simulated_feedback = {
                    "rating": 3,
                    "comments": {
                        "clarity": "Solution provided but formatting could be improved",
                        "accuracy": "Mathematically correct",
                        "completeness": "Used fallback formatting due to guardrails"
                    }
                }
            
            # Collect feedback using DSPy optimizer
            self.dspy_optimizer.collect_feedback(
                state["user_question"],
                state["final_solution"],
                simulated_feedback["rating"],
                simulated_feedback["comments"]
            )
            
            print(f"   Rating: {simulated_feedback['rating']}/5")
            
            return {
                **state,
                "feedback_rating": simulated_feedback["rating"],
                "feedback_comments": simulated_feedback["comments"]
            }
        except Exception as e:
            print(f"Feedback collection error: {str(e)}")
            return state