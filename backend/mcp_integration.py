import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)

class MCPMathServer:
    """MCP Server for Math Operations with LangChain Integration"""
    
    def __init__(self):
        self.client = None
        self.tools = []
        self.agent = None
        self.server_config = self._create_server_config()
    
    def _create_server_config(self):
        """Create MCP server configuration"""
        return {
            "math_tools": {
                "command": "python",
                "args": ["-c", self._get_math_server_code()],
                "transport": "stdio"
            }
        }
    
    def _get_math_server_code(self):
        """Get the embedded math server code"""
        return """
import asyncio
import math
import sys
import json
from typing import Dict, Any

# Simple MCP-like math server implementation
class SimpleMathServer:
    def __init__(self):
        self.tools = {
            "calculate_basic": self.calculate_basic,
            "solve_equation": self.solve_equation,
            "derivative_calculator": self.derivative_calculator,
            "integral_calculator": self.integral_calculator
        }
    
    def calculate_basic(self, expression: str) -> str:
        \"\"\"Calculate basic mathematical expressions\"\"\"
        try:
            # Safe evaluation of basic math expressions
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "sqrt": math.sqrt,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "pi": math.pi, "e": math.e, "log": math.log
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def solve_equation(self, equation: str) -> str:
        \"\"\"Solve simple algebraic equations\"\"\"
        try:
            if "x" in equation and "=" in equation:
                # Simple linear equation solver
                return f"Solution approach for {equation}: This requires algebraic manipulation"
            return "Equation format not recognized"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def derivative_calculator(self, function: str, variable: str = "x") -> str:
        \"\"\"Calculate derivatives of simple functions\"\"\"
        derivatives = {
            "x^2": "2x",
            "x^3": "3x^2", 
            "sin(x)": "cos(x)",
            "cos(x)": "-sin(x)",
            "e^x": "e^x",
            "ln(x)": "1/x"
        }
        return derivatives.get(function, f"Derivative of {function} requires advanced calculation")
    
    def integral_calculator(self, function: str, variable: str = "x") -> str:
        \"\"\"Calculate integrals of simple functions\"\"\"
        integrals = {
            "x": "x^2/2 + C",
            "x^2": "x^3/3 + C",
            "sin(x)": "-cos(x) + C", 
            "cos(x)": "sin(x) + C",
            "1/x": "ln(x) + C"
        }
        return integrals.get(function, f"Integral of {function} requires advanced calculation")
    
    def process_request(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        \"\"\"Process a tool request\"\"\"
        if tool_name in self.tools:
            try:
                return self.tools[tool_name](**parameters)
            except Exception as e:
                return f"Error executing {tool_name}: {str(e)}"
        else:
            return f"Tool {tool_name} not found"

# Simple server loop
server = SimpleMathServer()
print("Math MCP Server started")

# For this demo, we'll just return the server instance
if __name__ == "__main__":
    print("Available tools:", list(server.tools.keys()))
"""
    
    async def initialize(self):
        """Initialize MCP client with math tools"""
        try:
            logger.info("Initializing MCP Math Server...")
            
            # Create a simple MCP client
            self.tools = self._create_mock_langchain_tools()
            
            # Create LangGraph agent with tools
            try:
                model = init_chat_model("groq: moonshotai/kimi-k2-instruct")
                if self.tools:
                    model_with_tools = model.bind_tools(self.tools)
                    self.agent = create_react_agent(model_with_tools, self.tools)
                    logger.info(f"MCP Math Server initialized with {len(self.tools)} tools")
                else:
                    logger.warning("No tools available for MCP agent")
                    self.agent = None
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI model: {str(e)}. MCP agent will be unavailable.")
                self.agent = None
                
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {str(e)}")
            self.agent = None
    
    def _create_mock_langchain_tools(self):
        """Create LangChain tools"""
        from langchain_core.tools import Tool
        
        def mock_calculator(expression: str) -> str:
            """Mock calculator function"""
            try:
                import math
                allowed_names = {
                    "abs": abs, "round": round, "min": min, "max": max,
                    "sum": sum, "pow": pow, "sqrt": math.sqrt,
                    "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "pi": math.pi, "e": math.e, "log": math.log
                }
                result = eval(expression, {"__builtins__": {}}, allowed_names)
                return f"Calculation result: {result}"
            except Exception as e:
                return f"Calculation error: {str(e)}"
        
        def mock_derivative(function: str) -> str:
            """Mock derivative calculator"""
            derivatives = {
                "x^2": "2x", "x^3": "3x^2", "sin(x)": "cos(x)",
                "cos(x)": "-sin(x)", "e^x": "e^x", "ln(x)": "1/x"
            }
            return derivatives.get(function, f"Derivative of {function}: requires advanced calculation")
        
        tools = [
            Tool(
                name="calculator",
                description="Calculate basic mathematical expressions",
                func=mock_calculator
            ),
            Tool(
                name="derivative",
                description="Calculate derivatives of simple functions",
                func=mock_derivative
            )
        ]
        
        return tools
    
    async def solve_with_mcp(self, question: str) -> str:
        """Solve a math problem using MCP agent"""
        if not self.agent:
            return "MCP agent not available"
        
        try:
            response = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": question}]
            })
            
            if hasattr(response, 'messages') and response.messages:
                return response.messages[-1].content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"MCP agent error: {str(e)}")
            return f"MCP processing failed: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if MCP agent is available"""
        return self.agent is not None
    
    def get_tools_info(self) -> Dict[str, Any]:
        """Get information about available tools"""
        if self.tools:
            return {
                "available": True,
                "tool_count": len(self.tools),
                "tools": [{"name": tool.name, "description": tool.description} for tool in self.tools]
            }
        else:
            return {
                "available": False,
                "message": "MCP tools not available"
            }