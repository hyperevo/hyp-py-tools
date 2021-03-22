class BaseError(Exception):
    pass

class InvalidTimestampsInDataError(BaseError):
    """
    Raised inside sparse dataset where you try to add new data that includes timestamps that arent allowed
    """
    pass

class NotEnoughInputData(BaseError):
    """
    Raised when there isn't enough input data for the nn to run
    """
    pass