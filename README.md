# Agentic Math RAG with MCP Integration

A sophisticated Retrieval-Augmented Generation (RAG) system specifically designed for mathematical problem-solving, with integration to the Mathematical Computing Platform (MCP). This project combines advanced AI techniques with structured mathematical knowledge to provide accurate and reliable solutions to complex mathematical problems.

## 🚀 Features

- **Advanced RAG Architecture**: Implements a state-of-the-art Retrieval-Augmented Generation system for mathematical problem-solving
- **MCP Integration**: Seamless integration with the Mathematical Computing Platform for symbolic computation
- **Vector Search**: Utilizes Qdrant for efficient vector similarity search across mathematical concepts
- **Web Search Augmentation**: Integrates with Tavily for real-time web search to enhance answer quality
- **Guardrails**: Implements input/output validation and safety checks using Portkey AI
- **DSPy Optimization**: Uses DSPy for optimizing prompts and model interactions
- **Modern Web Interface**: React-based frontend with a clean, responsive UI
- **RESTful API**: FastAPI-based backend with comprehensive API documentation

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Vector Database**: Qdrant
- **Language Models**: Integration with various LLMs through LangChain
- **Mathematical Computation**: MCP
- **Web Search**: Tavily API
- **Guardrails**: Portkey AI
- **Optimization**: DSPy

### Frontend
- **Framework**: React
- **State Management**: React Hooks
- **Styling**: CSS Modules


## 🏗️ Project Structure

```
Maths/
├── backend/                    # Backend application
│   ├── agentic_rag.py          # Main RAG implementation
│   ├── config.py               # Configuration settings
│   ├── data_loader.py          # Data loading utilities
│   ├── dspy_optimizer.py       # DSPy optimization logic
│   ├── fastapi_app.py          # FastAPI application setup
│   ├── guardrails.py           # Input/output validation
│   ├── main.py                 # Entry point
│   ├── mcp_integration.py      # MCP server integration
│   ├── requirements.txt        # Python dependencies
│   ├── vector_store.py         # Vector store management
│   ├── web_search.py           # Web search functionality
│   └── workflow_nodes.py       # Workflow definition
│
├── frontend/                   # Frontend application
│   ├── public/                 # Static files
│   └── src/                    # React source code
│       ├── App.css             # Main styles
│       ├── App.js              # Main React component
│       ├── index.css           # Global styles
│       └── index.js            # Application entry point
│
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 16+
- Qdrant server
- API keys for required services (Groq, Tavily, Portkey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Haridas-Nishita/mathagent.git
   cd mathagent
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Configure environment variables**
   Create a `.env` file in the `backend` directory with the following variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   PORTKEY_API_KEY=your_portkey_api_key
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python fastapi_app.py
   ```

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application**
   Open your browser and navigate to `http://localhost:3000`

## 📚 API Documentation

Once the backend server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤖 How It Works

1. **Query Processing**: User inputs a mathematical query through the web interface
2. **Input Validation**: The system validates and processes the input using guardrails
3. **Knowledge Retrieval**: Relevant mathematical concepts and solutions are retrieved from the vector store
4. **Web Search (if needed)**: For recent or specialized topics, the system can augment with web search results
5. **MCP Integration**: Complex mathematical computations are offloaded to the MCP server
6. **Response Generation**: A comprehensive response is generated using the retrieved information
7. **Output Validation**: The final response is validated before being presented to the user

## 📊 Performance

The system is optimized for:
- High accuracy in mathematical problem-solving
- Low latency for common queries
- Scalability through distributed architecture
- Reliability through comprehensive error handling and fallback mechanisms

## 📄 License

This project is licensed under the MIT License 

