import os
import warnings
warnings.filterwarnings('ignore')

# Environment variables setup
os.environ["GROQ_API_KEY"] = "your groq api key"
os.environ["TAVILY_API_KEY"] = "your tavily api key"
os.environ["PORTKEY_API_KEY"] = "your portkey api key"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
REACT_FRONTEND_URLS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000"
]

# Model Configuration
DEFAULT_MODEL = "moonshotai/kimi-k2-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
VECTOR_COLLECTION = "jee_math_problems"
VECTOR_SIZE = 768

# Guardrails Configuration
IMPROVED_INPUT_GUARDRAIL_CONFIG = {
    "before_request_hooks": [
        {
            "type": "guardrail",
            "id": "math-input-guardrail",
            "checks": [
                {
                    "id": "default.regexMatch",
                    "parameters": {
                        "pattern": r".*(equation|solve|derivative|integral|limit|matrix|probability|geometry|algebra|calculus|trigonometry|statistics|graph|function|find|calculate|determine|evaluate|area|perimeter|volume|radius|diameter|triangle|circle|rectangle|square|angle|pythagorean|theorem|sin|cos|tan|mathematics|math|formula|explain|prove|show|demonstrate).*",
                        "match_type": "contains",
                        "case_sensitive": False
                    },
                    "on_fail": "deny"
                },
                {
                    "id": "default.detectGibberish",
                    "on_fail": "deny"
                },
                {
                    "id": "default.characterCount",
                    "parameters": {
                        "min_length": 10,
                        "max_length": 1000
                    },
                    "on_fail": "deny"
                }
            ]
        }
    ]
}

OUTPUT_GUARDRAIL_CONFIG = {
    "after_request_hooks": [
        {
            "type": "guardrail", 
            "id": "math-output-validation",
            "checks": [
                {
                    "id": "default.contains",
                    "parameters": {
                        "required_phrases": ["Step", "Solution", "Therefore", "Answer"],
                        "match_type": "any"
                    },
                    "on_fail": "retry"
                },
                {
                    "id": "default.characterCount",
                    "parameters": {
                        "min_length": 100,
                        "max_length": 3000
                    },
                    "on_fail": "log"
                },
                {
                    "id": "default.regexMatch",
                    "parameters": {
                        "pattern": r".*(step|solve|answer|therefore|hence|thus|final|result|solution).*",
                        "match_type": "contains",
                        "case_sensitive": False
                    },
                    "on_fail": "retry"
                },
                {
                    "id": "default.detectGibberish",
                    "on_fail": "retry"
                }
            ]
        }
    ]
}