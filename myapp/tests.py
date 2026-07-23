from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, ContactMessage, NewsletterSubscriber, Post


class StaticPageTests(TestCase):
    def test_static_pages_render(self):
        for name in [
            'home', 'blog', 'portfolio_details',
            'service_details', 'starter',
        ]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, msg=f'{name} did not return 200')


class BlogViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Travel')
        self.post = Post.objects.create(
            title='First Post', author='John Doe', category=self.category,
            excerpt='A short teaser.', content='Full post content.',
        )

    def test_blog_list_shows_posts(self):
        response = self.client.get(reverse('blog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First Post')

    def test_blog_list_filters_by_category(self):
        other_category = Category.objects.create(name='Design')
        Post.objects.create(
            title='Second Post', author='Jane Doe', category=other_category,
            content='Other content.',
        )
        response = self.client.get(reverse('blog'), {'category': self.category.pk})
        self.assertEqual(list(response.context['posts']), [self.post])

    def test_blog_details_renders_post(self):
        response = self.client.get(reverse('blog_details', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First Post')
        self.assertContains(response, 'Full post content.')

    def test_blog_details_404_for_missing_post(self):
        response = self.client.get(reverse('blog_details', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ContactViewTests(TestCase):
    def test_get_redirects_home(self):
        response = self.client.get(reverse('contact'))
        self.assertRedirects(response, reverse('home'))

    def test_post_creates_message_and_redirects(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'subject': 'Hello',
            'message': 'Just saying hi.',
        })
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, 'Jane Doe')
        self.assertEqual(message.email, 'jane@example.com')
        self.assertRedirects(response, '/#contact', fetch_redirect_response=False)

    def test_ajax_post_returns_ok(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'subject': 'Hello',
            'message': 'Just saying hi.',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
        self.assertEqual(ContactMessage.objects.count(), 1)


class NewsletterViewTests(TestCase):
    def test_get_redirects_home(self):
        response = self.client.get(reverse('newsletter'))
        self.assertRedirects(response, reverse('home'))

    def test_post_creates_subscriber(self):
        response = self.client.post(reverse('newsletter'), {'email': 'sub@example.com'})
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
        self.assertRedirects(response, '/#subscribe', fetch_redirect_response=False)

    def test_post_duplicate_email_does_not_create_second(self):
        NewsletterSubscriber.objects.create(email='sub@example.com')
        self.client.post(reverse('newsletter'), {'email': 'sub@example.com'})
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_post_without_email_redirects_without_creating(self):
        response = self.client.post(reverse('newsletter'), {})
        self.assertEqual(NewsletterSubscriber.objects.count(), 0)
        self.assertRedirects(response, '/#subscribe', fetch_redirect_response=False)

    def test_ajax_post_returns_ok(self):
        response = self.client.post(
            reverse('newsletter'), {'email': 'sub@example.com'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)


class ContactStaffViewsTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staff', password='pw12345', is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username='regular', password='pw12345', is_staff=False,
        )
        self.message = ContactMessage.objects.create(
            name='Jane Doe', email='jane@example.com',
            subject='Hello', message='Hi there.',
        )

    def test_contact_list_requires_staff(self):
        response = self.client.get(reverse('contact_list'))
        self.assertNotEqual(response.status_code, 200)

    def test_contact_list_denies_non_staff(self):
        self.client.login(username='regular', password='pw12345')
        response = self.client.get(reverse('contact_list'))
        self.assertNotEqual(response.status_code, 200)

    def test_contact_list_allows_staff(self):
        self.client.login(username='staff', password='pw12345')
        response = self.client.get(reverse('contact_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')

    def test_contact_edit_get_shows_form(self):
        self.client.login(username='staff', password='pw12345')
        response = self.client.get(reverse('contact_edit', args=[self.message.pk]))
        self.assertEqual(response.status_code, 200)

    def test_contact_edit_post_updates_message(self):
        self.client.login(username='staff', password='pw12345')
        response = self.client.post(reverse('contact_edit', args=[self.message.pk]), {
            'name': 'Jane Updated',
            'email': 'jane@example.com',
            'subject': 'Updated subject',
            'message': 'Updated message.',
        })
        self.assertRedirects(response, reverse('contact_list'))
        self.message.refresh_from_db()
        self.assertEqual(self.message.name, 'Jane Updated')
        self.assertEqual(self.message.subject, 'Updated subject')

    def test_contact_delete_requires_post(self):
        self.client.login(username='staff', password='pw12345')
        response = self.client.get(reverse('contact_delete', args=[self.message.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(ContactMessage.objects.filter(pk=self.message.pk).exists())

    def test_contact_delete_removes_message(self):
        self.client.login(username='staff', password='pw12345')
        response = self.client.post(reverse('contact_delete', args=[self.message.pk]))
        self.assertRedirects(response, reverse('contact_list'))
        self.assertFalse(ContactMessage.objects.filter(pk=self.message.pk).exists())

    def test_contact_delete_denies_non_staff(self):
        self.client.login(username='regular', password='pw12345')
        response = self.client.post(reverse('contact_delete', args=[self.message.pk]))
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(pk=self.message.pk).exists())

