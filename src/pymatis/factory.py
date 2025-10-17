"""Matis device factory."""

from pymatis.client import (
    AsyncMatisModbusClient,
    AsyncMatisModbusTcpClient,
    AsyncMatisModbusRtuClient,
    MatisBaseTransport,
    MatisTcpTransport,
    MatisRtuTransport,
)
from pymatis.exceptions import MatisException, MatisUnknownModelException
from pymatis.constants import MatisHardwareId
from pymatis.mt53r import MT53RAsx
from pymatis.device import MatisDevice


class MatisDeviceFactory:  # pylint: disable=too-few-public-methods
    """Matismart device factory."""

    def get_device_by_model_id(
        self,
        model: int,
        transport: MatisBaseTransport,
        address: int,
    ) -> MatisDevice:
        """Get device instance by model ID."""
        client: AsyncMatisModbusClient
        if isinstance(transport, MatisTcpTransport):
            transport.__class__ = MatisTcpTransport
            client = AsyncMatisModbusTcpClient(transport)
        elif isinstance(transport, MatisRtuTransport):
            transport.__class__ = MatisRtuTransport
            client = AsyncMatisModbusRtuClient(transport)
        else:
            raise MatisException(f"Unknown transport {transport}")

        try:
            mmodel = MatisHardwareId(model)
            if mmodel == MatisHardwareId.MT53RA_SX:
                return MT53RAsx(client, address)
            raise MatisUnknownModelException(f"Unknown device model {model}")
        except ValueError as ex:
            raise MatisUnknownModelException(f"Unknown device model {model}") from ex


factory = MatisDeviceFactory()
