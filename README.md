# Solakon Tracker for Home Assistant

This custom integration polls a Solakon device's local status API every 30 seconds:

`http://<device-host>/api/v1/status`

## Installation
### via HACS
add https://github.com/traukainehm/solakon-tracker as custom repository to HACS, install as integration

### Manual Installation
Copy `custom_components/solakon_tracker` into the `custom_components` directory of your Home Assistant configuration, then restart Home Assistant. Add **Solakon Tracker** from **Settings > Devices & services > Add integration** and enter the device's base URL, for example `http://192.168.188.114`.

## Entities

The integration creates sensors for instantaneous total and per-phase power, positive and returned energy totals, meter identification, and device hardware, firmware, serial number, Wi-Fi MAC address, and uptime. Device-information entities are marked as diagnostics. The polling interval defaults to 30 seconds and can be set from 5 to 3600 seconds during setup or reconfiguration.

The integration currently consumes `/api/v1/status`; additional API paths can be added when their URLs and response formats are available.
