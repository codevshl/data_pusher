# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from .models import Account, Destination
# import logging

# class AccountTests(APITestCase):
#     def test_create_account(self):
#         url = reverse('account-list')
#         data = {'email_id': 'contact@examplecorp.com', 'account_name': 'ExampleCorp'}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Account.objects.count(), 1)
#         self.assertEqual(Account.objects.get().email_id, 'contact@examplecorp.com')
#         self.assertIsNotNone(Account.objects.get().app_secret_token)


# class DestinationTests(APITestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         logging.basicConfig(level=logging.DEBUG)

#     def test_create_destination(self):
#         logging.debug("Creating an account for testing.")
#         self.account = Account.objects.create(email_id="user@example.com", account_name="Test User")
        
#         logging.debug("Posting to the destination list URL.")
#         url = reverse('destination-list')
#         data = {
#             'account': self.account.account_id,
#             'url': 'https://api.example.com/webhook',
#             'http_method': 'POST',
#             'headers': {'Content-Type': 'application/json'}
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(self.account.destinations.count(), 1)
#         self.assertEqual(self.account.destinations.first().url, 'https://api.example.com/webhook')
#         logging.debug("Test for creating destination passed.")


# class IncomingDataTests(APITestCase):
#     def setUp(self):
#         self.account = Account.objects.create(email_id="user@example.com", account_name="Test User")
#         self.destination = Destination.objects.create(
#             account=self.account,
#             url='https://api.example.com/webhook',
#             http_method='POST',
#             headers={'Content-Type': 'application/json'}
#         )

#     def test_incoming_data(self):
#         url = reverse('incoming_data')
#         data = {'data': 'test'}
#         headers = {'HTTP_CL-X-TOKEN': str(self.account.app_secret_token)}
#         response = self.client.post(url, data, format='json', **headers)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)



import uuid
from django.test import TestCase, Client
from django.urls import reverse
from .models import Account, Destination
import json


class IncomingDataTest(TestCase):
    def setUp(self):
        # Create a sample account with a valid UUID as the app_secret_token
        self.account = Account.objects.create(app_secret_token=uuid.uuid4())
        self.destination = Destination.objects.create(
            account=self.account, 
            url='http://example.com', 
            http_method='POST', 
            headers='{"Content-Type": "application/json"}'
        )
        # Client for making requests
        self.client = Client()

    def test_incoming_data(self):
        url = reverse('incoming_data')  # Ensure this matches the URL name in your urls.py
        data = {'key': 'value'}
        headers = {'HTTP_CL_X_TOKEN': self.account.app_secret_token}
        
        response = self.client.post(url, json.dumps(data), content_type='application/json', **headers)
        
        # Check response status and content
        self.assertEqual(response.status_code, 200)
        responses = json.loads(response.content.decode('utf-8'))  # Ensures correct decoding of the response content
        self.assertIn('responses', responses)  # Ensure there is a 'responses' key in the JSON response
