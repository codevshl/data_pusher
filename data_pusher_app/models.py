from django.db import models
import uuid

def generate_app_secret_token():
    # Generates a secure random UUID as the app secret token
    return uuid.uuid4().hex

class Account(models.Model):
    email_id = models.EmailField(unique=True) ## Key for headerfield(unique=True)
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_name = models.CharField(max_length=100)
    app_secret_token = models.UUIDField(max_length=32, default=generate_app_secret_token, unique=True, editable=False)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.account_name} ({self.email_id})"   


class Destination(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destinations')
    url = models.URLField()
    http_method = models.CharField(max_length=10, choices=(('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT')))
    headers = models.JSONField()

    def __str__(self):
        return f"Destination for {self.account.account_name} ({self.url})"
