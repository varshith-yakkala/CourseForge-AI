class CrossEncoderReranker:

    _model = None

    def __init__(self):
        pass

    @classmethod
    def get_model(cls):
        if cls._model is None:
            print("Loading CrossEncoder lazily...")
            from sentence_transformers import CrossEncoder
            cls._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            print("CrossEncoder loaded.")
        return cls._model

    def rerank(
        self,
        query: str,
        candidates: list,
        top_k: int = 5,
    ):

        if len(candidates) == 0:
            return []

        pairs = []

        for result in candidates:

            chunk = result["embedding"].chunk

            pairs.append(
                (
                    query,
                    chunk.content,
                )
            )

        model = self.get_model()
        scores = model.predict(
            pairs
        )

        ranked = []

        for score, result in zip(
            scores,
            candidates,
        ):

            ranked.append(
                {
                    **result,
                    "rerank_score": float(score),
                }
            )

        ranked.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return ranked[:top_k]