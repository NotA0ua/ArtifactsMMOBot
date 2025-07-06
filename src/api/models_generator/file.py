from typing import Protocol
from pathlib import Path


class FileWriterProtocol(Protocol):
    def write(self, file_path: str, content: str) -> None:
        pass


class LocalFileWriter:
    @staticmethod
    def write(file_path: str, content: str) -> None:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
