import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GeminiGenerator:
    """
    Kept the class name the same so the rest of the project
    doesn't need any import changes.
    """

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("Missing GROQ_API_KEY")

        self.client = Groq(api_key=api_key)

        self.model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

    def generate(
        self,
        prompt: str,
    ):

        print("\n" + "=" * 80)
        print("MODEL:", self.model)
        print("PROMPT LENGTH:", len(prompt))
        print("=" * 80)

        try:

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.2,
                max_tokens=4096,
            )

            answer = completion.choices[0].message.content

            if answer is None:
                answer = ""

            return {
                "success": True,
                "answer": answer.strip(),
                "error": None,
            }

        except Exception as e:

            print("\nGroq request failed.")
            print(type(e).__name__)
            print(e)

            return {
                "success": False,
                "answer": "",
                "error": str(e),
            }