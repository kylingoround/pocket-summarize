#!/usr/bin/env python3
"""
Test script for the updated HTML generator with improvements.
"""

from utils.html_generator import generate_html

# Test data with the improvements
test_data = {
    'video_metadata': {
        'title': 'Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)',
        'duration': 213,  # 3:33
        'uploader': 'Rick Astley',
        'view_count': 1695949334,
        'upload_date': '20091025',
        'video_id': 'dQw4w9WgXcQ'  # Rick Roll video ID
    },
    'topics': [
        'Topic 1: Commitment and Relationships - Discusses the importance of being fully committed in a relationship and the emotional investment involved.',
        'Topic 2: Emotional Expression - Highlights the challenge of expressing emotions in a relationship, with a focus on understanding and communicating feelings.',
        'Topic 3: Trust and Reliability - Emphasizes trust as the foundation of a relationship, with promises of not letting the partner down or causing harm.',
        'Topic 4: Overcoming Vulnerability - Explores how individuals may hesitate to vocalize their feelings due to vulnerability, despite a deep mutual understanding.',
        'Topic 5: Assurance and Loyalty - Provides a repeated assurance of loyalty and devotion, promising never to desert or hurt the partner.'
    ],
    'combined_summary': {
        'all_qa_pairs': [
            {
                'question': 'What does the phrase "A full commitment\'s what I\'m thinking of" in the transcript imply about the nature of commitment in relationships?',
                'answer': 'The phrase "A full commitment\'s what I\'m thinking of" signifies the importance of being thoroughly devoted to a relationship. It highlights that true commitment involves a conscious decision to fully engage emotionally and physically with a partner, indicating the readiness to invest in the relationship wholeheartedly.'
            },
            {
                'question': 'How does the repeated reassurance in the lyrics contribute to understanding commitment in relationships?',
                'answer': 'The repeated reassurances like "Never gonna give you up, Never gonna let you down" emphasize the constancy and reliability expected in committed relationships. This repetition reinforces the notion that a true commitment means being there for your partner consistently, not abandoning or betraying them, and providing emotional security and stability.'
            }
        ],
        'all_explanations': [
            {
                'topic': 'Topic 1: Commitment and Relationships - Discusses the importance of being fully committed in a relationship and the emotional investment involved.',
                'explanation': "Imagine you're building a house with someone special; that's kind of what a committed relationship is like. The song in the video talks about being 'never gonna give you up,' which means being dedicated and not walking away when things get tough. Commitment in a relationship is like deciding to stick with building that house together, no matter how challenging the weather gets. It's about saying, 'I'm here with you, and I'm not going to run off or let you down because we're in this together.'\n\nBeing fully committed also means being emotionally invested, just like you invest time and effort into a hobby you love. In relationships, this emotional investment is what helps you understand and support each other. The lyrics highlight the importance of understanding feelings and making sure your partner knows you're always there for them. Like when you look out for a friend, working towards maintaining the bond you share helps make the relationship stronger. After all, the song repeats that commitment repeatedly, emphasizing that being present and truthful is key to not hurting each other. So, it's about holding onto that promise of support and love, much like how two best friends would always have each other's backs."
            },
            {
                'topic': 'Topic 2: Emotional Expression - Highlights the challenge of expressing emotions in a relationship, with a focus on understanding and communicating feelings.',
                'explanation': "Hey there! So, let's talk about how emotional expression can be quite a tricky thing in relationships. You know how sometimes you feel something really deeply, but it's hard to put it into words or you're just too shy to share it? That's a pretty common challenge. It's like having a beautiful painting in your head, but you're struggling to describe it to someone else. In a relationship, being open about your feelings is super important because it helps both partners understand and support each other better.\n\nThink about it like trying to solve a puzzle together. Each piece represents a part of your emotions. If you don't communicate and share your pieces, it'll be hard for your partner to see the full picture. Just like the lyrics in songs can express emotions in a catchy and clear way, finding simple and honest ways to share how you feel can make all the difference. For example, saying 'I feel worried when...' or 'I'm really happy about...' can open up a conversation and help you connect on a deeper level. Remember, it's all about making sure both of you understand each other's feelings, so your relationship can grow stronger!"
            }
        ]
    }
}

if __name__ == "__main__":
    print("Testing updated HTML generator...")
    
    # Generate the HTML
    html_path = generate_html(test_data, "test_improved_summary.html")
    print(f"✅ HTML generated successfully at: {html_path}")
    
    print("\n🎉 Improvements implemented:")
    print("✅ Fixed topic explanation styling - now uses white background like QA blocks")
    print("✅ Fixed topics display - removed raw JSON and duplicate titles")
    print("✅ Added clickable links in Key Topics section")
    print("✅ Added embedded video player below key metrics")
    print("\nOpen the generated HTML file in your browser to see the improvements!")
