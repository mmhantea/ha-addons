#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

bashio::log.info "Starting Argon Neo 5 Monitor..."

UPDATE_INTERVAL=$(bashio::config 'update_interval')
BUTTON_SHORT=$(bashio::config 'button_short_press')
BUTTON_LONG=$(bashio::config 'button_long_press')
LOG_LEVEL=$(bashio::config 'log_level')

bashio::log.info "Button short press: ${BUTTON_SHORT}"
bashio::log.info "Button long press: ${BUTTON_LONG}"
bashio::log.info "Fan control: handled automatically by HAOS kernel"

exec python3 /argon_daemon.py \
    --update-interval "${UPDATE_INTERVAL}" \
    --button-short "${BUTTON_SHORT}" \
    --button-long "${BUTTON_LONG}" \
    --log-level "${LOG_LEVEL}"
