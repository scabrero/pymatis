"""Async client for Modbus devices."""

from __future__ import annotations

import asyncio
import logging
import time
import typing as t
from dataclasses import dataclass
from typing import List

import pymodbus.client as modbusClient
from pymodbus.constants import ExcCodes
from pymodbus.exceptions import ConnectionException as ModbusConnectionException
from pymodbus.exceptions import ModbusException, ModbusIOException
from pymodbus.pdu import ExceptionResponse, ModbusPDU
from pymodbus.pdu.register_message import (
    WriteMultipleRegistersResponse,
    WriteSingleRegisterResponse,
)

from pymatis.constants import Baudrate, Parity, StopBits

from .exceptions import (
    MatisAcknowledgeException,
    MatisConnectionException,
    MatisConnectionInterruptedException,
    MatisException,
    MatisIOException,
    MatisInvalidArgumentException,
    MatisReadException,
    MatisSlaveBusyException,
    MatisSlaveFailureException,
    MatisWriteException,
)
from .registers import RegisterAccess, RegisterBase

LOGGER = logging.getLogger(__name__)

T = t.TypeVar("T")

# Minimum time to wait between two commands sent to the device. If commands are sent too fast
# it will not respond. This happens when connected over USB.
MIN_TIME_BETWEEN_COMMANDS = 0.01


@dataclass
class MatisBaseTransport:
    """Base class to define the transport."""


@dataclass
class MatisTcpTransport(MatisBaseTransport):
    """Parameters for the TCP transport."""

    host: str = "192.168.1.200"
    port: int = 4196


@dataclass
class MatisRtuTransport(MatisBaseTransport):
    """Parameters for the serial transport."""

    device: str = "/dev/ttyACM0"
    baudrate: Baudrate = Baudrate.BAUD_9600
    data_bits: int = 8
    parity: Parity = Parity.PARITY_EVEN
    stop_bits: StopBits = StopBits.STOP_1


class AsyncMatisModbusClient:
    """The base class."""

    client: modbusClient.ModbusBaseClient
    ts: float
    lock: asyncio.Lock

    def __init__(self, client: modbusClient.ModbusBaseClient) -> None:
        self.client = client
        self.ts = 0
        self.lock = asyncio.Lock()

    def __del__(self):
        if hasattr(self, "client") and self.client.connected:
            LOGGER.debug("Closing modbus connection")
            self.client.close()

    async def _reconnect(self) -> bool:
        try:
            if not self.client.connected:
                LOGGER.debug("Establishing modbus connection")
                await self.client.connect()
            if not self.client.connected:
                LOGGER.error("Failed to establish modbus connection")
                self.client.close()
                raise MatisConnectionException
        except ModbusException as err:
            message = f"Failed to establish modbus connection: {err}"
            LOGGER.error(message)
            self.client.close()
            raise MatisConnectionException from err
        return self.client.connected

    async def _read_registers(self, register: int, length: int, slave: int) -> ModbusPDU:
        """Async read registers from device."""

        async with self.lock:
            LOGGER.debug(
                "Reading register %s with length %s from slave %s", register, length, slave
            )

            await self._reconnect()
            try:
                elapsed = time.time() - self.ts
                if elapsed < MIN_TIME_BETWEEN_COMMANDS:
                    delay = MIN_TIME_BETWEEN_COMMANDS - elapsed
                    await asyncio.sleep(delay)

                response = await self.client.read_holding_registers(
                    register,
                    count=length,
                    device_id=slave,  # pymodbus keyword was renamed
                )
                if isinstance(response, ExceptionResponse):
                    if response.exception_code == ExcCodes.DEVICE_BUSY:
                        message = (
                            "Got a SlaveBusy Modbus Exception while reading "
                            f"register {register} (length {length}) from slave {slave}"
                        )
                        LOGGER.info(message)
                        raise MatisSlaveBusyException(message)

                    if response.exception_code == ExcCodes.DEVICE_FAILURE:
                        message = (
                            "Got a SlaveFailure Modbus Exception while reading "
                            f"register {register} (length {length}) from slave {slave}"
                        )
                        LOGGER.info(message)
                        raise MatisSlaveFailureException(message)

                    if response.exception_code == ExcCodes.ACKNOWLEDGE:
                        message = (
                            f"Got ACK while reading register {register} (length {length}) "
                            f"from slave {slave}."
                        )
                        LOGGER.info(message)
                        raise MatisAcknowledgeException(message)

                    message = (
                        f"Got an error while reading register {register} "
                        f"(length {length}) from slave {slave}: {response}"
                    )
                    LOGGER.warning(message)
                    raise MatisReadException(message, modbus_exception_code=response.exception_code)

                if len(response.registers) != length:
                    message = (
                        f"Mismatch between number of requested registers ({length}) "
                        f"and number of received registers ({len(response.registers)})"
                    )
                    LOGGER.error(message)
                    raise MatisSlaveBusyException(message)
            except ModbusIOException as err:
                message = f"Could not read register, I/O exception: {err}"
                LOGGER.error(message)
                self.client.close()
                raise MatisIOException(message) from err
            except ModbusConnectionException as err:
                message = f"Could not read register, bad connection: {err}"
                LOGGER.error(message)
                self.client.close()
                raise MatisConnectionInterruptedException(message) from err
            except ModbusException as err:
                message = f"Modbus exception reading register: {err}"
                LOGGER.error(message)
                raise MatisException(message) from err
            finally:
                self.ts = time.time()
            return response

    async def _write_registers(self, register: int, value: list[int], slave: int) -> bool:
        """Async write registers to device."""

        async with self.lock:
            LOGGER.debug("Writing register %s: %s to slave %s", register, value, slave)

            await self._reconnect()

            single_register = len(value) == 1
            try:
                if single_register:
                    response = await self.client.write_register(
                        register,
                        value[0],
                        device_id=slave,  # pymodbus keyword was renamed
                    )
                else:
                    response = await self.client.write_registers(
                        register,
                        value,
                        device_id=slave,  # pymodbus keyword was renamed
                    )
                if isinstance(response, ExceptionResponse):
                    message = (
                        f"Failed to write value {value} to register {register}: "
                        f"{response.exception_code:02X}"
                    )
                    LOGGER.info(message)
                    raise MatisWriteException(
                        message, modbus_exception_code=response.exception_code
                    )
            except ModbusIOException as err:
                message = f"Could not write register, I/O exception: {err}"
                LOGGER.error(message)
                self.client.close()
                raise MatisIOException(message) from err
            except ModbusConnectionException as err:
                message = f"Could not write register, bad connection: {err}"
                LOGGER.error(message)
                self.client.close()
                raise MatisConnectionInterruptedException(message) from err
            except ModbusException as err:
                message = f"Could now write register: {err}"
                LOGGER.error(message)
                raise MatisException(message) from err
            if single_register:
                assert isinstance(response, WriteSingleRegisterResponse)
                r1: bool = response.address == register and response.registers == [value[0]]
                return r1
            assert isinstance(response, WriteMultipleRegistersResponse)
            r2: bool = response.address == register and response.count == len(value)
            return r2

    async def get_register(self, regdesc: RegisterBase[T], slave: int) -> T:
        """Get a register from device."""

        if RegisterAccess.READ not in regdesc.description.access:
            LOGGER.warning("Attempt to read not readable register %s", regdesc)
            raise ValueError(f"Attempt to read not readable register {regdesc}")

        response = await self._read_registers(
            regdesc.description.address, regdesc.description.length, slave
        )

        value = regdesc.decode(response.registers)
        if regdesc.result_adapter:
            return regdesc.result_adapter(value)
        return regdesc.result_type(value)

    async def get_multiple(self, regdesc: List[RegisterBase[T]], slave: int) -> List[T]:
        """Read multiple registers in one transaction."""
        if len(regdesc) == 0:
            msg = "Expected at least one register"
            raise MatisInvalidArgumentException(msg)

        for r in regdesc:
            if RegisterAccess.READ not in r.description.access:
                LOGGER.warning("Attempt to read not readable register %s", r)
                raise ValueError(f"Attempt to read not readable register {r}")

        for i in range(1, len(regdesc)):
            prev = regdesc[i - 1].description
            curr = regdesc[i].description
            if prev.address + prev.length > curr.address:
                msg = (
                    f"Requested registers must be in monotonically increasing order, "
                    f"but {prev.address} + {prev.length} > {curr.address}!"
                )
                raise MatisInvalidArgumentException(msg)

        start = regdesc[0].description
        end = regdesc[-1].description
        total_length = end.address + end.length - start.address
        LOGGER.debug("Reading %s registers starting from %s", total_length, start.address)

        response = await self._read_registers(start.address, total_length, slave)

        retval = []
        for r in regdesc:
            value = r.decode(
                response.registers[
                    r.description.address - start.address : r.description.address
                    - start.address
                    + r.description.length
                ]
            )
            retval.append(value)
        return retval

    async def set_register(self, register: RegisterBase[T], value: t.Any, slave: int) -> bool:
        """Write a register to the device."""

        if RegisterAccess.WRITE not in register.description.access:
            LOGGER.warning("Attempt to write not writable register %s", register)
            raise ValueError(f"Trying to write not writable register {register}")

        registers = register.encode(value)
        return await self._write_registers(register.description.address, registers, slave)

    async def connect(self) -> bool:
        """Establish underlying Modbus connection."""
        return await self._reconnect()

    def close(self) -> None:
        """Close underlying Modbus connection."""
        self.client.close()


class AsyncMatisModbusTcpClient(AsyncMatisModbusClient):
    """Matis client using Modbus TCP transport."""

    def __init__(self, transport: MatisTcpTransport) -> None:
        client = modbusClient.AsyncModbusTcpClient(transport.host, port=transport.port)
        super().__init__(client)


class AsyncMatisModbusRtuClient(AsyncMatisModbusClient):
    """Matis client using Modbus RTU transport."""

    def __init__(self, transport: MatisRtuTransport) -> None:
        baudrate: int
        if transport.baudrate == Baudrate.BAUD_2400:
            baudrate = 2400
        elif transport.baudrate == Baudrate.BAUD_4800:
            baudrate = 4800
        elif transport.baudrate == Baudrate.BAUD_9600:
            baudrate = 9600
        else:
            raise MatisInvalidArgumentException(f"Unhandled baudrate value {transport.baudrate}")

        parity: str
        if transport.parity == Parity.PARITY_EVEN:
            parity = "E"
        elif transport.parity == Parity.PARITY_ODD:
            parity = "O"
        elif transport.parity == Parity.PARITY_NONE:
            parity = "N"
        else:
            raise MatisInvalidArgumentException(f"Unhandled parity value {transport.parity}")

        stopbits: int
        if transport.stop_bits == StopBits.STOP_1:
            stopbits = 1
        elif transport.stop_bits == StopBits.STOP_2:
            stopbits = 2
        else:
            raise MatisInvalidArgumentException(f"Unhandled stop bits value {transport.stop_bits}")

        client = modbusClient.AsyncModbusSerialClient(
            transport.device,
            baudrate=baudrate,
            bytesize=transport.data_bits,
            parity=parity,
            stopbits=stopbits,
        )
        super().__init__(client)
