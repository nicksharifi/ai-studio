from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column

from .base import Base

TABLE_NAME = "ai_tags"


class Tag(Base):
    __tablename__ = TABLE_NAME

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tag={self.name}>"


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    import session

    _sesssion = session.make()

    # new_tag = Tag(name="Motivational")
    # session.add(new_tag)
    # session.commit()
    tags = _sesssion.query(Tag).all()
    for tag in tags:
        print(str(tag))

    _sesssion.close()
