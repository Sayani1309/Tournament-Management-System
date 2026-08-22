import pytest
from app import create_app
from app.extensions import db, require_role


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    assert "test" in app.config["SQLALCHEMY_DATABASE_URI"], (
        "Refusing to run tests against a non-test database!"
    )

    # Test-only route for require_role coverage — must be registered
    # before the app handles its first request, so it lives here, not
    # inside an individual test.
    @app.route("/api/v1/_test/organizer-only")
    @require_role("ORGANIZER")
    def _organizer_only():
        return {"ok": True}, 200

    with app.app_context():
        db.drop_all()   # clean slate even if a prior run crashed mid-way
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def _db_cleanup(app):
    """Wrap each test in a rollback so data doesn't leak between tests,
    without recreating the schema every time."""
    with app.app_context():
        yield
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()