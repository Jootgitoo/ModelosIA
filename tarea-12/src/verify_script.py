import sys
import os
from unittest.mock import MagicMock

# Mock gradio before importing the module
sys.modules["gradio"] = MagicMock()

# Add the current directory to sys.path to import practica_vuelo
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from practica_vuelo import chat_logic
except ImportError as e:
    print(f"Error importing chat_logic: {e}")
    sys.exit(1)

def run_test(test_name, input_text, expected_keywords):
    print(f"\n--- Running Test: {test_name} ---")
    print(f"User Input: {input_text}")
    
    # History can be empty for these single-turn tests
    history = []
    
    try:
        response = chat_logic(input_text, history)
        print(f"Bot Response: {response}")
        
        passed = True
        for kw in expected_keywords:
            if kw.lower() not in response.lower():
                print(f"FAILED: Expected keyword '{kw}' not found in response.")
                passed = False
        
        if passed:
            print("TEST PASSED ✅")
        else:
            print("TEST FAILED ❌")
            
    except Exception as e:
        print(f"TEST FAILED with Exception: {e}")

if __name__ == "__main__":
    print("Starting Verification...")
    
    # 1. Prueba de Éxito (Dato existente)
    run_test("Test 1: Berlin Price", "How much is a ticket to Berlin?", ["499", "Berlin"])
    
    # 2. Prueba de "Dato No Disponible"
    run_test("Test 2: Madrid Price", "How much is a ticket to Madrid?", ["unknown", "sorry", "unavailable"]) # Keywords might vary but 'sorry' or 'not have' is likely
    
    # 3. Prueba de Personalidad
    run_test("Test 3: Identity", "Who are you?", ["FlightAI", "helpful assistant"])
