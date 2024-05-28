# from django.db import models
# import uuid

# def generate_app_secret_token():
#     # Generates a secure random UUID as the app secret token
#     return uuid.uuid4().hex

# class Account(models.Model):
#     email_id = models.EmailField(unique=True) ## Key for headerfield(unique=True)
#     account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     account_name = models.CharField(max_length=100)
#     app_secret_token = models.UUIDField(max_length=32, default=generate_app_secret_token, unique=True, editable=False)
#     website = models.URLField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.account_name} ({self.email_id})"   


# class Destination(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destinations')
#     url = models.URLField()
#     http_method = models.CharField(max_length=10, choices=(('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT')))
#     headers = models.JSONField()

#     def __str__(self):
#         return f"Destination for {self.account.account_name} ({self.url})"






from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, RegexValidator
import uuid

def generate_app_secret_token():
    """
    Generate a secure random UUID as the app secret token.

    Returns:
        str: A secure random UUID in hexadecimal format.
    """
    return uuid.uuid4().hex

class Account(models.Model):
    """
    Model representing an account with unique email, account ID, account name, app secret token, and an optional website.

    Attributes:
        email_id (EmailField): The unique email ID of the account.
        account_id (UUIDField): The unique identifier for the account.
        account_name (CharField): The name of the account, limited to 100 characters.
        app_secret_token (UUIDField): The unique, secure secret token for the account.
        website (URLField): An optional URL field for the account's website.
    """
    email_id = models.EmailField(unique=True)
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_name = models.CharField(max_length=100)
    app_secret_token = models.UUIDField(default=generate_app_secret_token, unique=True, editable=False)
    website = models.URLField(blank=True, null=True)

    def clean(self):
        """
        Custom validation for the Account model.

        Raises:
            ValidationError: If the account_name contains 'example'.
        """
        if 'example' in self.account_name:
            raise ValidationError("Account name cannot contain 'example'.")

    def save(self, *args, **kwargs):
        """
        Override the save method to include custom validation before saving.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()  # Call the full_clean method before saving to run all validations
        super().save(*args, **kwargs)  # Call the real save method

    def __str__(self):
        """
        String representation of the Account model.

        Returns:
            str: The account name followed by the email ID in parentheses.
        """
        return f"{self.account_name} ({self.email_id})"



class Destination(models.Model):
    """
    Represents a destination for a given account with a specific URL and HTTP method.
    
    Attributes:
        account (ForeignKey): A reference to the related account.
        url (URLField): The URL of the destination, validated to ensure it is properly formatted.
        http_method (CharField): The HTTP method to be used for this destination, validated to be one of GET, POST, PUT, or DELETE.
        headers (JSONField): Any additional headers to be used in requests to the destination.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destinations')
    url = models.URLField(validators=[URLValidator()])  # Ensure the URL is valid
    http_method = models.CharField(
        max_length=10,
        choices=(('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')),
        validators=[RegexValidator(regex='^(GET|POST|PUT|DELETE)$', message='Invalid HTTP method')]
    )
    headers = models.JSONField()

    def clean(self):
        """
        Perform custom validation for the model.
        
        This method checks if the URL contains 'localhost' and raises a ValidationError if it does.
        Further custom validations can be added as needed.
        """
        if 'localhost' in self.url:
            raise ValidationError("URL cannot contain 'localhost'.")

    def save(self, *args, **kwargs):
        """
        Save the model instance to the database.
        
        This method calls the full_clean method before saving to ensure all validations are run.
        If an error occurs during saving, a ValidationError is raised with the error message.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()  # Call the full_clean method before saving to run all validations
        try:
            super().save(*args, **kwargs)  # Call the real save method
        except Exception as e:
            raise ValidationError(f"Error saving Destination: {str(e)}")

    def __str__(self):
        """
        Return a string representation of the model instance.
        
        Returns:
            str: A string that represents the destination, including the account name and URL.
        """
        return f"Destination for {self.account.account_name} ({self.url})"

