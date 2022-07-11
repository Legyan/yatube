from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PostCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает пост."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Test_first_name',
            'last_name': 'Test_second_name',
            'username': 'test_name',
            'email': 'test@email.com',
            'password1': 'ZAQxsw123',
            'password2': 'ZAQxsw123'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/')
        self.assertEqual(User.objects.count(), users_count + 1)
