from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_logout_page(self):
        """Страница /auth/logout/ доступна авторизированному пользователю."""
        response = self.authorized_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_page(self):
        """Страница /auth/signup/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_page(self):
        """Страница /auth/login/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_page(self):
        """Страница /auth/password_change/ доступна
        авторизированному пользователю."""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_page(self):
        """Страница /auth/password_change/done/ доступна
        авторизованному пользователю."""
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_page(self):
        """Страница /auth/password_reset/ доступна
        авторизированному пользователю."""
        response = self.authorized_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_page(self):
        """Страница /auth/password_reset/done/ доступна
        любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_done_page(self):
        """Страница /auth/password_reset/done/ доступна
        любому пользователю."""
        response = self.guest_client.get('/auth/reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
