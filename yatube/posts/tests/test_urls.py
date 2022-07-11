from http import HTTPStatus
from django.test import TestCase, Client

from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/test_user/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        cls.guest_client = Client()
        cls.user_2 = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_2)
        cls.author_post_user = cls.user
        cls.authorize_post_author_client = Client()
        cls.authorize_post_author_client.force_login(cls.author_post_user)
        cls.response_homepage = cls.guest_client.get('/')
        cls.response_group_list = cls.guest_client.get('/group/test_slug/')
        cls.response_profile = cls.authorized_client.get('/profile/test_user/')
        cls.response_post = cls.guest_client.get('/posts/1/')
        cls.response_post_create = cls.authorized_client.get('/create/')
        cls.response_author_edit = (
            cls.authorize_post_author_client.get('/posts/1/edit/'))
        cls.response_guest_create = cls.guest_client.get(
            '/create/', follow=True)
        cls.response_guest_edit = (
            cls.guest_client.get('/posts/1/edit/', follow=True))
        cls.response_not_author_edit = (
            cls.authorized_client.get('/posts/1/edit/', follow=True))
        cls.response_incorrect_url = (
            cls.authorized_client.get('/unexisting_page/'))
        cls.urls = {'create': '/auth/login/?next=/create/',
                    'edit': '/auth/login/?next=/posts/1/edit/',
                    'first_post': '/posts/1/'}

    def test_homepage(self):
        """Страница / доступна любому пользователю."""
        self.assertEqual(
            PostsURLTests.response_homepage.status_code, HTTPStatus.OK)

    def test_group(self):
        """Страница /group/test_slug/ доступна любому пользователю."""
        self.assertEqual(
            PostsURLTests.response_group_list.status_code, HTTPStatus.OK)

    def test_profile(self):
        """Страница /profile/test_user/ доступна любому пользователю."""
        self.assertEqual(
            PostsURLTests.response_profile.status_code, HTTPStatus.OK)

    def test_post_detail(self):
        """Страница /posts/1/ доступна любому пользователю."""
        self.assertEqual(
            PostsURLTests.response_post.status_code, HTTPStatus.OK)

    def test_create_post(self):
        """Страница /create/ доступна авторизованному пользователю."""
        self.assertEqual(
            PostsURLTests.response_post_create.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Страница /posts/1/edit/ доступна автору поста."""
        self.assertEqual(
            PostsURLTests.response_author_edit.status_code, HTTPStatus.OK)

    def test_create_url_redirect_guest_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        self.assertRedirects(
            PostsURLTests.response_guest_create,
            PostsURLTests.urls['create'])

    def test_edit_url_redirect_guest_on_login(self):
        """Страница /posts/1/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        self.assertRedirects(
            PostsURLTests.response_guest_edit,
            PostsURLTests.urls['edit'])

    def test_edit_url_redirect_not_author_on_login(self):
        """Страница /posts/1/edit/ перенаправит не автора поста
        на страницу поста.
        """
        self.assertRedirects(
            PostsURLTests.response_not_author_edit,
            PostsURLTests.urls['first_post'])

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in PostsURLTests.templates_url_names.items():
            with self.subTest(url=url):
                response = PostsURLTests.authorize_post_author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_incorrect_url(self):
        """Непредвиденная страница вызывает ошибку 404."""
        self.assertEqual(
            PostsURLTests.response_incorrect_url.status_code,
            HTTPStatus.NOT_FOUND)
