# Argon Neo 5 Monitor

Home Assistant add-on for monitoring CPU temperature and handling the power button on the Argon Neo 5 case for Raspberry Pi 5.

## What this add-on does

- **CPU temperature monitoring** — logs temperature at a configurable interval
- **Power button** — configurable actions for short and long press (reboot, shutdown, or none)

## Fan control

The fan on the Argon Neo 5 connects directly to the RPi5 PWM fan header and is controlled **automatically by the HAOS kernel thermal daemon** — no configuration needed. The fan will spin up as CPU temperature rises and slow down when it cools.

## Prerequisites

No special configuration required. The add-on works out of the box on HAOS with Raspberry Pi 5.

## Installation

1. In Home Assistant go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the **three dots** (top right) → **Repositories**
3. Add:
   ```
   https://github.com/mmhantea/ha-addons
   ```
4. Find **Argon Neo 5 Monitor** → **Install**
5. Configure and **Start**

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| Update Interval | `30s` | How often to log CPU temperature |
| Short Press | `reboot` | Power button short press action |
| Long Press | `shutdown` | Power button long press action |
| Log Level | `info` | `debug`, `info`, `warning`, `error` |

### Button actions

| Action | Description |
|--------|-------------|
| `reboot` | Restarts the Raspberry Pi |
| `shutdown` | Powers off the Raspberry Pi |
| `none` | Ignores the button press |

## Troubleshooting

**Button not working:**
- Check add-on logs for `Button monitoring started on GPIO 4`
- If you see `button monitoring disabled`, GPIO access may not be available

**Temperature not logging:**
- Set log level to `debug` to see every reading
- Default `info` level logs every `update_interval` seconds
