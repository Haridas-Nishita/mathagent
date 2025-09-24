import dspy
import pandas as pd
import os
from typing import Dict

class DSPyMathOptimizer:
    """DSPy-based optimizer for math education with human feedback"""
    
    def __init__(self):
        # Import configuration from config
        from config import DEFAULT_MODEL
        
        # Configure DSPy with Groq
        lm = dspy.LM(model=f"groq/{DEFAULT_MODEL}", api_key=os.environ.get("GROQ_API_KEY"))
        dspy.configure(lm=lm)
        
        self.rag_module = self._create_rag_module()
        self.feedback_data = []
        
    def _create_rag_module(self):
        """Create DSPy RAG module for math problems"""
        
        class MathRAG(dspy.Module):
            def __init__(self):
                super().__init__()
                self.generate_answer = dspy.ChainOfThought("question, context -> solution")
            
            def forward(self, question, context=""):
                prediction = self.generate_answer(question=question, context=context)
                return dspy.Prediction(solution=prediction.solution)
        
        return MathRAG()
    
    def solve_problem(self, question: str, context: str = ""):
        """Solve a math problem using the RAG module"""
        try:
            result = self.rag_module(question=question, context=context)
            return result.solution
        except Exception as e:
            return f"Error solving problem: {e}"
    
    def collect_feedback(self, question: str, generated_solution: str, rating: int, comments: dict):
        """Collect human feedback"""
        feedback_entry = {
            "question": question,
            "generated_solution": generated_solution,
            "rating": rating,
            "comments": comments,
            "timestamp": pd.Timestamp.now()
        }
        self.feedback_data.append(feedback_entry)
        print(f"Feedback collected: Rating {rating}/5")
    
    def get_feedback_analytics(self):
        """Get feedback analytics"""
        if not self.feedback_data:
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "rating_distribution": {}
            }
        
        df = pd.DataFrame(self.feedback_data)
        total = len(self.feedback_data)
        avg_rating = df['rating'].mean()
        
        rating_dist = {}
        for f in self.feedback_data:
            rating = f["rating"]
            rating_dist[rating] = rating_dist.get(rating, 0) + 1
        
        return {
            "total_feedback": total,
            "average_rating": round(avg_rating, 2),
            "rating_distribution": rating_dist
        }