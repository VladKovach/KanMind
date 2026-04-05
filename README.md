## Quick Start

### Live:

- https://kanmind.vladkovach.com

### Run Locally

Follow these steps to clone, setup, and run the development server.

#### Step 1: Clone Repository

```
git clone https://github.com/VladKovach/KanMind.git
cd KanMind
```

#### Step 2: Create Virtual Environment & Install Dependencies

##### Create venv

```
python -m venv venv
```

##### Activate (Windows)

```
venv\Scripts\activate
```

##### Activate (Linux/macOS)

```
source venv/bin/activate
```

##### Install deps

```
pip install -r requirements.txt
```

#### Step 3: Environment Setup

##### Copy .env

```
cp .env.template .env
```

#### Step 4: Database & Migrations

##### Apply migrations

```
python manage.py makemigrations
python manage.py migrate
```

#### Step 5: Run Development Server

```
python manage.py runserver
```

Access at http://127.0.0.1:8000/ or http://localhost:8000/.
