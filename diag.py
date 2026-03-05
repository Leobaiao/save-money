import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Current Directory: {os.getcwd()}")
print("--- sys.path ---")
for p in sys.path:
    print(p)

print("\n--- Testing Imports ---")
try:
    import flet
    print(f"Flet imported from: {flet.__file__}")
except Exception as e:
    print(f"Flet import failed: {e}")

try:
    import google
    print(f"Google package base imported from: {google.__path__}")
    import google.generativeai
    print("Google GenerativeAI imported successfully!")
except Exception as e:
    print(f"Google import failed: {e}")
