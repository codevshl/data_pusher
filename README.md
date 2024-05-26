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
