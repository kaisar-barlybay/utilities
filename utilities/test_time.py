import logging
from unittest import TestCase
import sys
from .time import Timer2
import time
sys.path.append(".")  # isort:skip
logger = logging.getLogger('default')


class TestViews(TestCase):

  @classmethod
  def setUpClass(self):
    super(TestViews, self).setUpClass()

  @classmethod
  def tearDownClass(self):
    super(TestViews, self).tearDownClass()

  # pytest -v -s utilities/test_time.py::TestViews::test_timer
  def test_timer(self):
    t = Timer2('asd')
    time.sleep(2)
    t.finish(None)
    # t2 = Timer2()
    # time.sleep(5)
    # t2.finish()
