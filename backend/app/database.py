#Centralizes the ORM setup, including the base class
# and session management for database interactions.

from sqlalchemy.orm import declarative_base

# The base class which all ORM models will inherit from.
Base = declarative_base()