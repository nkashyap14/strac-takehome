from abc import ABC, abstractmethod
from typing import List, Optional, Any
from pathlib import Path


class Config(ABC):
    """Interface for configurations"""

    @property
    @abstractmethod
    def credentials_data(self) -> dict:
        """Return credentials in dictionary format"""
        pass

    @property
    @abstractmethod
    def auth_scopes(self) -> List[str]:
        """Get authorization scopes"""
        pass

class CloudConfig(Config):
    """Subinterface of config that adds features for future cloud based configurations. In the future 
    to ensure that in the future if design decisions are made to add a more secure mechanism to retrieve a secret from a cloud provider
    that rather than having to modify existing code one could simply implement this subinterface of config"""


    @abstractmethod
    def fetch_secret(self, secret_name: str) -> str:
        """Returns a secret from the cloud provider"""
        pass

    @abstractmethod
    def store_secret(self, secret_name: str, secret_val: str) -> bool:
        """Store a secret in the cloud provider"""
        pass

class AuthProvider(ABC):
    """Base interface for authentication providers. Alternative authentication methods that could be implemented in the future could be 
    jwt, simple api key based authentication, service account json files, federated identities like openid connect, mfa"""

    @abstractmethod
    def get_credentials(self) -> Any:
        """Get valid credentials and return them"""
        pass

    @abstractmethod
    def refresh_credentials(self) -> bool:
        """Refreshes expired credentials"""
        pass