#!/bin/bash

echo "Starting MoMo SMS Data setup..."

# Check if script is being run with proper permissions
if [ ! -x "$0" ]; then
    echo "ERROR: Script is not executable. Run: chmod +x startup.sh"
    exit 1
fi

# Check Docker command availability
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_CMD="docker-compose"
    echo "Found docker-compose command"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_CMD="docker compose"
    echo "Found docker compose command"
else
    echo "ERROR: Neither docker-compose nor docker compose found. Please install Docker Compose."
    exit 1
fi

# Create .env if missing
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "DB_HOST=localhost
DB_NAME=momo_sms_app
DB_USER=admin
DB_PASSWORD=root
DB_PORT=3307" > .env
fi

echo "Starting Docker containers..."
if ! $DOCKER_CMD up -d >/dev/null 2>&1; then
    echo "ERROR: Failed to start Docker containers"
    exit 1
fi

echo "Waiting for database to be ready..."
sleep 5
until docker exec mysql_db mysqladmin ping -h localhost -uadmin -proot --silent 2>/dev/null; do
    echo "Still waiting for database..."
    sleep 2
done
echo "Database is ready!"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt -q >/dev/null 2>&1

echo "Setting up database schema..."
# Ensure admin user has proper permissions
docker exec mysql_db mysql -uroot -proot -h localhost -e "GRANT ALL PRIVILEGES ON momo_sms_app.* TO 'admin'@'%'; FLUSH PRIVILEGES;" >/dev/null 2>&1

if ! docker exec mysql_db mysql -uadmin -proot -h localhost momo_sms_app -e "SHOW TABLES;" 2>/dev/null | grep -q "Transactions"; then
    echo "Creating database tables..."
    # Run the database setup - only redirect stdout to suppress warnings
    docker exec -i mysql_db mysql -uadmin -proot -h localhost momo_sms_app < database/database_setup.sql >/dev/null
    SETUP_EXIT_CODE=$?
    if [ $SETUP_EXIT_CODE -ne 0 ]; then
        echo "ERROR: Failed to create database tables (exit code: $SETUP_EXIT_CODE)"
        exit 1
    fi
fi

TRANSACTION_COUNT=$(docker exec mysql_db mysql -uadmin -proot -h localhost momo_sms_app -e "SELECT COUNT(*) FROM Transactions;" 2>/dev/null | tail -1)
if [ "$TRANSACTION_COUNT" -eq 0 ]; then
    echo "Seeding sample data..."
    docker exec -i mysql_db mysql -uadmin -proot -h localhost momo_sms_app < database/data_seed.sql >/dev/null 2>&1
    echo "Sample data loaded!"
else
    echo "Database already has data"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Server: http://localhost:8000"
echo "API Docs: http://localhost:8000/api-docs"
echo "Auth: admin/admin"
echo ""

python main.py