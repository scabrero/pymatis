#!/usr/bin/env python3

"""Matis Command Line Interface."""

import argparse
import asyncio
import logging

from aiocmd import aiocmd

from pymatis.constants import Baudrate, Command, Parity, SerialConfig, StopBits
from pymatis.properties import MatisProperty as mp

try:
    from pymatis.client import AsyncMatisModbusRtuClient
except ModuleNotFoundError:
    import os
    import sys

    sys.path.append(f"{os.path.dirname(__file__)}/src")
    from pymatis.client import AsyncMatisModbusRtuClient

from pymatis.client import (
    AsyncMatisModbusClient,
    AsyncMatisModbusTcpClient,
    MatisRtuTransport,
    MatisTcpTransport,
)
from pymatis.exceptions import (
    MatisConnectionException,
    MatisInvalidArgumentException,
)
from pymatis.mt53r import (
    MT53RAsx,
)


class MatisMT53RAsxCLI(aiocmd.PromptToolkitCmd):
    """The MT53RAsx CLI interface."""

    def __init__(self, device_address: int, client: AsyncMatisModbusClient) -> None:
        super().__init__()
        self.prompt = f"[MT53RAsx@{device_address}]>> "
        self.dev = MT53RAsx(client, device_address)

    async def do_device_address(self) -> None:
        """Get the modbus device address."""
        addr = await self.dev.get(mp.MODBUS_ADDRESS)
        print(f"Device address: {addr}")

    async def do_set_device_address(self, address: str) -> None:
        """Set the modbus device address."""
        await self.dev.set(mp.MODBUS_ADDRESS, int(address))

    async def do_serial_config(self) -> None:
        """Get the serial config."""
        config = await self.dev.serial_config()
        print(f"Serial config: {config}")

    async def do_set_serial_config(self, baudrate, parity, stop_bits) -> None:
        """Set the serial config."""
        config = SerialConfig(
            baudrate=Baudrate.parse(baudrate),
            parity=Parity.parse(parity),
            stop_bits=StopBits.parse(stop_bits),
        )
        await self.dev.set_serial_config(config)

    async def do_status(self) -> None:
        """Print the device status."""
        await self.dev.dump()

    async def do_uptime(self) -> None:
        """Print device uptime."""
        uptime = await self.dev.get(mp.SYSTEM_CLOCK)
        print(f"{uptime}")

    async def do_reset(self) -> None:
        """Reset the device."""
        await self.dev.reset()

    async def do_set_auto_reclose_attempts(self, attempts: str) -> None:
        """Set the number of auto-reclose attempts."""
        value = int(attempts)
        await self.dev.set(mp.AR_TOTAL_ATTEMPTS, value)

    async def do_set_auto_reclose_wait_time(self, attempt: str, seconds: str) -> None:
        """Set an auto-reclose wait time."""
        amp = self.dev.ar_wait_time_mp(int(attempt))
        await self.dev.set(amp, int(seconds))

    async def do_set_auto_reclose_stable_time(self, attempt: str, seconds: str) -> None:
        """Set an auto-reclose stable time."""
        amp = self.dev.ar_stable_time_mp(int(attempt))
        await self.dev.set(amp, int(seconds))

    async def do_open(self) -> None:
        """Send open control command."""
        await self.dev.set(mp.CONTROL, Command.OPEN)

    async def do_close(self) -> None:
        """Send close control command."""
        await self.dev.set(mp.CONTROL, Command.CLOSE)

    async def do_lock(self) -> None:
        """Send lock control command."""
        await self.dev.set(mp.CONTROL, Command.LOCK)

    async def do_unlock(self) -> None:
        """Send lock control command."""
        await self.dev.set(mp.CONTROL, Command.UNLOCK)


class MatisClientCLI(aiocmd.PromptToolkitCmd):  # pylint: disable=too-few-public-methods
    """CLI client interface."""

    prompt = "[client]>> "

    def __init__(self, client: AsyncMatisModbusClient) -> None:
        """Init client context."""
        super().__init__()
        self.client = client

    async def do_MT53RAsx(self, address: str) -> None:  # pylint: disable=invalid-name
        """Switch to device context."""
        _address = int(address)
        await MatisMT53RAsxCLI(_address, self.client).run()


class MatisRootCLI(aiocmd.PromptToolkitCmd):
    """CLI root context."""

    prompt = ">> "
    intro = 'Welcome to MatisCLI. Type "help" for available commands.'
    client: AsyncMatisModbusClient | None = None

    async def do_connect_rtu(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        port: str = "/dev/ttyACM0",
        baudrate: str = "9600",
        data_bits: str = "8",
        parity: str = "N",
        stop_bits: str = "1",
    ) -> None:
        """Serial modbus."""
        if self.client:
            raise MatisConnectionException("Already connected")
        transport = MatisRtuTransport(
            device=port,
            baudrate=Baudrate.parse(baudrate),
            data_bits=int(data_bits),
            parity=Parity.parse(parity),
            stop_bits=StopBits.parse(stop_bits),
        )
        self.client = AsyncMatisModbusRtuClient(transport)
        await MatisClientCLI(self.client).run()

    async def do_connect_tcp(self, host: str = "192.168.1.200", port: int = 4196):
        """Connect to Ethernet modbus server."""
        if self.client:
            raise MatisConnectionException("Already connected")
        transport = MatisTcpTransport(host, port=port)
        self.client = AsyncMatisModbusTcpClient(transport)
        await MatisClientCLI(self.client).run()

    async def do_disconnect(self) -> None:
        """Disconnect from server."""
        if self.client:
            self.client = None

    async def do_set_log_level(self, level: str) -> None:
        "Set the log level: critical, fatal, error, warning, info or debug."
        logging.basicConfig()
        log = logging.getLogger()
        if level.casefold() == "critical".casefold():
            log.setLevel(logging.CRITICAL)
        elif level.casefold() == "fatal".casefold():
            log.setLevel(logging.FATAL)
        elif level.casefold() == "error".casefold():
            log.setLevel(logging.ERROR)
        elif level.casefold() == "warning".casefold():
            log.setLevel(logging.WARNING)
        elif level.casefold() == "info".casefold():
            log.setLevel(logging.INFO)
        elif level.casefold() == "debug".casefold():
            log.setLevel(logging.DEBUG)
        else:
            raise MatisInvalidArgumentException("Invalid log level")


async def main() -> None:
    """Run the async CLI."""
    await MatisRootCLI().run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Matis Command Line Interface",
    )
    args = parser.parse_args()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
