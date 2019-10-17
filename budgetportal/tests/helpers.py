"""
Common test helpers.
"""
import sys
import warnings
from datetime import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class BaseSeleniumTestCase(StaticLiveServerTestCase):
    """
    Base class for Selenium tests.

    This saves a screenshot to the current directory on test failure.
    """

    def setUp(self):
        super(BaseSeleniumTestCase, self).setUp()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        chrome_options.add_argument("--no-sandbox")
        self.selenium = webdriver.Chrome(chrome_options=chrome_options)

    def tearDown(self):
        super(BaseSeleniumTestCase, self).tearDown()
        try:
            # https://stackoverflow.com/questions/14991244/how-do-i-capture-a-screenshot-if-my-nosetests-fail
            if sys.exc_info()[0]:  # Returns the info of exception being handled
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
                if not self.selenium.get_screenshot_as_file("%s.png" % now):
                    warnings.warn("Selenium screenshot failed (IOError?)", UserWarning)

        finally:
            self.selenium.quit()
