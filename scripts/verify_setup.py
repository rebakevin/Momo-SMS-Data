from api.db.repository import TransactionRepository

def verify():
    print("Verifying setup...")
    repo = TransactionRepository()
    
    # 1. Test Connection
    conn = repo.db.get_connection()
    if not conn:
        print("FAIL: Could not connect to database")
        return
    conn.close()
    print("PASS: Database Connected")
    
    # 2. Test Create
    data = {
        "transaction_id": 99999,
        "date": "2026-02-02T12:00:00",
        "readable_date": "02 Feb 2026 12:00:00 PM",
        "amount_rwf": 500,
        "balance_rwf": 1000,
        "type": "received",
        "sender": "TestSender",
        "from": "TestUser",
        "phone": "0788123456"
    }
    
    print("Testing Create...")
    success, error, created_data = repo.create_transaction(data)
    if not success:
        print(f"FAIL: Create failed - {error}")
        return
    print(f"PASS: Created transaction {created_data.get('id')}")
    
    t_pk = created_data.get('id')
    t_id = 99999
    
    # 3. Test Get by ID
    print("Testing Get by ID...")
    success, error, retrieved = repo.get_transaction_by_id(t_id)
    if not success:
        print(f"FAIL: Get failed - {error}")
        return
    
    if retrieved['amount_rwf'] != 500:
        print(f"FAIL: Retrieved amount mismatch. Expected 500, got {retrieved['amount_rwf']}")
        return
    print("PASS: Retrieved transaction")
    
    # 4. Test Update
    print("Testing Update...")
    update_data = {"amount_rwf": 600}
    success, error, updated = repo.update_transaction(t_id, update_data)
    if not success:
        print(f"FAIL: Update failed - {error}")
        return
        
    if updated['amount_rwf'] != 600:
        print(f"FAIL: Updated amount mismatch. Expected 600, got {updated['amount_rwf']}")
        print(updated)
        return
    print("PASS: Updated transaction")
    
    # 5. Test Delete
    print("Testing Delete...")
    success, error, deleted_id = repo.delete_transaction(t_id)
    if not success:
        print(f"FAIL: Delete failed - {error}")
        return
    print("PASS: Deleted transaction")
    
    # Verify deletion
    success, error, _ = repo.get_transaction_by_id(t_id)
    if success:
        print("FAIL: Transaction still exists after delete")
        return
    print("PASS: Verified deletion")
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    verify()
