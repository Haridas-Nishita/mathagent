import pandas as pd
from datasets import load_dataset
from typing import List, Dict, Any

def load_jee_bench_data():
    """Load and preprocess JEE Bench dataset, keeping only math questions"""
    try:
        dataset = load_dataset("daman1209arora/jeebench")
        df = dataset['test'].to_pandas()
        
        df['subject'] = df['subject'].str.lower()
        math_keywords = ['math', 'mathematics', 'algebra', 'calculus', 'geometry', 'trigonometry']
        math_df = df[df['subject'].str.contains('|'.join(math_keywords), case=False, na=False)].copy()
        
        print(f"Found {len(math_df)} math questions out of {len(df)} total questions")
        
        knowledge_base = []
        for idx, row in math_df.iterrows():
            entry = {
                'id': f"jee_math_{idx}",
                'question': row.get('question', 'Question not available'),
                'description': row.get('description', ''),
                'answer': row.get('gold', ''),
                'topic': row.get('type', 'General'),
                'difficulty': 'Medium',
                'metadata': {
                    'source': 'JEE_Bench',
                    'subject': row.get('subject', 'Mathematics'),
                    'index': row.get('index', idx)
                }
            }
            knowledge_base.append(entry)
        
        print(f"Successfully loaded {len(knowledge_base)} math questions into knowledge base")
        return knowledge_base
    
    except Exception as e:
        print(f"Error loading JEE Bench data: {str(e)}")
        return []

def prepare_documents_for_vector_store(knowledge_base: List[Dict[str, Any]]):
    """Convert knowledge base to documents and metadata for vector store"""
    documents = []
    metadatas = []
    
    for item in knowledge_base:
        content = f"Question: {item['question']}"
        if item.get('description'):
            content += f"\nDescription: {item['description']}"
        if item.get('answer'):
            content += f"\nAnswer: {item['answer']}"
        
        documents.append(content)
        metadata = {
            'id': item['id'],
            'question': item['question'],
            'description': item.get('description', ''),
            'answer': item['answer'],
            'topic': item['topic'],
            'difficulty': item['difficulty'],
            'source': item['metadata']['source'],
            'subject': item['metadata']['subject'],
            'index': item['metadata']['index']
        }
        metadatas.append(metadata)
    
    return documents, metadatas