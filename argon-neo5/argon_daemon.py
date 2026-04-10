#!/usr/bin/env python3
"""Argon Neo 5 monitor daemon for Home Assistant (RPi5).

Monitors CPU temperature and handles power button actions.
Fan control is handled automatically by the HAOS kernel thermal daemon.
"""

import argparse
import logging
import signal
import subprocess
import sys
import time
import threading

GPIO_PIN = 4

logger = logging.getLogger("argon-neo5")


def get_cpu_temp():
    """Read CPU temperature in Celsius."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except (IOError, ValueError):
        logger.error("Failed to read CPU temperature")
        return None


def execute_action(action):
    """Execute button action."""
    if action == "reboot":
        logger.info("Executing reboot...")
        subprocess.run(["/sbin/reboot"], check=False)
    elif action == "shutdown":
        logger.info("Executing shutdown...")
        subprocess.run(["/sbin/poweroff"], check=False)


def monitor_button(button_short, button_long, stop_event):
    """Monitor GPIO button presses in a background thread."""
    try:
        import gpiod
    except ImportError:
        logger.warning("gpiod not available - button monitoring disabled")
        return

    try:
        chip = gpiod.Chip("/dev/gpiochip4")
        line = chip.get_line(GPIO_PIN)
        line.request(consumer="argon-neo5", type=gpiod.LINE_REQ_DIR_IN)
        logger.info("Button monitoring started on GPIO %d", GPIO_PIN)
    except Exception as e:
        logger.warning("Could not open GPIO: %s - button monitoring disabled", e)
        return

    while not stop_event.is_set():
        try:
            if line.get_value() == 0:
                press_start = time.time()
                while line.get_value() == 0 and not stop_event.is_set():
                    time.sleep(0.001)
                duration = time.time() - press_start

                if duration < 0.03:
                    logger.info("Short press detected (%.0fms)", duration * 1000)
                    execute_action(button_short)
                elif duration < 0.05:
                    logger.info("Long press detected (%.0fms)", duration * 1000)
                    execute_action(button_long)
        except Exception as e:
            logger.debug("GPIO read error: %s", e)

        stop_event.wait(0.01)

    line.release()
    chip.close()


def main():
    parser = argparse.ArgumentParser(description="Argon Neo 5 Monitor (RPi5)")
    parser.add_argument("--update-interval", type=int, default=30)
    parser.add_argument("--button-short", default="reboot", choices=["none", "reboot", "shutdown"])
    parser.add_argument("--button-long", default="shutdown", choices=["none", "reboot", "shutdown"])
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("Argon Neo 5 daemon starting")
    logger.info("Note: Fan is controlled automatically by HAOS kernel thermal daemon")
    logger.info("Button short press: %s | Long press: %s", args.button_short, args.button_long)

    stop_event = threading.Event()

    signal.signal(signal.SIGTERM, lambda s, f: stop_event.set())
    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())

    if args.button_short != "none" or args.button_long != "none":
        threading.Thread(
            target=monitor_button,
            args=(args.button_short, args.button_long, stop_event),
            daemon=True,
        ).start()

    while not stop_event.is_set():
        temp = get_cpu_temp()
        if temp is not None:
            logger.info("CPU temperature: %.1f°C", temp)
        stop_event.wait(args.update_interval)

    logger.info("Daemon stopped")


if __name__ == "__main__":
    main()
