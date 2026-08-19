# U3Choice

U3Choice is a full-stack social platform with user profiles, friendships, messaging, notifications, and search. It provides a foundation for building community-driven web apps.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Redis, Docker
- **Frontend:** Svelte 5, Vite
- **Auth:** JWT tokens stored in cookies
- **Search:** PostgreSQL trigram search engine

## Project Structure

```
U3Choice/
├── backend/          # FastAPI application
│   ├── api/            # API endpoints (auth, users, friendships, messages, notifications, search, security)
│   ├── models/          # SQLAlchemy models (user, friendship, message, notification)
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic (users, security, auth, search, etc.)
│   ├── database.py      # Database engine + init
│   ├── config.py          # Settings via .env
│   ├── requirements.txt
│   └── dockerfile
├── frontend/          # Svelte + Vite frontend
│   ├── src/
│   │   ├── lib/          # Reusable API client modules
│   │   └── routes/          # Page & layout components
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.js
│   └── dockerfile
├── docker-compose.yml       # Defines postgres, redis, backend, frontend services
└── .env.example          # Template for environment variables
```

## Features

- User authentication – sign up, login, JWT refresh
- User profiles & avatars – editable
- Friendship system (follow / unfollow)
- Messaging
- Notifications (Real-time via WebSockets)
- Search (available across users, posts, etc.)
- Security middleware (password hashing, protected routes)

## Getting Started (Docker)

1. Clone the repository and navigate into the project folder.
2. Copy `.env.example` to `.env` and fill in your database URLs, Redis URL, and JWT secret.
3. Start the stack:
   ```bash
   docker-compose up --build
   ```
   This starts:
   - `database` – PostgreSQL on `:5432`
   - `redis` – Redis on `:6379`
   - `backend` – FastAPI app on `:8000`
   - `frontend` – Vite dev server at `http://localhost:5173`

4. Open `http://localhost:5173` in your browser.

## Running Without Docker

- Backend:
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn api.main:app --reload
  ```
- Frontend:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## API Overview (main routes)

| Method | Endpoint                  | Description               |
| ------ | -------------------------- | --------------------------------------------------------------------- |
| POST   | `/api/auth/register`          | Create a new account          |
| POST   | `/api/auth/login`             | Login and get token            |
| POST   | `/api/auth/logout`            | Revoke token                             |
| PATCH   | `/api/users/{username}`         | Update current user profile       |
| POST   | `/api/users/follow`            | Follow a user                      |
| POST   | `/api/users/unfollow`          | Unfollow a user                          |
| GET    | `/api/messages/{id}`         | Get messages between users        |
| POST   | `/api/messages`               | Send a message                       |
| GET    | `/api/search?q={query}`     | Search users/posts                  |
| GET    | `/api/notifications`         | Get current user notifications |
| WS     | `/api/ws/notifications`       | Real-time notifications            |

## Configuration

- Backend settings are read from `backend/.env` (or environment).
- Frontend Vite dev server listens on port `5173`.
- CORS is allowed for `http://localhost:5173`.

## License

MIT