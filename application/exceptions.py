class ApplicationError(Exception):
    """
    Base class for all application errors.
    """
    pass


class ModelNotFoundError(ApplicationError):
    """
    Raised when a model is not found within a ModelFactory."""
    pass

class RunNotFoundError(ApplicationError):
    """
    Raised when a run is not found within the database."""
    pass

class ParametersNotFoundError(ApplicationError):
    """
    Raised when a parameter set is not found within"""
    pass