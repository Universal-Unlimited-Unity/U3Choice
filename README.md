```markdown
# U3Choice

U3Choice is a full-stack social platform featuring user profiles, friendships, real-time messaging, notifications, and search. The backend was designed and built by me using FastAPI, PostgreSQL, and Redis, while the frontend was built using Svelte 5.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, Docker
- **Frontend:** Svelte 5, Vite
- **Database Migrations:** Alembic
- **Testing & CI:** Pytest, GitHub Actions CI (tests run before pushing/merging)
- **Deployment & Hosting:** Azure Linux VM, Custom Domain DNS mapping, Docker Compose
- **Logging:** Python structured logging
- **Auth:** JWT stored in cookies
- **Search:** PostgreSQL trigram search
- **Real-time:** WebSockets for notifications & messages

## Features

- **Auth:** Register, login, JWT refresh, logout, protected routes, and token revocation
- **Profiles:** View/edit profile, avatar upload, change password, email, and phone
- **Friendships:** Follow and unfollow system
- **Messages:** Real-time 1-on-1 chat via WebSocket (`/api/ws/messages`)
- **Notifications:** Real-time alerts via WebSocket (`/api/ws/notifications`)
- **Search:** Global trigram search across users and messages via `/api/search?q=`
- **Database Migrations:** Managed schema versions and migrations with Alembic
- **Logging:** Request and error logging for debugging and tracking backend events
- **Automated Testing:** Pytest suite integrated into CI to validate endpoints and services

## Getting Started (Docker)

1. Clone the repo:
   ```bash
   git clone [https://github.com/Universal-Unlimited-Unity/U3Choice.git](https://github.com/Universal-Unlimited-Unity/U3Choice.git)
   cd U3Choice

```

2. Copy `.env.example` to `.env` and fill in your DB, Redis, and secret keys:
```bash
cp .env.example .env

```


3. Start the containers:
```bash
docker-compose up --build

```


4. Apply database migrations:
```bash
docker-compose exec backend alembic upgrade head

```



## Running Locally Without Docker

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

alembic upgrade head
uvicorn api.main:app --reload

```

### Frontend

```bash
cd frontend
npm install
npm run dev

```

## Testing & CI

Tests are written using `pytest`. The CI workflow automatically runs the test suite on every push and pull request to ensure nothing breaks.

Run tests locally:

```bash
cd backend
pytest

```

## Deployment

The application is deployed on an **Azure Virtual Machine** running Linux and containerized via Docker Compose. A custom domain is mapped directly to the Azure VM's public IP via DNS records.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Login and get token |
| POST | `/api/auth/logout` | Invalidate token |
| PATCH | `/api/users/{username}` | Update user profile |
| POST | `/api/friendships/follow` | Follow a user |
| POST | `/api/friendships/unfollow` | Unfollow a user |
| GET | `/api/messages/{id}` | Get chat history with a user |
| POST | `/api/messages` | Send a message |
| GET | `/api/search?q=` | Search users and messages |
| GET | `/api/notifications` | Get notifications |
| WS | `/api/ws/notifications` | Live notification stream |
| WS | `/api/ws/messages` | Live messaging stream |

## License

MIT

```

```
