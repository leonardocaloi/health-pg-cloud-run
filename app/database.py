import os
from model import Base
import sqlalchemy
from sqlalchemy.orm import sessionmaker

class Database:

    def __init__(self):
        self.engine = self.connect_unix_socket()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @staticmethod
    def connect_unix_socket():
        db_user = os.environ["DB_USER"]
        db_name = os.environ["DB_NAME"]
        unix_socket_path = os.environ["DB_INSTANCE_UNIX_SOCKET"]
        engine = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="postgresql+pg8000",
                username=db_user,
                database=db_name,
                query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"}),
            pool_recycle=3600)
        return engine

    def health_check(self):
        with self.engine.connect() as connection:
            result = connection.execute(sqlalchemy.sql.text("SELECT 1"))
            data = result.fetchone()
            if data != (1,):
                raise Exception("Failed to connect to the database")

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)