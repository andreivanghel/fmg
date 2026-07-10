class InfrastructureError(Exception):
    """
    Base class for all infrastructure errors.
    """
    pass

class DatabaseError(InfrastructureError):
    """
    Database error.
    """
    pass
