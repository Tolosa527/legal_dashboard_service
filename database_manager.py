import os
from typing import Optional
import psycopg
from pymongo import MongoClient
from pymongo.database import Database


class DatabaseManager:
    def __init__(self):
        self._postgres_conn: Optional[psycopg.Connection] = None
        self._mongo_client: Optional[MongoClient] = None
        self._mongo_db: Optional[Database] = None

    def connect_postgres(self, host: str = "localhost", port: int = 5432, 
                        database: str = "legal_dashboard", user: str = "postgres", 
                        password: str = "") -> psycopg.Connection:
        """Connect to PostgreSQL database"""
        if self._postgres_conn is None or self._postgres_conn.closed:
            connstring = f"host={host} port={port} dbname={database} user={user} password={password}"
            self._postgres_conn = psycopg.connect(connstring)
        return self._postgres_conn

    def connect_mongo(self, host: str = "localhost", port: int = 27017, 
                     database: str = "legal_dashboard") -> Database:
        """Connect to MongoDB database"""
        if self._mongo_client is None:
            self._mongo_client = MongoClient(host, port)
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
