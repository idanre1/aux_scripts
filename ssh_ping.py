import datetime
import timeit
import subprocess
import statistics as stat

def _test():
    p.stdin.write(b"z")
    assert p.stdout.read(1) == b"z"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    args = parser.parse_args()

    p = subprocess.Popen(["ssh", args.url, "cat"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)

    t = timeit.Timer(_test).repeat(repeat=6, number=1)
    mean=datetime.timedelta(seconds=stat.mean(t[1:])).microseconds / 1000.0
    print(f'Latencies (mean={mean}ms): {t[1:]}')
