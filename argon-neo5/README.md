# Argon Neo 5 Fan Control

Home Assistant add-on for controlling the fan and power button on the Argon Neo 5 case for Raspberry Pi 5.

## Features

- **Automatic fan control** — adjusts speed based on CPU temperature with configurable thresholds
- **Manual mode** — set a fixed fan speed
- **Power button** — configurable actions for short and long press (reboot, shutdown, or none)
- **Graceful shutdown** — fan turns off when the add-on stops

## Prerequisites

I2C must be enabled on your Raspberry Pi 5. Add to `/boot/config.txt`:

```
dtparam=i2c_arm=on
```

Reboot after making this change.

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| Fan Mode | `auto` | `auto`, `manual`, or `off` |
| Temperature Low | `45°C` | Fan off below this temp (auto mode) |
| Temperature High | `65°C` | Fan at 100% above this temp (auto mode) |
| Manual Speed | `50%` | Fixed speed in manual mode |
| Update Interval | `10s` | Temperature check frequency |
| Short Press | `reboot` | Power button short press action |
| Long Press | `shutdown` | Power button long press action |
| Log Level | `info` | `debug`, `info`, `warning`, `error` |

### Auto mode behavior

The fan speed is linearly interpolated between the low and high temperature thresholds:

- Below **temp_low** → fan off (0%)
- At **temp_high** → fan at 100%
- Between → proportional speed

Example with defaults (45-65°C): at 55°C the fan runs at 50%.

## Troubleshooting

### Verify hardware detection

```bash
i2cdetect -y 1
```

You should see `1a` in the output grid. If not:
- Check that I2C is enabled in `/boot/config.txt`
- Verify the case is properly connected

### Check add-on logs

Go to **Settings** → **Add-ons** → **Argon Neo 5 Fan Control** → **Log** tab.

Set log level to `debug` for detailed temperature and fan speed readings.

### Manual fan test

```bash
# Set fan to 75%
i2cset -y 1 0x1a 0x00 75

# Turn off
i2cset -y 1 0x1a 0x00 0
```

## Technical Details

- I2C address: `0x1a` on bus 1
- Fan speed range: 0-100 (percentage)
- Button GPIO: pin 4 (BCM)
- Temperature source: `/sys/class/thermal/thermal_zone0/temp`
