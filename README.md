
## Quick Start

### Option 1: Try Online Demo (Recommended for Testing)
- **Frontend**: [https://vladkovach.github.io/kan_mind/](https://vladkovach.github.io/kan_mind/) (GitHub Pages)
- **Backend API**: [https://kanmind.onrender.com/api/](https://kanmind.onrender.com/api/) (Render free tier)

**Notes**:
- Backend expires **January 28, 2026**.
- Free Render tier is slow: **First request takes up to 30 seconds** (cold start/build trigger).
- Subsequent requests faster (~few seconds) [web:84].

### Option 2: Run Locally
Follow these steps to clone, setup, and run the development server.

## Step 1: Clone Repository
```
git clone https://github.com/VladKovach/KanMind.git
cd KanMind
```
## Step 2: Create Virtual Environment & Install Dependencies
### Create venv
```
python -m venv venv
```
### Activate (Windows)
```
venv\Scripts\activate
```
### Activate (Linux/macOS)
```
source venv/bin/activate
```
### Install deps
```
pip install -r requirements.txt
```
## Step 3: Environment Setup
### Copy .env
```
cp .env.template .env
```

## Step 4: Database & Migrations
### Apply migrations 
```
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Run Development Server
```
python manage.py runserver
```
Access at http://127.0.0.1:8000/ or http://localhost:8000/.
