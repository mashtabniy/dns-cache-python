import os
import tempfile
import unittest
from time import time

from dns_cache import DNSCache


class TestDNSCache(unittest.TestCase):
    def test_add_and_find_record(self):
        cache = DNSCache()
        cache.add_record("Example.COM", "a", "93.184.216.34", 300, "resolver")

        record = cache.find_record("example.com", "A")

        self.assertIsNotNone(record)
        self.assertEqual(record.domain, "example.com")
        self.assertEqual(record.record_type, "A")
        self.assertEqual(record.value, "93.184.216.34")
        self.assertEqual(record.ttl, 300)
        self.assertEqual(record.source, "resolver")

    def test_add_replaces_existing_record(self):
        cache = DNSCache()
        first_insert = cache.add_record("example.com", "A", "1.1.1.1", 100, "s1")
        second_insert = cache.add_record("example.com", "A", "2.2.2.2", 200, "s2")

        record = cache.find_record("example.com", "A")

        self.assertTrue(first_insert)
        self.assertFalse(second_insert)
        self.assertEqual(cache.size, 1)
        self.assertEqual(record.value, "2.2.2.2")
        self.assertEqual(record.ttl, 200)

    def test_delete_record(self):
        cache = DNSCache()
        cache.add_record("example.com", "A", "1.1.1.1", 100, "s1")

        self.assertTrue(cache.delete_record("example.com", "A"))
        self.assertFalse(cache.delete_record("example.com", "A"))
        self.assertIsNone(cache.find_record("example.com", "A"))
        self.assertEqual(cache.size, 0)

    def test_update_ttl(self):
        cache = DNSCache()
        cache.add_record("example.com", "A", "1.1.1.1", 100, "s1")

        self.assertTrue(cache.update_ttl("example.com", "A", 500))
        self.assertEqual(cache.find_record("example.com", "A").ttl, 500)
        self.assertFalse(cache.update_ttl("missing.com", "A", 500))

    def test_update_ttl_invalid_value(self):
        cache = DNSCache()
        cache.add_record("example.com", "A", "1.1.1.1", 100, "s1")

        with self.assertRaises(ValueError):
            cache.update_ttl("example.com", "A", 0)

    def test_find_expired_record_deletes_it(self):
        cache = DNSCache()
        cache.add_record("old.com", "A", "1.1.1.1", 10, "s1", added_at=1000)

        self.assertIsNone(cache.find_record("old.com", "A"))
        self.assertEqual(cache.size, 0)

    def test_remove_expired_records(self):
        cache = DNSCache()
        cache.add_record("old.com", "A", "1.1.1.1", 10, "s1", added_at=1000)
        cache.add_record("fresh.com", "A", "2.2.2.2", 10000, "s1", added_at=time())

        removed = cache.remove_expired(now=1011)

        self.assertEqual(removed, 1)
        self.assertIsNone(cache.find_record("old.com", "A"))
        self.assertIsNotNone(cache.find_record("fresh.com", "A"))

    def test_count_by_type(self):
        cache = DNSCache()
        cache.add_record("a.com", "A", "1.1.1.1", 100, "s")
        cache.add_record("b.com", "A", "2.2.2.2", 100, "s")
        cache.add_record("c.com", "MX", "mail.c.com", 100, "s")

        self.assertEqual(cache.count_by_type(), [("A", 2), ("MX", 1)])

        cache.delete_record("a.com", "A")
        self.assertEqual(cache.count_by_type(), [("A", 1), ("MX", 1)])

    def test_save_and_load(self):
        cache = DNSCache()
        cache.add_record("example.com", "A", "93.184.216.34", 300, "resolver")
        cache.add_record("mail.com", "MX", "mail.mail.com", 600, "resolver")

        with tempfile.NamedTemporaryFile(delete=False) as temp:
            filename = temp.name

        try:
            cache.save_to_file(filename)

            loaded = DNSCache()
            loaded.load_from_file(filename)

            self.assertEqual(loaded.size, 2)
            self.assertEqual(loaded.find_record("example.com", "A").value, "93.184.216.34")
            self.assertEqual(loaded.find_record("mail.com", "MX").value, "mail.mail.com")
            self.assertEqual(loaded.count_by_type(), [("A", 1), ("MX", 1)])
        finally:
            os.remove(filename)

    def test_invalid_add_arguments(self):
        cache = DNSCache()

        with self.assertRaises(ValueError):
            cache.add_record("", "A", "1.1.1.1", 100, "s")

        with self.assertRaises(ValueError):
            cache.add_record("example.com", "", "1.1.1.1", 100, "s")

        with self.assertRaises(ValueError):
            cache.add_record("example.com", "A", "", 100, "s")

        with self.assertRaises(ValueError):
            cache.add_record("example.com", "A", "1.1.1.1", 0, "s")

        with self.assertRaises(ValueError):
            cache.add_record("example.com", "A", "1.1.1.1", 100, "")

    def test_hash_table_resizes_and_keeps_records(self):
        cache = DNSCache(initial_capacity=4)

        for i in range(100):
            cache.add_record(f"site{i}.com", "A", f"10.0.0.{i}", 1000, "generator")

        self.assertEqual(cache.size, 100)
        for i in range(100):
            record = cache.find_record(f"site{i}.com", "A")
            self.assertIsNotNone(record)
            self.assertEqual(record.value, f"10.0.0.{i}")


if __name__ == "__main__":
    unittest.main()
