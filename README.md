# User API Service

A simple Python Flask REST API for user management.

## Overview

This service provides CRUD operations for user management:
- Create users
- Read user details
- Update user information
- Delete users
- List all users

## Features

- RESTful API design
- SQLite database (easily replaceable with PostgreSQL/MySQL)
- CORS enabled for frontend integration
- Health check endpoint
- Docker containerized
- Logging with configurable levels
- Input validation
- Error handling

## API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "user-api",
  "timestamp": "2025-11-09T12:00:00",
  "version": "1.0.0"
}
```

### List Users
```
GET /users
```

Response:
```json
{
  "success": true,
  "count": 3,
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "created_at": "2025-11-09 12:00:00",
      "updated_at": "2025-11-09 12:00:00"
    }
  ]
}
```

### Get User by ID
```
GET /users/<id>
```

Response:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "created_at": "2025-11-09 12:00:00",
    "updated_at": "2025-11-09 12:00:00"
  }
}
```

### Create User
```
POST /users
Content-Type: application/json

{
  "username": "new_user",
  "email": "user@example.com",
  "full_name": "New User"
}
```

Response:
```json
{
  "success": true,
  "message": "User created successfully",
  "user_id": 4
}
```

### Update User
```
PUT /users/<id>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "full_name": "Updated Name"
}
```

Response:
```json
{
  "success": true,
  "message": "User updated successfully"
}
```

### Delete User
```
DELETE /users/<id>
```

Response:
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Test the API**:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/users
   ```

### Environment Variables

- `PORT`: Server port (default: 8080)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DATABASE_URL`: Database connection string (default: sqlite:///users.db)
- `SECRET_KEY`: Flask secret key (change in production!)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)
- `FLASK_ENV`: Flask environment (development/production)

## Docker

### Build Image
```bash
docker build -t user-api:latest .
```

### Run Container
```bash
docker run -d \
  --name user-api \
  -p 8080:8080 \
  -e LOG_LEVEL=INFO \
  user-api:latest
```

### With Custom Configuration
```bash
docker run -d \
  --name user-api \
  -p 8080:8080 \
  -e DATABASE_URL=sqlite:///data/users.db \
  -e SECRET_KEY=your-secret-key \
  -v $(pwd)/data:/app/data \
  user-api:latest
```

## Jenkins Build

This service uses the shared `pipeline-build` library for automated builds.

### Build Process

1. **Checkout**: Clone repository
2. **Setup**: Create Python virtual environment
3. **Test**: Run unit tests (if available)
4. **Build**: Package application
5. **Docker**: Build and tag Docker image
6. **Publish**: Push to Docker registry (on tag builds)
7. **Notify**: Send email notification

### Trigger Build

**Manual**:
- Go to Jenkins → user-api job
- Click "Build Now"

**Automated**:
- Push to `main` branch: Builds image with commit hash
- Push Git tag (e.g., `1.0.0`): Builds and publishes versioned image

### Build Configuration

Configured in `Jenkinsfile`:
- `APP_NAME`: user-api
- `NOTIFICATION_EMAIL`: dev-team@example.com

## Deployment

This service is deployed using Ansible playbooks from `pipeline-deployment` repository.

### Deploy to Environment

```bash
cd ../pipeline-deployment
ansible-playbook deploy-services.yml \
  -i ../deployment-config/inventory.ini \
  -e "env=dev service_name=user-api"
```

### Deployment Configuration

Service configuration is in `deployment-config/services/user-api/docker-compose.yaml.j2`

Environment-specific variables:
- `deployment-config/vars/dev-vars.yml`
- `deployment-config/vars/qa-vars.yml`
- `deployment-config/vars/prod-vars.yml`

## Testing

### Manual Testing

Test all endpoints:
```bash
# Health check
curl http://localhost:8080/health

# Get all users
curl http://localhost:8080/users

# Get specific user
curl http://localhost:8080/users/1

# Create user
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","email":"test@example.com","full_name":"Test User"}'

# Update user
curl -X PUT http://localhost:8080/users/1 \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Updated Name"}'

# Delete user
curl -X DELETE http://localhost:8080/users/1
```

### Load Testing

Using Apache Bench:
```bash
ab -n 1000 -c 10 http://localhost:8080/health
ab -n 1000 -c 10 http://localhost:8080/users
```

## Database

### SQLite (Default)

Database file: `users.db` in working directory

Schema:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Migrate to PostgreSQL

Update `DATABASE_URL`:
```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/users
```

Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

## Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

### Logs

**Docker**:
```bash
docker logs user-api -f
```

**Local**:
Logs are printed to stdout with timestamps

### Metrics

Access logs show:
- Timestamp
- Log level
- Message

Example:
```
2025-11-09 12:00:00 - __main__ - INFO - Starting User API on port 8080
2025-11-09 12:00:05 - __main__ - INFO - Created user: test_user (ID: 4)
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process using port 8080
lsof -ti:8080 | xargs kill -9
```

### Database Locked
SQLite can lock with concurrent writes. Use PostgreSQL for production.

### CORS Issues
Set `CORS_ORIGINS` environment variable:
```bash
export CORS_ORIGINS=http://localhost:3000,https://example.com
```

### Container Won't Start
Check logs:
```bash
docker logs user-api
```

Verify health:
```bash
docker inspect user-api
```

## Security

### Production Checklist

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Restrict CORS origins
- [ ] Add authentication/authorization
- [ ] Enable rate limiting
- [ ] Use environment variables for secrets
- [ ] Run as non-root user (already configured in Docker)
- [ ] Regular security updates

## Performance

### Benchmarks

Simple GET requests: ~1000 req/s on standard hardware

### Optimization Tips

1. **Use PostgreSQL**: Better for concurrent access
2. **Add caching**: Use Redis for frequently accessed data
3. **Connection pooling**: For database connections
4. **Enable compression**: gzip responses
5. **Load balancing**: Run multiple instances behind nginx/HAProxy

## Future Enhancements

- [ ] Add authentication (JWT tokens)
- [ ] Add pagination for user list
- [ ] Add search/filter capabilities
- [ ] Add user roles and permissions
- [ ] Add API rate limiting
- [ ] Add comprehensive test suite
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Add database migrations (Alembic)
- [ ] Add caching layer (Redis)

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Create pull request
5. Wait for CI/CD to pass
6. Deploy to dev environment for testing

## License

Internal use only - proprietary
