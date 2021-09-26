import logging
from urllib.parse import urljoin

from pyspcwebgw.const import AreaMode
from pyspcwebgw.utils import _load_enum

_LOGGER = logging.getLogger(__name__)


class Area:
    """Represents and SPC alarm system area."""
    SUPPORTED_SIA_CODES = {
        'CG',  # CLOSE AREA
        'OG',  # OPEN AREA
        'BV',  # BURGLARY VERIFIED
        'CL',  # CLOSING REPORT:  Triggered at full arm
        'NL',  # PERIMETER ARMED: Triggered at part-set (perimeter)
        'OP',  # OPENING REPORT:  Triggered during unset. Except when unsetting from OnlyDown via KeyFob (maybe a bug?)
        'ZG'   # USER ACCESSING END: Workaround because unset from KeyFob/Pad doesn't trigger NL/OP codes
    }

    def __init__(self, gateway, spc_area):
        self._gateway = gateway
        self._id = spc_area['id']
        self._name = spc_area['name']
        self._verified_alarm = False
        self.zones = None

        self._update(spc_area)

    def __str__(self):
        return '{id}: {name}. Mode: {mode}, last changed by {last}.'.format(
            name=self.name, id=self.id,
            mode=self.mode, last=self.last_changed_by)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def verified_alarm(self):
        return self._verified_alarm

    @property
    def mode(self):
        return self._mode

    @property
    def last_changed_by(self):
        if self._mode == AreaMode.UNSET:
            return self._last_set_user_name
        else:
            return self._last_unset_user_name

    def _update(self, api_data, sia_code=None):
        _LOGGER.debug("Update area %s", self.id)
        self._mode = _load_enum(AreaMode, api_data['mode'])
        self._verified_alarm = sia_code == 'BV'
        self._last_set_user_name = api_data.get('last_set_user_name', 'N/A')
        self._last_unset_user_name = api_data.get('last_unset_user_name', 'N/A')

    async def update_state(self, sia_code=None):
        method = "spc/area/{}".format(self.id)
        data = await self._gateway.async_get_request(method)
        if data:
            data = data['data']['area'][0]
            self._update(data)
