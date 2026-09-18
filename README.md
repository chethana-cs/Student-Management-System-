# Student Management System

A fullstack CRUD application for managing student records.

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, SQLite
- **Frontend:** Vue 3, Vite, Axios
- **Tests:** pytest

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

The API will be available at `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint          | Description         |
|--------|-------------------|---------------------|
| POST   | /students         | Create a student    |
| GET    | /students         | List all students   |
| GET    | /students/{id}    | Get a student       |
| PUT    | /students/{id}    | Update a student    |
| DELETE | /students/{id}    | Delete a student    |
| GET    | /health           | Health check        |
