"""Exceptions from the Matis library."""

from pymatis.properties import MatisProperty


class MatisException(Exception):
    """Base class for Matis exceptions."""


class MatisDecodeError(MatisException):
    """Decoding failed."""


class MatisEncodeError(MatisException):
    """Encoding failed."""


class MatisConnectionException(MatisException):
    """Exception connecting to device."""


class MatisPropertyNotSupported(MatisException):
    """The device does not support the property."""

    property: MatisProperty

    def __init__(self, p: MatisProperty):
        self.property = p


class MatisInvalidArgumentException(MatisException):
    """Invalid argument."""

    def __init__(self, message: str):
        super().__init__(message)


class MatisReadException(MatisException):
    """Exception reading register from device."""

    def __init__(self, message: str, modbus_exception_code: int | None):
        super().__init__(message)
        self.modbus_exception_code = modbus_exception_code


class MatisConnectionInterruptedException(MatisException):
    """Connection to the device was interrupted."""


class MatisSlaveBusyException(MatisException):
    """Non-fatal exception while trying to read from device."""


class MatisSlaveFailureException(MatisException):
    """Possibly fatal exception while trying to read from device."""


class MatisAcknowledgeException(MatisException):
    """Device accepted the request but needs time to process it."""


class MatisWriteException(MatisException):
    """Exception writing register to device."""

    def __init__(self, message: str, modbus_exception_code: int | None):
        super().__init__(message)
        self.modbus_exception_code = modbus_exception_code


class MatisBindingException(MatisException):
    """Binding failed."""


class MatisNotImplemented(MatisException):
    """Exception not implemented"""


class MatisUnknownModelException(MatisException):
    """Unknown model exception."""


class MatisIOException(MatisException):
    """I/O exception"""
