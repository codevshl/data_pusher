from rest_framework import viewsets
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
import requests
import json
import logging


# class AccountViewSet(viewsets.ModelViewSet):
#     queryset = Account.objects.all()
#     serializer_class = AccountSerializer

# class DestinationViewSet(viewsets.ModelViewSet):
#     queryset = Destination.objects.all()
#     serializer_class = DestinationSerializer

# @csrf_exempt
# @require_POST
# def incoming_data(request):
#     token = request.headers.get('CL-X-TOKEN')
#     if not token:
#         return JsonResponse({'error': 'Unauthenticated'}, status=401)

#     try:
#         account = Account.objects.get(app_secret_token=token)
#     except Account.DoesNotExist:
#         return JsonResponse({'error': 'Account not found'}, status=404)

#     # Ensure that request.body is correctly parsed to JSON
#     try:
#         data = json.loads(request.body.decode('utf-8'))
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON format'}, status=400)

#     destinations = Destination.objects.filter(account=account)
#     responses = []

#     for destination in destinations:
#         try:
#             # Assuming headers are stored as a JSON string in the database and need to be loaded
#             headers = json.loads(destination.headers) if isinstance(destination.headers, str) else destination.headers
#             headers['Content-Type'] = 'application/json'  # Ensure the Content-Type is set to application/json

#             if destination.http_method.lower() == 'get':
#                 response = requests.get(destination.url, headers=headers, params=data)
#             else:
#                 response = requests.request(method=destination.http_method.lower(), 
#                                             url=destination.url, 
#                                             headers=headers, 
#                                             json=data)  # Use json=data to automatically handle JSON serialization

#             responses.append({'url': destination.url, 'response': response.text, 'status_code': response.status_code})
#         except Exception as e:
#             responses.append({'url': destination.url, 'error': str(e)})

#     return JsonResponse({'responses': responses})


# @csrf_exempt
# @require_http_methods(["GET"])

# def get_destinations(request, account_id):
#     try:
#         account = Account.objects.get(pk=account_id)
#     except Account.DoesNotExist:
#         return JsonResponse({'error': 'Account not found'}, status=404)

#     destinations = Destination.objects.filter(account=account)
#     serializer = DestinationSerializer(destinations, many=True)
#     return JsonResponse(serializer.data, safe=False)    





class BaseViewSet(viewsets.ModelViewSet):
    """
    Base view set that includes error handling.

    This view set extends the standard ModelViewSet and adds
    custom error handling to log exceptions and return a 
    JSON response with the error message.
    """
    def handle_exception(self, exc):
        """
        Handle exceptions by logging them and returning a JSON response.

        Args:
            exc (Exception): The exception that was raised.

        Returns:
            JsonResponse: A JSON response containing the error message and a status code of 400.
        """
        # Log the exception
        logging.error(f"Error occurred: {exc}")
        # Return a JSON response with the error status and message
        response = JsonResponse({"error": str(exc)}, status=400)
        return response

class AccountViewSet(BaseViewSet):
    """
    View set for handling Account objects.
    
    Inherits from BaseViewSet to include custom error handling.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(BaseViewSet):
    """
    View set for handling Destination objects.
    
    Inherits from BaseViewSet to include custom error handling.
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer





class AccountVerifier:
    """
    A class to verify account tokens.

    Attributes:
    ----------
    token : str
        The token to be verified.
    """

    def __init__(self, token):
        """
        Initializes the AccountVerifier with a token.

        Parameters:
        ----------
        token : str
            The token to be verified.
        """
        self.token = token

    def verify_token(self):
        """
        Verifies the token and returns the associated account.

        Returns:
        -------
        JsonResponse
            A JSON response with an error message if unauthenticated or account not found.
        Account
            The account associated with the token if it exists.
        """
        if not self.token:
            # Return an error response if the token is missing
            return JsonResponse({'error': 'Unauthenticated'}, status=401)

        try:
            # Try to retrieve the account associated with the provided token
            account = Account.objects.get(app_secret_token=self.token)
            return account
        except Account.DoesNotExist:
            # Return an error response if the account does not exist
            return JsonResponse({'error': 'Account not found'}, status=404)


class JSONProcessor:
    """
    A class to process JSON data from a request body.

    Attributes:
    ----------
    request_body : bytes
        The request body containing JSON data.
    """

    def __init__(self, request_body):
        """
        Initializes the JSONProcessor with a request body.

        Parameters:
        ----------
        request_body : bytes
            The request body containing JSON data.
        """
        self.request_body = request_body

    def parse_json(self):
        """
        Parses the JSON data from the request body.

        Returns:
        -------
        dict
            The parsed JSON data.
        JsonResponse
            A JSON response with an error message if the JSON format is invalid.
        """
        try:
            # Attempt to decode and parse the JSON data from the request body
            data = json.loads(self.request_body.decode('utf-8'))
            return data
        except json.JSONDecodeError:
            # Return an error response if the JSON format is invalid
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)


class DestinationHandler:
    """
    Handles processing and sending HTTP requests to multiple destinations associated with a given account.
    
    Attributes:
        account (object): The account object used to filter destinations.
        data (dict): The data to be sent in the HTTP requests.
    """
    def __init__(self, account, data):
        """
        Initializes the DestinationHandler with the given account and data.

        Args:
            account (object): The account object used to filter destinations.
            data (dict): The data to be sent in the HTTP requests.
        """
        self.account = account
        self.data = data

    def process_destinations(self):
        """
        Processes all destinations associated with the account by sending HTTP requests
        with the provided data and headers. 

        Returns:
            list: A list of dictionaries containing the URL, response text, and status code for each destination.
                  In case of an error, the dictionary will contain the URL and the error message.
        """
        # Retrieve all destinations associated with the account
        destinations = Destination.objects.filter(account=self.account)
        responses = []

        # Iterate through each destination and send an HTTP request
        for destination in destinations:
            try:
                # Load headers from JSON string if necessary
                headers = json.loads(destination.headers) if isinstance(destination.headers, str) else destination.headers
                # Ensure the Content-Type is set to application/json
                headers['Content-Type'] = 'application/json'
                # Send the HTTP request and store the response
                response = self.send_request(destination, headers)
                responses.append({'url': destination.url, 'response': response.text, 'status_code': response.status_code})
            except Exception as e:
                # Handle any exceptions that occur during the request
                responses.append({'url': destination.url, 'error': str(e)})
        
        return responses

    def send_request(self, destination, headers):
        """
        Sends an HTTP request to the specified destination with the provided headers and data.

        Args:
            destination (object): The destination object containing the URL and HTTP method.
            headers (dict): The headers to include in the HTTP request.

        Returns:
            Response: The HTTP response object.
        """
        # Check the HTTP method and send the request accordingly
        if destination.http_method.lower() == 'get':
            return requests.get(destination.url, headers=headers, params=self.data)
        else:
            return requests.request(method=destination.http_method.lower(), url=destination.url, headers=headers, json=self.data)



@csrf_exempt
@require_POST
def incoming_data(request):
    """
    Handles incoming POST requests containing JSON data.

    This function verifies the account token from request headers, processes the 
    JSON data from the request body, and handles the data based on the verified account.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: A JSON response containing the processed data or an error message.
    """
    try:
        # Verify the account token from request headers
        verifier = AccountVerifier(request.headers.get('CL-X-TOKEN'))
        account = verifier.verify_token()
        
        # Parse JSON data from the request body
        processor = JSONProcessor(request.body)
        data = processor.parse_json()
        
        # Handle the data based on the verified account
        handler = DestinationHandler(account, data)
        responses = handler.process_destinations()

        # Return a JSON response containing the processed data
        return JsonResponse({'responses': responses})
    
    except ValueError as e:
        # Return a JSON response with a 401 status code for ValueError
        return JsonResponse({'error': str(e)}, status=401)
    
    except LookupError as e:
        # Return a JSON response with a 404 status code for LookupError
        return JsonResponse({'error': str(e)}, status=404)
    
    except Exception as e:
        # Return a JSON response with a 500 status code for any other exceptions
        return JsonResponse({'error': str(e)}, status=500)



class DestinationRetriever:
    """
    A class to retrieve account and associated destinations.
    
    Attributes:
        account_id (int): The ID of the account.
    """

    def __init__(self, account_id):
        """
        Initializes the DestinationRetriever with the given account ID.
        
        Args:
            account_id (int): The ID of the account to be retrieved.
        """
        self.account_id = account_id

    def get_account(self):
        """
        Retrieves the account object based on the account ID.
        
        Returns:
            Account: The retrieved account object.
        
        Raises:
            ValueError: If the account does not exist.
        """
        try:
            account = Account.objects.get(pk=self.account_id)
        except Account.DoesNotExist:
            raise ValueError("Account not found")
        return account

    def get_destinations(self, account):
        """
        Retrieves the destinations associated with the given account.
        
        Args:
            account (Account): The account object for which destinations are to be retrieved.
        
        Returns:
            QuerySet: A queryset of destinations associated with the account. 
            Returns an empty list if no destinations are found.
        """
        try:
            destinations = Destination.objects.filter(account=account)
        except Destination.DoesNotExist:
            # Handle the case where no destinations are found
            return []
        return destinations

    def serialize_destinations(self, destinations):
        """
        Serializes the list of destinations.
        
        Args:
            destinations (QuerySet): The queryset of destinations to be serialized.
        
        Returns:
            list: A list of serialized destination data.
        """
        serializer = DestinationSerializer(destinations, many=True)
        return serializer.data


@csrf_exempt
@require_http_methods(["GET"])
def get_destinations_view(request, account_id):
    """
    A view to handle GET requests for retrieving destinations of an account.
    
    Args:
        request (HttpRequest): The request object.
        account_id (int): The ID of the account for which destinations are to be retrieved.
    
    Returns:
        JsonResponse: A JSON response containing serialized destination data or an error message.
    """
    handler = DestinationRetriever(account_id)
    try:
        account = handler.get_account()
        destinations = handler.get_destinations(account)
        serialized_data = handler.serialize_destinations(destinations)
        return JsonResponse(serialized_data, safe=False)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=404)





