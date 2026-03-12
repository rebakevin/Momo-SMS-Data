#!/bin/bash
set -e

docker compose up -d >/dev/null 2>&1

sleep 5
until docker exec mysql_db mysqladmin ping -h localhost -uadmin -proot --silent 2>/dev/null; do
    sleep 2
done

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q >/dev/null 2>&1

if ! docker exec mysql_db mysql -uadmin -proot momo_sms_app -e "SHOW TABLES;" 2>/dev/null | grep -q "Transactions"; then
    docker exec -i mysql_db mysql -uadmin -proot momo_sms_app < database/database_setup.sql 2>/dev/null
fi

TRANSACTION_COUNT=$(docker exec mysql_db mysql -uadmin -proot momo_sms_app -e "SELECT COUNT(*) FROM Transactions;" 2>/dev/null | tail -1)
if [ "$TRANSACTION_COUNT" -eq 0 ]; then
    docker exec -i mysql_db mysql -uadmin -proot momo_sms_app < database/data_seed.sql >/dev/null 2>&1
fi

echo "✓ Setup complete"
echo ""
echo "Server: http://localhost:8000"
echo "API Docs: http://localhost:8000/api-docs"
echo "Auth: admin/admin"
echo ""

python main.py