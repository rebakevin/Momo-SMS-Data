import random
import time


def generate_transactions(num_records):
    transactions = []
    for i in range(num_records):
        txn_id = f"TXN{i:05d}"
        amount = round(random.uniform(10.0, 1000.0), 2)
        transactions.append({"id": txn_id, "amount": amount, "index": i})
    return transactions

def linear_search(transactions, target_id):
    for txn in transactions:
        if txn["id"] == target_id:
            return txn
    return None

def dictionary_lookup(txn_dict, target_id):
    return txn_dict.get(target_id)

def run_comparison():
    # 1. Setup Data
    num_records = 100000 
    print(f"Generating {num_records} records...")
    transactions = generate_transactions(num_records)
    
    # Create Dictionary
    print("Building dictionary...")
    start_setup = time.perf_counter()
    txn_dict = {txn["id"]: txn for txn in transactions}
    end_setup = time.perf_counter()
    print(f"Dictionary build time: {end_setup - start_setup:.6f} seconds")

    search_targets = [transactions[random.randint(0, num_records-1)]["id"] for _ in range(100)]
    
    # 2. Benchmark Linear Search
    print("\n--- Benchmarking Linear Search ---")
    start_linear = time.perf_counter()
    for target_id in search_targets:
        linear_search(transactions, target_id)
    end_linear = time.perf_counter()
    total_linear_time = end_linear - start_linear
    avg_linear_time = total_linear_time / len(search_targets)
    print(f"Total time for {len(search_targets)} searches: {total_linear_time:.6f} seconds")
    print(f"Average time per search: {avg_linear_time:.8f} seconds")

    # 3. Benchmark Dictionary Lookup
    print("\n--- Benchmarking Dictionary Lookup ---")
    start_dict = time.perf_counter()
    for target_id in search_targets:
        dictionary_lookup(txn_dict, target_id)
    end_dict = time.perf_counter()
    total_dict_time = end_dict - start_dict
    avg_dict_time = total_dict_time / len(search_targets)
    print(f"Total time for {len(search_targets)} searches: {total_dict_time:.6f} seconds")
    print(f"Average time per search: {avg_dict_time:.8f} seconds")

    # 4. Comparison
    if avg_dict_time > 0:
        speedup = avg_linear_time / avg_dict_time
        print(f"\nDictionary lookup was approximately {speedup:.2f}x faster than linear search.")
    else:
        print("\nDictionary lookup was too fast to measure accurately compared to linear search.")

if __name__ == "__main__":
    run_comparison()