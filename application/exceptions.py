class ApplicationError(Exception):
    """
    Base class for all application errors.
    """
    pass


class ModelNotFoundError(ApplicationError):
    """
    Raised when a model is not found within a ModelFactory.
    """
    pass

class RunNotFoundError(ApplicationError):
    """
    Raised when a run is not found within the database.
    """
    pass

class EarlyRunIdAssignmentError(ApplicationError):
    """
    Raised when attempting to create a new run in the database, but the model run instance already has an assigned id.
    """
    pass

class MissingRunIdError(ApplicationError):
    """
    Raised when attempting to update an existing run in the database, but the model run instance does not have an assigned id."""

class ParametersNotFoundError(ApplicationError):
    """
    Raised when a parameter set is not found within the database.
    """
    pass