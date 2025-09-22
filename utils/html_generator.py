import os
from datetime import datetime

def generate_html(summary_data, output_path="video_summary.html"):
    """
    Generate a beautiful HTML page for the video summary.
    
    Args:
        summary_data (dict): Dictionary containing all summary information
        output_path (str): Path where to save the HTML file
        
    Returns:
        str: Path to the generated HTML file
    """
    
    # Extract data from summary_data
    video_metadata = summary_data.get('video_metadata', {})
    topics = summary_data.get('topics', [])
    combined_summary = summary_data.get('combined_summary', {})
    qa_pairs = combined_summary.get('all_qa_pairs', [])
    friendly_explanations = combined_summary.get('all_explanations', [])
    
    # Format duration
    duration_seconds = video_metadata.get('duration', 0)
    duration_minutes = duration_seconds // 60
    duration_seconds = duration_seconds % 60
    duration_str = f"{duration_minutes}:{duration_seconds:02d}"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Summary: {video_metadata.get('title', 'Unknown Title')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        .video-title {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .video-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .meta-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .meta-label {{
            font-weight: bold;
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .meta-value {{
            color: #555;
            margin-top: 5px;
        }}
        
        .video-id {{
            background: #e9ecef;
            color: #6c757d;
            padding: 5px 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            display: inline-block;
            margin-top: 10px;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        .section-title {{
            font-size: 2em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            display: block;
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            margin: 10px auto;
            border-radius: 2px;
        }}
        
        .topics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .topic-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .topic-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        }}
        
        .topic-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .qa-item {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 3px solid #28a745;
        }}
        
        .question {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        
        .answer {{
            color: #555;
            line-height: 1.5;
        }}
        
        .explanation {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 3px solid #667eea;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        .explanation-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .explanation-content {{
            color: #555;
            line-height: 1.6;
        }}
        
        .video-embed {{
            width: 100%;
            max-width: 800px;
            height: 450px;
            border-radius: 10px;
            margin: 20px auto;
            display: block;
        }}
        
        .topic-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s ease;
        }}
        
        .topic-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .footer {{
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 40px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .video-title {{
                font-size: 1.8em;
            }}
            
            .section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="video-title">{video_metadata.get('title', 'Unknown Title')}</h1>
            <div class="video-meta">
                <div class="meta-item">
                    <div class="meta-label">Duration</div>
                    <div class="meta-value">{duration_str}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Uploader</div>
                    <div class="meta-value">{video_metadata.get('uploader', 'Unknown')}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Views</div>
                    <div class="meta-value">{video_metadata.get('view_count', 0):,}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Upload Date</div>
                    <div class="meta-value">{video_metadata.get('upload_date', 'Unknown')}</div>
                </div>
            </div>
            
            <!-- Video Shorthand -->
            <div style="text-align: center; margin-top: 15px;">
                <span class="video-id">{video_metadata.get('title', 'Unknown Title')[:50]}{'…' if len(video_metadata.get('title', '')) > 50 else ''}</span>
            </div>
            
            <!-- Video Embed -->
            <iframe class="video-embed" 
                    src="https://www.youtube.com/embed/{video_metadata.get('video_id', '')}" 
                    title="{video_metadata.get('title', 'Video')}"
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
        
        <div class="section">
            <h2 class="section-title">🎯 Key Topics</h2>
            <div class="topics-grid">
"""
    
    # Add topics with clickable links
    for i, topic in enumerate(topics, 1):
        # Clean topic title (remove "Topic X: " prefix if it exists)
        clean_topic = topic
        if topic.startswith(f"Topic {i}: "):
            clean_topic = topic[len(f"Topic {i}: "):]
        
        html_content += f"""
                <div class="topic-card">
                    <div class="topic-title">
                        <a href="#explanation-{i}" class="topic-link">{i}. {clean_topic}</a>
                    </div>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">❓ Questions & Answers</h2>
"""
    
    # Add Q&A pairs
    for i, qa in enumerate(qa_pairs, 1):
        html_content += f"""
            <div class="qa-item">
                <div class="question">Q{i}: {qa.get('question', 'No question')}</div>
                <div class="answer">A{i}: {qa.get('answer', 'No answer')}</div>
            </div>
"""
    
    html_content += """
        </div>
        
        <div class="section">
            <h2 class="section-title">💡 Friendly Explanations</h2>
"""
    
    # Add friendly explanations
    for i, explanation in enumerate(friendly_explanations, 1):
        # Get the topic title and clean it
        topic_title = topics[i-1] if i <= len(topics) else 'Unknown Topic'
        if topic_title.startswith(f"Topic {i}: "):
            clean_topic_title = topic_title[len(f"Topic {i}: "):]
        else:
            clean_topic_title = topic_title
        
        # Extract explanation content if it's a dict, otherwise use as is
        explanation_content = explanation
        if isinstance(explanation, dict):
            explanation_content = explanation.get('explanation', str(explanation))
        
        html_content += f"""
            <div class="explanation" id="explanation-{i}">
                <div class="explanation-title">Topic {i}: {clean_topic_title}</div>
                <div class="explanation-content">{explanation_content}</div>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Created with PocketFlow YouTube Summarizer</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

if __name__ == "__main__":
    # Test the function
    test_data = {
        'video_metadata': {
            'title': 'Test Video',
            'duration': 300,
            'uploader': 'Test User',
            'view_count': 1000,
            'upload_date': '20240101'
        },
        'topics': ['Topic 1', 'Topic 2', 'Topic 3'],
        'combined_summary': {
            'all_qa_pairs': [
                {'topic': 'Topic 1', 'question': 'What is topic 1?', 'answer': 'This is the answer for topic 1.'},
                {'topic': 'Topic 2', 'question': 'What is topic 2?', 'answer': 'This is the answer for topic 2.'}
            ],
            'all_explanations': [
                {'topic': 'Topic 1', 'explanation': 'This is a friendly explanation of topic 1.'},
                {'topic': 'Topic 2', 'explanation': 'This is a friendly explanation of topic 2.'}
            ]
        }
    }
    
    html_path = generate_html(test_data, "test_summary.html")
    print(f"HTML generated at: {html_path}")
