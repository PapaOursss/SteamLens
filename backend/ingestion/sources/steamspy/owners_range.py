from dataclasses import dataclass

RANGE_SEPARATOR = ".."
THOUSANDS_SEPARATOR = ","


@dataclass(frozen=True)
class OwnersRange:
    """Fourchette de propriétaires estimée par SteamSpy (« 1,000,000 .. 2,000,000 »)."""

    minimum: int
    maximum: int

    @classmethod
    def from_text(cls, text: str) -> "OwnersRange":
        parts = text.split(RANGE_SEPARATOR)
        if len(parts) != 2:
            raise ValueError(f"Fourchette de propriétaires illisible : {text!r}")
        minimum, maximum = (cls._parse_number(part) for part in parts)
        if minimum > maximum:
            raise ValueError(f"Fourchette de propriétaires inversée : {text!r}")
        return cls(minimum=minimum, maximum=maximum)

    @property
    def midpoint(self) -> int:
        return (self.minimum + self.maximum) // 2

    @staticmethod
    def _parse_number(part: str) -> int:
        return int(part.strip().replace(THOUSANDS_SEPARATOR, ""))
