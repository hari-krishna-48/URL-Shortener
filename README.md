# URL Shortener

This project is a microservices-based URL shortener with an authentication service, a static frontend UI, and an Nginx API gateway for load balancing. The intended workflow is to run everything via Docker Compose (gateway + multiple service instances + MongoDB).

**Key features**

1. JWT-based authentication.
2. Owner-only URL management (only the creator can update/delete).
3. MongoDB storage for shared persistence.
4. Nginx gateway with path-based routing and load balancing.

## Components

**1. Auth service** (`services/auth`)

- Flask API for user management and JWT issuing/verification.
- Passwords stored hashed (PBKDF2-HMAC-SHA256 + salt).
- Storage abstraction supports in-memory or MongoDB.

**2. URL shortener service** (`services/url-shortener`)

- Flask API for CRUD URL mappings.
- Requires JWT auth for all endpoints except `GET /<id>`.
- Stores owner per mapping and enforces access control.
- Storage abstraction supports in-memory or MongoDB.

**3. Frontend** (`services/frontend`)

- Flask static file server (HTML/JS/CSS).
- UI for login/register, token verify, shorten/edit/delete/list URLs.

**4. API gateway** (`nginx`)

- Nginx reverse proxy, load balances multiple instances.
- Routes:
  - `/auth/` -> auth service
  - `/shortener/` -> URL shortener service
  - `/frontend/` -> frontend service

**5. Docker Compose** (`docker-compose.yml`)

- Spins up MongoDB, Nginx gateway, 3 auth instances, 4 shortener instances, 2 frontend instances.

## Project Structure

- `services/auth/app.py` - Auth service routes
- `services/auth/jwt.py` - Manual JWT creation/verification
- `services/auth/storage/` - Auth storage abstraction + memory/DB implementations
- `services/auth/utils/password.py` - Password hashing/verification
- `services/auth/config.json` - Auth config (JWT + MongoDB)
- `services/url-shortener/app.py` - URL shortener routes
- `services/url-shortener/storage/` - Shortener storage abstraction + memory/DB implementations
- `services/url-shortener/utils/` - Helpers (auth client, encoding, validation, config)
- `services/url-shortener/config.json` - Shortener config (MongoDB + bonus flag)
- `services/frontend/static/` - Frontend HTML/JS/CSS
- `nginx/nginx.conf` - Gateway routing/load balancing
- `docker-compose.yml` - Multi-instance orchestration
- `test/test_app.py` - Integration tests

## Configuration

**Auth service (`services/auth/config.json`)**

- `jwt.secret`
- `jwt.ttl_seconds`
- `mongodb.*`

**URL shortener (`services/url-shortener/config.json`)**

- `mongodb.*`

**Environment variables (Docker)**

- `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_DATABASE`
- `AUTH_SERVICE_URL` (shortener -> auth verify)
- `DOCKER_ENV=true` (binds to 0.0.0.0 and adds instance header)

## Run with Docker Compose (Gateway + Multi-Instance)

```bash
docker-compose up --build
```

Gateway endpoints:

- Auth: `http://localhost/auth/`
- Shortener: `http://localhost/shortener/`
- Frontend: `http://localhost/frontend/`

MongoDB:

- External port `27018` -> container `27017`

## API Endpoints

All responses are JSON unless noted. Token is provided in `Authorization` header.

### Auth Service (via gateway `/auth`)

1. `POST /auth/users`

   - Create user
   - 201 `{"username":"..."}`
   - 409 `"duplicate"`
2. `PUT /auth/users`

   - Update password
   - 200 `{"username":"..."}`
   - 403 `"forbidden"`
3. `POST /auth/users/login`

   - Login, returns JWT
   - 201 `{"token":"<jwt>"}`
   - 403 `"forbidden"`
4. `POST /auth/auth/verify`

   - Verify JWT (used by shortener)
   - 200 `{"payload": {...}}`
   - 403 `"forbidden"`

### URL Shortener (via gateway `/shortener`)

5. `POST /shortener/` (auth required)

   - Create short URL
   - Body: `{ "value": "<long_url>" }`
   - 201 `{"id":"<short_id>"}`
   - 400 `"error"`
   - 403 `"forbidden"`
6. `GET /shortener/<id>` (public)

   - Resolve ID -> URL
   - 301 `{"value":"<long_url>"}`
   - 404 `"error"`
7. `PUT /shortener/<id>` (auth required, owner-only)

   - Update URL
   - Body: `{ "url": "<new_url>" }`
   - 200 `{"id":"<short_id>"}`
   - 400 `"error"`
   - 403 `"forbidden"`
   - 404 `"error"`
8. `DELETE /shortener/<id>` (auth required, owner-only)

   - 204 on success
   - 403 `"forbidden"`
   - 404 `"error"`
9. `GET /shortener/` (auth required)

   - List caller’s IDs
   - 200 `{"value":["id1","id2"]}` or `{"value": null}`
   - 403 `"forbidden"`
10. `DELETE /shortener/` (auth required)

    - Delete all entries (kept as 404 for test compatibility)
    - 404 `"error"`
    - 403 `"forbidden"`

## Testing

Start auth + shortener, then run:

```bash
python -s test/test_app.py
```

## Notes on Storage

MongoDB is used for persistence:

- Auth users collection stores `{ _id: <username>, password: <hash> }`
- Shortener mappings store `{ _id: <id>, url: <url>, owner: <username> }`
- Counters store `{ _id: "url_id", seq: <counter> }`
