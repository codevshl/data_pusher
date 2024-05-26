from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, DestinationViewSet, incoming_data
from django.views.generic.base import RedirectView

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'destinations', DestinationViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('server/incoming_data', incoming_data, name='incoming_data'),
# ]

urlpatterns = [
    path('', include(router.urls)),  # This automatically includes 'accounts/' and 'destinations/' from the router
    path('server/incoming_data', incoming_data, name='incoming_data'),
    #path('server/incoming_data/', RedirectView.as_view(url='/where-to-redirect/', permanent=False), name='test-redirect'),
]

