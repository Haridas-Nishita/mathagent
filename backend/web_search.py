from langchain_tavily import TavilySearch

class WebSearchManager:
    """Manages web search operations using Tavily"""
    
    def __init__(self):
        self.tavily_search = TavilySearch(
            max_results=5,
            topic="general",
            include_answer=True,
            search_depth="advanced",
            include_domains=["mathway.com", "wolframalpha.com", "khanacademy.org", "symbolab.com"]
        )
    
    def search(self, query: str):
        """Perform web search"""
        return self.tavily_search.invoke({"query": query})
    
    def process_results(self, results, max_results: int = 3):
        """Process and format web search results"""
        processed_results = []
        for result in results.get('results', [])[:max_results]:
            processed_results.append({
                'title': result.get('title', ''),
                'content': result.get('content', '')[:500],  # Limit content length
                'url': result.get('url', '')
            })
        return processed_results