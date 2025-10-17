"""Matismart MT53R recloser device implementation."""

from __future__ import annotations

import logging
import struct
from datetime import timedelta
from typing import Any, Dict, List

from pymatis.constants import (
    Baudrate,
    DisplayStatus,
    LocationHall,
    MatisHardwareId,
    Parity,
    ReclosingStatus,
    SerialConfig,
    StopBits,
)
from pymatis.device import MatisDevice
from pymatis.exceptions import MatisInvalidArgumentException
from pymatis.properties import MatisProperty as mp
from pymatis.registers import (
    RegisterAccess,
    RegisterBase,
    U8Register,
    U16Register,
    U32Register,
)

LOGGER = logging.getLogger(__name__)


def uptime_compose(value: int) -> timedelta:
    """Builds timedelta from system clock register value."""
    buf = value.to_bytes(4, "big")
    (seconds, hours) = struct.unpack(">HH", buf)
    return timedelta(hours=hours, seconds=seconds)


def timedelta_seconds(value: int) -> timedelta:
    """Builds a timedelta from a number of seconds."""
    return timedelta(seconds=value)


class MT53RAsx(MatisDevice):  # pylint: disable=too-many-public-methods
    """Represents a MT53RAsx device."""

    registers: List[RegisterBase] = [
        U8Register(
            mp.MODBUS_ADDRESS,
            0x00,
            RegisterAccess.READ | RegisterAccess.WRITE,
        ),
        U16Register(
            mp.SERIAL_BAUDRATE,
            0x01,
            RegisterAccess.READ | RegisterAccess.WRITE,
            result_type=Baudrate,
        ),
        U16Register(
            mp.SERIAL_PARITY,
            0x02,
            RegisterAccess.READ | RegisterAccess.WRITE,
            result_type=Parity,
        ),
        U16Register(
            mp.SERIAL_STOP_BITS,
            0x03,
            RegisterAccess.READ | RegisterAccess.WRITE,
            result_type=StopBits,
        ),
        U16Register(mp.SYSTEM_STATUS_CONTROL, 0x04, RegisterAccess.READ | RegisterAccess.WRITE),
        U16Register(mp.SYSTEM_UPGRADE_CONTROL, 0x05, RegisterAccess.READ | RegisterAccess.WRITE),
        U32Register(mp.SYSTEM_CLOCK, 0x06, RegisterAccess.READ, result_adapter=uptime_compose),
        U16Register(mp.HARDWARE_ID, 0x08, RegisterAccess.READ, result_type=MatisHardwareId),
        U16Register(mp.FIRMWARE_VERSION, 0x09, RegisterAccess.READ),
        U16Register(
            mp.AR_ENABLE,
            0x0A,
            RegisterAccess.READ | RegisterAccess.WRITE,
            result_type=bool,
        ),
        U16Register(
            mp.AR_TIMER,
            0x0B,
            RegisterAccess.READ,
            result_adapter=timedelta_seconds,
        ),
        U16Register(mp.DISPLAY_STATUS, 0x0C, RegisterAccess.READ, result_type=DisplayStatus),
        U16Register(mp.AUX_OUTPUT_STATUS, 0x0D, RegisterAccess.READ, result_type=bool),
        U16Register(mp.PADLOCK_STATUS, 0x0E, RegisterAccess.READ, result_type=bool),
        U16Register(mp.HANDLE_LOCATION, 0x0F, RegisterAccess.READ, result_type=LocationHall),
        U16Register(mp.AR_STATUS, 0x10, RegisterAccess.READ, result_type=ReclosingStatus),
        U16Register(mp.CONTROL, 0x11, RegisterAccess.READ | RegisterAccess.WRITE),
        U16Register(
            mp.REMOTE_CONTROL_ENABLE,
            0x12,
            RegisterAccess.READ | RegisterAccess.WRITE,
            result_type=bool,
        ),
        U16Register(
            mp.AR_TOTAL_ATTEMPTS,
            0x13,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=1,
            max_value=10,
        ),
        U16Register(
            mp.CLOSING_DELAY_COMPENSATION, 0x14, RegisterAccess.READ | RegisterAccess.WRITE
        ),
        U16Register(
            mp.OPENING_DELAY_COMPENSATION, 0x15, RegisterAccess.READ | RegisterAccess.WRITE
        ),
        U16Register(
            mp.CLOSING_RESET_COMPENSATION, 0x16, RegisterAccess.READ | RegisterAccess.WRITE
        ),
        U16Register(
            mp.OPENING_RESET_COMPENSATION, 0x17, RegisterAccess.READ | RegisterAccess.WRITE
        ),
        U16Register(mp.CLOSING_ACTION_TIME, 0x18, RegisterAccess.READ),
        U16Register(mp.OPENING_ACTION_TIME, 0x19, RegisterAccess.READ),
        U16Register(mp.CLOSING_RESET_TIME, 0x1A, RegisterAccess.READ),
        U16Register(mp.OPENING_RESET_TIME, 0x1B, RegisterAccess.READ),
        U16Register(mp.OPENING_LOCK_TIME, 0x1C, RegisterAccess.READ),
        U16Register(mp.UNLOCK_RESET_TIME, 0x1D, RegisterAccess.READ),
        U16Register(mp.MOTOR_RUNNING_TIME, 0x1F, RegisterAccess.READ),
        U16Register(mp.COMMAND_CLOSING_TIMES, 0x2B, RegisterAccess.READ),
        U16Register(mp.COMMAND_OPENING_TIMES, 0x2C, RegisterAccess.READ),
        U16Register(mp.COMMAND_LOCK_TIMES, 0x2D, RegisterAccess.READ),
        U16Register(mp.MANUAL_PADLOCK_TIMES, 0x2E, RegisterAccess.READ),
        U16Register(mp.MANUAL_CLOSING_TIMES, 0x2F, RegisterAccess.READ),
        U16Register(
            mp.AR_EXHAUSTED_TIMER,
            0x30,
            RegisterAccess.READ,
            result_adapter=timedelta_seconds,
        ),
        U16Register(mp.AR_CURRENT_ATTEMPT, 0x31, RegisterAccess.READ),
        U16Register(
            mp.AR_WAIT_TIME_1,
            0x32,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_2,
            0x33,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_3,
            0x34,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_4,
            0x35,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_5,
            0x36,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_6,
            0x37,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_7,
            0x38,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_8,
            0x39,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_9,
            0x3A,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_WAIT_TIME_10,
            0x3B,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_1,
            0x3C,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_2,
            0x3D,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_3,
            0x3E,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_4,
            0x3F,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_5,
            0x40,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_6,
            0x41,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_7,
            0x42,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_8,
            0x43,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_9,
            0x44,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
        U16Register(
            mp.AR_STABLE_TIME_10,
            0x45,
            RegisterAccess.READ | RegisterAccess.WRITE,
            min_value=5,
            max_value=3599,
            result_adapter=timedelta_seconds,
        ),
    ]

    async def serial_config(self) -> SerialConfig:
        """Get the serial configuration."""
        baudrate = await self.get(mp.SERIAL_BAUDRATE)
        parity = await self.get(mp.SERIAL_PARITY)
        stopbits = await self.get(mp.SERIAL_STOP_BITS)
        return SerialConfig(baudrate=baudrate, stop_bits=stopbits, parity=parity)

    async def set_serial_config(self, config: SerialConfig) -> bool:
        """Set the serial configuration."""
        return (
            await self.set(
                mp.SERIAL_BAUDRATE,
                config.baudrate,
            )
            and await self.set(
                mp.SERIAL_PARITY,
                config.parity,
            )
            and await self.set(
                mp.SERIAL_STOP_BITS,
                config.stop_bits,
            )
        )

    async def reset(self) -> bool:
        """Perform device soft reset."""
        return await self.set(mp.SYSTEM_STATUS_CONTROL, 2020)

    def ar_wait_time_mp(self, attempt: int) -> mp:  # pylint: disable=too-many-return-statements
        """Return the property for a reclose wait time attempt."""
        if attempt == 1:
            return mp.AR_WAIT_TIME_1
        if attempt == 2:
            return mp.AR_WAIT_TIME_2
        if attempt == 3:
            return mp.AR_WAIT_TIME_3
        if attempt == 4:
            return mp.AR_WAIT_TIME_4
        if attempt == 5:
            return mp.AR_WAIT_TIME_5
        if attempt == 6:
            return mp.AR_WAIT_TIME_6
        if attempt == 7:
            return mp.AR_WAIT_TIME_7
        if attempt == 8:
            return mp.AR_WAIT_TIME_8
        if attempt == 9:
            return mp.AR_WAIT_TIME_9
        if attempt == 10:
            return mp.AR_WAIT_TIME_10
        raise MatisInvalidArgumentException("Index out of range [0, 10]")

    def ar_stable_time_mp(self, attempt: int) -> mp:  # pylint: disable=too-many-return-statements
        """Return the property for a reclose stable time attempt."""
        if attempt == 1:
            return mp.AR_STABLE_TIME_1
        if attempt == 2:
            return mp.AR_STABLE_TIME_2
        if attempt == 3:
            return mp.AR_STABLE_TIME_3
        if attempt == 4:
            return mp.AR_STABLE_TIME_4
        if attempt == 5:
            return mp.AR_STABLE_TIME_5
        if attempt == 6:
            return mp.AR_STABLE_TIME_6
        if attempt == 7:
            return mp.AR_STABLE_TIME_7
        if attempt == 8:
            return mp.AR_STABLE_TIME_8
        if attempt == 9:
            return mp.AR_STABLE_TIME_9
        if attempt == 10:
            return mp.AR_STABLE_TIME_10
        raise MatisInvalidArgumentException("Index out of range [0, 10]")

    async def fetch(self) -> Dict[mp, Any]:
        """Fetch all device data in a single modbus transaction."""
        results = await self.client.get_multiple(self.registers, self.slave_id)
        data: Dict[mp, Any] = {}

        for reg, result in zip(self.registers, results, strict=True):
            if reg.result_adapter:
                data[reg.mproperty] = reg.result_adapter(result)
            else:
                data[reg.mproperty] = reg.result_type(result)
        return data

    async def dump(self) -> None:  # pylint: disable=too-many-statements
        """Dump all device data to stdout."""
        data = await self.fetch()

        print("MT53RAsx status")
        print("---------------")
        print("  Hardware:")
        print(f"    {'ID:': <25}{data[mp.HARDWARE_ID]}")
        print("")
        print("  Software:")
        print(f"    {'Version:': <25}{data[mp.FIRMWARE_VERSION]}")
        print("")
        print("  Serial:")
        print(f"    {'Baudrate:': <25}{data[mp.SERIAL_BAUDRATE]}")
        print(f"    {'Parity:': <25}{data[mp.SERIAL_PARITY]}")
        print(f"    {'Stop bits:': <25}{data[mp.SERIAL_STOP_BITS]}")
        print("")
        print("  Modbus:")
        print(f"    {'Device address:': <25}{data[mp.MODBUS_ADDRESS]}")
        print("")
        print("  System:")
        print(f"    {'Uptime:': <25}{data[mp.SYSTEM_CLOCK]}")
        print(f"    {'Display:': <25}{data[mp.DISPLAY_STATUS]}")
        print(f"    {'Aux output:': <25}{data[mp.AUX_OUTPUT_STATUS]}")
        print(f"    {'Padlock:': <25}{data[mp.PADLOCK_STATUS]}")
        print(f"    {'Hall sensor flags:': <25}{data[mp.HANDLE_LOCATION]}")
        print(f"    {'Remote control enabled:': <25}{data[mp.REMOTE_CONTROL_ENABLE]}")
        print("")
        print("  Auto-reclose:")
        print(f"    {'Enabled:': <25}{data[mp.AR_ENABLE]}")
        print(
            f"    {'Attempt:': <25}{data[mp.AR_CURRENT_ATTEMPT]}",
            "/",
            f"{data[mp.AR_TOTAL_ATTEMPTS]}",
        )
        print(f"    {'Reclose timer:': <25}{data[mp.AR_TIMER]}")
        print(f"    {'Exhausted timer:': <25}{data[mp.AR_EXHAUSTED_TIMER]}")
        print(f"    {'Status:': <25}{data[mp.AR_STATUS]}")
        for i in range(1, 11):
            wait = data[self.ar_wait_time_mp(i)]
            stable = data[self.ar_stable_time_mp(i)]
            s = f"Reclose/Stable time {i}: "
            print(f"    {s: <25}{wait} / {stable}")
        print("")
        print("  Statistics:")
        print(f"    {'Closing action time:': <25}{data[mp.CLOSING_ACTION_TIME]}")
        print(f"    {'Opening action time:': <25}{data[mp.OPENING_ACTION_TIME]}")
        print(f"    {'Closing reset time:': <25}{data[mp.CLOSING_RESET_TIME]}")
        print(f"    {'Opening reset time:': <25}{data[mp.OPENING_RESET_TIME]}")
        print(f"    {'Opening lock time:': <25}{data[mp.OPENING_LOCK_TIME]}")
        print(f"    {'Unlock reset time:': <25}{data[mp.UNLOCK_RESET_TIME]}")
        print(f"    {'Motor running time:': <25}{data[mp.MOTOR_RUNNING_TIME]}")
        print(f"    {'Command closing times:': <25}{data[mp.COMMAND_CLOSING_TIMES]}")
        print(f"    {'Command opening times:': <25}{data[mp.COMMAND_OPENING_TIMES]}")
        print(f"    {'Command lock times:': <25}{data[mp.COMMAND_LOCK_TIMES]}")
        print(f"    {'Manual padlock times:': <25}{data[mp.MANUAL_PADLOCK_TIMES]}")
        print(f"    {'Manual closing times:': <25}{data[mp.MANUAL_CLOSING_TIMES]}")
