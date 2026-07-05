from app.database import Base, engine
from app import models

print("Creating Database...")

Base.metadata.create_all(bind=engine)

print("Database Created Successfully!")
print(engine.url)