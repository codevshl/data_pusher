

# Data Pusher

## Overview
Data Pusher is a Django web application designed to efficiently handle JSON data received on a server, authenticate it using an app secret token, and distribute this data across various platforms using defined webhook URLs associated with each account.


## Features

- **Account Management**: Create, retrieve, update, and delete accounts.
- **Destination Management**: Manage webhook URLs and settings for each account.
- **Data Handling**: Receive and distribute JSON data based on account settings and authentication.


## Process

1. **Application Setup**: Build a Django web application.
2. **APIs**:
   - **Account APIs**: Create, Read, Update, Delete (CRUD) operations for accounts.
   - **Destination APIs**: CRUD operations for destinations related to accounts.
3. **Destination Retrieval**: API to retrieve destinations for a given account ID.
4. **Data Reception**:
   - **Endpoint**: `/server/incoming_data` accepts only POST requests in JSON format.
   - **Authentication**: Must include an `app_secret_token` in the `CL-X-TOKEN` header.
   - **Data Distribution**: Upon validating the data and token, it sends the data to the specified destinations.


## Installation

**Prerequisites**:
- Python 3.10 or higher
- Django 3.x
- Django REST Framework

**Setup**:

0. Create and activate a virtual environment:
   ``` python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

1. Clone the repository:
   ```
   git clone https://github.com/codevshl/data_pusher.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python manage.py migrate
   ```

4. Run the server:
   ```
   python manage.py runserver
   ```

API Endpoints:

- **Accounts**:
  - `POST /api/accounts/`: Create a new account.                [Images/PUT_Accounts](Images/PUT_Accounts.png)
  - `GET /api/accounts/<id>/`: Retrieve a specific account.     [Images/GET_Accounts](Images/GET_Accounts.png)
  - `PUT /api/accounts/<id>/`: Update a specific account.       [Images/PUT_Accounts](Images/PUT_Accounts.png)
  - `DELETE /api/accounts/<id>/`: Delete a specific account.    [Images/DELETE_Accounts](Images/DELETE_Accounts.png)

- **Destinations**:
  - `POST /api//destinations/`: Create a new destination.             [Images/POST_Destinations](Images/POST_Destinations.png)
  - `GET /api/destinations/<id>/`: Retrieve a specific destination.   [Images/GET_Destinations](Images/GET_Destinations.png)
  - `PUT /destinations/<id>/`: Update a specific destination.         [Images/PUT_Accounts](Images/PUT_Accounts.png)
  - `DELETE /destinations/<id>/`: Delete a specific destination.      [Images/DELETE_Destinations](Images/DELETE_Destinations.png)
  - `GET /api/acccounts/<account_id>/destinations/`: Retrieve all destinations for specific account.   [Images/GET_Accounts_Destinations](Images/GET_Accounts_Destinations.png)

- **Incoming Data**:
  - `POST /api//server/incoming_data`: Receive and forward data to account destinations. Requires `CL-X-TOKEN` header for authentication.  [Images/POST_IncomingData](Images/POST_IncomingData.png)
  


## Running Tests

**Running Tests for a Specific App (here `data_pusher_app`)**

```
 python manage.py test data_pusher_app 
```

**Running Specific Test Modules**

``` 
python manage.py test data_pusher_app.tests.test_models
```

**Running Specific Test Files**

```
python manage.py test data_pusher_app.tests.test_views.test_some_views --verbosity=2
```

## General Tips for Running Tests

**Verbosity**: You can control the verbosity of the test output using the `--verbosity` flag. Verbosity levels range from 0 to 3, where 3 is the most verbose.

**Keep Database**: By default, Django will create a new test database every time you run tests. If you want to keep the test database between test runs (not recommended in most cases), you can use the `--keepdb` flag.

**Parallel Execution**: If you want to speed up your test runs, you can execute tests in parallel using the `--parallel` flag.



