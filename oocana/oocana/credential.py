from dataclasses import dataclass

__all__ = ["CredentialInput"]


@dataclass(frozen=True)
class CredentialInput:
    """
    Represents a credential input for authentication queries.

    Attributes:
        type: The type of credential (e.g., 'oauth', 'api_key')
        id: The unique identifier for the credential
    """
    type: str
    id: str
