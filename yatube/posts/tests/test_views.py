import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Post, Group, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        Group.objects.create(
            title='Тестовая группа №2',
            slug='test_slug2',
            description='Тестовое описание'
        )
        cls.NUMBER_OF_POSTS = 13
        cls.PAGE_LIMIT = 10
        for i in range(cls.NUMBER_OF_POSTS):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый пост',
                image=cls.uploaded
            )
        cls.kwargs_username = {'username': cls.user.username}
        cls.kwargs_first_post = {'post_id': 1}
        cls.kwargs_slug = {'slug': 'test_slug'}
        cls.templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs=cls.kwargs_slug): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs=cls.kwargs_username): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs=cls.kwargs_first_post): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs=cls.kwargs_first_post): 'posts/create_post.html',
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.response_index = cls.authorized_client.get(
            reverse('posts:index'))
        cls.response_group = cls.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs=cls.kwargs_slug))
        cls.response_profile = cls.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs=cls.kwargs_username))
        cls.response_post = cls.authorized_client.get(
            reverse('posts:post_detail', kwargs=cls.kwargs_first_post))
        cls.response_create = cls.authorized_client.get(
            reverse('posts:post_create'))
        cls.response_edit = cls.authorized_client.get(
            reverse('posts:post_edit', kwargs=cls.kwargs_first_post))
        cls.expected_post = {'username': 'auth',
                             'text': 'Тестовый пост',
                             'group': 'Тестовая группа',
                             'image': cls.uploaded}
        cls.response_index_first = cls.authorized_client.get(
            reverse('posts:index'))
        cls.response_index_second = cls.authorized_client.get(
            reverse('posts:index') + '?page=2')
        cls.response_profile_first = cls.authorized_client.get(
            reverse('posts:profile',
                    kwargs=cls.kwargs_username))
        cls.response_profile_second = cls.authorized_client.get(
            reverse('posts:profile',
                    kwargs=cls.kwargs_username) + '?page=2')
        cls.response_group_first = cls.authorized_client.get(
            reverse('posts:group_list', kwargs=cls.kwargs_slug))
        cls.response_group_second = cls.authorized_client.get(
            reverse('posts:group_list', kwargs=cls.kwargs_slug) + '?page=2')
        cls.response_empty_group = cls.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug2'}))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def get_post_obj_dict(self, post_obj):
        res_dict = dict()
        res_dict['post_text'] = post_obj.text
        res_dict['post_author_username'] = post_obj.author.username
        res_dict['post_group'] = post_obj.group
        res_dict['post_image'] = post_obj.image
        return res_dict

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in ViewsPostTest.templates_names.items():
            with self.subTest(template=template):
                response = ViewsPostTest.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        post = ViewsPostTest.get_post_obj_dict(
            self, ViewsPostTest.response_index.context['page_obj'][0])
        self.assertEqual(post['post_author_username'], 'auth')
        self.assertEqual(post['post_text'], 'Тестовый пост')
        self.assertEqual(str(post['post_group']), 'Тестовая группа')
        self.assertEqual(post['post_image'].read(), ViewsPostTest.small_gif)
        post['post_image'].close()

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = ViewsPostTest.response_group.context['group']
        post = ViewsPostTest.get_post_obj_dict(
            self, ViewsPostTest.response_group.context['page_obj'][0])
        self.assertEqual(post['post_author_username'], 'auth')
        self.assertEqual(post['post_text'], 'Тестовый пост')
        self.assertEqual(str(post['post_group']), 'Тестовая группа')
        self.assertEqual(group, ViewsPostTest.group)
        self.assertEqual(post['post_image'].read(), ViewsPostTest.small_gif)
        post['post_image'].close()

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        author = ViewsPostTest.response_profile.context['author']
        post = ViewsPostTest.get_post_obj_dict(
            self, ViewsPostTest.response_profile.context['page_obj'][0])
        self.assertEqual(post['post_author_username'], 'auth')
        self.assertEqual(post['post_text'], 'Тестовый пост')
        self.assertEqual(str(post['post_group']), 'Тестовая группа')
        self.assertEqual(author, ViewsPostTest.user)
        self.assertEqual(post['post_image'].read(), ViewsPostTest.small_gif)
        post['post_image'].close()

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        count = ViewsPostTest.response_post.context['count']
        post = ViewsPostTest.get_post_obj_dict(
            self, ViewsPostTest.response_post.context['post'])
        self.assertEqual(post['post_author_username'], 'auth')
        self.assertEqual(post['post_text'], 'Тестовый пост')
        self.assertEqual(str(post['post_group']), 'Тестовая группа')
        self.assertEqual(post['post_image'].read(), ViewsPostTest.small_gif)
        self.assertEqual(count, 13)
        post['post_image'].close()

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        for val, expected in ViewsPostTest.form_fields.items():
            with self.subTest(value=val):
                form_field = (
                    ViewsPostTest.response_create.context['form'].fields[val])
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        for val, expected in ViewsPostTest.form_fields.items():
            with self.subTest(value=val):
                form_field = (
                    ViewsPostTest.response_edit.context['form'].fields[val])
                self.assertIsInstance(form_field, expected)

    def test_first_page_index_contains_ten_records(self):
        self.assertEqual(
            self.response_index_first.context['page_obj'].end_index(),
            ViewsPostTest.PAGE_LIMIT)

    def test_second_page_index_contains_three_records(self):
        self.assertEqual(
            self.response_index_second.context['page_obj'].end_index(),
            ViewsPostTest.NUMBER_OF_POSTS)

    def test_first_page_profile_contains_ten_records(self):
        self.assertEqual(
            self.response_profile_first.context['page_obj'].end_index(),
            ViewsPostTest.PAGE_LIMIT)

    def test_second_page_profile_contains_three_records(self):
        self.assertEqual(
            self.response_profile_second.context['page_obj'].end_index(),
            ViewsPostTest.NUMBER_OF_POSTS)

    def test_first_page_group_contains_ten_records(self):
        self.assertEqual(
            self.response_group_first.context['page_obj'].end_index(),
            ViewsPostTest.PAGE_LIMIT)

    def test_second_page_group_contains_three_records(self):
        self.assertEqual(
            self.response_group_second.context['page_obj'].end_index(),
            ViewsPostTest.NUMBER_OF_POSTS)

    def test_second_test_group_have_not_posts(self):
        self.assertEqual(
            self.response_empty_group.context['page_obj'].end_index(), 0)


class ViewsCommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.first_post = reverse('posts:post_detail', kwargs={'post_id': 1})
        cls.first_post_comments = reverse('posts:add_comment',
                                          kwargs={'post_id': 1})
        cls.response_comment_guest = cls.guest_client.get(
            cls.first_post_comments)
        cls.response_comment_authrorized = cls.authorized_client.get(
            cls.first_post_comments)
        cls.response_add_comment_authrorized = cls.authorized_client.post(
            cls.first_post_comments,
            data={'text': 'Тестовый комментарий'},
            follow=True)
        cls.response_add_comment_guest = cls.guest_client.post(
            cls.first_post_comments,
            data={'text': 'Тестовый комментарий от гостя'},
            follow=True)
        cls.redir_authorization = '/auth/login/?next=/posts/1/comment/'

    def test_add_comment_guest(self):
        """Неваторизированный пользователь не может оставлять комментарии."""
        self.assertRedirects(self.response_comment_guest,
                             self.redir_authorization)
        self.assertFalse(
            Comment.objects.filter(
                text='Тестовый комментарий от гостя'
            ).exists())

    def test_add_comment_authorized(self):
        """Авторизированный пользователь может оставлять комментарии."""
        self.assertRedirects(self.response_comment_authrorized,
                             self.first_post)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text='Тестовый комментарий'
            ).exists())


class ViewsCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.index_url = reverse('posts:index')

    def test_cache_index(self):
        """Список записей index кешируется"""
        first_response = ViewsCacheTest.authorized_client.get(
            self.index_url)
        Post.objects.create(
            text='Тестовый пост 2',
            author=ViewsCacheTest.user, )
        second_response = ViewsCacheTest.authorized_client.get(
            self.index_url)
        cache.clear()
        third_response = ViewsCacheTest.authorized_client.get(
            self.index_url)
        self.assertEqual(first_response.content, second_response.content)
        self.assertNotEqual(second_response.content, third_response.content)


class ViewsFollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.follower = User.objects.create_user(username='follower')
        cls.non_follower = User.objects.create_user(username='non_follower')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)
        cls.non_follower_client = Client()
        cls.non_follower_client.force_login(cls.non_follower)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'author'}))
        cls.response_follower_list = cls.follower_client.get(
            reverse('posts:follow_index'))
        cls.response_follower_index = cls.follower_client.get(
            reverse('posts:index'))
        cls.response_non_follower_list = cls.non_follower_client.get(
            reverse('posts:follow_index'))
        cls.response_non_follower_index = cls.non_follower_client.get(
            reverse('posts:index'))

    def test_follow_list(self):
        self.assertEqual(
            self.response_follower_list.context['page_obj'].end_index(),
            self.response_follower_index.context['page_obj'].end_index())
        self.assertNotEqual(
            self.response_non_follower_list.context['page_obj'].end_index(),
            self.response_non_follower_index.context['page_obj'].end_index())

    def test_follow_unfollow(self):
        self.follower_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': 'author'}))
        unfollow = not Post.objects.filter(
            author__following__user=self.follower).exists()
        self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'author'}))
        follow = Post.objects.filter(
            author__following__user=self.follower).exists()
        self.assertTrue(follow)
        self.assertTrue(unfollow)

    def test_second_follow(self):
        count_before = self.follower.follower.count()
        response_second_follow = self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'author'}))
        count_after = self.follower.follower.count()
        self.assertEqual(count_after, count_before)
        self.assertRedirects(response_second_follow,
                             reverse('posts:profile',
                                     kwargs={'username': 'author'}))
