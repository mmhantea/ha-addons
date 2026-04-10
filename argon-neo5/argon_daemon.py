#!/usr/bin/env python3
"""Argon Neo 5 monitor daemon for Home Assistant (RPi5).

Monitors CPU temperature.
Fan is controlled automatically by HAOS kernel thermal daemon.
Power button is handled directly by RPi5 hardware.
"""

import argparse
import logging
import signal
import time

logger = logging.getLogger("argon-neo5")


def get_cpu_temp():
    """Read CPU temperature in Celsius."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except (IOError, ValueError):
        logger.error("Failed to read CPU temperature")
        return None


def main():
    parser = argparse.ArgumentParser(description="Argon Neo 5 Monitor (RPi5)")
    parser.add_argument("--update-interval", type=int, default=30)
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("Argon Neo 5 monitor starting")
    logger.info("Fan: auto (HAOS kernel) | Button: hardware (RPi5)")

    stop = [False]
    signal.signal(signal.SIGTERM, lambda s, f: stop.__setitem__(0, True))
    signal.signal(signal.SIGINT, lambda s, f: stop.__setitem__(0, True))

    while not stop[0]:
        temp = get_cpu_temp()
        if temp is not None:
            logger.info("CPU temperature: %.1f°C", temp)
        time.sleep(args.update_interval)

    logger.info("Daemon stopped")


if __name__ == "__main__":
    main()
