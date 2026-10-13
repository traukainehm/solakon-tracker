from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, STATUS_PATH, UPDATE_INTERVAL


class SolakonCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, host: str) -> None:
        self.host = host
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self.session.get(f"{self.host}{STATUS_PATH}") as response:
                response.raise_for_status()
                payload = await response.json()
        except (ClientError, OSError, ValueError) as err:
            raise UpdateFailed(f"Unable to fetch Solakon status: {err}") from err

        if not isinstance(payload, dict):
            raise UpdateFailed("Solakon returned an invalid status response")
        return payload