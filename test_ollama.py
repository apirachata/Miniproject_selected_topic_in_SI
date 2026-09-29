import ollama

def test_chat():
    try:
        response = ollama.chat(
            model='qwen2.5-coder:7b',
            messages=[{'role': 'user', 'content': 'Test message, reply with hello'}],
            stream=False
        )
        print("Response:", response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_chat()
