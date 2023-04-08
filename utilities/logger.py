import os
from typing import Any, List
from .file import check_create_file
import logging
import colorlog


def skip_venv_msgs(record):
  if '\\venv\\' not in record.pathname and '\\Local\\Programs\\Python\\' not in record.pathname:
    return True
  else:
    return False


def get_logger(DEBUG: bool, project_name: str, app_names: List[str], root_app_name: str = 'project') -> Any:
  app_names += ['default', 'utilities', 'tests']
  loggers = {
      'utilities': {
          'handlers': [],
          'level': 'DEBUG' if DEBUG else 'INFO',
      }
  }

  for app_name in app_names:
    loggers[app_name] = {
        'handlers': ['file', 'console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    }
  logs_path = os.path.join(os.getcwd().split(project_name, 1)[0], project_name, root_app_name, 'logs', 'main.log')
  check_create_file(logs_path)

  return {
      'version': 1,
      'disable_existing_loggers': False,
      'formatters': {
          'myformatter': {
              'format': '{lineno}): [{levelname}][{asctime}][{pathname}][{funcName}]:\n {message}',
              # '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
              # {process: d} {thread: d}
              'style': '{',
              # 'datefmt': '%Y-%m-%d:%H:%M:%S',
              'datefmt': '%H:%M:%S',
          },
          'colored': {
              '()': 'colorlog.ColoredFormatter',
              # { % (pathname)s: % (lineno)d}
              'format': "%(log_color)s%(levelname)s: %(asctime_log_color)s[%(asctime)s] %(pathname_log_color)s%(pathname)s:%(lineno_log_color)s%(lineno)d %(funcName_log_color)s%(funcName)s %(message_log_color)s%(message)s",
              'datefmt': '%Y-%m-%d %H:%M:%S',
              'log_colors': {
                  'DEBUG': 'cyan',
                  'INFO': 'green',
                  'WARNING': 'yellow',
                  'ERROR': 'red',
                  'CRITICAL': 'red,bg_white',
              },
              'secondary_log_colors': {
                  'message': {
                      'DEBUG': 'cyan',
                      'INFO': 'green',
                      'WARNING': 'bold_yellow',
                      'ERROR': 'red',
                      'CRITICAL': 'blue,bg_white',
                  },
                  'lineno': {
                      'DEBUG': 'red',
                      'INFO': 'red',
                      'WARNING': 'red',
                      'ERROR': 'red',
                      'CRITICAL': 'red,bg_white',
                  },
                  'levelname': {
                      'DEBUG': 'cyan',
                      'INFO': 'green',
                      'WARNING': 'yellow',
                      'ERROR': 'red',
                      'CRITICAL': 'red,bg_white',
                  },
                  'asctime': {
                      'DEBUG': 'yellow',
                      'INFO': 'yellow',
                      'WARNING': 'yellow',
                      'ERROR': 'yellow',
                      'CRITICAL': 'yellow,bg_white',
                  },
                  'pathname': {
                      'DEBUG': 'green',
                      'INFO': 'green',
                      'WARNING': 'green',
                      'ERROR': 'red',
                      'CRITICAL': 'green,bg_white',
                  },
                  'funcName': {
                      'DEBUG': 'purple',
                      'INFO': 'purple',
                      'WARNING': 'purple',
                      'ERROR': 'purple',
                      'CRITICAL': 'purple,bg_white',
                  },
              }
          }
      },
      'filters': {
          'skip_unreadable_posts': {
              '()': 'django.utils.log.CallbackFilter',
              'callback': skip_venv_msgs,
          }
      },
      'handlers': {
          'console': {
              'level': 'DEBUG',
              'class': 'colorlog.StreamHandler',
              'formatter': 'colored',
              'filters': ['skip_unreadable_posts'],
          },
          'file': {
              'level': 'DEBUG' if DEBUG else 'INFO',
              'class': 'logging.FileHandler',
              'filename': logs_path,
              'encoding': 'utf8',
              'formatter': 'colored',
              'filters': ['skip_unreadable_posts'],
          },
      },
      'root': {
          'handlers': [],
          'level': 'DEBUG' if DEBUG else 'INFO',
      },
      'loggers': loggers
  }


def get_script_logger(level):
  logger = logging.getLogger('default')
  formatter = colorlog.ColoredFormatter(
      fmt='%(log_color)s%(levelname)s: %(asctime_log_color)s[%(asctime)s] %(pathname_log_color)s%(pathname)s:%(lineno_log_color)s%(lineno)d %(funcName_log_color)s%(funcName)s %(message_log_color)s%(message)s',
      log_colors={
          'DEBUG': 'cyan',
          'INFO': 'green',
          'WARNING': 'yellow',
          'ERROR': 'red',
          'CRITICAL': 'red,bg_white',
      },
      datefmt='%Y-%m-%d %H:%M:%S',
      secondary_log_colors={
          'message': {
              'DEBUG': 'cyan',
              'INFO': 'green',
              'WARNING': 'bold_yellow',
              'ERROR': 'red',
              'CRITICAL': 'blue,bg_white',
          },
          'lineno': {
              'DEBUG': 'red',
              'INFO': 'red',
              'WARNING': 'red',
              'ERROR': 'red',
              'CRITICAL': 'red,bg_white',
          },
          'levelname': {
              'DEBUG': 'cyan',
              'INFO': 'green',
              'WARNING': 'yellow',
              'ERROR': 'red',
              'CRITICAL': 'red,bg_white',
          },
          'asctime': {
              'DEBUG': 'yellow',
              'INFO': 'yellow',
              'WARNING': 'yellow',
              'ERROR': 'yellow',
              'CRITICAL': 'yellow,bg_white',
          },
          'pathname': {
              'DEBUG': 'green',
              'INFO': 'green',
              'WARNING': 'green',
              'ERROR': 'red',
              'CRITICAL': 'green,bg_white',
          },
          'funcName': {
              'DEBUG': 'purple',
              'INFO': 'purple',
              'WARNING': 'purple',
              'ERROR': 'purple',
              'CRITICAL': 'purple,bg_white',
          },
      }

  )
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)

  logger.addHandler(handler)
  logger.setLevel(level)
  return logger
