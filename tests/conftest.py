import logging
import subprocess
import time
from contextlib import contextmanager
from typing import Dict, Generator, List

import pytest
import requests
from faker import Faker
from playwright.sync_api import Browser, sync_playwright
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, get_engine, get_sessionmaker
from app.models.user import User


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

fake = Faker()
Faker.seed(12345)

test_engine = get_engine(database_url=settings.DATABASE_URL)
TestingSessionLocal = get_sessionmaker(engine=test_engine)


def create_fake_user() -> Dict[str, str]:
    return {
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "password": "TestPass123",
    }


@contextmanager
def managed_db_session():
    session = TestingSessionLocal()

    try:
        yield session
    except SQLAlchemyError as error:
        logger.error(f"Database error: {error}")
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture(scope="session")
def setup_test_database(request):
    logger.info("Setting up test database...")

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    preserve_db = request.config.getoption("--preserve-db")

    if not preserve_db:
        logger.info("Cleaning up test database...")
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_test_database, request) -> Generator[Session, None, None]:
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        preserve_db = request.config.getoption("--preserve-db")

        if not preserve_db:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()

        session.close()


@pytest.fixture
def fake_user_data() -> Dict[str, str]:
    return create_fake_user()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user_data = create_fake_user()
    user = User.register(db_session, user_data)

    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def seed_users(db_session: Session, request) -> List[User]:
    try:
        number_of_users = request.param
    except AttributeError:
        number_of_users = 5

    users = []

    for _ in range(number_of_users):
        user_data = create_fake_user()
        user = User.register(db_session, user_data)
        users.append(user)

    db_session.commit()

    return users


def wait_for_server(url: str, timeout: int = 30) -> bool:
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass

        time.sleep(1)

    return False


class ServerStartupError(Exception):
    pass


@pytest.fixture(scope="session")
def fastapi_server():
    server_url = "http://127.0.0.1:8000"

    process = subprocess.Popen(
        ["python", "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        if not wait_for_server(server_url, timeout=30):
            raise ServerStartupError("Failed to start test server")

        yield
    finally:
        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def page(browser_context: Browser):
    context = browser_context.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
    )

    page = context.new_page()

    try:
        yield page
    finally:
        page.close()
        context.close()


def pytest_addoption(parser):
    parser.addoption(
        "--preserve-db",
        action="store_true",
        default=False,
        help="Keep test database after tests.",
    )

    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run tests marked as slow.",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="use --run-slow to run")

        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)