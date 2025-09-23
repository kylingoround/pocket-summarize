#!/usr/bin/env python3
"""
Test script to verify the rate limit fix works correctly.
This script tests the enhanced call_llm function with retry mechanisms.
"""

import os
import sys
import time
from utils.call_llm import call_llm

def test_rate_limit_handling():
    """Test the rate limit handling in call_llm function."""
    print("🧪 Testing Rate Limit Handling...")
    print("=" * 50)
    
    # Test 1: Basic functionality
    print("Test 1: Basic LLM call")
    try:
        response = call_llm("What is 2+2?")
        print(f"✅ Basic call successful: {response[:50]}...")
    except Exception as e:
        print(f"❌ Basic call failed: {e}")
        return False
    
    # Test 2: Multiple rapid calls to trigger rate limiting
    print("\nTest 2: Multiple rapid calls (may trigger rate limiting)")
    start_time = time.time()
    success_count = 0
    
    for i in range(5):
        try:
            response = call_llm(f"What is {i+1} times {i+1}?")
            success_count += 1
            print(f"  Call {i+1}: ✅ Success")
        except Exception as e:
            print(f"  Call {i+1}: ❌ Failed - {e}")
    
    end_time = time.time()
    print(f"\n📊 Results:")
    print(f"  - Successful calls: {success_count}/5")
    print(f"  - Total time: {end_time - start_time:.2f} seconds")
    print(f"  - Average time per call: {(end_time - start_time)/5:.2f} seconds")
    
    return success_count >= 3  # At least 3 out of 5 should succeed

def test_with_retry_parameters():
    """Test call_llm with custom retry parameters."""
    print("\nTest 3: Custom retry parameters")
    try:
        # Test with more aggressive retry settings
        response = call_llm("Explain the concept of rate limiting in APIs", max_retries=2, base_delay=0.5)
        print(f"✅ Custom retry successful: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Custom retry failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Rate Limit Fix Test Suite")
    print("=" * 50)
    
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ API Key found: {os.environ.get('OPENAI_API_KEY')[:10]}...")
    
    # Run tests
    test1_passed = test_rate_limit_handling()
    test2_passed = test_with_retry_parameters()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"  - Rate limit handling: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  - Custom retry parameters: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Rate limit fix is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
