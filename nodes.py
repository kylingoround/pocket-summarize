from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.youtube_metadata import get_video_metadata
from utils.transcriber import get_youtube_transcript
from utils.html_generator import generate_html
from utils.text_splitter import split_text_into_chunks, DEFAULT_MAX_CHARS_PER_CHUNK
import json
import re


MAX_CHARS_PER_CHUNK = DEFAULT_MAX_CHARS_PER_CHUNK
MAX_TOPIC_CHUNKS = 2
MAX_TOPIC_CONTEXT_CHARS = MAX_CHARS_PER_CHUNK * MAX_TOPIC_CHUNKS


def build_topic_context(topic, transcript_chunks, max_chunks=MAX_TOPIC_CHUNKS):
    """Return concatenated transcript chunks relevant to ``topic`` within bounds."""
    if not transcript_chunks:
        return ""

    topic_lower = topic.lower()
    matching_chunks = []
    for chunk in transcript_chunks:
        if topic_lower in chunk.lower():
            matching_chunks.append(chunk)
        if len(matching_chunks) >= max_chunks:
            break

    if not matching_chunks:
        matching_chunks = transcript_chunks[:max_chunks]

    context = "\n\n".join(matching_chunks[:max_chunks]).strip()

    if len(context) > MAX_TOPIC_CONTEXT_CHARS:
        raise ValueError("Topic context exceeds maximum allowed characters for prompts")

    return context

class ExtractVideoDataNode(Node):
    """Extract video metadata and transcript from YouTube URL."""
    
    def prep(self, shared):
        return shared["youtube_url"]
    
    def exec(self, youtube_url):
        # Get video metadata
        video_metadata = get_video_metadata(youtube_url)
        
        # Get transcript
        transcript = get_youtube_transcript(youtube_url)
        transcript_chunks = split_text_into_chunks(transcript, max_chars=MAX_CHARS_PER_CHUNK)

        return {
            "video_metadata": video_metadata,
            "transcript": transcript,
            "transcript_chunks": transcript_chunks
        }

    def post(self, shared, prep_res, exec_res):
        shared["video_metadata"] = exec_res["video_metadata"]
        shared["transcript"] = exec_res["transcript"]
        shared["transcript_chunks"] = exec_res["transcript_chunks"]
        return "default"

class ExtractTopicsNode(Node):
    """Use LLM to identify interesting topics from transcript."""

    def prep(self, shared):
        return {
            "transcript_chunks": shared.get("transcript_chunks", [])
        }

    def exec(self, data):
        transcript_chunks = data.get("transcript_chunks", [])

        if not transcript_chunks:
            return [
                "Main topic discussed in the video",
                "Key insights and lessons",
                "Important facts and data",
                "Practical advice and tips",
                "Interesting examples and stories"
            ]

        candidate_topics = []

        for index, chunk in enumerate(transcript_chunks, start=1):
            if len(chunk) > MAX_CHARS_PER_CHUNK:
                raise ValueError("Transcript chunk exceeds configured maximum size")

            prompt = f"""
Analyze the following portion of a video transcript. List up to three of the most interesting or important topics mentioned in this portion.

Transcript chunk {index}:
{chunk}

Return your answer in JSON with the following structure:
{{
    "candidate_topics": [
        "Topic name: one sentence explanation"
    ]
}}
"""

            response = call_llm(prompt)

            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    chunk_topics = result.get("candidate_topics", [])
                else:
                    chunk_topics = [line.lstrip('-•* ').strip() for line in response.split('\n') if line.strip()]
                candidate_topics.extend([topic for topic in chunk_topics if topic])
            except Exception as e:
                print(f"Error parsing topics for chunk {index}: {e}")

        if not candidate_topics:
            return [
                "Main topic discussed in the video",
                "Key insights and lessons",
                "Important facts and data",
                "Practical advice and tips",
                "Interesting examples and stories"
            ]

        normalized_topics = []
        for topic in candidate_topics:
            normalized = topic.lower().strip()
            normalized_topics.append((normalized, topic))

        # Keep the first occurrence formatting for each normalized topic
        unique_topics = {}
        for normalized, original in normalized_topics:
            unique_topics.setdefault(normalized, original)

        candidate_lines = []
        current_length = 0
        for topic_value in unique_topics.values():
            line = f"- {topic_value}"
            if current_length + len(line) + 1 > MAX_CHARS_PER_CHUNK:
                break
            candidate_lines.append(line)
            current_length += len(line) + 1

        if not candidate_lines and unique_topics:
            first_topic = next(iter(unique_topics.values()))
            candidate_lines.append(f"- {first_topic}")

        candidate_summary = "\n".join(candidate_lines)

        final_prompt = f"""
You are given candidate topics extracted from individual chunks of a video transcript. Select the five topics that best capture the overall video.

Candidate topics:
{candidate_summary}

Return the final topics in JSON format as:
{{
    "topics": [
        "Topic 1: Brief description",
        "Topic 2: Brief description",
        "Topic 3: Brief description",
        "Topic 4: Brief description",
        "Topic 5: Brief description"
    ]
}}
"""

        response = call_llm(final_prompt)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                topics = result.get("topics", [])
            else:
                topics = [line.lstrip('-•* ').strip() for line in response.split('\n') if line.strip()]
            return topics[:5]
        except Exception as e:
            print(f"Error parsing final topics: {e}")
            return list(unique_topics.values())[:5]

    def post(self, shared, prep_res, exec_res):
        shared["topics"] = exec_res
        return "default"

class ProcessTopicsBatch(BatchNode):
    """Map each topic individually to generate Q&A pairs and explanations."""
    
    def prep(self, shared):
        # Return topics with transcript chunks for batch processing
        transcript_chunks = shared.get("transcript_chunks", [])
        topics = shared["topics"]
        return [(topic, transcript_chunks) for topic in topics]

    def exec(self, topic_data):
        # Process ONE topic at a time
        topic, transcript_chunks = topic_data
        context_text = build_topic_context(topic, transcript_chunks)

        if not context_text:
            context_text = "Transcript unavailable. Provide helpful content based on the topic title only."

        # Generate Q&A pairs for this specific topic
        qa_prompt = f"""
Based on the following video transcript, create 2-3 thoughtful questions and answers specifically for this topic: "{topic}"

Transcript:
{context_text}

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
{context_text}

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