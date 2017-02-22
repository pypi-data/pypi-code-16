import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.test.utils import override_settings

from blogging.actions import (make_draft, make_post_type_action,
                              make_published, make_selected, update_counters)
from blogging.models import Post


class ActionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user',
                                        password="123",
                                        is_superuser=True,
                                        is_active=True)

    def test_make_draft(self):
        post_1, created = Post.objects.get_or_create(
            title="post 1", slug="post-1", status=Post.PUBLISHED,
            published_on=datetime.datetime(2010, 1, 1),
            author=self.user
        )
        post_2, created = Post.objects.get_or_create(
            title="post 2", slug="post-2", status=Post.DRAFT,
            published_on=datetime.datetime(2010, 1, 1),
            author=self.user
        )

        data = {
            'action': 'make_draft',
            '_selected_action': Post.objects.all().values_list('pk', flat=True)
        }
        # print(type(self.client))
        # print(help(self.client.login))
        self.assertEqual(Post.objects.filter(status=Post.DRAFT).count(), 1)
        self.assertEqual(Post.objects.filter(status=Post.PUBLISHED).count(), 1)
        change_url = reverse('admin:blogging_post_changelist')
        self.client.login(username=self.user.username, password='123')
        res=self.client.post('/login/', {'username':'test_user','password':'123'}, follow=True)
        print res.content
        response = self.client.post(change_url, data, follow=True)
        print response.content
        self.assertContains(response, "marked")

        self.assertEqual(Post.objects.filter(status=Post.DRAFT).count(), 1)
        self.assertEqual(Post.objects.filter(status=Post.PUBLISHED).count(), 1)
        # make_draft()
