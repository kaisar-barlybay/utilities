from typing import Literal, List
from .utils import chunks
# import gc
# import spacy
# from spacy import Language as SpacyLanguage
import logging
# from string import punctuation
# from heapq import nlargest
from langdetect.lang_detect_exception import LangDetectException
from langdetect import detect  # type: ignore
from .time import Timer
import translators as ts
import traceback
logger = logging.getLogger('default')

ls = Literal['ru', 'en', 'zh-CN']


class NLPFactory:
  english_labels = ['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']
  russian_labels = ['LOC', 'ORG', 'PER']

  def __init__(self) -> None:
    self.timer = Timer(True)

  # def __get_stopwords(self, lang_code: ls) -> List[str]:
  #   match lang_code:
  #     case 'en':
  #       from spacy.lang.en.stop_words import STOP_WORDS
  #       return list(STOP_WORDS)
  #     case 'ru':
  #       from spacy.lang.ru.stop_words import STOP_WORDS
  #       return list(STOP_WORDS)
  #     case 'zh-CN':
  #       from spacy.lang.zh import STOP_WORDS
  #       return list(STOP_WORDS)
  #     case _:
  #       return []

  # def __get_nlp(self, lang_code: ls) -> SpacyLanguage:
  #   match lang_code:
  #     case 'en':
  #       return spacy.load('en_core_web_sm')
  #     case 'ru':
  #       return spacy.load('ru_core_news_sm')
  #     case 'zh-CN':
  #       return spacy.load('zh_core_web_sm')
  #     case _:
  #       return spacy.load('en_core_web_sm')

  def detect_lang_code(self, text: str) -> str:
    try:
      code = detect(text)
    except LangDetectException as e:
      logger.error(f"[no features] text has no features => en language ({text})")
      return 'en'
    match code:
      case 'zh-cn':
        return 'zh-CN'
      case _:
        return code

  def translate_text(self, text: str, from_lang_code: ls, to_lang_code: ls) -> str:
    translated_text = ""
    task_id = f'Translated text with length {len(text)} from {from_lang_code} to {to_lang_code}'
    self.timer.start(task_id)
    for chunk_idx, chunk in enumerate(chunks(text)):
      task_id2 = f'chunk translation task of chunk with length {len(chunk)}'
      self.timer.start(task_id2, 4)
      try:
        translation = ts.google(chunk,
                                from_language=from_lang_code,
                                to_language=to_lang_code)
      except TypeError as e:
        logger.error(f"[ERROR] [{traceback.format_exc()}] {chunk}")
        translation = chunk
      translated_text += ' ' + translation
      self.timer.finish(task_id2, translation)

    self.timer.finish(task_id)
    return translated_text
