"""Constants and data types used by this library."""

from enum import Flag, IntEnum
from dataclasses import dataclass


class Baudrate(IntEnum):
    """Serial port baudrate."""

    BAUD_2400 = 1
    BAUD_4800 = 2
    BAUD_9600 = 3

    @classmethod
    def parse(cls, value: int | str):  # pylint: disable=too-many-return-statements
        """Instantiate by string."""
        if int(value) == 2400:
            return cls(cls.BAUD_2400)
        if int(value) == 4800:
            return cls(cls.BAUD_4800)
        if int(value) == 9600:
            return cls(cls.BAUD_9600)
        raise ValueError(f"Unknown baudrate value {value}")

    def __str__(self) -> str:
        if self.value == self.BAUD_2400:
            return "2400"
        if self.value == self.BAUD_4800:
            return "4800"
        if self.value == self.BAUD_9600:
            return "9600"
        raise ValueError(f"Unknown baudrate value {self.value}")


class Parity(IntEnum):
    """Serial port parity."""

    PARITY_NONE = 1
    PARITY_EVEN = 2
    PARITY_ODD = 3

    @classmethod
    def parse(cls, value: str):
        """Instantiate by string."""
        if value.casefold() == "none".casefold() or value.casefold() == "N".casefold():
            return cls(cls.PARITY_NONE)
        if value.casefold() == "odd".casefold() or value.casefold() == "O".casefold():
            return cls(cls.PARITY_ODD)
        if value.casefold() == "even".casefold() or value.casefold() == "E".casefold():
            return cls(cls.PARITY_EVEN)
        raise ValueError(f"Unknown parity value {value}")

    def __str__(self) -> str:
        if self.value == self.PARITY_NONE:
            return "N"
        if self.value == self.PARITY_ODD:
            return "O"
        if self.value == self.PARITY_EVEN:
            return "E"
        raise ValueError(f"Unknown parity value {self.value}")


class StopBits(IntEnum):
    """Serial port stop bits."""

    STOP_1 = 1
    STOP_1_5 = 2
    STOP_2 = 3

    @classmethod
    def parse(cls, value: float | str):
        """Instantiate by string."""
        if isinstance(value, float) and value == 1:
            return cls(cls.STOP_1)
        if isinstance(value, float) and value == 1.5:
            return cls(cls.STOP_1_5)
        if isinstance(value, float) and value == 2:
            return cls(cls.STOP_2)
        if isinstance(value, str) and value == "1":
            return cls(cls.STOP_1)
        if isinstance(value, str) and value == "1.5":
            return cls(cls.STOP_1_5)
        if isinstance(value, str) and value == "2":
            return cls(cls.STOP_2)
        raise ValueError(f"Unknown stop_bits value {value}")

    def __str__(self) -> str:
        if self.value == self.STOP_1:
            return "1"
        if self.value == self.STOP_1_5:
            return "1.5"
        if self.value == self.STOP_2:
            return "2"
        raise ValueError(f"Unknown stop_bits value {self.value}")


class DisplayStatus(IntEnum):
    """Front LED status."""

    RED_ON = 1
    GREEN_ON = 2
    RED_FLASH = 4
    GREEN_FLASH = 5
    RED_GREEN_FLASH = 15

    @classmethod
    def parse(cls, value: int | str):
        """Instantiate by string."""
        if int(value) == 1:
            return cls(cls.RED_ON)
        if int(value) == 2:
            return cls(cls.GREEN_ON)
        if int(value) == 4:
            return cls(cls.RED_FLASH)
        if int(value) == 5:
            return cls(cls.GREEN_FLASH)
        if int(value) == 15:
            return cls(cls.RED_GREEN_FLASH)
        raise ValueError(f"Unknown stop_bits value {value}")

    def __str__(self) -> str:
        if self.value == self.RED_ON:
            return "Red on"
        if self.value == self.GREEN_ON:
            return "Green on"
        if self.value == self.RED_FLASH:
            return "Red flash"
        if self.value == self.GREEN_FLASH:
            return "Green flash"
        if self.value == self.RED_GREEN_FLASH:
            return "Red/Green flash"
        raise ValueError(f"Unknown stop_bits value {self.value}")


class LocationHall(Flag):
    """hall effect sensor location flags."""

    OPEN = 0x0001
    RESET = 0x0002
    CLOSED = 0x0004
    MOTOR_FAULT = 0x0008


class ReclosingStatus(Flag):
    """Reclosing status."""

    INITIAL = 0x0000
    COMMAND_OPENING = 0x0002
    COMMAND_CLOSING = 0x0004
    COMMAND_LOCK = 0x0008
    COMMAND_UNLOCK = 0x0010
    AUTOMATIC_OPENING = 0x0020
    AUTOMATIC_CLOSING = 0x0040
    MANUAL_CLOSING = 0x0400
    FAULT_OPENING = 0x0800
    PADLOCKED = 0x8000


class Command(IntEnum):
    """Remote control command."""

    OPEN = 1
    CLOSE = 2
    LOCK = 3
    UNLOCK = 4


@dataclass
class SerialConfig:
    """Serial config."""

    baudrate: Baudrate
    parity: Parity
    stop_bits: StopBits


class MatisHardwareId(IntEnum):
    """Matismart hardware ID."""

    MT53RA_SX = 523

    def __str__(self) -> str:
        if self.value == self.MT53RA_SX:
            return "MT53RAsx"
        raise ValueError(f"Unknown value {self.value}")
