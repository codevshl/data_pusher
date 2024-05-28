from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, DestinationViewSet, incoming_data, get_destinations_view
from django.views.generic.base import RedirectView

# router = DefaultRouter()
# router.register(r'accounts', AccountViewSet)
# router.register(r'destinations', DestinationViewSet)

# # urlpatterns = [
# #     path('', include(router.urls)),
# #     path('server/incoming_data', incoming_data, name='incoming_data'),
# # ]

# urlpatterns = [
#     path('', include(router.urls)),  # This automatically includes 'accounts/' and 'destinations/' from the router
#     path('server/incoming_data', incoming_data, name='incoming_data'),
#     #path('server/incoming_data/', RedirectView.as_view(url='/where-to-redirect/', permanent=False), name='test-redirect'),
#     path('accounts/<uuid:account_id>/destinations', get_destinations, name='get_destinations'),
# ]



class RouterConfig:
    """
    A class to configure and manage the routing for the application.

    Attributes
    ----------
    router : DefaultRouter
        An instance of DefaultRouter to manage the routes.

    Methods
    -------
    setup_routes():
        Registers the viewsets to the router.
    get_router_urls():
        Returns the URLs managed by the router.
    """
    def __init__(self):
        """
        Initializes the RouterConfig instance and sets up the routes.
        """
        self.router = DefaultRouter()
        self.setup_routes()

    def setup_routes(self):
        """
        Registers the viewsets to the router.
        Handles any exceptions during the registration process.
        """
        try:
            self.router.register(r'accounts', AccountViewSet)
            self.router.register(r'destinations', DestinationViewSet)
        except Exception as e:
            print(f"Error registering routes: {e}")

    def get_router_urls(self):
        """
        Returns the URLs managed by the router.

        Returns
        -------
        list
            A list of URLs managed by the router.
        """
        return self.router.urls


class URLPatterns:
    """
    A class to manage the URL patterns for the application.

    Attributes
    ----------
    router_urls : list
        A list of URLs managed by the router.
    urlpatterns : list
        A list of URL patterns for the application.

    Methods
    -------
    create_urlpatterns():
        Creates and returns the URL patterns for the application.
    """
    def __init__(self, router_config):
        """
        Initializes the URLPatterns instance and creates the URL patterns.

        Parameters
        ----------
        router_config : RouterConfig
            An instance of RouterConfig to get the router URLs.
        """
        self.router_urls = router_config.get_router_urls()
        self.urlpatterns = self.create_urlpatterns()

    def create_urlpatterns(self):
        """
        Creates and returns the URL patterns for the application.
        Handles any exceptions during the creation process.

        Returns
        -------
        list
            A list of URL patterns for the application.
        """
        try:
            return [
                path('', include(self.router_urls)),
                path('server/incoming_data', incoming_data, name='incoming_data'),
                path('accounts/<uuid:account_id>/destinations', get_destinations_view, name='get_destinations_view'),
            ]
        except Exception as e:
            print(f"Error creating URL patterns: {e}")


# Usage
router_config = RouterConfig()
urlpatterns = URLPatterns(router_config).urlpatterns

