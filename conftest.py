from utilities.logger import get_script_logger


def pytest_sessionstart(session):
  """
  Called after the Session object has been created and
  before performing collection and entering the run test loop.
  """
  # configure logger for each test case once
  logger = get_script_logger('DEBUG')
