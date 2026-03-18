class DomainError(Exception):
    """
    Base class for all domain errors.
    """
    pass


class InvalidStateTransitionError(DomainError):
    """
    Raised when an entity performs a forbidden state change.
    """
    pass

class ModelExecutionError(DomainError):
    """
    Raised when an error is encountered during the execution of a model.
    """
    pass

class RunAlreadyStartedError(DomainError):
    """
    Raised when trying to start a run that has already started.
    """
    pass

class EmptyParameterSet(DomainError):
    """
    Raised when trying to create an empty parameter set.
    """

### we need to separate domain errors from database errors and in general implementation errors!
### ideally the separation should also be granular within the domain errors
### so that we can manage each relevant distinction within business errors
### we can manage instruction flow based on the exceptions encountered / raised!!!
### ---> followup!