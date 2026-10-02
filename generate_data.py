from dns_cache import DNSCache


def generate_records(filename: str, count: int) -> None:
    cache = DNSCache(initial_capacity=2_097_152)
    types = ["A", "AAAA", "CNAME", "MX", "TXT"]

    for i in range(count):
        domain = f"site{i}.example.com"
        record_type = types[i % len(types)]
        value = f"192.168.{(i // 256) % 256}.{i % 256}"
        ttl = 300 + (i % 3600)
        source = "generated"
        cache.add_record(domain, record_type, value, ttl, source)

    cache.save_to_file(filename)


if __name__ == "__main__":
    generate_records("dns_records_1000000.csv", 1_000_000)
    print("Файл dns_records_1000000.csv создан.")
