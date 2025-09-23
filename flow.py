from pocketflow import Flow
from nodes import (
    ExtractVideoDataNode,
    ExtractTopicsNode, 
    ProcessTopicsBatch,
    CombineResults,
    GenerateHTMLNode
)

def create_youtube_summarizer_flow():
    """Create and return a YouTube video summarizer flow."""
    
    # Create nodes with retry mechanisms for LLM-heavy operations
    extract_data = ExtractVideoDataNode()
    extract_topics = ExtractTopicsNode(max_retries=3, wait=5)  # Retry with 5s wait
    process_topics = ProcessTopicsBatch(max_retries=3, wait=5)  # Retry with 5s wait
    combine_results = CombineResults()
    generate_html = GenerateHTMLNode()
    
    # Connect nodes in sequence with Map Reduce pattern
    extract_data >> extract_topics >> process_topics >> combine_results >> generate_html
    
    # Create flow starting with data extraction
    return Flow(start=extract_data)

if __name__ == "__main__":
    # Test the flow
    flow = create_youtube_summarizer_flow()
    
    # Example shared store
    shared = {
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll for testing
        "video_metadata": {},
        "transcript": "",
        "topics": [],
        "topic_results": [],
        "combined_summary": {},
        "html_file_path": ""
    }
    
    print("Running YouTube Summarizer Flow...")
    flow.run(shared)
    
    print(f"Video Title: {shared['video_metadata'].get('title', 'Unknown')}")
    print(f"Topics Found: {len(shared['topics'])}")
    print(f"Q&A Pairs: {len(shared['combined_summary'].get('all_qa_pairs', []))}")
    print(f"HTML Generated: {shared['html_file_path']}")