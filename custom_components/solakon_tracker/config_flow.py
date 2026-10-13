from __future__ import annotations

from urllib.parse import urlsplit

import voluptuous as vol
from aiohttp import ClientError

from homeassistant.config_entries import ConfigFlow
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_HOST,
    CONF_UPDATE_INTERVAL,
    DEFAULT_HOST,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    STATUS_PATH,
)


def _normalize_host(value: str) -> str:
    host = value.strip().rstrip("/")
    if "://" not in host:
        host = f"http://{host}"
    parsed = urlsplit(host)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Enter a valid device host")
    parsed.port
    return f"{parsed.scheme}://{parsed.netloc}"


async def _validate_host(hass: HomeAssistant, host: str) -> None:
    session = async_get_clientsession(hass)
    async with session.get(f"{host}{STATUS_PATH}") as response:
        response.raise_for_status()
        payload = await response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("extracted"), dict):
        raise ValueError("Unexpected status response")


class SolakonConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_reconfigure(self, user_input: dict | None = None):
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                host = _normalize_host(user_input[CONF_HOST])
                await _validate_host(self.hass, host)
            except (ValueError, ClientError, OSError):
                errors["base"] = "cannot_connect"
            else:
                if host != entry.data[CONF_HOST]:
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_HOST: host,
                        CONF_UPDATE_INTERVAL: int(user_input[CONF_UPDATE_INTERVAL]),
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=entry.data.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=5,
                            max=3600,
                            step=1,
                            unit_of_measurement="s",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                host = _normalize_host(user_input[CONF_HOST])
                await _validate_host(self.hass, host)
            except (ValueError, ClientError, OSError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Solakon Tracker",
                    data={
                        CONF_HOST: host,
                        CONF_UPDATE_INTERVAL: int(user_input[CONF_UPDATE_INTERVAL]),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(
                        CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=5,
                            max=3600,
                            step=1,
                            unit_of_measurement="s",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )