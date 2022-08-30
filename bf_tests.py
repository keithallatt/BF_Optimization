import time

from bf_interpreter import run_bf, BFTokenizer
import numpy as np
from operator import mul, add
from tqdm import trange
import concurrent.futures
from multiprocessing.pool import ThreadPool

func = np.vectorize(mul)

b1, e1, s1 = 0, 255, 1
b2, e2, s2 = 0, 255, 1

d1 = len(list(range(b1, e1, s1)))
d2 = len(list(range(b2, e2, s2)))

Xs = np.zeros((d1 * d2, 1), dtype=int)
Xs = np.repeat(Xs, 2, 1)

Xs[:, 0] = b1 + np.repeat(np.arange(d1).reshape((d1, 1)), d2, axis=1).reshape((d1*d2,)) * s1
Xs[:, 1] = b2 + np.repeat(np.arange(d2).reshape((d2, 1)), d1, axis=1).T.reshape((d1*d2,)) * s2

Ts = func(Xs[:, 0], Xs[:, 1]) % 256  # this 256 is from using bytes
Ts = Ts.reshape((Ts.shape[0], 1))

results = {}
lowest_unfinished = 0


def test(bf_code, offset=0, every=100):
    bf_token = BFTokenizer()
    bf_token.parse_code(bf_code)
    bf_token.build_functions()

    w = np.where(np.arange(Xs.shape[0]) % every == offset % every)
    xs = Xs[w]
    ts = Ts[w]

    n, sx, st = xs.shape[0], xs.shape[1], ts.shape[1]
    global results

    with trange(n, desc=f"Thread {offset}", position=offset, leave=False) as tr:  # if lowest_unfinished == offset else range(n):
        for i in tr:
            tr.position = offset - len(results.keys())

            tape_contents = {k: xs[i, k] for k in range(sx)}
            expected_output = {0: ts[i, k] for k in range(st) if ts[i, k]}

            tape_output = run_bf(bf_code, tape_contents, pre_compiled=bf_token).tape_contents

            if expected_output != tape_output:
                retval = False
                break
        else:
            retval = True

    results[offset] = retval

    return retval


def brute_force_no_io(label, code, num_processes=32):
    """
    Find the BF code that emulates the behaviour described with inputs X and corresponding outputs t.
    """
    # valid_chars = "+-<>[]"  # no io

    messy_and_fast = True

    t1 = time.perf_counter()
    if messy_and_fast:
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
            future_to_test = {executor.submit(test, code, i, num_processes): i for i in range(num_processes)}
            for future in concurrent.futures.as_completed(future_to_test):
                test_ = future_to_test[future]
                try:
                    data = future.result()
                except Exception as exc:
                    results[test_] = str(exc)
                else:
                    results[test_] = str(data)

    else:
        pool = ThreadPool(num_processes)
        tasks = range(num_processes)

        def apply_test(bf, index, total):
            res = test(bf, index, total)
            results[index] = res

        for i, tst in enumerate(tasks, 1):
            pool.apply_async(apply_test, args=(code, i, num_processes))
        pool.close()
        pool.join()

    # print('===RESULTS===')
    # for key in sorted(results.keys()):
    #     print(str(key).rjust(4), results[key])
    # print('=============')

    t2 = time.perf_counter()

    if all(results.values()):
        # then it works.
        print(f"The code \n\"{code}\";\nSolves the problem of {label}.\nComputed in {t2-t1:.2f} "
              f"seconds on {num_processes} processes")


if __name__ == '__main__':
    brute_force_no_io("multiplication", "[>[>+>+<<-]>>[<<+>>-]<<<-]>[-]>[<<+>>-]", 8)
