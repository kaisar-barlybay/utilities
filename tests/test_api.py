from unittest import TestCase
import sys
import logging

import pytest

logger = logging.getLogger('default')
sys.path.append(".")  # isort:skip


class TestViews(TestCase):

  @classmethod
  def setUpClass(self):
    super(TestViews, self).setUpClass()

  @classmethod
  def tearDownClass(self):
    super(TestViews, self).tearDownClass()

  # pytest -v -s tests/test_api.py::TestViews::test_format
  @pytest.mark.run_these_please
  def test_format(self):
    from utilities.utils import call_path

    logger.debug('hello world')
    logger.debug(call_path())
