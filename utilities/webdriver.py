import logging

from utilities.base import Base
from .file import check_create_dir
import os
from typing import Literal, Union
from selenium import webdriver
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
logger = logging.getLogger('default')


class Webdriver(Base):
  def __init__(self,
               webdriver_type: Literal['chromedriver', 'pdf_chrome_driver', 'tordriver'], debug: bool) -> None:
    self.selenium_downloads_path: Union[None, str] = None
    port = 0
    chrome_options = None
    service_args = None
    desired_capabilities = None
    service_log_path = None
    keep_alive = None
    self.debug = debug
    self.chrome_driver_path = self.env('CHROME_DRIVER_PATH')
    self.firefox_binary_path = self.env('FIREFOX_BINARY_PATH')
    self.firefox_profile_path = self.env('FIREFOX_PROFILE_PATH')
    self.geckodriver_path = self.env('GECKODRIVER_PATH')

    match webdriver_type:
      case 'chromedriver':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        if not self.debug:
          chrome_options.add_argument("headless")
        chrome_options.add_argument('--disable-gpu')
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_argument("chrome_cookies")
        chrome_options.add_argument('lang=ru')
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--log-level=3")
        self.driver = Chrome(self.chrome_driver_path, port, chrome_options, service_args, desired_capabilities, service_log_path, chrome_options, keep_alive=keep_alive)
      case 'pdf_chrome_driver':
        chrome_options = webdriver.ChromeOptions()
        # prepare selenium directory
        selenium_downloads_path = os.path.join(os.getcwd(), 'selenium_downloads')
        check_create_dir(selenium_downloads_path)

        # configure chromedriver for download
        profile = {
            "download.default_directory": selenium_downloads_path,
            "download.prompt_for_download": False,  # To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
        }
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", profile)
        self.selenium_downloads_path = selenium_downloads_path
        self.driver = Chrome(self.chrome_driver_path, port, chrome_options, service_args, desired_capabilities, service_log_path, chrome_options, keep_alive=keep_alive)
      case 'tordriver':
        # print(firefox_binary_path, firefox_profile_path, geckodriver_path)
        # print(r"C:\geckodriver.exe" == geckodriver_path)
        binary = FirefoxBinary(self.firefox_binary_path)
        profile = FirefoxProfile(self.firefox_profile_path)
        # profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")
        profile.set_preference("javascript.enabled", True)
        profile.set_preference('network.proxy.type', 4)
        profile.set_preference('network.proxy.socks', '127.0.0.1')
        profile.set_preference('network.proxy.socks_port', 9050)
        profile.set_preference("network.proxy.socks_remote_dns", False)

        profile.update_preferences()

        os.popen(self.firefox_binary_path)

        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['proxy'] = {
            "proxyType": "MANUAL",
            'socksProxy': '127.0.0.1:9150',
            "socksVersion": 5
        }

        options = webdriver.FirefoxOptions()
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36")
        # options.add_argument('lang=ru')
        if not self.debug:
          options.add_argument("--headless")
        self.driver = Firefox(
            profile,
            binary,
            # capabilities=firefox_capabilities,
            options=options,
            executable_path=self.geckodriver_path
        )
      case _:
        self.driver = None

  def scroll_down_page(self):
    ''' Функция прокрутки страницы '''
    position_before = self.driver.execute_script("return window.scrollY")
    height = self.driver.execute_script("return document.body.clientHeight / 2")
    self.driver.execute_script("window.scrollTo(0, window.scrollY + %s)" % height)
    position_after = self.driver.execute_script("return window.scrollY")

    if position_before == position_after:
      return 'end'
    else:
      return "continue"
