from sqlalchemy import Integer, ForeignKey, ForeignKey, Table, Column

from .base import Base


# Cache dictionary to store created tables
created_tables = {}


def many_to_many_relation(left_table_name: str, right_table_name: str):
    table_key = f"{left_table_name}_{right_table_name}"
    # Check if the table has already been created
    if table_key in created_tables:
        # Return the existing table
        return created_tables[table_key]

    new_table = Table(
        f"{left_table_name}_{right_table_name}",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column(f"{left_table_name}_id", ForeignKey(f"{left_table_name}.id", ondelete="CASCADE"), nullable=False),
        Column(f"{right_table_name}_id", ForeignKey(f"{right_table_name}.id", ondelete="CASCADE"), nullable=False),
    )
    created_tables[table_key] = new_table
    return new_table
