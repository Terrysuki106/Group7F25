from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config import Config

class Database:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.engine = create_engine(cfg.db_url, echo=True, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def init_db(self):
        if self.cfg.reset_mode:
            print("RESET_MODE ON → flushing database...")
            Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
        else:
            print("RESET_MODE OFF → connecting to existing database...")
            Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.SessionLocal()
