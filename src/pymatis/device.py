"""Matismart device implementation."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from pymatis.client import AsyncMatisModbusClient
from pymatis.exceptions import MatisPropertyNotSupported
from pymatis.properties import MatisProperty
from pymatis.registers import RegisterBase

LOGGER = logging.getLogger(__name__)


class MatisDevice:
    """Base class for Matis devices."""

    client: AsyncMatisModbusClient
    slave_id: int
    registers: List[RegisterBase]
    regmap: Dict[MatisProperty, RegisterBase]

    def __init__(self, client: AsyncMatisModbusClient, address: int) -> None:
        self.client = client
        self.slave_id = address
        self.regmap: Dict[MatisProperty, RegisterBase] = {
            regdesc.mproperty: regdesc for regdesc in self.registers
        }

    async def get(self, mp: MatisProperty) -> Any:
        """Get a device characteristic."""
        if mp not in self.regmap:
            raise MatisPropertyNotSupported(mp)
        regdesc = self.regmap[mp]
        return await self.client.get_register(regdesc, self.slave_id)

    async def set(self, mp: MatisProperty, value: Any) -> bool:
        """Get a device characteristic."""
        if mp not in self.regmap:
            raise MatisPropertyNotSupported(mp)
        regdesc = self.regmap[mp]
        result = await self.client.set_register(regdesc, value, self.slave_id)
        if mp == MatisProperty.MODBUS_ADDRESS and result:
            self.slave_id = value
        return result

    async def fetch(self) -> Dict[MatisProperty, Any]:
        """Fetch device data."""
        raise NotImplementedError

    async def connect(self) -> bool:
        """Establish underlying Modbus connection."""
        return await self.client.connect()

    def close(self) -> None:
        """Close underlying Modbus connection."""
        return self.client.close()
