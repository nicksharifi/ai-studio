from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column

from .base import Base


TABLE_NAME = "ai_languages"


class Language(Base):
    __tablename__ = TABLE_NAME

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"<Language={self.name}>"


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    import session

    _sesssion = session.make()

    # session.add(Language(name="Spanish"))
    # session.commit()
    languages = _sesssion.query(Language).all()
    for language in languages:
        print(language.id, language.name)

    _sesssion.close()
