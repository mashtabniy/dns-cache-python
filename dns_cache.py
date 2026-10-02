from __future__ import annotations
import csv
from time import time
from typing import Optional
from dns_record import DNSRecord
from hash_table import HashTable
from type_counter import TypeCounter


class DNSCache:
    def __init__(self, initial_capacity: int = 1024):
        self._table = HashTable(initial_capacity=initial_capacity)
        self._type_counter = TypeCounter()

    @property
    def size(self) -> int:
        return self._table.size

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        domain = domain.strip().lower()
        if not domain:
            raise ValueError("Доменное имя не может быть пустым")
        return domain

    @staticmethod
    def _normalize_type(record_type: str) -> str:
        record_type = record_type.strip().upper()
        if not record_type:
            raise ValueError("Тип записи не может быть пустым")
        return record_type

    @classmethod
    def _make_key(cls, domain: str, record_type: str) -> str:
        return cls._normalize_domain(domain) + "|" + cls._normalize_type(record_type)

    def add_record(
        self,
        domain: str,
        record_type: str,
        value: str,
        ttl: int,
        source: str,
        added_at: Optional[float] = None,
    ) -> bool:
        """
        Добавляет или заменяет DNS-запись.

        Возвращает:
        True — добавлена новая запись;
        False — существующая запись с таким domain + type заменена.
        """
        domain = self._normalize_domain(domain)
        record_type = self._normalize_type(record_type)
        value = value.strip()
        source = source.strip()

        if not value:
            raise ValueError("Значение записи не может быть пустым")
        if ttl <= 0:
            raise ValueError("TTL должен быть положительным")
        if not source:
            raise ValueError("Источник записи не может быть пустым")
        if added_at is None:
            added_at = time()

        key = self._make_key(domain, record_type)
        old_record = self._table.get(key)

        record = DNSRecord(
            domain=domain,
            record_type=record_type,
            value=value,
            ttl=ttl,
            added_at=added_at,
            source=source,
        )

        inserted = self._table.put(key, record)

        if old_record is None:
            self._type_counter.increment(record_type)
        elif old_record.record_type != record_type:
            self._type_counter.decrement(old_record.record_type)
            self._type_counter.increment(record_type)

        return inserted

    def find_record(self, domain: str, record_type: str) -> Optional[DNSRecord]:
        key = self._make_key(domain, record_type)
        record = self._table.get(key)

        if record is None:
            return None

        if record.is_expired():
            self.delete_record(domain, record_type)
            return None

        return record

    def delete_record(self, domain: str, record_type: str) -> bool:
        key = self._make_key(domain, record_type)
        removed = self._table.delete(key)

        if removed is None:
            return False

        self._type_counter.decrement(removed.record_type)
        return True

    def update_ttl(self, domain: str, record_type: str, new_ttl: int) -> bool:
        if new_ttl <= 0:
            raise ValueError("TTL должен быть положительным")

        key = self._make_key(domain, record_type)

        def updater(record: DNSRecord) -> None:
            record.ttl = new_ttl

        return self._table.update(key, updater)

    def remove_expired(self, now: Optional[float] = None) -> int:
        if now is None:
            now = time()

        removed = self._table.remove_if(lambda record: record.is_expired(now))

        for record in removed:
            self._type_counter.decrement(record.record_type)

        return len(removed)

    def count_by_type(self) -> list[tuple[str, int]]:
        return self._type_counter.items()

    def all_records(self) -> list[DNSRecord]:
        return list(self._table.records())

    def save_to_file(self, filename: str) -> None:
        with open(filename, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["domain", "record_type", "value", "ttl", "added_at", "source"])
            for record in self._table.records():
                writer.writerow(record.to_csv_row())

    def load_from_file(self, filename: str) -> None:
        self._table = HashTable(initial_capacity=1024)
        self._type_counter.clear()

        with open(filename, "r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)
            header = next(reader, None)

            expected_header = ["domain", "record_type", "value", "ttl", "added_at", "source"]
            if header != expected_header:
                raise ValueError("Некорректный заголовок CSV-файла")

            for row in reader:
                record = DNSRecord.from_csv_row(row)
                self.add_record(
                    domain=record.domain,
                    record_type=record.record_type,
                    value=record.value,
                    ttl=record.ttl,
                    added_at=record.added_at,
                    source=record.source,
                )
