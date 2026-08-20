"""Safe exception hierarchy for Alpaca historical market-data access."""


class AlpacaDataError(Exception):
    """Base class for expected Alpaca data-client failures."""


class AlpacaCredentialsError(AlpacaDataError):
    """Raised when required credentials are not configured."""


class AlpacaAuthenticationError(AlpacaDataError):
    """Raised when Alpaca rejects credentials or data entitlement."""


class AlpacaRateLimitError(AlpacaDataError):
    """Raised when rate-limit retries are exhausted."""


class AlpacaRequestError(AlpacaDataError):
    """Raised for transport failures or rejected permanent requests."""


class AlpacaResponseError(AlpacaDataError):
    """Raised when a successful response is malformed or inconsistent."""


class AlpacaPaginationError(AlpacaResponseError):
    """Raised when pagination cannot continue safely."""


class DuplicateBarError(AlpacaResponseError):
    """Raised when more than one bar has the same timestamp."""
