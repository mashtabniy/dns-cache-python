from dataclasses import dataclass
from time import time
from typing import Optional


@dataclass
class DNSRecord:
    domain: str
    record_type: str
    value: str
    ttl: int
    added_at: float
    source: str

    def is_expired(self, now: Optional[float] = None) -> bool:
        if now is None:
            now = time()
        return now >= self.added_at + self.ttl

    def to_csv_row(self) -> list[str]:
        return [
            self.domain,
            self.record_type,
            self.value,
            str(self.ttl),
            str(self.added_at),
            self.source,
        ]

    @staticmethod
    def from_csv_row(row: list[str]) -> "DNSRecord":
        if len(row) != 6:
            raise ValueError("Некорректная строка файла: ожидается 6 полей")
        domain, record_type, value, ttl, added_at, source = row
        return DNSRecord(
            domain=domain,
            record_type=record_type,
            value=value,
            ttl=int(ttl),
            added_at=float(added_at),
            source=source,
        )
