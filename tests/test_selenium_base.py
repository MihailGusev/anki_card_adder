from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse_lazy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from .selenium_pages import LoginPage
from anki_word_adder.apps.accounts.models import Learner, Settings, Language


class TestsBase(StaticLiveServerTestCase):
    """Base class for every other selenium test class"""

    def setUp(self) -> None:
        """Create driver"""
        super().setUp()
        service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def tearDown(self) -> None:
        super().tearDown()
        self.driver.quit()


class TestsLoginRequired(TestsBase):
    """Base class for every page that requires user being logged in"""

    def setUp(self) -> None:
        """Creates one user and default settings for him"""
        super().setUp()
        username = 'existent_username'
        password = 'existent_password'
        language = Language(code='ru', name='Russian')
        language.save()

        learner = Learner(username=username)
        learner.set_password(password)
        learner.save()

        Settings(learner=learner, language=language).save()
        self.driver.get('%s%s' % (self.live_server_url, reverse_lazy('accounts:login')))
        LoginPage(self.driver).login(username, password)
