# Data Pusher

## Overview
Data Pusher is a Django web application designed to efficiently handle JSON data received on a server, authenticate it using an app secret token, and distribute this data across various platforms using defined webhook URLs associated with each account.

## Features

- **Account Management**: Create, retrieve, update, and delete accounts.
- **Destination Management**: Manage webhook URLs and settings for each account.
- **Data Handling**: Receive and distribute JSON data based on account settings and authentication.

## Installation

**Prerequisites**:
- Python 3.7 or higher
- Django 3.x
- Django REST Framework

**Setup**:
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/data-pusher.git
   cd data-pusher

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

3. Initialize the database:
   ```bash
   python manage.py migrate

4. Run the server:
   ```bash
   python manage.py runserver

## API Documentation
**Authentication**
- All endpoints are accessed from the base URL http://localhost:8000/.
- All API requests must include an app secret token in the headers as CL-X-TOKEN.

**Endpoints**
- **Accounts**
  ```json
  { "email_id": "user@example.com", "account_name": "User's Account" }

- **Destinations**
  ```json
  { "account": "uuid-of-account", "url": "https://api.example.com/webhook", "http_method": "POST", "headers": "{\"Content-Type\": \"application/json\"}" }

- **Data Handling**
  ```json
  { "data": "value" }

## Running Tests
```bash
python manage.py test data_pusher_app --verbosity=3






