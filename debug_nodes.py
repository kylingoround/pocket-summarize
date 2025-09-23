#!/usr/bin/env python3
"""
Debug script to help identify which node is causing rate limit issues.
This script adds detailed logging to track LLM calls and identify bottlenecks.
"""

import sys
import time
from flow import create_youtube_summarizer_flow

def debug_youtube_summarizer():
    """Run the YouTube summarizer with detailed debugging output."""
    
    print("🔍 YouTube Summarizer Debug Mode")
    print("=" * 50)
    
    # Get YouTube URL from user
    youtube_url = input("Enter YouTube video URL: ").strip()
    
    if not youtube_url:
        print("❌ Error: Please provide a valid YouTube URL")
        return False
    
    # Initialize shared store
    shared = {
        "youtube_url": youtube_url,
        "video_metadata": {},
        "transcript": "",
        "topics": [],
        "topic_results": [],
        "combined_summary": {},
        "html_file_path": ""
    }
    
    print(f"📺 Processing: {youtube_url}")
    print("🔍 Debug mode: Will show detailed LLM call tracking")
    print()
    
    try:
        # Create flow with debugging
        flow = create_youtube_summarizer_flow()
        
        print("🚀 Starting flow execution with debug logging...")
        print("📊 Watch for these indicators:")
        print("   🔍 ExtractTopicsNode: Processing transcript chunks")
        print("   📝 ProcessTopicsBatch: Processing individual topics")
        print("   📞 LLM calls: Each API request")
        print("   ❌ FAILED: Rate limit or other errors")
        print()
        
        start_time = time.time()
        flow.run(shared)
        total_time = time.time() - start_time
        
        print()
        print("✅ Flow execution completed successfully!")
        print(f"⏱️  Total execution time: {total_time:.2f} seconds")
        
        # Display results
        print()
        print("📊 Results Summary:")
        print(f"📹 Video: {shared['video_metadata'].get('title', 'Unknown Title')}")
        print(f"🎯 Topics Found: {len(shared['topics'])}")
        print(f"❓ Q&A Pairs: {len(shared['combined_summary'].get('all_qa_pairs', []))}")
        print(f"💡 Explanations: {len(shared['combined_summary'].get('all_explanations', []))}")
        print(f"🌐 HTML Summary: {shared['html_file_path']}")
        
        return True
        
    except Exception as e:
        print()
        print("❌ Flow execution failed!")
        print(f"💥 Error: {str(e)}")
        print()
        print("🔍 Debug Information:")
        print("   - Check the output above to see which node failed")
        print("   - Look for '❌ FAILED' messages to identify the problematic LLM call")
        print("   - The last successful node before the error is likely the culprit")
        return False

def main():
    """Main function."""
    print("🐛 YouTube Summarizer Node Debugger")
    print("This script helps identify which node is causing rate limit issues.")
    print()
    
    success = debug_youtube_summarizer()
    
    if success:
        print()
        print("🎉 Debug completed successfully!")
        print("If you encountered rate limits, check the output above to see:")
        print("   - Which node was running when the error occurred")
        print("   - How many LLM calls were made before the failure")
        print("   - The size of prompts being sent")
    else:
        print()
        print("⚠️  Debug completed with errors.")
        print("Use the information above to identify the problematic node.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
