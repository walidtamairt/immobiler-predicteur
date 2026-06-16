from main import app


def test_root_main_exposes_fastapi_app():
    assert app.title == "Real Estate AI Platform"
