import dspy
from typing import Optional

class EnglishToMiradSignature(dspy.Signature):
    """Translate English text to Mirad."""
    english_text = dspy.InputField(desc="English text to translate")
    mirad_text = dspy.OutputField(desc="Translated text in Mirad")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1")

class TranslatorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(EnglishToMiradSignature)
    
    def forward(self, english_text: str) -> dspy.Prediction:
        """Translate English text to Mirad."""
        prediction = self.generate(english_text=english_text)
        return dspy.Prediction(
            mirad_text=prediction.mirad_text,
            confidence=prediction.confidence
        )
