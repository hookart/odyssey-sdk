class OdysseyAPIError(Exception):
    """Base exception for Odyssey API errors"""


class PrivateKeyError(OdysseyAPIError):
    """Raised when a private key is required but not provided, or is invalid"""


class APIKeyError(OdysseyAPIError):
    """Raised when an API key is required but not provided, or is invalid"""
