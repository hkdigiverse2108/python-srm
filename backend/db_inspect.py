
from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = "postgresql://postgres:0412@localhost:5432/AI SETU"

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("Tables found in DB:")
for table_name in inspector.get_table_names():
    print(f"- {table_name}")
    for fk in inspector.get_foreign_keys(table_name):
        print(f"  FK: {fk['name']} -> {fk['referred_table']}.{fk['referred_columns']}")

