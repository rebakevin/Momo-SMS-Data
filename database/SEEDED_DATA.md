# Seeded Data Reference

This document shows what sample data is included in `data_seed.sql`.

## Transaction Categories (5 records)

| ID | Name | Description |
|----|------|-------------|
| 1 | Mobile Money Transfer | Person to person money transfer via mobile |
| 2 | Bill Payment | Utility and service bill payments |
| 3 | Airtime Purchase | Mobile airtime and data bundle purchases |
| 4 | Merchant Payment | Payments to registered merchants |
| 5 | Salary Payment | Salary and payroll disbursements |

## Users (7 records)

| ID | Name | Phone Number |
|----|------|--------------|
| 1 | Kevin Rebakure | 0788123630 |
| 2 | Jane Doe | 0789456123 |
| 3 | John Smith | 0787654321 |
| 4 | Alice Johnson | 0781111111 |
| 5 | Bob Wilson | 0782222222 |
| 6 | Sarah Williams | 0783333333 |
| 7 | David Brown | 0784444444 |

## Sample Transactions (7 records)

| ID | Date | Type | Amount | Balance | Contact | Category |
|----|------|------|--------|---------|---------|----------|
| 1 | 10 Mar 2026 09:15 AM | received | 50,000 | 50,000 | Kevin Rebakure | Mobile Transfer |
| 2 | 10 Mar 2026 02:30 PM | sent | 15,000 | 35,000 | Jane Doe | Mobile Transfer |
| 3 | 11 Mar 2026 10:00 AM | sent | 8,500 | 26,500 | EUCL | Bill Payment |
| 4 | 11 Mar 2026 04:45 PM | received | 120,000 | 146,500 | ABC Company | Salary Payment |
| 5 | 12 Mar 2026 08:20 AM | sent | 2,000 | 144,500 | Airtel Rwanda | Airtime Purchase |
| 6 | 12 Mar 2026 11:10 AM | sent | 5,500 | 139,000 | Simba Supermarket | Merchant Payment |
| 7 | 12 Mar 2026 03:30 PM | received | 10,000 | 149,000 | John Smith | Mobile Transfer |

## Transaction Story

The sample data tells a realistic mobile money story:

1. **Day 1 Morning (Mar 10)**: Start with receiving 50,000 RWF
2. **Day 1 Afternoon**: Send 15,000 RWF to Jane Doe
3. **Day 2 Morning (Mar 11)**: Pay 8,500 RWF electricity bill
4. **Day 2 Afternoon**: Receive 120,000 RWF salary
5. **Day 3 Morning (Mar 12)**: Buy 2,000 RWF airtime
6. **Day 3 Late Morning**: Pay 5,500 RWF at supermarket
7. **Day 3 Afternoon**: Receive 10,000 RWF from friend

**Final Balance: 149,000 RWF**

## System Logs (8 records)

The seed script also creates 8 system log entries documenting each transaction and the seeding process itself.

## How to Use This Data

After running the seed script, you can:

1. **Test GET endpoints** - View all seeded transactions
2. **Test filtering** - Filter by date, type, or amount
3. **Update transactions** - Modify amounts and see balance recalculation
4. **Delete transactions** - Remove specific transactions
5. **Create new transactions** - New balance starts from 149,000 RWF

## Re-seeding the Database

To reset and re-seed the database:

```bash
# Clear all data
docker exec mysql_db mysql -uadmin -proot momo_sms_app -e "DELETE FROM \`System Logs\`; DELETE FROM \`Transactions\`; DELETE FROM \`Users\`; DELETE FROM \`Transaction Categories\`;"

# Re-seed
docker exec -i mysql_db mysql -uadmin -proot momo_sms_app < database/data_seed.sql
```

## Testing API with Seeded Data

```bash
# Get all transactions (will show the 7 seeded transactions)
curl -u admin:admin http://localhost:8000/transactions

# Get specific transaction
curl -u admin:admin http://localhost:8000/transactions/1

# Create a new transaction (balance will start from 149,000)
curl -u admin:admin -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "M-Money",
    "amount": 5000,
    "direction": "sent",
    "contact_name": "Test User",
    "phone": "0781234567"
  }'
```
