class PromptBuilder:

    def build(self, query, results):

        context = ""

        for result in results:
            context += result["embedding"].chunk.content
            context += "\n\n"

        return f"""
You are InsightForge AI.

You are answering questions about uploaded documents.

Use ONLY the information in the context.

If the context contains enough information,
answer naturally.

If the answer is only partially available,
say what is available.

Only say
"I don't have enough information."
when absolutely nothing relevant exists.

Context:

{context}

Question:

{query}

Answer:
"""