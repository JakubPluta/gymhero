from collections import UserDict
import pytest
from gymhero.database.utils import key_column_from


@pytest.fixture
def context():
    class Context:
        def __init__(self):
            self.current_parameters = {"column_name": "First Name"}

        def __getitem__(self, key):
            if key == "current_parameters":
                return self.current_parameters
            return self.current_parameters[key]

    return Context()


def test_default_function(context):
    # Test case for retrieving a column value with spaces and uppercase letters
    print(context)
    expected_output = "first_name"
    assert key_column_from("column_name")(context) == expected_output

    # Test case for retrieving a column value with special characters
    context["current_parameters"]["column_name"] = "Last-Name"
    expected_output = "last-name"
    assert key_column_from("column_name")(context) == expected_output

    # Test case for retrieving a column value with no spaces or special characters
    context["current_parameters"]["column_name"] = "age"
    expected_output = "age"
    assert key_column_from("column_name")(context) == expected_output
