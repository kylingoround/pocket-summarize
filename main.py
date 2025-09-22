from flow import create_youtube_summarizer_flow

def main():
    """Main function to run the YouTube video summarizer."""
    
    # Get YouTube URL from user
    youtube_url = input("Enter YouTube video URL: ").strip()
    
    if not youtube_url:
        print("Error: Please provide a valid YouTube URL")
        return
    
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
    
    # Create and run the flow
    print("🎬 Starting YouTube Video Summarizer...")
    print(f"📺 Processing: {youtube_url}")
    print()
    
    try:
        flow = create_youtube_summarizer_flow()
        flow.run(shared)
        
        # Display results
        print("✅ Summary Complete!")
        print()
        print(f"📹 Video: {shared['video_metadata'].get('title', 'Unknown Title')}")
        print(f"⏱️  Duration: {shared['video_metadata'].get('duration', 0)} seconds")
        print(f"👤 Channel: {shared['video_metadata'].get('uploader', 'Unknown')}")
        print(f"👀 Views: {shared['video_metadata'].get('view_count', 0):,}")
        print()
        print(f"🎯 Topics Found: {len(shared['topics'])}")
        for i, topic in enumerate(shared['topics'], 1):
            print(f"   {i}. {topic}")
        print()
        print(f"❓ Q&A Pairs: {len(shared['combined_summary'].get('all_qa_pairs', []))}")
        print(f"💡 Explanations: {len(shared['combined_summary'].get('all_explanations', []))}")
        print()
        print(f"🌐 HTML Summary: {shared['html_file_path']}")
        print()
        print("🎉 Your video summary is ready! Open the HTML file in your browser to view it.")
        
    except Exception as e:
        print(f"❌ Error processing video: {str(e)}")
        print("Please check that the URL is valid and the video has captions available.")

if __name__ == "__main__":
    main()