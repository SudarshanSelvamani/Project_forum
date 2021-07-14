from django.contrib.auth.models import User
from django.urls import resolve, reverse
from ..forms import SignUpForm
from django.test import TestCase
from ..views import signup

# Create your tests here.

class SignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_page_is_served_right(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)
    
    def test_presence_of_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_response_contains_SignUpForm_object(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_SignUpForm_inputs(self):
        '''
        The view must contain five inputs: csrf, username, email, password1, password2
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)
    
    def test_SignUpForm_has_fields(self):
        form = SignUpForm()
        expected = ['username', 'email', 'password1', 'password2',]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)



class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'john',
            'email':'example@example.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')

    def test_redirect_to_home_page(self):
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.home_url)

    def test_user_is_created(self):
        self.assertTrue(User.objects.exists())

    def test_user_is_authenticated(self):
        '''
        Create a new request to an arbitrary page.
        The resulting response should now have a `user` to its context,
        after a successful sign up.
        '''
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_invalid_form_input_redirects_to_same_page(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_invalid_input_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_invalid_input_does_not_create_user(self):
        self.assertFalse(User.objects.exists())
