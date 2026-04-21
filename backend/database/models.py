from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "smartpack.db")
DB_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()

class Box(Base):
    __tablename__ = "boxes"
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅ INTEGER ID
    box_type = Column(String)
    efficiency = Column(Float)
    co2_saved = Column(Float)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    items = relationship("Item", back_populates="box", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    weight = Column(Float)
    fragile = Column(Boolean)
    box_id = Column(Integer, ForeignKey("boxes.id"))
    box = relationship("Box", back_populates="items")

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully.")
