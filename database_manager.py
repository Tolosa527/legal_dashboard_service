import os
from typing import Optional
import psycopg
from pymongo import MongoClient
from pymongo.database import Database


class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None
    _mongo_client: Optional[MongoClient] = None
    _mongo_db: Optional[Database] = None
    _postgres_conn: Optional[psycopg.Connection] = None

    def __new__(cls):
        """Singleton pattern for database connections."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def connect_postgres(self, host: str = "localhost", port: int = 5432, 
                        database: str = "legal_dashboard", user: str = "postgres", 
                        password: str = "") -> psycopg.Connection:
        """Connect to PostgreSQL database"""
        if self._postgres_conn is None or self._postgres_conn.closed:
            connstring = f"host={host} port={port} dbname={database} user={user} password={password}"
            self._postgres_conn = psycopg.connect(connstring)
        return self._postgres_conn

    def connect_mongo(self, host: str = "localhost", port: int = 27017, 
                     database: str = "legal_dashboard", username: str = None, 
                     password: str = None, auth_database: str = "admin") -> Database:
        """Connect to MongoDB database with connection pooling."""
        if self._mongo_client is None:
            if username and password:
                # Connect with authentication using authSource and connection pooling
                self._mongo_client = MongoClient(
                    host, port, 
                    username=username, 
                    password=password,
                    authSource=auth_database,
                    maxPoolSize=20,  # Connection pool size
                    serverSelectionTimeoutMS=5000,  # Timeout for server selection
                    connectTimeoutMS=10000,  # Connection timeout
                    maxIdleTimeMS=45000,  # Max idle time for connections
                )
            else:
                # Connect without authentication
                self._mongo_client = MongoClient(
                    host, port,
                    maxPoolSize=20,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    maxIdleTimeMS=45000,
                )
        self._mongo_db = self._mongo_client[database]
        return self._mongo_db

    def close_postgres(self):
        """Close PostgreSQL connection"""
        if self._postgres_conn and not self._postgres_conn.closed:
            self._postgres_conn.close()
            self._postgres_conn = None

    def close_mongo(self):
        """Close MongoDB connection"""
        if self._mongo_client:
            self._mongo_client.close()
            self._mongo_client = None
            self._mongo_db = None

    def close_all(self):
        """Close all database connections"""
        self.close_postgres()
        self.close_mongo()

    @property
    def postgres(self) -> Optional[psycopg.Connection]:
        """Get PostgreSQL connection"""
        return self._postgres_conn

    @property
    def mongo(self) -> Optional[Database]:
        """Get MongoDB database"""
        return self._mongo_db

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
