import ollama

from django.conf import settings


class AIService:
    """
    Central AI service for Nivqora Task.

    The rest of the application communicates with AI
    through this class instead of directly calling Ollama.
    """

    def __init__(self):
        self.provider = getattr(
            settings,
            "AI_PROVIDER",
            "ollama"
        ).lower()

        self.model = getattr(
            settings,
            "AI_MODEL",
            "llama3.2:3b"
        )

    def generate(self, prompt):
        """
        Generate an AI response using the configured provider.
        """

        if self.provider == "ollama":
            return self._generate_ollama(prompt)

        if self.provider == "gemini":
            return self._generate_gemini(prompt)

        if self.provider == "groq":
            return self._generate_groq(prompt)

        raise ValueError(
            f"Unsupported AI provider: {self.provider}"
        )

    def _generate_ollama(self, prompt):
        """
        Generate a response using local Ollama.
        """

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]

    def _generate_gemini(self, prompt):
        """
        Gemini integration will be added later.
        """

        raise NotImplementedError(
            "Gemini integration is not configured yet."
        )

    def _generate_groq(self, prompt):
        """
        Groq integration will be added later.
        """

        raise NotImplementedError(
            "Groq integration is not configured yet."
        )