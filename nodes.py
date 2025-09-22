from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.youtube_metadata import get_video_metadata
from utils.transcriber import get_youtube_transcript
from utils.html_generator import generate_html
import json
import re

class ExtractVideoDataNode(Node):
    """Extract video metadata and transcript from YouTube URL."""
    
    def prep(self, shared):
        return shared["youtube_url"]
    
    def exec(self, youtube_url):
        # Get video metadata
        video_metadata = get_video_metadata(youtube_url)
        
        # Get transcript
        transcript = get_youtube_transcript(youtube_url)
        
        return {
            "video_metadata": video_metadata,
            "transcript": transcript
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["video_metadata"] = exec_res["video_metadata"]
        shared["transcript"] = exec_res["transcript"]
        return "default"

class ExtractTopicsNode(Node):
    """Use LLM to identify interesting topics from transcript."""
    
    def prep(self, shared):
        return shared["transcript"]
    
    def exec(self, transcript):
        prompt = f"""
Analyze the following video transcript and identify the 5 most interesting and important topics discussed.

Transcript:
{transcript}

Please return your response in the following JSON format:
{{
    "topics": [
        "Topic 1: Brief description",
        "Topic 2: Brief description", 
        "Topic 3: Brief description",
        "Topic 4: Brief description",
        "Topic 5: Brief description"
    ]
}}

Focus on:
- Main themes and concepts
- Key insights or lessons
- Important facts or data points
- Practical advice or tips
- Interesting stories or examples

Make sure each topic is distinct and meaningful.
"""
        
        response = call_llm(prompt)
        
        # Extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result["topics"]
            else:
                # Fallback: try to extract topics from text
                lines = response.split('\n')
                topics = []
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                        topic = line.lstrip('-•* ').strip()
                        if topic:
                            topics.append(topic)
                return topics[:5]  # Limit to 5 topics
        except Exception as e:
            print(f"Error parsing topics: {e}")
            # Fallback: return generic topics
            return [
                "Main topic discussed in the video",
                "Key insights and lessons",
                "Important facts and data",
                "Practical advice and tips",
                "Interesting examples and stories"
            ]
    
    def post(self, shared, prep_res, exec_res):
        shared["topics"] = exec_res
        return "default"

class ProcessTopicsBatch(BatchNode):
    """Map each topic individually to generate Q&A pairs and explanations."""
    
    def prep(self, shared):
        # Return topics with transcript for batch processing
        transcript = shared["transcript"]
        topics = shared["topics"]
        # Return list of tuples (topic, transcript) for each topic
        return [(topic, transcript) for topic in topics]
    
    def exec(self, topic_data):
        # Process ONE topic at a time
        topic, transcript = topic_data
        
        # Generate Q&A pairs for this specific topic
        qa_prompt = f"""
Based on the following video transcript, create 2-3 thoughtful questions and answers specifically for this topic: "{topic}"

Transcript:
{transcript}

Please return your response in the following JSON format:
{{
    "qa_pairs": [
        {{
            "question": "What is the main point about {topic}?",
            "answer": "Detailed answer based on the transcript..."
        }},
        {{
            "question": "Why is {topic} important?",
            "answer": "Detailed answer explaining the importance..."
        }}
    ]
}}

Guidelines:
- Create 2-3 Q&A pairs specifically for this topic
- Questions should be clear and specific to this topic
- Answers should be comprehensive and based on the actual transcript content
- Make questions that would help someone understand this specific topic better
- Ensure answers are accurate and well-supported by the transcript
"""
        
        qa_response = call_llm(qa_prompt)
        
        # Generate explanation for this specific topic
        explanation_prompt = f"""
Based on the following video transcript, create a friendly, accessible explanation specifically for this topic: "{topic}"

Transcript:
{transcript}

Please return your response in the following JSON format:
{{
    "explanation": "A friendly, easy-to-understand explanation of {topic}. Write this as if explaining to a friend who has no prior knowledge. Use simple language, analogies, and examples to make it accessible and engaging."
}}

Guidelines:
- Write in a conversational, friendly tone
- Use simple language that anyone can understand
- Include analogies or examples to make concepts clearer
- Avoid jargon and technical terms (or explain them if necessary)
- Make it engaging and interesting to read
- The explanation should be 2-3 paragraphs long
- Base explanation on the actual content from the transcript
- Focus specifically on this topic: {topic}
"""
        
        explanation_response = call_llm(explanation_prompt)
        
        # Parse Q&A pairs
        try:
            qa_json_match = re.search(r'\{.*\}', qa_response, re.DOTALL)
            if qa_json_match:
                qa_json_str = qa_json_match.group(0)
                qa_result = json.loads(qa_json_str)
                qa_pairs = qa_result.get("qa_pairs", [])
            else:
                # Fallback: create basic Q&A pairs
                qa_pairs = [{
                    "question": f"What is the main point about {topic}?",
                    "answer": f"This topic is discussed in the video and covers important aspects related to {topic}."
                }]
        except Exception as e:
            print(f"Error parsing Q&A pairs for topic '{topic}': {e}")
            qa_pairs = [{
                "question": f"What is the main point about {topic}?",
                "answer": f"This topic is discussed in the video and covers important aspects related to {topic}."
            }]
        
        # Parse explanation
        try:
            exp_json_match = re.search(r'\{.*\}', explanation_response, re.DOTALL)
            if exp_json_match:
                exp_json_str = exp_json_match.group(0)
                exp_result = json.loads(exp_json_str)
                explanation = exp_result.get("explanation", f"This is an interesting topic discussed in the video. {topic} is explored in detail, providing valuable insights and information that viewers can learn from.")
            else:
                # Fallback: create basic explanation
                explanation = f"This is an interesting topic discussed in the video. {topic} is explored in detail, providing valuable insights and information that viewers can learn from."
        except Exception as e:
            print(f"Error parsing explanation for topic '{topic}': {e}")
            explanation = f"This is an interesting topic discussed in the video. {topic} is explored in detail, providing valuable insights and information that viewers can learn from."
        
        # Return structured data for this topic
        return {
            "topic": topic,
            "qa_pairs": qa_pairs,
            "explanation": explanation
        }
    
    def post(self, shared, prep_res, exec_res_list):
        # Store all topic results
        shared["topic_results"] = exec_res_list
        return "default"

class CombineResults(Node):
    """Reduce all topic results into a unified summary structure for HTML generation."""
    
    def prep(self, shared):
        return shared["topic_results"]
    
    def exec(self, topic_results):
        # Flatten and organize Q&A pairs and explanations for HTML generation
        all_qa_pairs = []
        all_explanations = []
        
        for result in topic_results:
            # Add topic to each Q&A pair for context
            for qa in result["qa_pairs"]:
                qa["topic"] = result["topic"]
            all_qa_pairs.extend(result["qa_pairs"])
            all_explanations.append({
                "topic": result["topic"],
                "explanation": result["explanation"]
            })
        
        return {
            "all_qa_pairs": all_qa_pairs,
            "all_explanations": all_explanations
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["combined_summary"] = exec_res
        return "default"

class GenerateHTMLNode(Node):
    """Create beautiful HTML page with all the summary data."""
    
    def prep(self, shared):
        return {
            "video_metadata": shared["video_metadata"],
            "topics": shared["topics"],
            "combined_summary": shared["combined_summary"]
        }
    
    def exec(self, summary_data):
        # Generate HTML file
        html_file_path = generate_html(summary_data)
        return html_file_path
    
    def post(self, shared, prep_res, exec_res):
        shared["html_file_path"] = exec_res
        return "default"