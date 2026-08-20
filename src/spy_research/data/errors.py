"""Exception hierarchy for raw market-data persistence."""


class RawDataError(Exception):
    """Base class for expected raw-data storage failures."""


class RawDataScopeError(RawDataError):
    """Raised when a request falls outside the frozen Phase 1 scope."""


class RawDataConflictError(RawDataError):
    """Raised when an immutable bar key has different stored content."""

    def __init__(self, conflict_count: int) -> None:
        self.conflict_count = conflict_count
        super().__init__(
            f"Detected {conflict_count} conflicting raw bar record(s); "
            "existing data was not overwritten"
        )


class RawDataCorruptionError(RawDataError):
    """Raised when a Parquet partition cannot be read or validated."""


class RawDataWriteError(RawDataError):
    """Raised when an atomic Parquet write cannot be completed."""
