from logic_controller import LogicController

def test_logic():
    lc = LogicController()
    
    # Test Garbage Filtering
    garbage = "Hello <|endoftext|> [INST] Do something [/INST] User: What? ### Assistant: Fine."
    cleaned = lc.clean_garbage(garbage)
    print(f"Cleaned: {cleaned}")
    
    # Test Looping Detection
    history = [{"role": "Assistant", "content": "The sky is blue."}]
    looping_text = "The sky is blue."
    is_looping = lc.is_looping(looping_text, history)
    print(f"Is looping: {is_looping}")
    
    # Test N-Gram Repetition
    repetitive_text = "I like apples I like apples I like apples I like apples"
    is_rep = lc.check_n_gram_repetition(repetitive_text)
    print(f"Internal repetition: {is_rep}")

if __name__ == "__main__":
    test_logic()
