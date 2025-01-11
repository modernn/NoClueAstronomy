### **README.md**

---

# **Astronomical Events Viewer**

## **Overview**

The **Astronomical Events Viewer** is a web application that allows users to track and view upcoming astronomical events, such as meteor showers and eclipses. It features a **FastAPI backend** for serving event data and a **Streamlit frontend** for a user-friendly interface. The application supports user authentication and secure communication via JWT tokens.

---

## **Features**

### Backend (FastAPI)
- Fetch all astronomical events.
- Fetch a specific event by its ID.
- Secure endpoints using JWT authentication.
- Serve event data from a static JSON file.

### Frontend (Streamlit)
- User authentication using `streamlit-authenticator`.
- Display a list of upcoming astronomical events.
- Search for events by their unique ID.
- Secure API calls with JWT tokens.

---

## **Project Structure**

```plaintext
project/
│
├── backend/                      # FastAPI backend
│   ├── __init__.py               # Makes this directory a package
│   ├── main.py                   # FastAPI entry point
│   ├── routes/                   # API routes
│   │   ├── __init__.py
│   │   └── events.py             # Routes for event-related endpoints
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── event_model.py        # Pydantic models for validation
│   ├── utils/                    # Utility functions (e.g., JWT handling)
│   │   ├── __init__.py
│   │   └── jwt_handler.py        # JWT token creation and validation
│   └── data/                     # Static data (sample events)
│       └── data.json
│
├── frontend/                     # Streamlit frontend
│   ├── __init__.py
│   └── streamlit_app.py          # Streamlit entry point
│
├── tests/                        # Tests for backend and frontend
│   ├── test_backend.py           # Tests for FastAPI endpoints
│   └── test_frontend.py          # Tests for Streamlit app (basic functionality)
│
├── .env                          # Environment variables (e.g., secret keys)
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

---

## **Setup Instructions**

### Prerequisites
- Python 3.10 or higher
- Pip (Python package manager)

### 1. Clone the repository
```bash
git clone <repository_url>
cd project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root and add the following:
```plaintext
JWT_SECRET=your-secret-key
```

### 4. Run the backend
```bash
cd src/backend
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`.

### 5. Run the frontend
In a new terminal window:
```bash
cd src/frontend
streamlit run streamlit_app.py
```
The frontend will be available at `http://localhost:8501`.

---

## **Usage**

1. Open the Streamlit app in your browser.
2. Log in using the provided credentials (`streamlit-authenticator`).
3. View a list of upcoming astronomical events.
4. Search for specific events by their ID.
5. Make secure requests to the backend using JWT tokens.

---

## **Sample Data**

Sample astronomical events are stored in `backend/data/data.json`. You can modify this file to add your own events.

---

## **Testing**

### Run tests
```bash
pytest
```

### Test coverage
- **Backend**: Tests for FastAPI endpoints (e.g., `/events`, `/events/{id}`).
- **Frontend**: Basic tests for Streamlit user interactions.

---

## **Dependencies**

Listed in `requirements.txt`:
- `fastapi`
- `uvicorn`
- `pydantic`
- `streamlit`
- `streamlit-authenticator`
- `python-jose`
- `pytest`
- `requests`

---

## **Future Enhancements**
- Add database integration (e.g., PostgreSQL) for dynamic event storage.
- Implement user registration and profile management.
- Provide event notifications and reminders.
- Incorporate advanced visualization features (e.g., interactive star maps).

---

## **License**

This project is licensed under the NOLICENSE License. See the `LICENSE` file for details.

---

## **Contributors**

- **Lincoln Larson** - [My GitHub Profile](https://github.com/modernn/)

---

Let me know if further modifications are needed!