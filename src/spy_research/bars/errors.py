"""Exception hierarchy for processed five-minute storage."""


class ProcessedDataError(Exception):
    """Base class for expected processed-data failures."""


class ProcessedDataScopeError(ProcessedDataError):
    """A request falls outside the frozen SPY/RTH/5Min scope."""


class ProcessedDataConflictError(ProcessedDataError):
    """An immutable processed identity has different content."""

    def __init__(self, conflict_count: int) -> None:
        self.conflict_count = conflict_count
        super().__init__(
            f"Detected {conflict_count} conflicting processed bar record(s); "
            "existing data was not overwritten"
        )


class ProcessedDataCorruptionError(ProcessedDataError):
    """A processed Parquet partition cannot be read or validated."""


class ProcessedDataWriteError(ProcessedDataError):
    """An atomic processed Parquet write could not complete."""
