from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent
db_path = ROOT_PATH / "agent" / "agents.db"
DATABASE_URL = f"sqlite:///{db_path.as_posix()}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
