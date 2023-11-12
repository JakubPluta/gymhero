
def key_column_from(column_name):
    """Retrieves the value of the specified column from the given context.
    """
    def default_function(context) -> str:
        return context.current_parameters.get(column_name).lower().replace(" ", "_")
    return default_function
