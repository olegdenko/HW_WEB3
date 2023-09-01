import multiprocessing
import time


def factorize_number(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors


def factorize(*numbers):
    result = []
    for number in numbers:
        result.append(factorize_number(number))
    return result


if __name__ == '__main__':
    numbers = (128, 255, 99999, 10651060)

    # Synchron
    start_time = time.time()
    results = factorize(*numbers)
    end_time = time.time()
    print(f"Synchron calculation is done {end_time - start_time:.4f} sec.")

    assert results[0] == [1, 2, 4, 8, 16, 32, 64, 128]
    assert results[1] == [1, 3, 5, 15, 17, 51, 85, 255]
    assert results[2] == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333,
                          99999]
    assert results[3] == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079,
                          152158, 304316, 380395, 532553, 760790, 1065106,
                          1521580, 2130212, 2662765, 5325530, 10651060]

    # Multiprocesing
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    start_time = time.time()
    results = pool.map(factorize_number, numbers)
    end_time = time.time()
    print(f"Multi-process calculation is done {end_time - start_time:.4f} sec.")

    assert results[0] == [1, 2, 4, 8, 16, 32, 64, 128]
    assert results[1] == [1, 3, 5, 15, 17, 51, 85, 255]
    assert results[2] == [1, 3, 9, 41, 123, 271,
                          369, 813, 2439, 11111, 33333, 99999]
    assert results[3] == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079,
                          152158, 304316, 380395, 532553, 760790, 1065106,
                          1521580, 2130212, 2662765, 5325530, 10651060]
