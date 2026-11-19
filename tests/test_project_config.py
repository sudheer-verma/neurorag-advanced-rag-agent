from scripts.validate_project import validate_env, validate_postman


def test_postman_collection_is_valid():
    validate_postman()


def test_env_ignore_and_example_are_configured():
    validate_env()
