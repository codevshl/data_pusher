
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from data_pusher_app.models import Account, Destination

def create_account():
    """ Helper function to create a valid account for use in tests. """
    return Account.objects.create(email_id='test@example.com', account_name='ValidName')


class DestinationModelTest(TestCase):
    def setUp(self):
        self.account = create_account()

    def test_url_validation(self):
        """ Test that the URL must be valid according to Django's URLValidator. """
        headers_example = {"Content-Type": "application/json"}  # Example headers

        # This instance should be valid and not raise a ValidationError
        dest = Destination(account=self.account, url='http://validurl.com', http_method='GET', headers=headers_example)
        try:
            dest.full_clean()  # This should not raise any ValidationError
        except ValidationError:
            self.fail("full_clean raised ValidationError unexpectedly!")

        # This instance should raise a ValidationError due to invalid URL
        with self.assertRaises(ValidationError):
            invalid_dest = Destination(account=self.account, url='not_a_valid_url', http_method='GET', headers=headers_example)
            invalid_dest.full_clean()

    def test_http_method_validation(self):
        """ Test the HTTP method validation. """
        valid_methods = ['GET', 'POST', 'PUT','DELETE']
        headers_example = {"Content-Type": "application/json"}  # Example headers

        for method in valid_methods:
            dest = Destination(account=self.account, url='http://validurl.com', http_method=method, headers=headers_example)
            try:
                dest.full_clean()  # Should not raise an exception
            except ValidationError:
                self.fail(f"HTTP method {method} failed validation unexpectedly.")

        with self.assertRaises(ValidationError):
            invalid_dest = Destination(account=self.account, url='http://validurl.com', http_method='DELETE')
            invalid_dest.full_clean()

    def test_custom_clean_url_forbidden_localhost(self):
        """ Test custom validation that prevents 'localhost' in URLs. """
        headers_example = {"Content-Type": "application/json"}  # Example headers
        dest = Destination(account=self.account, url='http://localhost:8000', http_method='GET', headers=headers_example)
        with self.assertRaises(ValidationError):
            dest.clean()

    def test_save_method(self):
        """ Test the save method, particularly the exception handling within it. """
        headers_example = {"Content-Type": "application/json"}  # Example headers
        dest = Destination(account=self.account, url='http://validurl.com', http_method='GET', headers=headers_example)
        # Save should pass without exceptions since it's a valid Destination
        dest.save()

        # Test saving with an invalid URL to trigger exception handling
        dest.url = 'http://localhost:8000'  # Invalid URL as per custom clean
        with self.assertRaises(ValidationError):
            dest.save()

    def test_model_str_representation(self):
        """ Test the string representation of the Destination model. """
        headers_example = {"Content-Type": "application/json"}  # Example headers
        dest = Destination(account=self.account, url='http://example.com', http_method='GET', headers=headers_example)
        expected_string = f"Destination for {self.account.account_name} (http://example.com)"
        self.assertEqual(str(dest), expected_string)
