"""Application version lookup backed by installed package metadata."""

from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    """Return the installed package version or a source-tree fallback."""

    try:
        return version("spy-research")
    except PackageNotFoundError:
        return "0+unknown"
