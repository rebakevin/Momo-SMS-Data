# MoMo SMS Data

This is a simple MoMo simulation app built in pure Python

## Documentation
- The API endpoints are documented in `docs/api_docs.md`
- Screenshots for testing the endpoints are in `screenshots` directory

## Other documents 
- [Database_Design_Document_Cohort1_Team2](docs/Database_Design_Document_Cohort1_Team2.pdf)
- [PDF Report](docs/Building-and-Securing-a-REST_API_Group3-Cohort1_Report.pdf)
- [Team participation sheet](https://docs.google.com/spreadsheets/d/1NCB-1ds53lkJXSDRUqGpbYZV42F7CvnEn9rMcusWH8g/edit?usp=sharing)

## Features
- Basic CRUD endpoints
  - Create transactions
  - Get all transactions
  - Get transaction by id
  - Delete transaction
  - Update transasction
- Basic auth
- A python script to transform `xml` data to `JSON`
- OpenAPI / Swagger documentation

## How to run the app

### Prerequisites
Before running the app, make sure you have the following installed:
- **Docker** and **Docker Compose** (for MySQL database)
- **Python 3** (version 3.8 or higher)
- **pip** (Python package manager)
- **git** (to clone the repository)

### Option 1: Automated Setup (Recommended)
- Clone the app `git clone https://github.com/rebakevin/Momo-SMS-Data.git`
- Change directory into the project `cd Momo-SMS-Data`
- Make the startup script executable: `chmod +x startup.sh`
- Run `./startup.sh` to install the requirements and start the server at `http://localhost:8000`
- The documentation will be at `http://localhost:8000/api-docs`

### Option 2: Manual Setup (If automated setup fails)

#### Step 1: Clone and Setup Environment
```bash
git clone https://github.com/rebakevin/Momo-SMS-Data.git
cd Momo-SMS-Data
```

#### Step 2: Start MySQL Database
```bash
# Start the MySQL container
docker-compose up -d

# Wait for database to be ready (about 10-15 seconds)
# You can check if it's ready with:
docker exec mysql_db mysqladmin ping -h localhost -uadmin -proot --silent
```

#### Step 3: Create Environment File
```bash
# Create .env file with database credentials
cat > .env << EOF
DB_HOST=localhost
DB_NAME=momo_sms_app
DB_USER=admin
DB_PASSWORD=root
DB_PORT=3307
EOF
```

#### Step 4: Setup Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 5: Setup Database Schema
```bash
# Grant permissions to admin user (important!)
docker exec mysql_db mysql -uroot -proot -h localhost -e "GRANT ALL PRIVILEGES ON momo_sms_app.* TO 'admin'@'%'; FLUSH PRIVILEGES;"

# Create database tables
docker exec -i mysql_db mysql -uadmin -proot -h localhost momo_sms_app < database/database_setup.sql

# Seed sample data
docker exec -i mysql_db mysql -uadmin -proot -h localhost momo_sms_app < database/data_seed.sql
```

#### Step 6: Start the Application
```bash
# Start the server (make sure you're still in the virtual environment)
python main.py
```

The server will start at `http://localhost:8000` and API documentation will be available at `http://localhost:8000/api-docs`

#### Step 7: Verify Installation

**Option A: Test in Browser**
```bash
# Open this URL in your browser:
http://localhost:8000/transactions
```
You should see a login popup asking for username and password. Enter:
- **Username**: `admin`
- **Password**: `admin`

**Option B: Test with curl (without credentials)**
```bash
# Test the API with curl (in another terminal)
curl -i http://localhost:8000/transactions
```
You should see a response like:
```http
HTTP/1.0 401 Unauthorized
Server: BaseHTTP/0.6 Python/3.12.3
Content-type: application/json
WWW-Authenticate: Basic realm="Momo API"

{"error": "Unauthorized: Invalid or missing credentials"}
```

**Option C: Test with curl (with credentials)**
```bash
# Test the API with curl (in another terminal)
curl -u admin:admin http://localhost:8000/transactions
```

You should see a JSON response with transaction data.

## API Authentication
All API endpoints require Basic Authentication:
- **Username**: `admin`
- **Password**: `admin`

Example usage:
```bash
curl -u admin:admin http://localhost:8000/transactions
```

## Troubleshooting

### Automated Setup Issues
- If startup.sh fails with "permission denied": Run `chmod +x startup.sh`
- If startup.sh fails: Make sure Docker is running
- If port 8000 is busy: Kill existing processes with `pkill -f "python main.py"`
- If database connection fails: Check that MySQL container is healthy with `docker ps`

### Manual Setup Issues
- **Docker command not found**: Install Docker and Docker Compose
- **Python not found**: Install Python 3.8+ and pip
- **Database connection fails**: 
  - Check MySQL container: `docker ps | grep mysql_db`
  - Check database readiness: `docker exec mysql_db mysqladmin ping -h localhost -uadmin -proot --silent`
  - Grant permissions: `docker exec mysql_db mysql -uroot -proot -h localhost -e "GRANT ALL PRIVILEGES ON momo_sms_app.* TO 'admin'@'%'; FLUSH PRIVILEGES;"`
- **Virtual environment issues**: 
  - Make sure Python 3 is installed: `python3 --version`
  - Delete and recreate: `rm -rf venv && python3 -m venv venv`
- **Port conflicts**: Kill existing processes: `pkill -f "python main.py"`
- **Permission denied on database**: Ensure the grant command in Step 5 was executed successfully

### Common Verification Commands
```bash
# Check if database is running
docker ps | grep mysql_db

# Check if tables exist
docker exec mysql_db mysql -uadmin -proot -h localhost momo_sms_app -e "SHOW TABLES;"

# Check if data exists
docker exec mysql_db mysql -uadmin -proot -h localhost momo_sms_app -e "SELECT COUNT(*) FROM Transactions;"

# Test authentication in browser (should show login popup)
# Open: http://localhost:8000/transactions

# Test authentication without credentials (should return 401)
curl -i http://localhost:8000/transactions

# Test authentication with credentials (should return data)
curl -u admin:admin http://localhost:8000/transactions
```

### Clean Start (If everything fails)
```bash
# Stop and remove everything
docker-compose down -v
rm -rf venv .env

# Start fresh with either Option 1 or Option 2
```

