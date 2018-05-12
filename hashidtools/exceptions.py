from zope.schema._bootstrapinterfaces import ValidationError


class InvalidHashID(ValidationError):
    """The specified HashID is not valid."""


class IDRegisterError(ValueError):
    """IntId Registration error."""
