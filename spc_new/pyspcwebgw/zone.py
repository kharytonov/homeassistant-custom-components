import logging
from urllib.parse import urljoin

from .const import ZoneInput, ZoneType, ZoneStatus
from .utils import _load_enum

_LOGGER = logging.getLogger(__name__)


class Zone:
    """Represents an SPC alarm system zone."""
    SUPPORTED_SIA_CODES = {
        'ZO',  # ZONE OPEN
        'ZC',  # ZONE CLOSE
        'ZX',  # ZONE SHORT
        'ZD',  # ZONE DISCON
        'ZM',  # ZONE MASKED
        'BA',  # BURGLARY ALARM
        'BB',  # BURGLARY BYPASS
        'BU',  # BURGLARY UNBYPASS
        'BR',  # BURGLARY RESTORAL
        'BC',  # BURGLARY CANCEL
    }

    def __init__(self, gateway, area, spc_zone):
        self._gateway = gateway
        self._id = spc_zone['id']
        self._name = spc_zone['zone_name']
        self._area = area

        self._update(spc_zone)

    def __str__(self):
        return '{id}: {name} ({type}). Input: {inp}, status: {status}'.format(
            id=self.id, name=self.name, type=self.type,
            inp=self.input, status=self.status)

    @property
    def id(self):
        return self._id

    @property
    def unique_id(self):
        return "{}-{}".format(self.gateway.serial_number, self.id)

    @property
    def name(self):
        return self._name

    @property
    def input(self):
        return self._input

    @property
    def type(self):
        return self._type

    @property
    def status(self):
        return self._status

    @property
    def area(self):
        return self._area

    def _update(self, spc_zone, sia_code=None):
        _LOGGER.debug("Update zone %s", self.id)

        self._input = _load_enum(ZoneInput, spc_zone['input'])
        self._type = _load_enum(ZoneType, spc_zone['type'])
        self._status = _load_enum(ZoneStatus, spc_zone['status'])

    async def update_state(self, sia_code=None):
        data = await self._gateway.async_get_request("spc/zone/{}".format(self.id))
        if data:
            if isinstance(data['data']['zone'], list):
                data = data['data']['zone'][0]
            else:
                data = data['data']['zone']
            self._update(data, sia_code)
