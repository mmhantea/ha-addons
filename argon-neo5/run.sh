#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

bashio::log.info "Starting Argon Neo 5 Fan Control..."

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
