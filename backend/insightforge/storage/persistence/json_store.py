import json
import os


class JsonStore:

    def __init__(self, file_path: str):

        self.file_path = file_path

        os.makedirs(
            os.path.dirname(file_path),
            exist_ok=True,
        )

        if not os.path.exists(file_path):

            with open(
                file_path,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump([], f)

    def load(self):

        with open(
            self.file_path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    def save(self, data):

        with open(
            self.file_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )


JSONStore = JsonStore