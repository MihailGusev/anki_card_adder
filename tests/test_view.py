from django.test import TestCase
from django.urls import reverse_lazy

from anki_word_adder.apps.accounts.models import Learner, Settings, Language, Word, Feedback, Request

existent_username = 'existent_username'
existent_password = 'existent_password'
existent_credentials = {'username': existent_username, 'password': existent_password}

new_username = 'new_username'
new_password = 'new_password'
new_credentials = {'username': new_username, 'password': new_password}


def default_setup():
    language = Language(code='ru', name='Russian')
    language.save()

    learner = Learner(username=existent_username)
    learner.set_password(existent_password)
    learner.save()

    Settings(learner=learner, language=language).save()


class TestRegister(TestCase):
    url = reverse_lazy('accounts:register')

    @classmethod
    def setUpTestData(cls):
        default_setup()

    def test_get_authenticated(self):
        """Authenticated user must be redirected to the main view"""
        self.client.login(username=existent_username, password=existent_password)

        response = self.client.get(self.url, follow=True)
        self.assertEqual(200, response.status_code)
        redirect_addr = response.redirect_chain[0][0]
        self.assertEqual(TestMain.url, redirect_addr)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_post_unauthenticated_existent_credentials(self):
        """If user already exists, show registration again"""
        response = self.client.post(self.url,
                                    {'username': existent_username,
                                     'password1': existent_password,
                                     'password2': existent_password},
                                    follow=True)
        self.assertEqual(200, response.status_code)
        form = response.context_data['form']
        self.assertFalse(form.is_valid())
        self.assertEqual('register.html', response.templates[0].name)

    def test_post_unauthenticated_new_credentials(self):
        """If user does not exist, create one and redirect to main"""
        response = self.client.post(self.url,
                                    {'username': new_username,
                                     'password1': new_password,
                                     'password2': new_password},
                                    follow=True)
        self.assertEqual(200, response.status_code)
        redirect_addr = response.redirect_chain[0][0]
        self.assertEqual(TestMain.url, redirect_addr)
        learner = Learner.objects.get(username=new_username)
        self.assertIsNotNone(learner)
        self.assertIsNotNone(Settings.objects.get(learner=learner))


class TestLogin(TestCase):
    url = reverse_lazy('accounts:login')

    @classmethod
    def setUpTestData(cls):
        default_setup()

    def test_get_authenticated(self):
        """Authenticated user must be redirected to the main view"""
        self.client.login(username=existent_username, password=existent_password)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(200, response.status_code)
        redirect_addr = response.redirect_chain[0][0]
        self.assertEqual(TestMain.url, redirect_addr)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_post_unauthenticated_invalid_credentials(self):
        """Unuthenticated user with invalid credentials must be shown login page again"""
        response = self.client.post(self.url, new_credentials, follow=True)
        self.assertEqual(200, response.status_code)
        form = response.context_data['form']
        self.assertFalse(form.is_valid())
        self.assertEqual('login.html', response.templates[0].name)

    def test_post_unauthenticated_valid_credentials(self):
        """Unuthenticated user with the correct credentials must be logged in and redirected to the main view"""
        response = self.client.post(self.url, existent_credentials, follow=True)
        self.assertEqual(200, response.status_code)
        redirect_addr = response.redirect_chain[0][0]
        self.assertEqual(TestMain.url, redirect_addr)


class TestLogout(TestCase):
    url = reverse_lazy('accounts:logout')

    @classmethod
    def setUpTestData(cls):
        default_setup()

    def test_post_redirect_to_login(self):
        """Logout must redirect to login"""
        self.client.login(username=existent_username, password=existent_password)
        response = self.client.post(self.url, follow=True)
        redirect_addr = response.redirect_chain[0][0]
        self.assertEqual(TestLogin.url, redirect_addr)


class TestMain(TestCase):
    url = reverse_lazy('main')

    @classmethod
    def setUpTestData(cls):
        default_setup()

    def test_get_authenticated(self):
        """There must be 'learner_settings' object for authenticated user"""
        self.client.login(username=existent_username, password=existent_password)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTrue('learner_settings' in response.context)

    def test_get_unauthenticated(self):
        """Redirect unauthenticated user to login page"""
        response = self.client.get(self.url, follow=True)
        self.assertEqual(200, response.status_code)
        redirect_addr = response.redirect_chain[0][0]
        expected = TestLogin.url
        self.assertEqual(expected, redirect_addr[:len(expected)])


class TestGuide(TestCase):
    url = reverse_lazy('guide')

    def test_get_authenticated(self):
        self.client.login(username=existent_username, password=existent_password)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


class TestWordData(TestCase):
    existent_word = 'word'
    existent_word_url = reverse_lazy('word_data', kwargs={'word': existent_word})
    non_existent_word_url = reverse_lazy('word_data', kwargs={'word': '1234'})

    @classmethod
    def setUpTestData(cls):
        default_setup()
        Word(name=cls.existent_word).save()

    def test_get_unauthenticated(self):
        """Must redirect unauthenticated user to login page"""
        response = self.client.get(self.existent_word_url, follow=True)
        self.assertEqual(200, response.status_code)
        redirect_addr = response.redirect_chain[0][0]
        expected = TestLogin.url
        # There's 'next' parameter we don't care about
        self.assertEqual(expected, redirect_addr[:len(expected)])

    def test_get_authenticated_existent_word(self):
        """Mustn't contain 'errors' field in response"""
        self.client.login(username=existent_username, password=existent_password)
        request_count = Request.objects.all().count()
        response = self.client.get(self.existent_word_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(request_count + 1, Request.objects.all().count())
        self.assertNotIn('errors'.encode('utf-8'), response.content)

    def test_get_authenticated_non_existent_word(self):
        """Must contain 'errors' field in response"""
        self.client.login(username=existent_username, password=existent_password)
        request_count = Request.objects.all().count()
        response = self.client.get(self.non_existent_word_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(request_count, Request.objects.all().count())
        self.assertIn('errors'.encode('utf-8'), response.content)


class TestFeedback(TestCase):
    url = reverse_lazy('feedback')

    @classmethod
    def setUpTestData(cls):
        default_setup()

    def test_post_authenticated(self):
        """Authenticated user must be able to leave feedback"""
        self.client.login(username=existent_username, password=existent_password)
        feedback_count = Feedback.objects.all().count()
        response = self.client.post(self.url, {'feedback': ''}, content_type='application/json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(feedback_count + 1, Feedback.objects.all().count())

    def test_post_unauthenticated(self):
        """Unauthencitated user must not be able to leave feedback"""
        feedback_count = Feedback.objects.all().count()
        response = self.client.post(self.url, {'feedback': ''}, content_type='application/json', follow=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual(feedback_count, Feedback.objects.all().count())
