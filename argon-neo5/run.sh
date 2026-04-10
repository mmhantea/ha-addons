#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

bashio::log.info "Starting Argon Neo 5 Monitor..."
bashio::log.info "Fan: controlled by HAOS kernel | Button: handled by RPi5 hardware"

UPDATE_INTERVAL=$(bashio::config 'update_interval')
LOG_LEVEL=$(bashio::config 'log_level')

exec python3 /argon_daemon.py \
    --update-interval "${UPDATE_INTERVAL}" \
    --log-level "${LOG_LEVEL}"
