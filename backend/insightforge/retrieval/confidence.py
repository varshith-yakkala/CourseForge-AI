from statistics import mean


class ConfidenceEstimator:

    def estimate(
        self,
        results: list,
    ) -> float:

        if not results:
            return 0.0

        rerank_scores = []

        retrieval_scores = []

        for result in results:

            rerank_scores.append(
                max(
                    0.0,
                    result.get(
                        "rerank_score",
                        0.0,
                    ),
                )
            )

            retrieval_scores.append(
                max(
                    0.0,
                    result.get(
                        "score",
                        0.0,
                    ),
                )
            )

        rerank_component = min(
            mean(rerank_scores) / 10,
            1.0,
        )

        retrieval_component = min(
            mean(retrieval_scores),
            1.0,
        )

        evidence_component = min(
            len(results) / 5,
            1.0,
        )

        confidence = (
            0.55 * rerank_component
            + 0.30 * retrieval_component
            + 0.15 * evidence_component
        )

        confidence = max(
            0.0,
            min(
                confidence,
                1.0,
            ),
        )

        return round(
            confidence,
            2,
        )