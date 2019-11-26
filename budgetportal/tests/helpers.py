"""
Common test helpers.
"""
import sys
import warnings
from datetime import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


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
        self.selenium.implicitly_wait(10)
        self.wait = WebDriverWait(self.selenium, 5)

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

    def wait_until_text_in(self, selector, text):
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, selector), text
            )
        )
