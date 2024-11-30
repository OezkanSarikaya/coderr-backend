
# Coderr Backend

Coderr is a platform for freelancers in web development. This is a learning project.  
The backend provides the API for the frontend, which can be found here: [Coderr Frontend Repository](https://github.com/OezkanSarikaya/coderr-frontend).  

**Version:** 1.0  

## Features

- Registration and login as either a **Business User (Provider)** or a **Customer User (Client)**.
- Users can edit their profiles.
- Only **Business Users** can create and edit offers.
- **Customer Users** can place orders for offers.
- Only **Business Users** can manage orders.
- Only **Customer Users** can create, edit, or delete reviews only for **Business Users**.
- HTML tags are removed from all text inputs to ensure clean data.

---

## Prerequisites

- **Python** (Version 3.x)
- **Django** (Version 5.x)  
  All required dependencies can be installed via the `requirements.txt` file (see below).

---

## Installation

### 1. Clone the project
```bash
git clone git@github.com:OezkanSarikaya/coderr-backend.git
```

### 2. Create and activate a virtual environment
```bash
python -m venv env
"env/Scripts/activate"
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Migrate the database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate the database with test data and a guest account
```bash
python db_fill.py
```

### 6. Start the server
```bash
python manage.py runserver
```

---

## Usage

- The backend endpoint is available at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Once the server is running, the backend can be used with the frontend.  
  Frontend Repository: [Coderr Frontend Repository](https://github.com/OezkanSarikaya/coderr-frontend)

---

## License

This project is part of a learning exercise and is not intended for production use.
