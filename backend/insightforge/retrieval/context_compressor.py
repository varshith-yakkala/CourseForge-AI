from difflib import SequenceMatcher


class ContextCompressor:

    def __init__(
        self,
        similarity_threshold: float = 0.90,
    ):

        self.threshold = similarity_threshold

    def compress(
        self,
        results: list,
        max_chunks: int = 5,
    ):

        compressed = []

        existing_text = []

        for result in results:

            text = result["embedding"].chunk.content

            duplicate = False

            for previous in existing_text:

                similarity = SequenceMatcher(
                    None,
                    previous,
                    text,
                ).ratio()

                if similarity >= self.threshold:

                    duplicate = True

                    break

            if duplicate:

                continue

            compressed.append(result)

            existing_text.append(text)

            if len(compressed) >= max_chunks:

                break

        return compressed