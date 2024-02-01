import time
from multiprocessing import Pool, cpu_count

def factorize_sync(*numbers):
    results = []
    for number in numbers:
        factors = []
        for i in range(1, number + 1):
            if number % i == 0:
                factors.append(i)
        results.append(factors)
    return results

def factorize_parallel(*numbers):
    pool = Pool(processes=cpu_count())
    results = pool.map(factorize_single, numbers)
    pool.close()
    pool.join()
    return results

def factorize_single(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors

# Testowanie funkcji
if __name__ == "__main__":
    start_time_sync = time.time()
    a_sync, b_sync, c_sync, d_sync = factorize_sync(128, 255, 99999, 10651060)
    end_time_sync = time.time()
    time_sync = end_time_sync - start_time_sync

    start_time_parallel = time.time()
    a_parallel, b_parallel, c_parallel, d_parallel = factorize_parallel(128, 255, 99999, 10651060)
    end_time_parallel = time.time()
    time_parallel = end_time_parallel - start_time_parallel

    assert a_sync == a_parallel
    assert b_sync == b_parallel
    assert c_sync == c_parallel
    assert d_sync == d_parallel

    print("Wyniki testów są zgodne.")
    print(f"Czas wykonania synchronicznej wersji: {time_sync} sekund")
    print(f"Czas wykonania równoległej wersji: {time_parallel} sekund")
