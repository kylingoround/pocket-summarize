#!/usr/bin/env python3
"""
Run YouTube summarizer with comprehensive logging to identify issues.
This script provides detailed output and saves logs to file.
"""

import sys
import time
from flow import create_youtube_summarizer_flow
from utils.flow_logger import setup_logging

def main():
    """Main function with comprehensive logging."""
    
    print("🔍 YouTube Summarizer - Debug Mode with Logging")
    print("=" * 60)
    
    # Get YouTube URL from user
    youtube_url = input("Enter YouTube video URL: ").strip()
    
    if not youtube_url:
        print("❌ Error: Please provide a valid YouTube URL")
        return False
    
    # Setup logging
    logger = setup_logging()
    
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
    
    logger.logger.info(f"📺 Processing URL: {youtube_url}")
    logger.logger.info("🔍 Debug mode: Detailed logging enabled")
    
    try:
        # Create and run the flow
        flow = create_youtube_summarizer_flow()
        
        logger.logger.info("🚀 Starting flow execution...")
        start_time = time.time()
        
        flow.run(shared)
        
        total_time = time.time() - start_time
        logger.logger.info(f"✅ Flow execution completed in {total_time:.2f} seconds")
        
        # Log final summary
        summary_data = {
            "video_title": shared['video_metadata'].get('title', 'Unknown'),
            "video_duration": shared['video_metadata'].get('duration', 0),
            "transcript_length": len(shared.get('transcript', '')),
            "topics_found": len(shared.get('topics', [])),
            "qa_pairs": len(shared['combined_summary'].get('all_qa_pairs', [])),
            "explanations": len(shared['combined_summary'].get('all_explanations', [])),
            "html_file": shared.get('html_file_path', ''),
            "execution_time": f"{total_time:.2f} seconds"
        }
        
        logger.log_summary(summary_data)
        
        print()
        print("🎉 SUCCESS! Check the log file for detailed analysis.")
        print(f"📁 Log file: {logger.log_file}")
        
        return True
        
    except Exception as e:
        logger.log_error("Flow", str(e), {
            "youtube_url": youtube_url,
            "shared_keys": list(shared.keys()),
            "topics_count": len(shared.get('topics', [])),
            "transcript_length": len(shared.get('transcript', ''))
        })
        
        print()
        print("❌ FAILED! Check the log file for detailed error analysis.")
        print(f"📁 Log file: {logger.log_file}")
        print(f"💥 Error: {str(e)}")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
