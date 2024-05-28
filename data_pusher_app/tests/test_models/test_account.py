
from django.test import TestCase
from django.core.exceptions import ValidationError
from uuid import UUID
from data_pusher_app.models import Account

def is_uuid(uuid_string):
    try:
        UUID(uuid_string, version=4)
        return True
    except ValueError:
        return False


class AccountModelTest(TestCase):
    def test_account_default_values(self):
        """ Test the default values are assigned correctly. """
        account = Account(email_id='test@example.com', account_name='ValidName')
        account.save()
        self.assertTrue(is_uuid(account.account_id.hex))
        self.assertTrue(is_uuid(account.app_secret_token.hex))

    def test_email_field(self):
        """ Test the email field uniqueness and proper email format. """
        Account.objects.create(email_id='unique@example.com', account_name='NameOne')
        with self.assertRaises(ValidationError):
            new_account = Account(email_id='unique@example.com', account_name='NameTwo')
            new_account.full_clean()

    def test_account_name_validation(self):
        """ Test custom validation that prevents 'example' in account names. """
        with self.assertRaises(ValidationError):
            account = Account(email_id='another@example.com', account_name='invalid_example')
            account.clean()

    def test_app_secret_token_uniqueness(self):
        """ Test that app secret token is unique across different instances. """
        account1 = Account.objects.create(email_id='email1@example.com', account_name='NameOne')
        account2 = Account.objects.create(email_id='email2@example.com', account_name='NameTwo')
        self.assertNotEqual(account1.app_secret_token, account2.app_secret_token)

    def test_model_str_representation(self):
        """ Test the string representation of the Account model. """
        account = Account(email_id='test@example.com', account_name='TestAccount')
        self.assertEqual(str(account), 'TestAccount (test@example.com)')

    def test_save_method(self):
        """ Test the save method, particularly the validation call within it. """
        account = Account(email_id='valid@example.com', account_name='TestSave')
        # Save should pass without exceptions since it's a valid account
        account.save()
        # Modify account to invalid state and test save
        account.account_name = 'invalid_example'
        with self.assertRaises(ValidationError):
            account.save()
