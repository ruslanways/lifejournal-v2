"""
App-level conftest that imports global fixtures from tests/conftest.py.

This makes fixtures from tests/conftest.py available to all tests in apps/
while keeping the global fixtures organized in tests/ alongside end-to-end tests.
"""
pytest_plugins = ["tests.conftest"]

