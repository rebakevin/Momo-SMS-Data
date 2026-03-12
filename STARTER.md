# MoMo SMS Data - Getting Started Guide

This guide will help you set up and run the MoMo SMS Data API application from scratch.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+** (Python 3.12 recommended)
- **Docker** (for MySQL database)
- **Docker Compose** (usually comes with Docker Desktop)
- **Git** (for cloning the repository)
- **curl** or **Postman** (for testing API endpoints)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/rebakevin/Momo-SMS-Data.git
cd Momo-SMS-Data
```

### 2. Set Up the Database (Docker)

The application uses a MySQL database running in a Docker container. The database configuration is defined in `docker-compose.yml`:

**Default Database Configuration:**
- **Host:** localhost
- **Port:** 3307 (mapped from container's 3306)
- **Database Name:** momo_sms_app
- **Username:** admin
- **Password:** root

#### Start the MySQL Database Container

```bash
docker compose up -d
```

This will:
- Download the MySQL 8.0 image (if not already available)
- Create a container named `mysql_db`
- Start the database on port 3307
- Create a persistent volume for data storage

#### Verify Database is Running

```bash
docker ps | grep mysql_db
```

You should see the `mysql_db` container in the list with status "Up".

### 3. Set Up Python Virtual Environment

Create and activate a virtual environment to isolate project dependencies:

#### On Linux/Mac:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### On Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**Note:** Your terminal prompt should change to show `(venv)` when the virtual environment is active.

### 4. Install Dependencies

With the virtual environment activated, install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `mysql-connector-python` - Database connectivity
- `pydantic` - Data validation
- `requests` - HTTP library
- `python-dotenv` - Environment variable management
- `apispec` - OpenAPI specification generation
- And other dependencies

### 5. Initialize the Database Schema

Run the database setup script to create all necessary tables:

```bash
docker exec -i mysql_db mysql -uadmin -proot momo_sms_app < database/database_setup.sql
```

This creates:
- `Transaction Categories` table
- `Users` table
- `Transactions` table
- `System Logs` table

#### Verify Tables Were Created

```bash
docker exec mysql_db mysql -uadmin -proot -e "USE momo_sms_app; SHOW TABLES;"
```

### 6. Seed Sample Data (Optional)

To populate the database with sample transactions for testing:

```bash
docker exec -i mysql_db mysql -uadmin -proot momo_sms_app < database/data_seed.sql
```

This adds:
- 5 transaction categories
- 7 sample users
- 7 sample transactions with realistic data
- System log entries

### 7. Run the Application

Start the API server:

```bash
python main.py
```

You should see output similar to:
```
Starting server on port 8000...
API Documentation: http://localhost:8000/api-docs
OpenAPI Spec: http://localhost:8000/openapi.json
Press Ctrl+C to stop the server
```

**The application is now running!** 🎉

## 🧪 Testing the Application

### Access API Documentation

Open your browser and navigate to:
- **Swagger UI:** http://localhost:8000/api-docs
- **OpenAPI Spec:** http://localhost:8000/openapi.json

### Test with curl

All API endpoints require **Basic Authentication**:
- **Username:** `admin`
- **Password:** `admin`

#### 1. Test Authentication

```bash
curl -u admin:admin http://localhost:8000/
```

Expected response:
```json
{"message": "Authentication successful"}
```

#### 2. Get All Transactions

```bash
curl -u admin:admin http://localhost:8000/transactions | python3 -m json.tool
```

#### 3. Get Transaction by ID

```bash
curl -u admin:admin http://localhost:8000/transactions/1 | python3 -m json.tool
```

#### 4. Create New Transaction

```bash
curl -u admin:admin -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "M-Money",
    "amount": 10000,
    "direction": "received",
    "contact_name": "Kevin Rebakure",
    "phone": "0788123630"
  }' | python3 -m json.tool
```

#### 5. Update Transaction

```bash
curl -u admin:admin -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "Updated Sender",
    "amount": 15000
  }' | python3 -m json.tool
```

#### 6. Delete Transaction

```bash
curl -u admin:admin -X DELETE http://localhost:8000/transactions/1 | python3 -m json.tool
```

## ⚙️ Environment Variables (Optional)

You can customize database settings using a `.env` file in the project root:

Create `.env`:
```bash
DB_HOST=localhost
DB_NAME=momo_sms_app
DB_USER=admin
DB_PASSWORD=root
DB_PORT=3307
```

The application will automatically load these values if the file exists.

## 📝 API Request Format

When creating or updating transactions, use this JSON format:

```json
{
  "sender": "string",           // Required: M-Money, MTN, Airtel, etc.
  "amount": number,              // Required: Positive number
  "direction": "sent|received",  // Required: Either "sent" or "received"
  "contact_name": "string",      // Required: Contact name
  "phone": "string"              // Required: Phone number (will be masked)
}
```

**Note:** The API automatically:
- Calculates running balance
- Masks phone numbers for privacy
- Generates timestamps
- Creates human-readable dates

## 🛑 Stopping the Application

### Stop the API Server
Press `Ctrl+C` in the terminal where the server is running.

### Deactivate Virtual Environment
```bash
deactivate
```

### Stop the Database Container
```bash
docker compose down
```

To completely remove the database and all data:
```bash
docker compose down -v
```

## 🐛 Troubleshooting

### Issue: Port 3307 Already in Use

**Solution:** Change the port in `docker-compose.yml`:
```yaml
ports:
  - "3308:3306"  # Change 3307 to 3308 or any available port
```

Also update the port in `.env` file or use default.

### Issue: Database Connection Failed

**Check if MySQL container is running:**
```bash
docker ps | grep mysql_db
```

**Check container logs:**
```bash
docker logs mysql_db
```

**Wait for database to be healthy:**
```bash
docker exec mysql_db mysqladmin ping -h localhost -uadmin -proot
```

### Issue: Permission Denied on venv

**On Linux/Mac:**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

### Issue: Module Not Found Error

**Ensure virtual environment is activated:**
```bash
# Look for (venv) in your terminal prompt
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "python" Command Not Found

**Use python3 instead:**
```bash
python3 main.py
```

Or create an alias:
```bash
alias python=python3
```

## 📁 Project Structure

```
Momo-SMS-Data/
├── api/                    # API logic
│   ├── controller.py       # Request handler
│   ├── routes.py           # Route definitions
│   ├── service.py          # Business logic
│   ├── auth.py             # Authentication
│   └── db/                 # Database layer
│       ├── db.py           # Database connection
│       ├── models.py       # Pydantic models
│       └── repository.py   # Database queries
├── database/               # Database scripts
│   ├── database_setup.sql  # Schema creation
│   └── data_seed.sql       # Sample data
├── docs/                   # Documentation
│   └── api_docs.md         # API documentation
├── openapi/                # OpenAPI/Swagger
│   ├── docs.py             # Swagger UI
│   └── openapi_generator.py
├── docker-compose.yml      # Docker configuration
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── README.md               # Project overview
```

## 🔒 Security Notes

- **Default credentials are for development only**
- Change the database password in production
- The API uses Basic Authentication (not recommended for production)
- Phone numbers are automatically masked (e.g., *******630)
- Consider implementing JWT tokens for production use

## 📚 Additional Resources

- **API Documentation:** See `docs/api_docs.md` for endpoint details
- **Database Design:** Check `docs/Database_Design_Document_Cohort1_Team2.pdf`
- **Project Report:** Read `docs/Building-and-Securing-a-REST_API_Group3-Cohort1_Report.pdf`

## 💡 Tips

1. **Keep the virtual environment activated** while developing
2. **Use docker compose logs -f mysql_db** to monitor database logs
3. **Create a .gitignore** to avoid committing `venv/` and `.env`
4. **Use Postman or Thunder Client** for easier API testing
5. **Check docker disk usage** periodically: `docker system df`

## 🆘 Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review error messages in the terminal
3. Check Docker logs: `docker logs mysql_db`
4. Verify all prerequisites are installed
5. Ensure ports 8000 and 3307 are available

---

**Happy Coding!** 🚀

For more information, visit the [GitHub Repository](https://github.com/rebakevin/Momo-SMS-Data)
