import pandas as pd
from django.db.models import QuerySet
import environ  # type: ignore
from typing import TypeVar
from datetime import datetime
from typing import Literal, Generator, Union, List
import requests
import pytz
import inspect
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
IMethod = Literal['GET', 'POST']

env = environ.Env()
environ.Env.read_env()


def json_default() -> dict:
  return {}


def get_engine(username: Union[str, None] = None, password: Union[str, None] = None, host: Union[str, None] = None, db_name: Union[str, None] = None) -> Engine:
  return create_engine(f"postgresql://{username or env('DATABASE_USER')}:{password or env('DATABASE_PASSWORD')}@{host or env('DATABASE_HOST')}:5432/{db_name or env('DATABASE_NAME')}")


def localize(dt: datetime) -> datetime:
  return pytz.timezone('Asia/Almaty').localize(dt)


def format_datetime(dt: datetime) -> str:
  if dt is not None:
    return dt.strftime('%Y-%m-%d %H:%M:%S')
  return ''


def chunks(text: str, threshold: int = 5000) -> Generator[str, None, None]:
  paragraphs = [p for p in text.split('\n')]
  chunk = ''
  par_sep = '\n'
  sent_sep = '.'
  word_sep = ' '

  for par_idx, paragraph in enumerate(paragraphs):
    if par_idx != 0:
      chunk += par_sep
    for _ in range(2):
      if len(chunk) + len(paragraph) + 1 > threshold:
        if chunk != '':
          yield chunk
          chunk = ''
          continue
        else:
          sentences = [p for p in paragraph.split('.')]
          for sent_idx, sentence in enumerate(sentences):
            if sent_idx != 0 or sentence == '':
              chunk += sent_sep
            for _ in range(2):
              if len(chunk) + len(sentence) + 1 > threshold:
                if chunk != '':
                  yield chunk
                  chunk = ''
                  continue
                else:
                  words = [p for p in sentence.split(' ')]
                  for word_idx, word in enumerate(words):
                    if word == 'systems':
                      pass
                    if word_idx != 0:
                      chunk += word_sep
                    if len(chunk) + len(word) + 1 > threshold:
                      yield chunk
                      chunk = ''
                    chunk += word
              else:
                sent_sep = par_sep + sent_sep if sent_idx == len(sentences) - 1 else sent_sep
                chunk += sentence
                break
            sent_sep = '.'
      else:
        chunk += paragraph
        break
    par_sep = '\n'
  yield chunk


def denonify(d: dict) -> dict:
  # note that using d.keys() here insted of d.items() allows us change(via del) d size while iterating
  for k in list(d.keys()):
    v = d[k]
    try:
      if v == None or v == [] or v == {} or v == '' or pd.isnull(v):
        del d[k]
    except:
      if v == None or v == [] or v == {} or v == '' or pd.isnull(v).all():
        del d[k]
  return d


def is_string_true(string: Union[str, None]) -> Union[bool, None]:
  if string is None:
    return None
  return string in ['True', 'true', 'TRUE', 1]


T = TypeVar('T')


def batches(l: Union[QuerySet[T], List[T]], batch_size: int) -> Generator[List[T], None, None]:
  if isinstance(l, QuerySet):
    t = l.count()
  elif isinstance(l, list):
    t = len(l)
  else:
    raise ValueError
  for i in range((t - 1) // batch_size + 1):
    yield l[i*batch_size:(i+1)*batch_size]


def format_traceback(limit: int):
  return '->'.join([inspect.stack()[func_level].function for func_level in reversed(range(1, limit))])


def call_path():
  return f'{inspect.stack()[2].filename}:{inspect.stack()[2].lineno} {inspect.stack()[2].function}'


def fetch(url: str, method: IMethod = 'GET', params={}, data={}, stream=False):
  # SSLError - dh key too small
  requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
  config = {
      "method": method,
      "url": url,
      "params": params,
      "data": data,
      "stream": stream,
      # "headers": {
      #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
      # }
  }

  r = requests.request(**config, verify=False)

  r.encoding = r.apparent_encoding

  return r
