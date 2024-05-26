from rest_framework import viewsets
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import requests
import json

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@csrf_exempt
@require_POST
def incoming_data(request):
    token = request.headers.get('CL-X-TOKEN')
    if not token:
        return JsonResponse({'error': 'Unauthenticated'}, status=401)

    try:
        account = Account.objects.get(app_secret_token=token)
    except Account.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)

    # Ensure that request.body is correctly parsed to JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    destinations = Destination.objects.filter(account=account)
    responses = []

    for destination in destinations:
        try:
            # Assuming headers are stored as a JSON string in the database and need to be loaded
            headers = json.loads(destination.headers) if isinstance(destination.headers, str) else destination.headers
            headers['Content-Type'] = 'application/json'  # Ensure the Content-Type is set to application/json

            if destination.http_method.lower() == 'get':
                response = requests.get(destination.url, headers=headers, params=data)
            else:
                response = requests.request(method=destination.http_method.lower(), 
                                            url=destination.url, 
                                            headers=headers, 
                                            json=data)  # Use json=data to automatically handle JSON serialization

            responses.append({'url': destination.url, 'response': response.text, 'status_code': response.status_code})
        except Exception as e:
            responses.append({'url': destination.url, 'error': str(e)})

    return JsonResponse({'responses': responses})