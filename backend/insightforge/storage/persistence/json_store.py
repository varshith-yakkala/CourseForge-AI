import json
import os


class JsonStore:

    def __init__(self, file_path: str | Path | None = None, storage_file: str | Path | None = None):
        target_path = file_path or storage_file or "documents.json"
        self.file_path = str(target_path)

        parent_dir = os.path.dirname(self.file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        if not os.path.exists(self.file_path):

            with open(
                self.file_path,
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