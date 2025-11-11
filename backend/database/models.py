"""
Database models for PartSelect Chat Agent
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    Table,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

Base = declarative_base()

# Association table for many-to-many relationship
part_model_compatibility = Table(
    "part_model_compatibility",
    Base.metadata,
    Column("part_id", Integer, ForeignKey("parts.id")),
    Column("model_id", Integer, ForeignKey("models.id")),
)


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True)
    part_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50))
    price = Column(Float, nullable=False)
    description = Column(Text)
    brand = Column(String(100))
    image_url = Column(String(500))
    installation_difficulty = Column(String(20))
    installation_steps = Column(JSON)
    common_symptoms = Column(JSON)

    # Relationships
    compatible_models = relationship(
        "Model", secondary=part_model_compatibility, back_populates="compatible_parts"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "part_number": self.part_number,
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "price": self.price,
            "description": self.description,
            "brand": self.brand,
            "image_url": self.image_url,
            "installation_difficulty": self.installation_difficulty,
            "installation_steps": self.installation_steps,
            "common_symptoms": self.common_symptoms,
        }


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    model_number = Column(String(50), unique=True, nullable=False)
    brand = Column(String(100))
    appliance_type = Column(String(50))

    # Relationships
    compatible_parts = relationship(
        "Part", secondary=part_model_compatibility, back_populates="compatible_models"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "model_number": self.model_number,
            "brand": self.brand,
            "appliance_type": self.appliance_type,
        }


# FIXED: Always use the database in the database directory
# Get the absolute path to the database directory
if __file__:
    # When imported as a module
    current_dir = os.path.dirname(os.path.abspath(__file__))
else:
    # Fallback
    current_dir = os.path.abspath("./database")

db_path = os.path.join(current_dir, "partselect.db")

# Create directory if it doesn't exist
os.makedirs(current_dir, exist_ok=True)

# Database setup
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully!")
    print(f"✓ Database location: {db_path}")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Print database location when imported (for debugging)
if not os.path.exists(db_path):
    print(f"⚠️  WARNING: Database not found at {db_path}")
    print(f"   Please run: cd {current_dir} && python seed_data.py")
