
from requests import Request
from deep_translator import GoogleTranslator
from pprint import PrettyPrinter
from typing import Any, Literal, Union, List, Tuple
from .time import now
from datetime import datetime
from .utils import denonify
from django.http.request import QueryDict
import paramiko  # type: ignore
import os
import logging
from .time import Timer2
import environ  # type: ignore
from zoneinfo import ZoneInfo
import traceback
from io import BytesIO
import inspect
import json
env = environ.Env()
environ.Env.read_env()
pp = PrettyPrinter(indent=2)
logger = logging.getLogger('default')


class Base:
  def denonify(self, d: dict) -> dict:
    return denonify(d)

  def pprint_request(self, req: Request):
    return ('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

  def timer(self, task_name: str):
    return Timer2(task_name)

  def now(self) -> datetime:
    return now()

  def env(self, key: str) -> str:
    return env(key)

  def get_serializer_name(self, GET: QueryDict) -> str | None:
    view = GET.get('view', None)
    row = GET.get('row', None)
    element = GET.get('element', None)
    item = GET.get('item', None)
    targets = [view, row, element, item]
    try:
      return next(item for item in targets if item is not None)
    except StopIteration as e:
      return None

  def translate_text(self, text: str, from_lang_code: str, to_lang_code: str) -> str:
    import translators as ts
    try:
      return GoogleTranslator(source=from_lang_code, target=to_lang_code).translate(text)
    except Exception as e:
      logger.error(f"[ERROR] [{traceback.format_exc()}] {text}")
      return ''

  def dict_to_file(self, path: str, data: dict) -> None:
    with open(path, 'w', encoding="utf-8") as f:
      for field_name, content in data.items():
        match content:
          case dict():
            s = pp.pformat(content)
          case datetime():
            s = content
          case _:
            s = json.dumps(content)
        f.write(f'[{field_name}]\n{s}\n\n')

  def current_line(self) -> str:
    method_name = inspect.stack()[1][3]
    lineno = inspect.stack()[1][2]
    caller_path = inspect.stack()[1][1]
    return f'{caller_path}:{lineno}'

  def format_datetime(self, dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")

  def disjoint_dict(self, d: dict, keys: List[str]) -> dict:
    return {k: v for k, v in d.items() if k not in keys}

  def get_text(self, file_name: str) -> str | None:
    def t(encoding: str) -> str:
      with open(file_name, 'r', encoding=encoding) as f_read:
        return f_read.read()
    try:
      try:
        return t('utf-8')
      except UnicodeDecodeError as e:
        return t('ISO-8859-1')
    except Exception as e:
      logger.error(e)
      return None

  def is_true(self, val: Any) -> bool:
    return val in [True, 'True', 'true', 1]

  def path_to_stream(self, path: str) -> BytesIO:
    with open(path, "rb") as fh:
      return BytesIO(fh.read())

  def open_socket(self, ip: str, username: str, password: str, port: Union[int, None] = None) -> Tuple[paramiko.SSHClient, paramiko.SFTPClient]:
    db_ssh = self.get_ssh(ip=ip, username=username, password=password, port=port)
    db_sftp = db_ssh.open_sftp()
    return db_ssh, db_sftp

  def get_ssh(self, ip: str, username: str, password: str, port: Union[int, None] = None) -> paramiko.SSHClient:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if port is not None:
      ssh.connect(ip, username=username, port=port, password=password)
    else:
      ssh.connect(ip, username=username, password=password)
    return ssh

  def localize(self, dt: datetime) -> datetime:
    return dt.replace(tzinfo=ZoneInfo('Asia/Almaty'))

  # linux join functionality if you are using windows
  def join(self, a: str, *p: tuple) -> (Union[str, Any]):
    a = os.fspath(a)
    sep = self._get_sep(a)
    path = a
    if not p:
      path[:0] + sep  # 23780: Ensure compatible data type even if p is null.
    for b in map(os.fspath, p):
      if b.startswith(sep):
        path = b
      elif not path or path.endswith(sep):
        path += b
      else:
        path += sep + b

    return path

  def _get_sep(self, path: str) -> Literal[b'/', '/']:
    if isinstance(path, bytes):
      return b'/'
    else:
      return '/'
