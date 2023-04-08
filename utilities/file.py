from pathlib import Path
import os


def file_or_dir_exists(path: str) -> None:
  return os.path.exists(path)


def check_create_dir(path: str) -> None:
  Path(path).mkdir(parents=True, exist_ok=True)


def check_create_file(path_and_file: str) -> None:
  path, f = os.path.split(path_and_file)
  check_create_dir(path)
  Path(path_and_file).touch(exist_ok=True)
