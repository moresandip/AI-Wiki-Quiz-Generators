from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import TypeDecorator
import json
import os

class JSONEncodedDict(TypeDecorator):
    impl = Text
    def process_bind_param(self, value, dialect):
        if value is None: return None
        return json.dumps(value)
    def process_result_value(self, value, dialect):
        if value is None: return None
        return json.loads(value)

db_path = "test_json.db"
if os.path.exists(db_path):
    os.remove(db_path)

engine = create_engine(f"sqlite:///{db_path}")
Base = declarative_base()

class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(Integer, primary_key=True)
    data = Column(JSONEncodedDict)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Test Insert
    item = TestModel(data={"key": "value"})
    session.add(item)
    session.commit()
    print("Insert successful")

    # Test Select
    item = session.query(TestModel).first()
    print(f"Select: {item.data} (Type: {type(item.data)})")

    # Test Update
    item.data = {"key": "new_value"}
    session.commit()
    print("Update successful")

except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
    if os.path.exists(db_path):
        os.remove(db_path)
