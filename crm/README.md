# CRM Django Application with Celery Integration

This Django application provides a comprehensive CRM system with GraphQL API and asynchronous task processing using Celery.

## Features

- **GraphQL API** for CRUD operations on Customers, Products, and Orders
- **Celery Task Queue** for asynchronous processing
- **Scheduled Reports** using Celery Beat
- **Redis** as message broker and result backend
- **Automated CRM Reports** generated weekly

## Prerequisites

- Python 3.8+
- Django 4.2+
- Redis server
- Git

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start Redis

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### On macOS:
```bash
brew install redis
brew services start redis
```

#### On Windows:
- Download Redis from https://redis.io/download
- Or use Docker: `docker run -d -p 6379:6379 redis:alpine`

#### Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Seed Database (Optional)

```bash
python seed_db.py
```

## Running the Application

### 1. Start Django Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

### 2. Start Celery Worker

Open a new terminal window in the same directory and activate your virtual environment:

```bash
celery -A crm worker -l info
```

### 3. Start Celery Beat (Scheduler)

Open another terminal window and run:

```bash
celery -A crm beat -l info
```

## Celery Configuration

### Task Schedule

The application includes a scheduled task that generates weekly CRM reports:

- **Task**: `generate_crm_report`
- **Schedule**: Every Monday at 6:00 AM UTC
- **Function**: Collects total customers, orders, and revenue
- **Output**: Logs to `/tmp/crm_report_log.txt`

### Manual Task Execution

You can manually trigger the CRM report generation:

```bash
python manage.py shell
```

```python
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

## Monitoring and Logs

### Check Celery Status

```bash
celery -A crm inspect active
celery -A crm inspect scheduled
```

### View CRM Report Logs

```bash
cat /tmp/crm_report_log.txt
```

### View Celery Logs

Celery worker and beat processes will output logs to the terminal where they're running.

## GraphQL API

### Access GraphQL Playground

Visit `http://localhost:8000/graphql/` to access the GraphQL playground.

### Sample Queries

#### Get All Customers
```graphql
query {
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
        createdAt
      }
    }
  }
}
```

#### Get Report Data (Manual Query)
```graphql
query {
  allCustomers {
    edges {
      node {
        id
      }
    }
  }
  allOrders {
    edges {
      node {
        id
        totalAmount
      }
    }
  }
}
```

## Project Structure

```
crm/
├── __init__.py          # Celery app initialization
├── celery.py            # Celery configuration
├── tasks.py             # Celery tasks including CRM report generation
├── models.py            # Django models (Customer, Product, Order)
├── schema.py            # GraphQL schema definitions
├── settings.py          # CRM-specific settings
├── views.py             # Django views
├── admin.py             # Django admin configuration
├── apps.py              # Django app configuration
├── migrations/          # Database migrations
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```
   Error: Redis connection failed
   ```
   - Ensure Redis server is running: `redis-cli ping`
   - Check Redis is running on port 6379

2. **Celery Worker Not Starting**
   ```
   Error: No such transport: redis
   ```
   - Install redis: `pip install redis`
   - Verify Redis is accessible

3. **Task Not Executing**
   - Check Celery worker logs
   - Verify task name in settings matches task definition
   - Ensure Django settings are properly configured

4. **Log File Permission Issues**
   - Create `/tmp` directory if it doesn't exist
   - Ensure write permissions for the application

### Development Tips

1. **Monitor Celery Tasks**
   ```bash
   celery -A crm events
   ```

2. **Clear Celery Queue**
   ```bash
   celery -A crm purge
   ```

3. **Reset Celery Beat Schedule**
   ```bash
   python manage.py migrate django_celery_beat
   ```

## Testing

### Run Django Tests
```bash
python manage.py test
```

### Test Celery Tasks
```bash
python manage.py shell
```

```python
from crm.tasks import test_celery_task
result = test_celery_task.delay()
print(result.get())
```

## Production Deployment

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/crm_celery.conf`:

```ini
[program:crm_celery_worker]
command=/path/to/venv/bin/celery -A crm worker -l info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_error.log

[program:crm_celery_beat]
command=/path/to/venv/bin/celery -A crm beat -l info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat_error.log
```

### Using Docker

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
  
  celery_worker:
    build: .
    command: celery -A crm worker -l info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
  
  celery_beat:
    build: .
    command: celery -A crm beat -l info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
