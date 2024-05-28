from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from data_pusher_app.models import Account, Destination
from data_pusher_app.views import AccountViewSet, DestinationViewSet, incoming_data, AccountVerifier, JSONProcessor, DestinationHandler, BaseViewSet, DestinationRetriever, get_destinations_view
import json
import uuid

class BaseViewSetTest(TestCase):
    @patch('logging.error')
    def test_handle_exception(self, mock_logging):
        viewset = BaseViewSet()
        response = viewset.handle_exception(Exception("Test Error"))
        mock_logging.assert_called_once_with("Error occurred: Test Error")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"error": "Test Error"}')

class AccountViewSetTest(TestCase):
    def setUp(self):
        self.account = Account.objects.create(email_id='test@example.com', account_name='Test Account')

    def test_queryset_returns_accounts(self):
        viewset = AccountViewSet()
        queryset = viewset.get_queryset()
        self.assertIn(self.account, list(queryset))

class DestinationViewSetTest(TestCase):
    def setUp(self):
        # Create an Account instance with a valid UUID for app_secret_token
        self.account = Account.objects.create(
            email_id='test@example.com', 
            account_name='ValidName', 
            app_secret_token=uuid.uuid4()  # Generate a valid UUID
        )
        
        # Now create a Destination instance using the Account
        self.destination = Destination.objects.create(
            account=self.account,
            url='http://example.com',
            http_method='GET',
            headers='{"Content-Type": "application/json"}'
        )

    def test_queryset_returns_destinations(self):
        viewset = DestinationViewSet()
        queryset = viewset.get_queryset()
        self.assertIn(self.destination, list(queryset))

class AccountVerifierTest(TestCase):
    def test_verify_token_with_no_token(self):
        """ Test verifying with no token provided should return a 401 unauthenticated response """
        verifier = AccountVerifier(token=None)
        response = verifier.verify_token()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, b'{"error": "Unauthenticated"}')

    @patch('data_pusher_app.models.Account.objects.get')
    def test_verify_token_with_valid_token(self, mock_get):
        """ Test verifying with a valid token should return the Account object """
        valid_token = uuid.uuid4() 
        mock_account = Account(app_secret_token=valid_token)
        mock_get.return_value = mock_account
        verifier = AccountVerifier(token=valid_token)
        account = verifier.verify_token()
        self.assertIsInstance(account, Account)
        self.assertEqual(account.app_secret_token, valid_token)
        mock_get.assert_called_with(app_secret_token = valid_token)


    @patch('data_pusher_app.models.Account.objects.get')
    def test_verify_token_with_invalid_token(self, mock_get):
        """ Test verifying with an invalid token should return a 404 not found response """
        mock_get.side_effect = Account.DoesNotExist
        verifier = AccountVerifier(token='invalid_token')
        response = verifier.verify_token()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'{"error": "Account not found"}')

class JSONProcessorTest(TestCase):
    def test_parse_json_valid(self):
        # Test with valid JSON data
        valid_json_bytes = json.dumps({'key': 'value'}).encode('utf-8')
        processor = JSONProcessor(request_body=valid_json_bytes)
        expected_data = {'key': 'value'}
        result = processor.parse_json()
        self.assertEqual(result, expected_data)

    def test_parse_json_invalid(self):
        # Test with invalid JSON data
        invalid_json_bytes = b'{"key": "value" incomplete'
        processor = JSONProcessor(request_body=invalid_json_bytes)
        expected_response = JsonResponse({'error': 'Invalid JSON format'}, status=400)
        result = processor.parse_json()
        
        # Comparing the JsonResponse objects
        self.assertIsInstance(result, JsonResponse)
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.content, expected_response.content)




class DestinationHandlerTest(TestCase):
    def setUp(self):
        # Setup an account instance
        self.account = Account(email_id='test@example.example', account_name='ValidName')
        
        # Simulate data to be sent to destinations
        self.data = {'key': 'value'}

        # Mock destination that would be retrieved from the database
        self.destination = Destination(
            account=self.account,
            url="http://example.com/api",
            http_method="GET",
            headers=json.dumps({'Authorization': 'Bearer token', 'Content-Type': 'application/json'})
        )

    @patch('data_pusher_app.models.Destination.objects.filter')
    @patch('requests.get')
    def test_process_destinations(self, mock_get, mock_filter):
        # Set up the mock objects
        mock_filter.return_value = [self.destination]
        mock_response = MagicMock()
        mock_response.text = 'Success'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Initialize the handler with the account and data
        handler = DestinationHandler(account=self.account, data=self.data)

        # Execute the method under test
        responses = handler.process_destinations()

        # Assertions
        mock_filter.assert_called_once_with(account=self.account)  # Ensure destinations are filtered by account
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0]['url'], 'http://example.com/api')
        self.assertEqual(responses[0]['response'], 'Success')
        self.assertEqual(responses[0]['status_code'], 200)


    @patch('requests.get')
    def test_send_request_get_method(self, mock_get):
        handler = DestinationHandler(account=self.account, data=self.data)
        mock_response = MagicMock()
        mock_response.text = 'Success'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = handler.send_request(self.destination, json.loads(self.destination.headers))

        mock_get.assert_called_with(self.destination.url, headers={'Authorization': 'Bearer token', 'Content-Type': 'application/json'}, params=self.data)
        self.assertEqual(response.text, 'Success')
        self.assertEqual(response.status_code, 200)


    @patch('requests.request')
    def test_send_request_post_method(self, mock_request):
        self.destination.http_method = "POST"
        handler = DestinationHandler(account=self.account, data=self.data)
        mock_response = MagicMock()
        mock_response.text = 'Posted'
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        response = handler.send_request(self.destination, json.loads(self.destination.headers))

        mock_request.assert_called_with(method='post', url=self.destination.url, headers={'Authorization': 'Bearer token', 'Content-Type': 'application/json'}, json=self.data)
        self.assertEqual(response.text, 'Posted')
        self.assertEqual(response.status_code, 201)


    @patch('requests.request')
    @patch('data_pusher_app.models.Destination.objects.filter')
    def test_process_destinations_exception_handling(self, mock_filter, mock_request):
        self.destination.http_method = "POST"
        mock_filter.return_value = [self.destination]
        mock_request.side_effect = Exception("Network failure")

        handler = DestinationHandler(account=self.account, data=self.data)
        responses = handler.process_destinations()

        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0]['url'], 'http://example.com/api')
        self.assertIn('error', responses[0])
        self.assertEqual(responses[0]['error'], 'Network failure')




class DestinationRetrieverTest(TestCase):
    def setUp(self):
        self.account_id = 1
        self.retriever = DestinationRetriever(account_id=self.account_id)

    @patch('data_pusher_app.models.Account.objects.get')
    def test_get_account_success(self, mock_get):
        mock_get.return_value = MagicMock(spec=Account)
        account = self.retriever.get_account()
        mock_get.assert_called_once_with(pk=self.account_id)
        self.assertIsInstance(account, Account)

    @patch('data_pusher_app.models.Account.objects.get')
    def test_get_account_not_found(self, mock_get):
        mock_get.side_effect = Account.DoesNotExist
        with self.assertRaises(ValueError) as context:
            self.retriever.get_account()
        self.assertTrue("Account not found" in str(context.exception))

    @patch('data_pusher_app.models.Destination.objects.filter')
    def test_get_destinations(self, mock_filter):
        account = MagicMock(spec=Account)
        mock_filter.return_value = [MagicMock(spec=Destination), MagicMock(spec=Destination)]
        destinations = self.retriever.get_destinations(account)
        mock_filter.assert_called_once_with(account=account)
        self.assertEqual(len(destinations), 2)

    @patch('data_pusher_app.models.Destination.objects.filter')
    def test_get_destinations_empty(self, mock_filter):
        account = MagicMock(spec=Account)
        mock_filter.return_value = []
        destinations = self.retriever.get_destinations(account)
        self.assertEqual(destinations, [])

    @patch('data_pusher_app.views.DestinationSerializer')
    def test_serialize_destinations(self, mock_serializer_class):
        destinations = [MagicMock(spec=Destination), MagicMock(spec=Destination)]
        mock_serializer_instance = mock_serializer_class.return_value
        mock_serializer_instance.data = {'serialized': 'data'}

        data = self.retriever.serialize_destinations(destinations)

        mock_serializer_class.assert_called_once_with(destinations, many=True)
        self.assertEqual(data, {'serialized': 'data'})





class GetDestinationsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('data_pusher_app.views.DestinationRetriever')
    def test_get_destinations_view_success(self, mock_retriever):
        request = self.factory.get('/path/to/view')
        mock_instance = mock_retriever.return_value
        mock_instance.get_account.return_value = MagicMock()
        mock_instance.get_destinations.return_value = MagicMock()
        mock_instance.serialize_destinations.return_value = [{'id': 1, 'url': 'http://example.com'}]

        response = get_destinations_view(request, account_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[{"id": 1, "url": "http://example.com"}]')

    @patch('data_pusher_app.views.DestinationRetriever')
    def test_get_destinations_view_account_not_found(self, mock_retriever):
        request = self.factory.get('/path/to/view')
        mock_instance = mock_retriever.return_value
        mock_instance.get_account.side_effect = ValueError("Account not found")

        response = get_destinations_view(request, account_id=1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'{"error": "Account not found"}')
