from .database import engine, SQL_AVAILABLE, Base
from .models import Quiz

def init_db():
    if SQL_AVAILABLE and engine:
        Base.metadata.create_all(bind=engine)
