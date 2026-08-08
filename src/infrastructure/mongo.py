from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


DATABASE_HOST: str = "mongodb://rag_project:rag@127.0.0.1:27017/rag_database?authSource=admin"
class MongoDatabaseConnector:
    _instance: MongoClient | None = None

    def __new__(cls, *args, **kwargs) -> MongoClient:
        if cls._instance is None:
            try:
                cls._instance = MongoClient(DATABASE_HOST)
            except ConnectionFailure as e:
                logger.error(f"Couldn't connect to the database: {e!s}")

                raise

        logger.info(f"Connection to MongoDB with URI successful: {DATABASE_HOST}")

        return cls._instance


connection = MongoDatabaseConnector()
