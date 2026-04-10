# Changelog

## 1.0.4

- Rewritten fan control to use RPi5 native PWM fan header (no I2C required)
- Fan controlled via /sys/class/hwmon/pwmfan (hwmon3/pwm1)
- PWM fan path detected dynamically at startup
- Button monitoring via lgpio (RPi5 compatible)
- Removed smbus2 and i2c-tools dependencies

## 1.0.3

- Reverted I2C auto-configuration attempts from run.sh
- Removed full_access and SYS_ADMIN privileges added in 1.0.2

## 1.0.2

- Added SYS_ADMIN privilege and full_access to attempt boot partition mount
- Attempt to auto-enable I2C at addon startup (unsuccessful)

## 1.0.1

- Added automatic I2C enablement at startup via boot partition mount
- Added build.yaml to enable local Docker build on Home Assistant

## 1.0.0

- Initial release
- Automatic fan control based on CPU temperature (linear interpolation)
- Manual fan speed mode
- Configurable temperature thresholds
- Power button support (short/long press → reboot/shutdown/none)
- Configurable update interval and log level
