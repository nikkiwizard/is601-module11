from app.database import get_engine, get_sessionmaker, get_db


def test_get_engine_and_sessionmaker():
    engine = get_engine("sqlite:///:memory:")
    Session = get_sessionmaker(engine)
    s = Session()
    assert s is not None
    s.close()


def test_get_db_generator_closes_session():
    gen = get_db()
    db = next(gen)
    assert db is not None
    # close generator to trigger finally
    gen.close()


def test_get_engine_default_uses_settings():
    # call without args to use settings.DATABASE_URL
    e = get_engine()
    assert e is not None


def test_get_sessionmaker_without_engine_calls_get_engine():
    Session = get_sessionmaker()
    s = Session()
    assert s is not None
    s.close()
