from datetime import datetime, date
import pytz
import time
from typing import Any,  Union
import logging
from .utils import call_path


logger = logging.getLogger('default')


def format_datetime(dt: datetime) -> str:
  if dt is not None:
    return dt.strftime('%Y-%m-%d %H:%M:%S')
  return ''


def format_date(dt: Union[datetime, date]) -> str:
  return f"{dt.strftime('%Y-%m-%d')}"


def now() -> datetime:
  return pytz.timezone('Asia/Almaty').localize(datetime.now())


def get_time(y: int, b: int = 1, d: int = 1, h: int = 0, m: int = 0, s: int = 0, assumed_tz: str = 'Asia/Almaty', desired_tz: str = 'Asia/Almaty') -> datetime:
  return pytz.timezone(assumed_tz).localize(datetime(y, b, d, h, m, s)).astimezone(pytz.timezone(desired_tz))


class Timer:
  def __init__(self, debug: bool) -> None:
    self.debug = debug
    self.tasks = {}

  def start(self, task_id: Union[int, str], threshold: float = None) -> None:
    self.tasks[task_id] = {
        "start": time.time(),
        "threshold": threshold
    }

  """  use threshold to filter out logging messages on minimal delta value(delta threshold)  """

  def finish(self, task_id: Union[int, str], result: Any = None) -> None | float:
    t = None
    self.tasks[task_id]["finish"] = time.time()
    self.tasks[task_id]["delta"] = self.tasks[task_id]["finish"] - self.tasks[task_id]["start"]
    if self.tasks[task_id]["threshold"] is not None:
      if self.tasks[task_id]["delta"] < self.tasks[task_id]["threshold"]:
        return t
    if self.debug:
      t = round(self.tasks[task_id]['delta'], 6)
      logger.info(
          f"\n{call_path()} [TIMER #{task_id}] was finished in {t} seconds{f' with result: {result}' if result is not None else ''}")
    try:
      del self.tasks[task_id]
    except Exception as e:
      pass
    return t


class Timer2:
  def __init__(self, task_name: str | None = None) -> None:
    self.start = time.time()
    self.task_name = task_name
    self.elapsed_time: float | None = None

  def finish(self, result: Any = None) -> None | float:
    finish = time.time()
    delta = finish - self.start
    self.elapsed_time = round(delta, 6)
    logger.info(f"\n{call_path()} [TIMER #{self.task_name}] was finished in {self.elapsed_time} seconds{f' with result: {result}' if result is not None else ''}")


def parse_dt_str(dt_str: str) -> datetime:
  d_formats = [
      r'%d %m %Y %H:%M:%S %z',
      r'%Y-%m-%dT%H:%M:%S.%fZ',  # '2022-04-27T00:00:00.000Z'
  ]
  for d_format in d_formats:
    try:
      return datetime.strptime(dt_str, d_format)
    except ValueError as e:
      pass
