from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///review.db"

engine = create_engine(DATABASE_URL,echo=True)

def create_tables():
    """Create all tables defined my SQLModel Class"""
    SQLModel.metadata.create_all(engine)
    
    
def get_session():
    """Dependency that provides a database session per request"""
    with Session(engine) as session:
        yield session    