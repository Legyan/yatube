import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Comment, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded
        )
        cls.first_post_id = {'post_id': 1}
        cls.form = PostForm()
        cls.form_data = {
            'text': 'Тестовый текст',
            'group': cls.group.pk,
            'image': cls.small_gif,
        }
        cls.form_data_edit = {
            'text': 'Тестовый текст отредактированный',
            'group': cls.group.pk,
            'image': cls.small_gif,
        }
        cls.form_data_comment = {'text': 'Тестовый комментарий', }
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostFormTests.user)
        cls.redir_url_create = reverse(
            'posts:profile', kwargs={'username': cls.user.username})
        cls.redir_url_edit = reverse(
            'posts:post_detail', kwargs=cls.first_post_id)
        cls.comment = 'posts:post_detail'
        cls.edit_text = 'Тестовый текст отредактированный'
        cls.viewname = {'create': 'posts:post_create',
                        'edit': 'posts:post_edit',
                        'comment': 'posts:add_comment'}

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает пост."""
        posts_count = Post.objects.count()
        response = PostFormTests.authorized_client.post(
            reverse(PostFormTests.viewname['create']),
            data=PostFormTests.form_data,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.redir_url_create)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма редактирует пост."""
        response = PostFormTests.authorized_client.post(
            reverse(PostFormTests.viewname['edit'],
                    kwargs=PostFormTests.first_post_id),
            data=PostFormTests.form_data_edit,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.redir_url_edit)
        self.assertEqual(
            Post.objects.get(pk=1).text, PostFormTests.edit_text)

    def test_create_comment(self):
        """Валидная форма создает комментарий."""
        comment = Comment.objects.filter(post_id=1)
        comments_count = comment.count()
        response = PostFormTests.authorized_client.post(
            reverse(PostFormTests.viewname['comment'],
                    kwargs=PostFormTests.first_post_id),
            data=PostFormTests.form_data_comment,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.redir_url_edit)
        self.assertEqual(
            comment.count(), comments_count + 1)
