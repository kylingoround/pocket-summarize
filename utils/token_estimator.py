"""
Simple token estimation utility for debugging rate limit issues.
This provides rough estimates without requiring tiktoken dependency.
"""

def estimate_tokens(text):
    """
    Rough token estimation: ~4 characters per token for English text.
    This is a simplified estimate - actual tokenization may vary.
    """
    if not text:
        return 0
    
    # Rough estimate: 4 characters per token
    # This is conservative - actual ratio is usually 3-4 chars per token
    return len(text) // 4

def analyze_prompt_tokens(prompt_text):
    """Analyze a prompt and return token usage breakdown."""
    total_tokens = estimate_tokens(prompt_text)
    
    # Split prompt into parts for analysis
    lines = prompt_text.split('\n')
    instruction_tokens = 0
    content_tokens = 0
    
    in_content_section = False
    for line in lines:
        line_tokens = estimate_tokens(line)
        
        if 'transcript' in line.lower() or 'content' in line.lower():
            in_content_section = True
        
        if in_content_section and not line.startswith(' '):
            content_tokens += line_tokens
        else:
            instruction_tokens += line_tokens
    
    return {
        'total_tokens': total_tokens,
        'instruction_tokens': instruction_tokens,
        'content_tokens': content_tokens,
        'estimated_cost_usd': total_tokens * 0.00003  # Rough GPT-4o pricing
    }

def print_token_analysis(prompt_text, label="Prompt"):
    """Print detailed token analysis for a prompt."""
    analysis = analyze_prompt_tokens(prompt_text)
    
    print(f"📊 {label} Token Analysis:")
    print(f"   Total tokens: ~{analysis['total_tokens']:,}")
    print(f"   Instructions: ~{analysis['instruction_tokens']:,}")
    print(f"   Content: ~{analysis['content_tokens']:,}")
    print(f"   Estimated cost: ${analysis['estimated_cost_usd']:.4f}")
    
    # Rate limit warnings
    if analysis['total_tokens'] > 8000:
        print("   ⚠️  WARNING: Large prompt (>8k tokens)")
    if analysis['total_tokens'] > 15000:
        print("   🚨 CRITICAL: Very large prompt (>15k tokens)")
    
    return analysis

if __name__ == "__main__":
    # Test with a sample prompt
    sample_prompt = """
Analyze the following portion of a video transcript. List up to five of the most interesting or important topics mentioned in this portion.

Transcript portion 1:
This is a sample transcript that would be typical for a YouTube video. It contains multiple paragraphs of content discussing various topics. Each paragraph might be several hundred words long, covering different aspects of the main subject. The transcript would continue with more content, including examples, explanations, and detailed information that viewers would find valuable. This pattern would repeat throughout the video, creating a substantial amount of text content that needs to be processed and analyzed.

Return your answer in JSON with the following structure:
{
    "candidate_topics": [
        "Topic name: one sentence explanation"
    ]
}
"""
    
    print_token_analysis(sample_prompt, "Sample Prompt")
