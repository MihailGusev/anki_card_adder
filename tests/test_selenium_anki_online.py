# https://www.selenium.dev/documentation/webdriver/getting_started/
import time
import subprocess

from django.urls import reverse_lazy

from .selenium_pages import RegisterPage, MainPage
from .test_selenium_base import TestsBase, TestsLoginRequired


def run_anki():
    path = 'C:\\Program Files\\Anki\\anki.exe'
    return subprocess.Popen([path])


class TestsRegister(TestsBase):
    url = reverse_lazy('accounts:register')

    @classmethod
    def setUpClass(cls) -> None:
        cls.anki = run_anki()
        # Give some tome to run anki and AnkiConnect server
        time.sleep(2)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.anki.terminate()
        super().tearDownClass()

    def setUp(self) -> None:
        """Create driver and open registragion page"""
        super().setUp()
        self.driver.get('%s%s' % (self.live_server_url, self.url))

    def test_register_with_new_credentials_and_select_deck(self):
        """Registering when anki is running and with valid credentials must:
        1) open main page
        2) show two info messages (about language and added note type)
        3) show deck selector controls
        When deck is selected card adding controls must be shown
        """
        RegisterPage(self.driver).register()
        main_page = MainPage(self.driver)
        main_page.wait_messages(2)

        self.assertTrue(main_page.are_deck_selection_controls_visible())
        self.assertFalse(main_page.are_card_adding_controls_visible())
        self.assertEqual(2, main_page.get_info_messages_count())
        self.assertEqual(0, main_page.get_error_messages_count())

        main_page.submit_deck_id()
        self.assertTrue(main_page.are_deck_selection_controls_removed())
        self.assertTrue(main_page.are_card_adding_controls_visible())


class TestsMain(TestsLoginRequired):
    def test_get(self):
        """Just registered existing user must see new note message and deck controls if Anki is online"""
        main_page = MainPage(self.driver)
        main_page.wait_messages(1)
        self.assertTrue(main_page.are_deck_selection_controls_visible())
        self.assertFalse(main_page.are_card_adding_controls_visible())
        self.assertEqual(1, main_page.get_info_messages_count())
        self.assertEqual(0, main_page.get_error_messages_count())

        main_page.submit_deck_id()
        self.assertTrue(main_page.are_deck_selection_controls_removed())
        self.assertTrue(main_page.are_card_adding_controls_visible())
