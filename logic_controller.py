import re
import collections

class LogicController:
    """
    Monitors and filters LLM outputs to ensure logical consistency and 
    prevent repetitive loops or 'garbage' content.
    """
    
    def __init__(self, repetition_threshold=0.8, window_size=5):
        self.repetition_threshold = repetition_threshold
        self.window_size = window_size
        self.garbage_patterns = [
            r"<\|.*?\|>",  # Remove special tokens
            r"\[INST\].*?\[/INST\]",  # Remove leaked instructions
            r"### (System|User|Assistant):",  # Remove prompt markers
            r"User:.*",  # Remove hallucinated user input
        ]

    def clean_garbage(self, text: str) -> str:
        """Removes common LLM artifacts and leaked prompt tokens."""
        for pattern in self.garbage_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text.strip()

    def is_looping(self, new_text: str, history: list) -> bool:
        """
        Detects if the model is repeating itself based on word overlap 
        with recent history.
        """
        if not history:
            return False
            
        new_words = set(new_text.lower().split())
        if not new_words:
            return False

        # Check against last few turns
        for prior in history[-3:]:
            prior_text = prior.get("content", "")
            prior_words = set(prior_text.lower().split())
            if not prior_words:
                continue
                
            overlap = len(new_words & prior_words) / len(new_words | prior_words)
            if overlap >= self.repetition_threshold:
                return True
        return False

    def check_n_gram_repetition(self, text: str, n=4) -> bool:
        """Checks for internal repetition within a single response."""
        words = text.lower().split()
        if len(words) < n * 2:
            return False
            
        grams = [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]
        counts = collections.Counter(grams)
        
        if any(count > 2 for count in counts.values()):
            return True
        return False

    def validate_response(self, text: str, history: list) -> (str, bool):
        """
        Main entry point for validation. Returns (cleaned_text, is_valid).
        """
        cleaned = self.clean_garbage(text)
        
        if not cleaned:
            return "[System: Empty response detected]", False
            
        if self.is_looping(cleaned, history):
            return "[System: Loop detected]", False
            
        if self.check_n_gram_repetition(cleaned):
            return "[System: Internal repetition detected]", False
            
        return cleaned, True
