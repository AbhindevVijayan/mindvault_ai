#!/usr/bin/env python
"""
Test script to verify Ollama integration with MindVault chat system.
Run from project root: python scripts/test_ollama.py
"""

import os
import sys
import subprocess

# Ensure project root is on PYTHONPATH so `config` package is importable
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bookmarks.utils import chat_response, _call_ollama


def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    print("\n[TEST 1] Ollama Connection")
    print("-" * 50)

    try:
        import requests
        model_name = os.getenv('OLLAMA_MODEL', 'mistral:latest')
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': model_name, 'prompt': 'test', 'stream': False},
            timeout=5
        )
        if response.status_code == 200:
            print("✓ Ollama HTTP API is running on localhost:11434")
            return True
        else:
            print(f"✗ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to Ollama HTTP API on localhost:11434 (HTTP request failed)")
        print("  - Trying CLI fallback (calling `ollama` directly)")
        try:
            list_proc = subprocess.run(["ollama", "list"], capture_output=True, text=False, timeout=10)
            model_name = os.getenv('OLLAMA_MODEL', 'mistral:latest')
            list_out = list_proc.stdout.decode('utf-8', errors='replace') if list_proc.stdout else ''
            if list_proc.returncode != 0:
                err = list_proc.stderr.decode('utf-8', errors='replace') if list_proc.stderr else ''
                print("✗ Failed to run `ollama list`:", err or list_out)
                return False
            if model_name in list_out or model_name.split(':')[0] in list_out:
                print("✓ Ollama CLI model is installed")
                return True
            else:
                print("✗ Model not found in `ollama list`. Pull the model first: ollama pull <model>")
                return False
        except FileNotFoundError:
            print("✗ `ollama` CLI not found. Install Ollama: https://ollama.ai")
            return False
        except Exception as e:
            print(f"✗ CLI fallback error: {e}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_ollama_inference():
    """Test inference with _call_ollama function."""
    print("\n[TEST 2] Ollama Inference")
    print("-" * 50)

    try:
        result = _call_ollama("Hello, who are you?")
        if result:
            print(f"✓ Ollama response: {result[:100]}...")
            return True
        else:
            print("✗ Ollama returned empty response")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_chat_response_priority():
    """Test full chat_response with priority order."""
    print("\n[TEST 3] Chat Response Priority (Ollama → OpenAI → Fallback)")
    print("-" * 50)

    try:
        # Test 1: Simple greeting
        response = chat_response("Hello")
        print(f"Response to 'Hello': {response[:80]}...")

        # Test 2: Summary question
        response = chat_response("How do I summarize an article?")
        print(f"Response to 'How do I summarize?': {response[:80]}...")

        # Test 3: Bookmark question
        response = chat_response("Tell me about bookmarks")
        print(f"Response to 'Tell me about bookmarks': {response[:80]}...")

        print("✓ Chat response system working")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_environment_setup():
    """Check environment configuration."""
    print("\n[TEST 4] Environment Configuration")
    print("-" * 50)

    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_serpapi = bool(os.getenv('SERPAPI_API_KEY'))

    print(f"OPENAI_API_KEY: {'Set' if has_openai else 'Not set (optional)'}")
    print(f"SERPAPI_API_KEY: {'Set' if has_serpapi else 'Not set (optional)'}")
    print("✓ Environment check complete")
    return True


def main():
    print("\n" + "=" * 50)
    print("MindVault AI Chat System - Integration Test")
    print("=" * 50)

    results = []

    # Test 1: Connection
    results.append(("Ollama Connection", test_ollama_connection()))

    # Test 2: Inference
    if results[0][1]:  # Only run if connection succeeds
        results.append(("Ollama Inference", test_ollama_inference()))
    else:
        print("\n[TEST 2] Ollama Inference - SKIPPED (no connection)")

    # Test 3: Chat Response
    results.append(("Chat Response Priority", test_chat_response_priority()))

    # Test 4: Environment
    results.append(("Environment Setup", test_environment_setup()))

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n✓ All tests passed! Your chat system is ready.")
    else:
        print("\n✗ Some tests failed. See details above.")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
