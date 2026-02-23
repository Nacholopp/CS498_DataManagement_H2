import time, uuid, statistics, requests

US = "http://34.68.248.167:8080"
EU = "http://34.78.178.238:8080"

def timed(method, url, **kwargs):
    t0 = time.perf_counter()
    r = requests.request(method, url, timeout=10, **kwargs)
    dt = (time.perf_counter() - t0) * 1000
    return r, dt

def avg_latency(base, endpoint, method="GET", n=10):
    times = []
    for i in range(n):
        if method == "POST":
            uname = f"lat_{endpoint.strip('/')}_{i}_{uuid.uuid4().hex[:6]}"
            r, dt = timed("POST", f"{base}{endpoint}", json={"username": uname})
        else:
            r, dt = timed("GET", f"{base}{endpoint}")
        r.raise_for_status()
        times.append(dt)
    return statistics.mean(times), times

def eventual_consistency_test(register_base, list_base, loops=100):
    misses = 0
    for _ in range(loops):
        uname = f"ec_{uuid.uuid4().hex}"

        # Register in one region
        r1, _ = timed("POST", f"{register_base}/register", json={"username": uname})
        r1.raise_for_status()

        # Immediately read from the other region
        r2, _ = timed("GET", f"{list_base}/list")
        r2.raise_for_status()

        users = r2.json().get("users", [])
        if uname not in users:
            misses += 1

    return misses

def main():
    # empezar limpio
    requests.post(f"{US}/clear", timeout=10)
    requests.post(f"{EU}/clear", timeout=10)

    # IV-A
    reg_us_avg, _ = avg_latency(US, "/register", "POST", 10)
    reg_eu_avg, _ = avg_latency(EU, "/register", "POST", 10)
    list_us_avg, _ = avg_latency(US, "/list", "GET", 10)
    list_eu_avg, _ = avg_latency(EU, "/list", "GET", 10)

    print("IV-A Latency (10 req each) [ms]")
    print(f"US /register avg: {reg_us_avg:.2f}")
    print(f"EU /register avg: {reg_eu_avg:.2f}")
    print(f"US /list avg:     {list_us_avg:.2f}")
    print(f"EU /list avg:     {list_eu_avg:.2f}")

    # IV-B
    misses = eventual_consistency_test(US, EU, 100)
    print("\nIV-B Eventual Consistency (100 iterations)")
    print(f"Misses (US register -> EU list immediately): {misses} / 100")

if __name__ == "__main__":
    main()
