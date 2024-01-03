from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import User
import pytest


class UserSignUpAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_signup_successful(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': '123'
        }

        response = self.client.post('/users/signup/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['description'],
                         "Congratulations! you are registered successfully. Confirm your email to activate your account")

        # Check if the user was created in the database
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_signup_existing_email(self):
        # Create a user with the email that we are going to use in the test
        User.objects.create(username='existinguser', email='testuser@example.com', password='existingpassword')

        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }

        response = self.client.post('/users/signup/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'],
                         "Email is already registered.Confirm your email to activate your account")

    def test_user_signup_existing_username(self):
        # Create a user with the username that we are going to use in the test
        User.objects.create(username='testuser', email='existinguser@example.com', password='existingpassword')

        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }

        response = self.client.post('/users/signup/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['username'][0],
                         "A user with that username already exists.Confirm your email to activate your account")


class UserLoginAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')

        self.test_user.is_email_verified = True
        self.test_user.save()

    def test_user_login_successful(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

        response = self.client.post('/api/token/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

        # You may want to validate other aspects of the response, such as user details or additional information.

    def test_user_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'incorrectpassword'
        }

        response = self.client.post('/api/token/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertIn('detail', response.data)
