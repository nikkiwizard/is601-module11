from app import database_init
from app.database import Base, get_engine


def test_init_and_drop_db():
    # use a temporary sqlite engine to avoid touching files
    engine = get_engine("sqlite:///:memory:")
    # create tables via Base
    Base.metadata.create_all(bind=engine)
    # call module functions (they use module-level engine in app.database)
    # ensure init_db and drop_db can be called without raising
    database_init.init_db()
    database_init.drop_db()


def test_run_module_executes_init(monkeypatch):
    import runpy

    # Running the module should not raise
    runpy.run_module("app.database_init", run_name="__main__")
