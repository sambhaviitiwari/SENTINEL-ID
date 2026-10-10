from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./sentinel.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
def migrate_case_analysis_details():
    from sqlalchemy import inspect, text

    inspector = inspect(engine)

    if "cases" not in inspector.get_table_names():
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("cases")
    }

    if "analysis_details" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE cases "
                    "ADD COLUMN analysis_details TEXT"
                )
            )