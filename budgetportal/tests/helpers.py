"""
Common test helpers.
"""
import sys
import warnings
from datetime import datetime

from django.core.management import call_command
from django.contrib.staticfiles.testing import LiveServerTestCase
from django.db import connections
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BaseSeleniumTestCase(LiveServerTestCase):
    """
    Base class for Selenium tests.

    This saves a screenshot to the current directory on test failure.
    """

    def setUp(self):
        super(BaseSeleniumTestCase, self).setUp()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        chrome_options.add_argument("--no-sandbox")
        d = DesiredCapabilities.CHROME
        d["loggingPrefs"] = {"browser": "ALL"}
        self.selenium = webdriver.Chrome(
            chrome_options=chrome_options, desired_capabilities=d
        )
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
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), text)
        )

    def _fixture_teardown(self):
        # Allow TRUNCATE ... CASCADE and don't emit the post_migrate signal
        # when flushing only a subset of the apps
        for db_name in self._databases_names(include_mirrors=False):
            # Flush the database
            inhibit_post_migrate = (
                self.available_apps is not None
                or (  # Inhibit the post_migrate signal when using serialized
                    # rollback to avoid trying to recreate the serialized data.
                    self.serialized_rollback
                    and hasattr(connections[db_name], "_test_serialized_contents")
                )
            )
            call_command(
                "flush",
                verbosity=0,
                interactive=False,
                database=db_name,
                reset_sequences=False,
                allow_cascade=True,
                inhibit_post_migrate=inhibit_post_migrate,
            )


class WagtailHackLiveServerTestCase(LiveServerTestCase):
    """
    We need to overload the LiveServerTestCase class to resolve:
    https://github.com/wagtail/wagtail/issues/1824
    """
    def _fixture_teardown(self):
        # Allow TRUNCATE ... CASCADE and don't emit the post_migrate signal
        # when flushing only a subset of the apps
        for db_name in self._databases_names(include_mirrors=False):
            # Flush the database
            inhibit_post_migrate = (
                self.available_apps is not None
                or (  # Inhibit the post_migrate signal when using serialized
                    # rollback to avoid trying to recreate the serialized data.
                    self.serialized_rollback
                    and hasattr(connections[db_name], "_test_serialized_contents")
                )
            )
            call_command(
                "flush",
                verbosity=0,
                interactive=False,
                database=db_name,
                reset_sequences=False,
                allow_cascade=True,
                inhibit_post_migrate=inhibit_post_migrate,
            )
