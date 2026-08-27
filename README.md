# U3Choice

U3Choice is a full-stack social platform featuring user profiles, friendships, real-time messaging, notifications, and search.

The backend was designed and built by me using **FastAPI, PostgreSQL, and Redis**, while the frontend was built using **Svelte 5**.

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Docker

### Frontend

- Svelte 5
- Vite

### DevOps & Infrastructure

- Docker Compose
- Azure Linux VM
- Custom domain with DNS mapping
- GitHub Actions CI

### Database & Testing

- Alembic
- Pytest
- PostgreSQL trigram search

### Other

- Python structured logging
- JWT authentication stored in cookies
- WebSockets for real-time communication

## Features

### Authentication

- User registration
- Login
- JWT authentication
- Token refresh
- Logout
- Token revocation
- Protected routes

### User Profiles

- View and edit profiles
- Avatar upload
- Change password
- Change email
- Change phone number

### Friendships

- Follow users
- Unfollow users

### Real-Time Messaging

- Real-time 1-on-1 messaging
- WebSocket-based communication
- Chat history

WebSocket endpoint:

```text
/api/ws/messages
```

### Notifications

- Real-time notifications
- WebSocket-based notification stream

WebSocket endpoint:

```text
/api/ws/notifications
```

### Search

Global search across users and messages using PostgreSQL trigram search.

```text
GET /api/search?q=
```

### Database Migrations

Database schema changes are managed using **Alembic**.

### Logging

The backend includes structured request and error logging for debugging and monitoring application events.

### Automated Testing

The project includes a **Pytest** test suite integrated with GitHub Actions CI.

Tests are automatically executed on pushes and pull requests.

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Git
- Docker
- Docker Compose

### Clone the Repository

```bash
git clone https://github.com/Universal-Unlimited-Unity/U3Choice.git
cd U3Choice
```

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then configure your database credentials, Redis configuration, JWT secrets, and other required environment variables.

### Start the Application

Build and start all services using Docker Compose:

```bash
docker compose up --build
```

### Apply Database Migrations

After the containers are running:

```bash
docker compose exec backend alembic upgrade head
```

## Running Locally Without Docker

### Backend

Create and activate a virtual environment:

```bash
cd backend
python -m venv venv
```

#### Windows

```powershell
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the database migrations:

```bash
alembic upgrade head
```

Start the FastAPI development server:

```bash
uvicorn api.main:app --reload
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Testing

Tests are written using **Pytest**.

Run the test suite locally:

```bash
cd backend
pytest
```

GitHub Actions automatically runs the test suite on every push and pull request.

## CI/CD

The project uses **GitHub Actions** to automatically run tests before changes are merged.

The CI pipeline helps ensure that new changes do not break existing functionality.

## Deployment

U3Choice is deployed on an **Azure Linux Virtual Machine**.

The application is containerized using **Docker Compose**, with the backend, frontend, PostgreSQL, Redis, and other services running as containers.

A custom domain is mapped to the Azure VM through DNS records.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create an account |
| `POST` | `/api/auth/login` | Login and authenticate |
| `POST` | `/api/auth/logout` | Invalidate session/token |
| `PATCH` | `/api/users/{username}` | Update user profile |
| `POST` | `/api/friendships/follow` | Follow a user |
| `POST` | `/api/friendships/unfollow` | Unfollow a user |
| `GET` | `/api/messages/{id}` | Get chat history with a user |
| `POST` | `/api/messages` | Send a message |
| `GET` | `/api/search?q=` | Search users and messages |
| `GET` | `/api/notifications` | Get notifications |
| `WS` | `/api/ws/notifications` | Real-time notification stream |
| `WS` | `/api/ws/messages` | Real-time messaging stream |

## License

This project is licensed under the **MIT License**.
