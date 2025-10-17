"""Register definitions."""

import typing as t
from dataclasses import dataclass
from enum import Flag, auto

from pymodbus.client.mixin import ModbusClientMixin

from pymatis.properties import MatisProperty

from .exceptions import MatisInvalidArgumentException

T = t.TypeVar("T")


class RegisterAccess(Flag):
    """Register access flags."""

    READ = auto()
    WRITE = auto()
    STATUS = auto()


@dataclass(frozen=True)
class RegisterDescription:
    """Register description."""

    address: int
    length: int
    access: RegisterAccess
    min: int
    max: int


class RegisterBase(t.Generic[T]):
    """Base class for register definitions."""

    description: RegisterDescription
    datatype: ModbusClientMixin.DATATYPE
    mproperty: MatisProperty
    result_type: type
    result_adapter: t.Callable[[t.Any], t.Any] | None

    def __init__(
        self,
        description: RegisterDescription,
        mproperty: MatisProperty,
        result_type: type,
        result_adapter: t.Callable[[t.Any], t.Any] | None,
    ) -> None:
        """Initialize the register instance."""
        self.description = description
        self.mproperty = mproperty
        self.result_type = result_type
        self.result_adapter = result_adapter

    def decode(self, registers: list[int]) -> T:
        """Decode register bytes to value."""
        return ModbusClientMixin.convert_from_registers(
            registers, self.datatype, word_order="little"
        )  # type: ignore

    def encode(self, value: T) -> list[int]:
        """Encode value to register bytes."""
        return ModbusClientMixin.convert_to_registers(
            value,  # type: ignore
            self.datatype,
            word_order="little",
        )

    def __repr__(self) -> str:
        return str(self.description.address)


class NumberRegister(RegisterBase[T]):
    """Base class for number registers."""

    def clamp(self, value: int) -> int:
        """Clamp provided value to datatype range."""
        rmin = self.description.min
        rmax = self.description.max
        if value < rmin or value > rmax:
            raise MatisInvalidArgumentException(
                f"Property {self.mproperty} value {value} is out of range [{rmin}..{rmax}]"
            )
        return value

    def decode(self, registers: list[int]) -> T:
        """Decode register bytes to value."""
        result: T = t.cast(
            T,
            ModbusClientMixin.convert_from_registers(registers, self.datatype, word_order="little"),
        )
        return result

    def encode(self, value: T) -> list[int]:
        """Encode value to register bytes."""
        try:
            if isinstance(value, (str, int, bool, float)):
                reg_value = int(value)
            else:
                raise MatisInvalidArgumentException(f"Unsupported type {type(value)}")
            reg_value = self.clamp(reg_value)
        except ValueError as ex:
            msg = f"Invalid value {value}"
            raise MatisInvalidArgumentException(msg) from ex
        return ModbusClientMixin.convert_to_registers(reg_value, self.datatype, word_order="little")


class U8Register(NumberRegister[int]):
    """Unsigned 8-bit entry, sent to modbus as UINT16 register."""

    datatype = ModbusClientMixin.DATATYPE.UINT16

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        mp: MatisProperty,
        address: int,
        access: RegisterAccess,
        min_value=0,
        max_value=2**8 - 1,
        result_type: type = int,
        result_adapter: t.Callable[[t.Any], t.Any] | None = None,
    ) -> None:
        """Initialize the U8Register instance."""
        description = RegisterDescription(address, 1, access, min_value, max_value)
        super().__init__(description, mp, result_type, result_adapter)


class U16Register(NumberRegister[int]):
    """Unsigned 16-bit register."""

    datatype = ModbusClientMixin.DATATYPE.UINT16

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        mp: MatisProperty,
        address: int,
        access: RegisterAccess,
        min_value=0,
        max_value=2**16 - 1,
        result_type: type = int,
        result_adapter: t.Callable[[t.Any], t.Any] | None = None,
    ) -> None:
        """Initialize the U16Register instance."""
        description = RegisterDescription(address, 1, access, min_value, max_value)
        super().__init__(description, mp, result_type, result_adapter)


class U32Register(NumberRegister[int]):
    """Unsigned 32-bit register."""

    datatype = ModbusClientMixin.DATATYPE.UINT32

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        mp: MatisProperty,
        address: int,
        access: RegisterAccess,
        min_value=0,
        max_value=2**32 - 1,
        result_type: type = int,
        result_adapter: t.Callable[[t.Any], t.Any] | None = None,
    ) -> None:
        """Initialize the U32Register instance."""
        description = RegisterDescription(address, 2, access, min_value, max_value)
        super().__init__(description, mp, result_type, result_adapter)
