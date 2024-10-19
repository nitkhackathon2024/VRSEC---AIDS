from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Initialize the base class for the models
Base = declarative_base()

# Define the User model
class User(Base)
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    skills = Column(String, nullable=False)
    strengths = Column(String, nullable=False)
    areas_for_improvement = Column(String, nullable=False)

# Create an SQLite database and connect to it
engine = create_engine('sqliteusers.db', echo=True)

# Create the session
Session = sessionmaker(bind=engine)
session = Session()

# Create the tables in the database
Base.metadata.create_all(engine)

print(Database setup completed!)
