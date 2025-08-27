"""
Application settings module.
Manages environment variables and configuration settings.
"""

import os
from typing import Optional


class Settings:
    """Application settings class for managing environment variables."""

    # PostgreSQL settings
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "legal_dashboard")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres123")

    # MongoDB settings - connection string approach
    MONGO_CONNECTION_STRING: str = os.getenv(
        "MONGO_CONNECTION_STRING",
        "mongodb://admin:adminpassword@localhost:27017/legal_dashboard?authSource=admin",
    )
    MONGO_DATABASE: str = os.getenv("MONGO_DB", "legal_dashboard")

    @classmethod
    def get_postgres_connection_string(cls) -> str:
        """Build PostgreSQL connection string."""
        return f"host={cls.POSTGRES_HOST} port={cls.POSTGRES_PORT} dbname={cls.POSTGRES_DB} user={cls.POSTGRES_USER} password={cls.POSTGRES_PASSWORD}"

    @classmethod
    def get_mongo_connection_string(cls) -> str:
        """Get MongoDB connection string based on environment."""
        env = os.getenv("ENV", "development")
        if env == "production":
            return cls.MONGO_CONNECTION_STRING
        # Construct connection string for development
        user = os.getenv("MONGO_USER", "admin")
        password = os.getenv("MONGO_PASSWORD", "adminpassword")
        host = os.getenv("MONGO_HOST", "localhost")
        port = os.getenv("MONGO_PORT", "27017")
        db = os.getenv("MONGO_DB", "legal_dashboard")
        auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")
        return (
            f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource={auth_source}"
        )

    @classmethod
    def get_mongo_database(cls) -> str:
        """Get MongoDB database name."""
        return cls.MONGO_DATABASE


# Create a singleton instance
settings = Settings()
