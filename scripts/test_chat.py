import sys
from pathlib import Path
# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bookmarks.utils import chat_response

print('Testing chat_response fallback...')
print('Q: What is the capital of France?')
print('A:', chat_response('What is the capital of France?'))
print('\nQ: Explain recursion in simple terms.')
print('A:', chat_response('Explain recursion in simple terms.'))
