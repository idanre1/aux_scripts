def timeit(f, *args, **kwargs):
    import time
    from datetime import timedelta
    start = time.time()
    result=f(*args, **kwargs)
    end = time.time()
    print(timedelta(seconds=(end-start)))
    return result