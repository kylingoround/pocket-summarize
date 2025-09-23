from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.youtube_metadata import get_video_metadata
from utils.transcriber import get_youtube_transcript
from utils.html_generator import generate_html
from utils.text_splitter import split_text_into_chunks, DEFAULT_MAX_CHARS_PER_CHUNK
from utils.token_estimator import estimate_tokens
import json
import re
import logging
import time


MAX_CHARS_PER_CHUNK = DEFAULT_MAX_CHARS_PER_CHUNK
MAX_TOPIC_CHUNKS = 2
MAX_TOPIC_CONTEXT_CHARS = MAX_CHARS_PER_CHUNK * MAX_TOPIC_CHUNKS


def build_topic_context(topic, transcript_chunks, max_chunks=MAX_TOPIC_CHUNKS):
    """Return concatenated transcript chunks relevant to ``topic`` within bounds."""
    print(f"🔍 Building context for topic: '{topic}'")
    
    if not transcript_chunks:
        print(f"⚠️  No transcript chunks available for topic: '{topic}'")
        return ""

    topic_lower = topic.lower()
    matching_chunks = []
    for i, chunk in enumerate(transcript_chunks):
        if topic_lower in chunk.lower():
            matching_chunks.append(chunk)
            print(f"   ✅ Found matching chunk {i+1} (size: {len(chunk)} chars)")
        if len(matching_chunks) >= max_chunks:
            print(f"   🛑 Reached max chunks limit ({max_chunks})")
            break

    if not matching_chunks:
        print(f"   📄 No matching chunks found, selecting chunks to fit within limit")
        # Smart selection: pick chunks that fit within the limit
        selected_chunks = []
        current_size = 0
        
        for chunk in transcript_chunks:
            # Account for separator (\n\n) between chunks
            separator_size = 2 if selected_chunks else 0
            chunk_with_separator = current_size + separator_size + len(chunk)
            
            if chunk_with_separator <= MAX_TOPIC_CONTEXT_CHARS:
                selected_chunks.append(chunk)
                current_size = chunk_with_separator
            else:
                break
        
        matching_chunks = selected_chunks
        print(f"   📊 Selected {len(matching_chunks)} chunks to fit within limit")

    # Build context
    context = "\n\n".join(matching_chunks).strip()
    context_size = len(context)
    
    print(f"   📊 Context size: {context_size:,} chars (limit: {MAX_TOPIC_CONTEXT_CHARS:,})")
    
    if context_size > MAX_TOPIC_CONTEXT_CHARS:
        print(f"   ❌ ERROR: Context still exceeds limit by {context_size - MAX_TOPIC_CONTEXT_CHARS:,} chars")
        print(f"   🔍 Topic: '{topic}'")
        print(f"   📄 Matching chunks: {len(matching_chunks)}")
        print(f"   📏 Chunk sizes: {[len(chunk) for chunk in matching_chunks]}")
        
        # Final fallback: truncate to fit
        print(f"   🔧 FIXING: Truncating context to fit within limit")
        context = context[:MAX_TOPIC_CONTEXT_CHARS]
        print(f"   ✅ Context truncated, new size: {len(context):,}")

    print(f"   ✅ Context built successfully")
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
        
        print(f"📹 ExtractVideoDataNode: Video extracted successfully")
        print(f"   Title: {exec_res['video_metadata'].get('title', 'Unknown')}")
        print(f"   Transcript length: {len(exec_res['transcript']):,} characters")
        print(f"   Chunks created: {len(exec_res['transcript_chunks'])}")
        print(f"   Chunk sizes: {[len(chunk) for chunk in exec_res['transcript_chunks'][:3]]}...")
        
        return "default"

class ExtractTopicsNode(Node):
    """Use LLM to identify interesting topics from transcript."""
    
    def __init__(self, max_retries=3, wait=5):
        super().__init__(max_retries=max_retries, wait=wait)
        self.node_name = "ExtractTopicsNode"

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

        # OPTIMIZATION: Instead of processing each chunk individually,
        # combine multiple chunks into a single analysis to reduce LLM calls
        combined_chunks = []
        current_length = 0
        max_combined_length = MAX_CHARS_PER_CHUNK * 3  # Allow up to 3 chunks worth of content
        
        for chunk in transcript_chunks:
            if len(chunk) > MAX_CHARS_PER_CHUNK:
                raise ValueError("Transcript chunk exceeds configured maximum size")
            
            if current_length + len(chunk) > max_combined_length:
                # Start a new combined chunk
                combined_chunks.append(chunk)
                current_length = len(chunk)
            else:
                # Add to current combined chunk
                if combined_chunks:
                    combined_chunks[-1] += "\n\n" + chunk
                    current_length += len(chunk) + 2
                else:
                    combined_chunks.append(chunk)
                    current_length = len(chunk)

        # Limit to first 5 combined chunks to control token usage
        combined_chunks = combined_chunks[:5]
        
        candidate_topics = []

        # Process combined chunks instead of individual chunks
        print(f"🔍 {self.node_name}: Processing {len(combined_chunks)} combined chunks")
        
        for index, combined_chunk in enumerate(combined_chunks, start=1):
            prompt = f"""
Analyze the following portion of a video transcript. List up to five of the most interesting or important topics mentioned in this portion.

Transcript portion {index}:
{combined_chunk}

Return your answer in JSON with the following structure:
{{
    "candidate_topics": [
        "Topic name: one sentence explanation"
    ]
}}
"""
            
            estimated_tokens = estimate_tokens(prompt)
            print(f"📞 {self.node_name}: Making LLM call {index}/{len(combined_chunks)} (chunk: {len(combined_chunk)} chars, ~{estimated_tokens:,} tokens)")
            start_time = time.time()
            
            try:
                response = call_llm(prompt)
                elapsed = time.time() - start_time
                print(f"✅ {self.node_name}: LLM call {index} completed in {elapsed:.2f}s")
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ {self.node_name}: LLM call {index} FAILED after {elapsed:.2f}s - {str(e)}")
                raise

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
                print(f"Error parsing topics for portion {index}: {e}")

        if not candidate_topics:
            return [
                "Main topic discussed in the video",
                "Key insights and lessons",
                "Important facts and data",
                "Practical advice and tips",
                "Interesting examples and stories"
            ]

        # Deduplicate topics
        normalized_topics = []
        for topic in candidate_topics:
            normalized = topic.lower().strip()
            normalized_topics.append((normalized, topic))

        # Keep the first occurrence formatting for each normalized topic
        unique_topics = {}
        for normalized, original in normalized_topics:
            unique_topics.setdefault(normalized, original)

        # OPTIMIZATION: Skip the second LLM call and directly select top topics
        # Sort by length (longer descriptions usually indicate more important topics)
        sorted_topics = sorted(unique_topics.values(), key=len, reverse=True)
        
        # Return top 5 topics directly
        return sorted_topics[:5]

    def post(self, shared, prep_res, exec_res):
        shared["topics"] = exec_res
        print(f"📋 {self.node_name}: Extracted {len(exec_res)} topics:")
        for i, topic in enumerate(exec_res, 1):
            print(f"   {i}. {topic}")
        return "default"

class ProcessTopicsBatch(BatchNode):
    """Map each topic individually to generate Q&A pairs and explanations."""
    
    def __init__(self, max_retries=3, wait=5):
        super().__init__(max_retries=max_retries, wait=wait)
        self.node_name = "ProcessTopicsBatch"
    
    def prep(self, shared):
        # Return topics with transcript chunks for batch processing
        transcript_chunks = shared.get("transcript_chunks", [])
        topics = shared["topics"]
        print(f"🔄 {self.node_name}: Starting batch processing of {len(topics)} topics")
        print(f"📄 {self.node_name}: Available transcript chunks: {len(transcript_chunks)}")
        return [(topic, transcript_chunks) for topic in topics]

    def exec(self, topic_data):
        # Process ONE topic at a time
        topic, transcript_chunks = topic_data
        context_text = build_topic_context(topic, transcript_chunks)

        if not context_text:
            context_text = "Transcript unavailable. Provide helpful content based on the topic title only."

        print(f"📝 {self.node_name}: Processing topic '{topic}' (context: {len(context_text)} chars)")

        # OPTIMIZATION: Combine Q&A and explanation generation into a single LLM call
        combined_prompt = f"""
Based on the following video transcript, create both Q&A pairs and an explanation specifically for this topic: "{topic}"

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
    ],
    "explanation": "A friendly, easy-to-understand explanation of {topic}. Write this as if explaining to a friend who has no prior knowledge. Use simple language, analogies, and examples to make it accessible and engaging."
}}

Guidelines:
- Create 2-3 Q&A pairs specifically for this topic
- Questions should be clear and specific to this topic
- Answers should be comprehensive and based on the actual transcript content
- Write explanation in a conversational, friendly tone
- Use simple language that anyone can understand
- Include analogies or examples to make concepts clearer
- Avoid jargon and technical terms (or explain them if necessary)
- Make it engaging and interesting to read
- The explanation should be 2-3 paragraphs long
- Base everything on the actual content from the transcript
- Focus specifically on this topic: {topic}
"""
        
        estimated_tokens = estimate_tokens(combined_prompt)
        print(f"📞 {self.node_name}: Making LLM call for topic '{topic}' (prompt: {len(combined_prompt)} chars, ~{estimated_tokens:,} tokens)")
        start_time = time.time()
        
        try:
            combined_response = call_llm(combined_prompt)
            elapsed = time.time() - start_time
            print(f"✅ {self.node_name}: LLM call for topic '{topic}' completed in {elapsed:.2f}s")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ {self.node_name}: LLM call for topic '{topic}' FAILED after {elapsed:.2f}s - {str(e)}")
            raise
        
        # Parse combined response
        try:
            json_match = re.search(r'\{.*\}', combined_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                qa_pairs = result.get("qa_pairs", [])
                explanation = result.get("explanation", f"This is an interesting topic discussed in the video. {topic} is explored in detail, providing valuable insights and information that viewers can learn from.")
            else:
                # Fallback: create basic Q&A pairs and explanation
                qa_pairs = [{
                    "question": f"What is the main point about {topic}?",
                    "answer": f"This topic is discussed in the video and covers important aspects related to {topic}."
                }]
                explanation = f"This is an interesting topic discussed in the video. {topic} is explored in detail, providing valuable insights and information that viewers can learn from."
        except Exception as e:
            print(f"Error parsing combined response for topic '{topic}': {e}")
            qa_pairs = [{
                "question": f"What is the main point about {topic}?",
                "answer": f"This topic is discussed in the video and covers important aspects related to {topic}."
            }]
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
        
        print(f"📋 {self.node_name}: Batch processing completed")
        print(f"   Topics processed: {len(exec_res_list)}")
        for i, result in enumerate(exec_res_list, 1):
            topic = result.get('topic', 'Unknown')
            qa_count = len(result.get('qa_pairs', []))
            print(f"   {i}. '{topic}' - {qa_count} Q&A pairs")
        
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
        
        print(f"🔄 CombineResults: Results combined successfully")
        print(f"   Total Q&A pairs: {len(exec_res.get('all_qa_pairs', []))}")
        print(f"   Total explanations: {len(exec_res.get('all_explanations', []))}")
        
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
        
        print(f"🌐 GenerateHTMLNode: HTML file created successfully")
        print(f"   File path: {exec_res}")
        
        return "default"