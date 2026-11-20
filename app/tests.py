"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .roles import is_client, is_manager
from .models import Blog, Category, EducationalMaterial, MaterialComment

# TODO: Configure your database in settings.py and sync before running tests.

class ViewTest(TestCase):
    """Tests for the application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(ViewTest, cls).setUpClass()
            django.setup()

    def test_home(self):
        """Tests the home page."""
        response = self.client.get('/')
        self.assertContains(response, 'Home Page', 1, 200)

    def test_contact(self):
        """Tests the contact page."""
        response = self.client.get('/contact')
        self.assertContains(response, 'Contact', 3, 200)

    def test_about(self):
        """Tests the about page."""
        response = self.client.get('/about')
        self.assertContains(response, 'About', 3, 200)


class RolesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        client_g, _ = Group.objects.get_or_create(name='Клиент')
        manager_g, _ = Group.objects.get_or_create(name='Менеджер')

        cls.client_user = User.objects.create_user('client1', password='pass12345')
        cls.client_user.groups.add(client_g)

        cls.manager_user = User.objects.create_user('manager1', password='pass12345')
        cls.manager_user.groups.add(manager_g)

        cls.admin_user = User.objects.create_superuser('admin1', password='pass12345')

    # Ожидаемый код ответа: гость, клиент, менеджер, администратор
    MATRIX = [
        ('home',                    200, 200, 200, 200),
        ('blog',                    200, 200, 200, 200),
        ('catalog',                 200, 200, 200, 200),
        ('cart',                    302, 200, 403, 403),
        ('my_orders',               302, 200, 403, 403),
        ('manager_orders',          302, 403, 200, 403),
        ('admin_catalog_dashboard', 302, 403, 403, 200),
        ('newpost',                 302, 403, 403, 200),
    ]

    def test_access_matrix(self):
        users = [None, self.client_user, self.manager_user, self.admin_user]
        names = ['гость', 'клиент', 'менеджер', 'администратор']
        for page, *expected in self.MATRIX:
            for user, role, code in zip(users, names, expected):
                with self.subTest(page=page, role=role):
                    self.client.logout()
                    if user:
                        self.client.force_login(user)
                    self.assertEqual(self.client.get(reverse(page)).status_code, code)

    def test_registration_assigns_client_group(self):
        self.client.post(reverse('registration'), {
            'username': 'newbie',
            'password1': 'Str0ng!pass_91',
            'password2': 'Str0ng!pass_91',
        })
        user = User.objects.get(username='newbie')
        self.assertTrue(user.groups.filter(name='Клиент').exists())

    def test_manager_wins_over_client(self):
        both = User.objects.create_user('both', password='pass12345')
        both.groups.add(*Group.objects.filter(name__in=['Клиент', 'Менеджер']))
        self.assertTrue(is_manager(both))
        self.assertFalse(is_client(both))

    def test_material_comments_by_role(self):
        category = Category.objects.create(name='Тест', slug='test')
        material = EducationalMaterial.objects.create(
            title='Материал', short_description='кратко', full_description='полно',
            category=category, is_free=True)
        url = reverse('material_detail', args=[material.pk])

        self.client.logout()
        self.assertEqual(self.client.post(url, {'text': 'привет'}).status_code, 302)

        self.client.force_login(self.manager_user)
        self.assertEqual(self.client.post(url, {'text': 'привет'}).status_code, 403)
        self.assertEqual(MaterialComment.objects.count(), 0)

        self.client.force_login(self.client_user)
        self.assertEqual(self.client.post(url, {'text': 'Отлично!'}).status_code, 302)
        self.assertEqual(MaterialComment.objects.get().author, self.client_user)
        self.assertContains(self.client.get(url), 'Отлично!')


    def test_admin_edit_and_delete(self):
        category = Category.objects.create(name='К1', slug='k1')
        material = EducationalMaterial.objects.create(
            title='М1', short_description='к', full_description='п',
            category=category, is_free=True)
        post = Blog.objects.create(title='Н1', description='d', content='c')

        urls = [
            reverse('admin_edit_category', args=[category.pk]),
            reverse('admin_delete_category', args=[category.pk]),
            reverse('admin_edit_material', args=[material.pk]),
            reverse('admin_delete_material', args=[material.pk]),
            reverse('edit_post', args=[post.pk]),
            reverse('delete_post', args=[post.pk]),
        ]

        # клиент и менеджер: 403, ничего не удалено
        for user in (self.client_user, self.manager_user):
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user.username, url=url):
                    self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Category.objects.exists())
        self.assertTrue(Blog.objects.exists())

        # администратор: изменение
        self.client.force_login(self.admin_user)
        self.client.post(reverse('admin_edit_category', args=[category.pk]),
                        {'name': 'К1 новое', 'slug': 'k1', 'description': ''})
        category.refresh_from_db()
        self.assertEqual(category.name, 'К1 новое')

        # GET на удаление только показывает подтверждение
        self.assertEqual(self.client.get(urls[5]).status_code, 200)
        self.assertTrue(Blog.objects.filter(pk=post.pk).exists())

        # POST удаляет; удаление категории каскадно удаляет материалы
        self.client.post(urls[5])
        self.assertFalse(Blog.objects.filter(pk=post.pk).exists())
        self.client.post(urls[1])
        self.assertFalse(Category.objects.exists())
        self.assertFalse(EducationalMaterial.objects.exists())