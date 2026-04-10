#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

bashio::log.info "Starting Argon Neo 5 Fan Control..."

# Enable I2C if not already enabled (one-time configuration)
bashio::log.info "Checking I2C configuration..."
if ! grep -q "dtparam=i2c_arm=on" /mnt/boot/firmware/config.txt 2>/dev/null; then
    bashio::log.info "Enabling I2C in boot configuration..."
    if mount /dev/nvme0n1p1 /mnt 2>/dev/null; then
        echo "dtparam=i2c_arm=on" >> /mnt/config.txt
        umount /mnt
        bashio::log.info "I2C enabled. Rebooting system..."
        sleep 2
        /sbin/reboot
        exit 0
    else
        bashio::log.warning "Could not mount boot partition. I2C may need manual configuration."
    fi
else
    bashio::log.info "I2C is already configured."
fi

# Read configuration from HA
FAN_MODE=$(bashio::config 'fan_mode')
TEMP_LOW=$(bashio::config 'temp_low')
TEMP_HIGH=$(bashio::config 'temp_high')
MANUAL_SPEED=$(bashio::config 'manual_speed')
UPDATE_INTERVAL=$(bashio::config 'update_interval')
BUTTON_SHORT=$(bashio::config 'button_short_press')
BUTTON_LONG=$(bashio::config 'button_long_press')
LOG_LEVEL=$(bashio::config 'log_level')

bashio::log.info "Fan mode: ${FAN_MODE}"
bashio::log.info "Temperature range: ${TEMP_LOW}°C - ${TEMP_HIGH}°C"
bashio::log.info "Button short press: ${BUTTON_SHORT}"
bashio::log.info "Button long press: ${BUTTON_LONG}"

# Check I2C device
if ! i2cdetect -y 1 2>/dev/null | grep -q "1a"; then
    bashio::log.warning "Argon Neo 5 not detected on I2C bus 1 (address 0x1a)"
    bashio::log.warning "Make sure I2C is enabled and the case is properly connected"
fi

# Launch daemon
exec python3 /argon_daemon.py \
    --fan-mode "${FAN_MODE}" \
    --temp-low "${TEMP_LOW}" \
    --temp-high "${TEMP_HIGH}" \
    --manual-speed "${MANUAL_SPEED}" \
    --update-interval "${UPDATE_INTERVAL}" \
    --button-short "${BUTTON_SHORT}" \
    --button-long "${BUTTON_LONG}" \
    --log-level "${LOG_LEVEL}"
