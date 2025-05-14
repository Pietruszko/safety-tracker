### Setup Instructions

#### 1. Clone and prepare the repository
```bash
git clone https://github.com/Pietruszko/safety-tracker
cd safety-tracker
```

#### 2. Set up virtual environment
```bash
python -m venv venv # or python3
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

#### 3. Install requirements
```bash
pip install -r requirements.txt
```

#### 4. Configure environment
1. Rename the template file:
   ```bash
   cp .env.template .env
   ```
2. Edit the `.env` file with your configuration:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=safety_tracker
   DB_USER=postgres
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   DB_PORT=5432
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

#### 5. Set up PostgreSQL database
```bash
sudo -u postgres psql -c "CREATE DATABASE safety_tracker;"
sudo -u postgres psql -c "CREATE USER tracker_user WITH PASSWORD 'yourpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE safety_tracker TO tracker_user;"
```

#### 6. Run migrations
```bash
python manage.py migrate
```

#### 7. Start development server
```bash
python manage.py runserver
```

The API will be available at: http://localhost:8000/

---

### If I had more time I would...

#### 1. Create better documentation
#### 2. Run more comprehensive tests
#### 3. Implement all bonus ideas

---

### About spam prevention

> How would you prevent location spam?
> 
> 
> For example, if a device starts sending pings every second instead of every few minutes — what could you do on the backend to handle that?

##### First of all I would implement rate limiting that would prevent spam at the API level (for example 1 ping for 1-5 minutes).
##### But let's say high-frequency was intended (e.g emergency mode), then I would consider switching to another database for this task.
##### Also very helpful would be visualizing anomalies, so creating some sort of dashboard would be beneficial too.

