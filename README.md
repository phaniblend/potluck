# Potluck - Homemade Food Marketplace

## Description
A peer-to-peer marketplace connecting home chefs with local food lovers.

## Tech Stack
- Backend: Flask (Python)
- Database: SQLite
- Frontend: Vanilla JavaScript, HTML5, CSS3
- Deployment: Railway

## Setup Instructions
1. Navigate to backend directory: `cd backend`
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update values
6. Initialize database: `python ../database/init_db.py`
7. Run application: `python app.py`

## Project Structure
```
potluck/
├── backend/          # Flask backend
├── frontend/         # Frontend files
├── database/         # Database schemas and scripts
├── docs/            # Documentation
├── scripts/         # Utility scripts
└── tests/           # Test files
```
