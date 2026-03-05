import os
import google.generativeai as genai

# Use the key from the terminal if not in environment
api_key = os.getenv('GEMINI_API_KEY') or input("Digite sua API Key para diagnostico: ").strip()
genai.configure(api_key=api_key)

print("\n--- Modelos Disponíveis ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Nome: {m.name}")
            print(f"Display Name: {m.display_name}")
            print(f"Descrição: {m.description}")
            print("-" * 30)
except Exception as e:
    print(f"Erro ao listar modelos: {e}")
