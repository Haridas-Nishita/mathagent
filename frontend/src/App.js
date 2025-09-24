import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

// Configure axios with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Header Component
const Header = ({ systemStatus }) => (
  <div className="header">
    <div className="header-content">
      <div className="title-section">
        <h1>🧮 Agentic Math RAG</h1>
        <p>AI-Powered Math Education with Advanced MCP Integration</p>
      </div>
      <div className="status-grid">
        <div className="status-card">
          <div className={`status-dot ${systemStatus?.status || 'loading'}`}></div>
          <div className="status-info">
            <span className="status-label">System</span>
            <span className="status-value">{systemStatus?.status || 'Loading...'}</span>
          </div>
        </div>
        {systemStatus?.mcp_available !== undefined && (
          <div className="status-card">
            <div className={`status-dot ${systemStatus.mcp_available ? 'healthy' : 'degraded'}`}></div>
            <div className="status-info">
              <span className="status-label">MCP Tools</span>
              <span className="status-value">{systemStatus.mcp_available ? 'Active' : 'Inactive'}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  </div>
);

// Question Input Component
const QuestionInput = ({ question, setQuestion, onSubmit, isLoading }) => (
  <div className="question-card">
    <div className="card-header">
      <h3>💡 Ask Your Math Question</h3>
      <p>Enter any mathematical problem and get step-by-step solutions</p>
    </div>
    <div className="input-group">
      <div className="textarea-container">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Example: What is the derivative of x² + 3x + 2?"
          rows={4}
          disabled={isLoading}
          className="math-input"
        />
        <div className="input-decoration"></div>
      </div>
      <button 
        onClick={onSubmit}
        disabled={isLoading || !question.trim()}
        className={`solve-btn ${isLoading ? 'loading' : ''}`}
      >
        {isLoading ? (
          <>
            <div className="loading-spinner"></div>
            <span>Solving...</span>
          </>
        ) : (
          <>
            <span className="btn-icon">🚀</span>
            <span>Solve with AI</span>
          </>
        )}
      </button>
    </div>
  </div>
);

// Enhanced Solution Display Component
const SolutionDisplay = ({ solution, onFeedback }) => {
  const [showFeedback, setShowFeedback] = useState(false);
  const [rating, setRating] = useState(5);
  const [comments, setComments] = useState({
    clarity: '',
    accuracy: '',
    completeness: ''
  });

  const handleFeedbackSubmit = async () => {
    try {
      await onFeedback(solution.session_id, rating, comments);
      setShowFeedback(false);
      // Success animation or notification could be added here
    } catch (error) {
      console.error('Feedback submission failed:', error);
    }
  };

  return (
    <div className="solution-card">
      <div className="card-header">
        <h3>✨ Solution</h3>
      </div>
      
      {/* Enhanced Solution Info */}
      <div className="solution-metrics">
        <div className="metric-card">
          <div className="metric-icon">🎯</div>
          <div className="metric-content">
            <span className="metric-label">Confidence</span>
            <span className={`metric-value confidence-${solution.confidence >= 0.8 ? 'high' : 'medium'}`}>
              {(solution.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">⚡</div>
          <div className="metric-content">
            <span className="metric-label">Response Time</span>
            <span className="metric-value">{solution.processing_time.toFixed(1)}s</span>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">🔧</div>
          <div className="metric-content">
            <span className="metric-label">Source</span>
            <div className="sources-container">
              {solution.sources.map((source, index) => (
                <span key={index} className={`source-badge ${source.toLowerCase().replace(/\s+/g, '-')}`}>
                  {source}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Guardrails Status */}
      <div className="guardrails-panel">
        <h4>🛡️ Quality Checks</h4>
        <div className="guardrails-grid">
          <div className={`guardrail-badge ${solution.guardrails_passed.input ? 'passed' : 'failed'}`}>
            <span className="badge-icon">{solution.guardrails_passed.input ? '✅' : '❌'}</span>
            <span>Input Validation</span>
          </div>
          <div className={`guardrail-badge ${solution.guardrails_passed.output ? 'passed' : 'failed'}`}>
            <span className="badge-icon">{solution.guardrails_passed.output ? '✅' : '❌'}</span>
            <span>Output Quality</span>
          </div>
        </div>
      </div>

      {/* Question Display */}
      <div className="content-section">
        <h4>❓ Your Question</h4>
        <div className="question-display">
          {solution.question}
        </div>
      </div>

      {/* Solution Display */}
      <div className="content-section">
        <h4>💡 Step-by-Step Solution</h4>
        <div className="solution-content">
          {solution.solution.split('\n').map((line, index) => (
            <p key={index} className={line.trim() ? 'solution-line' : 'solution-break'}>
              {line}
            </p>
          ))}
        </div>
      </div>

      {/* Enhanced Feedback Section */}
      <div className="feedback-section">
        <button 
          onClick={() => setShowFeedback(!showFeedback)}
          className="feedback-toggle"
        >
          <span className="feedback-icon">⭐</span>
          <span>{showFeedback ? 'Hide Feedback' : 'Rate This Solution'}</span>
          <span className={`chevron ${showFeedback ? 'up' : 'down'}`}>▼</span>
        </button>

        {showFeedback && (
          <div className="feedback-form">
            <div className="rating-section">
              <label>Overall Rating</label>
              <div className="star-rating">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRating(star)}
                    className={`star ${star <= rating ? 'filled' : ''}`}
                  >
                    ⭐
                  </button>
                ))}
              </div>
            </div>

            <div className="comments-grid">
              <div className="comment-field">
                <label>💬 Clarity</label>
                <input
                  type="text"
                  value={comments.clarity}
                  onChange={(e) => setComments({...comments, clarity: e.target.value})}
                  placeholder="How clear was the explanation?"
                />
              </div>
              <div className="comment-field">
                <label>🎯 Accuracy</label>
                <input
                  type="text"
                  value={comments.accuracy}
                  onChange={(e) => setComments({...comments, accuracy: e.target.value})}
                  placeholder="How accurate was the solution?"
                />
              </div>
              <div className="comment-field">
                <label>📋 Completeness</label>
                <input
                  type="text"
                  value={comments.completeness}
                  onChange={(e) => setComments({...comments, completeness: e.target.value})}
                  placeholder="How complete was the solution?"
                />
              </div>
            </div>

            <button onClick={handleFeedbackSubmit} className="submit-feedback-btn">
              <span>Submit Feedback</span>
              <span className="btn-arrow">→</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Analytics Dashboard
const Analytics = ({ analytics, knowledgeBaseStats, mcpTools, systemComponents }) => (
  <div className="analytics-dashboard">
    <div className="dashboard-header">
      <h3>📊 System Analytics</h3>
      <p>Real-time insights into system performance</p>
    </div>
    
    <div className="analytics-grid">
      {/* System Health Card */}
      <div className="analytics-card system-health">
        <div className="card-icon">⚙️</div>
        <h4>System Health</h4>
        <div className="health-grid">
          {systemComponents && Object.entries(systemComponents.components || {}).map(([component, status]) => (
            <div key={component} className={`health-item ${status ? 'healthy' : 'unhealthy'}`}>
              <span className="health-icon">{status ? '🟢' : '🔴'}</span>
              <span className="health-name">{component.replace('_', ' ')}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Feedback Analytics Card */}
      <div className="analytics-card feedback-stats">
        <div className="card-icon">💬</div>
        <h4>User Feedback</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-number">{analytics?.total_feedback || 0}</span>
            <span className="stat-label">Total Reviews</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{analytics?.average_rating || 0}/5</span>
            <span className="stat-label">Average Rating</span>
          </div>
        </div>
        {analytics?.rating_distribution && Object.keys(analytics.rating_distribution).length > 0 && (
          <div className="rating-bars">
            {Object.entries(analytics.rating_distribution).map(([rating, count]) => (
              <div key={rating} className="rating-bar">
                <span className="bar-label">{rating}⭐</span>
                <div className="bar-track">
                  <div 
                    className="bar-fill"
                    style={{width: `${(count / analytics.total_feedback) * 100}%`}}
                  ></div>
                </div>
                <span className="bar-count">{count}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Knowledge Base Card */}
      <div className="analytics-card knowledge-base">
        <div className="card-icon">📚</div>
        <h4>Knowledge Base</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-number">{knowledgeBaseStats?.total_problems || 0}</span>
            <span className="stat-label">Math Problems</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{knowledgeBaseStats?.topics?.length || 0}</span>
            <span className="stat-label">Topics</span>
          </div>
        </div>
      </div>

      {/* MCP Tools Card */}
      <div className="analytics-card mcp-tools">
        <div className="card-icon">🔧</div>
        <h4>MCP Integration</h4>
        <div className="mcp-status">
          <div className={`mcp-indicator ${mcpTools?.available ? 'active' : 'inactive'}`}>
            <span className="indicator-dot"></span>
            <span>{mcpTools?.available ? 'Active' : 'Inactive'}</span>
          </div>
          {mcpTools?.available && (
            <div className="tool-count">
              <span className="count-number">{mcpTools.tool_count}</span>
              <span className="count-label">Tools Available</span>
            </div>
          )}
        </div>
        {mcpTools?.tools && (
          <div className="tools-list">
            {mcpTools.tools.slice(0, 3).map((tool, index) => (
              <div key={index} className="tool-item">
                <span className="tool-name">{tool.name}</span>
                <span className="tool-desc">{tool.description.substring(0, 40)}...</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  </div>
);

function App() {
  // State management (removed streaming and MCP checkbox states)
  const [question, setQuestion] = useState('');
  const [solution, setSolution] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [knowledgeBaseStats, setKnowledgeBaseStats] = useState(null);
  const [mcpTools, setMcpTools] = useState(null);
  const [activeTab, setActiveTab] = useState('solve');

  // Load initial data
  useEffect(() => {
    loadSystemData();
    const interval = setInterval(loadSystemData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSystemData = async () => {
    try {
      // Load all system data in parallel
      const [statusRes, analyticsRes, kbRes, mcpRes] = await Promise.all([
        api.get('/health'),
        api.get('/feedback/analytics'),
        api.get('/knowledge-base/stats'),
        api.get('/mcp/tools')
      ]);

      setSystemStatus(statusRes.data);
      setAnalytics(analyticsRes.data);
      setKnowledgeBaseStats(kbRes.data);
      setMcpTools(mcpRes.data);
    } catch (error) {
      console.error('Failed to load system data:', error);
    }
  };

  // Simplified solve function - always uses MCP
  const handleSolve = async () => {
    if (!question.trim()) return;

    setIsLoading(true);
    setSolution(null);

    try {
      const response = await api.post('/solve', {
        question: question.trim(),
        use_mcp: true  // Always use MCP
      });

      setSolution(response.data);
    } catch (error) {
      console.error('Error solving problem:', error);
      // Could add a toast notification here
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (sessionId, rating, comments) => {
    try {
      await api.post('/feedback', {
        session_id: sessionId,
        rating,
        comments
      });

      // Reload analytics after feedback
      const analyticsResponse = await api.get('/feedback/analytics');
      setAnalytics(analyticsResponse.data);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      throw error;
    }
  };

  return (
    <div className="App">
      <Header systemStatus={systemStatus} />

      {/* Enhanced Navigation */}
      <div className="nav-container">
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'solve' ? 'active' : ''}`}
            onClick={() => setActiveTab('solve')}
          >
            <span className="tab-icon">🧮</span>
            <span>Solve Problems</span>
          </button>
          <button 
            className={`nav-tab ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <span className="tab-icon">📊</span>
            <span>Analytics</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {activeTab === 'solve' && (
          <div className="solve-section">
            <QuestionInput
              question={question}
              setQuestion={setQuestion}
              onSubmit={handleSolve}
              isLoading={isLoading}
            />

            {solution && (
              <SolutionDisplay 
                solution={solution}
                onFeedback={handleFeedback}
              />
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <Analytics 
            analytics={analytics}
            knowledgeBaseStats={knowledgeBaseStats}
            mcpTools={mcpTools}
            systemComponents={systemStatus}
          />
        )}
      </div>
    </div>
  );
}

export default App;
