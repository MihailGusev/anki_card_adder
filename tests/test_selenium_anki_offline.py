from django.urls import reverse_lazy

from .selenium_pages import RegisterPage, MainPage
from .test_selenium_base import TestsBase, TestsLoginRequired


class TestsRegister(TestsBase):
    url = reverse_lazy('accounts:register')

    def setUp(self) -> None:
        """Create driver and open registragion page"""
        super().setUp()
        self.driver.get('%s%s' % (self.live_server_url, self.url))

    def test_register_with_new_credentials(self):
        """Registering when anki is not running and with valid credentials must:
        1) open main page
        2) show one info message (about language)
        3) show one error message (about being unable to connect to Anki)"""
        RegisterPage(self.driver).register()
        main_page = MainPage(self.driver)
        main_page.wait_messages(2)
        self.assertFalse(main_page.are_deck_selection_controls_visible())
        self.assertFalse(main_page.are_card_adding_controls_visible())
        self.assertEqual(1, main_page.get_info_messages_count())
        self.assertEqual(1, main_page.get_error_messages_count())


class TestsMain(TestsLoginRequired):
    def test_get(self):
        """Existing user must see error message on the main page if anki is offline"""
        main_page = MainPage(self.driver)
        main_page.wait_messages(1)
        self.assertFalse(main_page.are_deck_selection_controls_visible())
        self.assertFalse(main_page.are_card_adding_controls_visible())
        self.assertEqual(0, main_page.get_info_messages_count())
        self.assertEqual(1, main_page.get_error_messages_count())
