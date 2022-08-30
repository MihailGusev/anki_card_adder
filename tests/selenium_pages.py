# https://www.selenium.dev/documentation/webdriver/getting_started/
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class BasePage:
    """Base class for all pages"""

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver


class RegisterPage(BasePage):
    def register(self, username='new_username', password='new_password'):
        """Fill register form and sumbit it"""
        self.driver.find_element(By.ID, 'id_username').send_keys(username)
        self.driver.find_element(By.ID, 'id_password1').send_keys(password)
        self.driver.find_element(By.ID, 'id_password2').send_keys(password)
        self.driver.find_element(By.ID, 'submit').click()


class LoginPage(BasePage):
    def login(self, username, password):
        """Fill login form and sumbit it"""
        self.driver.find_element(By.ID, 'id_username').send_keys(username)
        self.driver.find_element(By.ID, 'id_password').send_keys(password)
        self.driver.find_element(By.ID, 'submit').click()


class MainPage(BasePage):
    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self.wait = WebDriverWait(self.driver, timeout=5)
        self.message_container = driver.find_element(By.ID, 'message-container')
        self.deck_selection_controls = driver.find_element(By.ID, 'deck-selection-controls')
        self.card_adding_controls = driver.find_element(By.ID, 'card-adding-controls')
        self.submit_deck_button = driver.find_element(By.ID, 'submit-deck-id')

    def wait_messages(self, count):
        """Wait until message container has at least 'count' messages in it"""
        self.wait.until(lambda d: len(self.message_container.find_elements(By.CLASS_NAME, 'alert')) > count - 1)

    def get_info_messages_count(self):
        """Get count of information alerts"""
        return len(self.message_container.find_elements(By.CLASS_NAME, 'alert-info'))

    def get_error_messages_count(self):
        """Get count of error alerts"""
        return len(self.message_container.find_elements(By.CLASS_NAME, 'alert-danger'))

    def are_deck_selection_controls_visible(self):
        """Return true of deck selection controls are visible"""
        classes = self.deck_selection_controls.get_attribute('class').split()
        return 'hidden' not in classes

    def are_deck_selection_controls_removed(self):
        """Return true if deck selection controls are not in the DOM"""
        return len(self.driver.find_elements(By.ID, 'deck-selection-controls')) == 0

    def are_card_adding_controls_visible(self):
        """Return true of card adding controls are visible"""
        classes = self.card_adding_controls.get_attribute('class').split()
        return 'hidden' not in classes

    def submit_deck_id(self):
        self.submit_deck_button.click()
        self.wait.until(lambda d: self.are_card_adding_controls_visible())
