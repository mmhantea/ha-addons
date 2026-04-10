#!/usr/bin/env python3
"""Argon Neo 5 fan control daemon for Home Assistant."""

import argparse
import logging
import signal
import subprocess
import sys
import time
import threading

I2C_BUS = 1
I2C_ADDR = 0x1A
FAN_REGISTER = 0x00
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


def set_fan_speed(bus, speed):
    """Set fan speed (0-100)."""
    speed = max(0, min(100, int(speed)))
    try:
        bus.write_byte_data(I2C_ADDR, FAN_REGISTER, speed)
        logger.debug("Fan speed set to %d%%", speed)
    except IOError:
        logger.error("Failed to set fan speed via I2C")


def calculate_auto_speed(temp, temp_low, temp_high):
    """Linear interpolation between temp_low (0%) and temp_high (100%)."""
    if temp <= temp_low:
        return 0
    if temp >= temp_high:
        return 100
    return int((temp - temp_low) / (temp_high - temp_low) * 100)


def execute_action(action):
    """Execute button action using subprocess with fixed commands."""
    if action == "reboot":
        logger.info("Executing reboot...")
        subprocess.run(["/sbin/reboot"], check=False)
    elif action == "shutdown":
        logger.info("Executing shutdown...")
        subprocess.run(["/sbin/poweroff"], check=False)
    else:
        logger.debug("Button action: none")


def monitor_button(button_short, button_long, stop_event):
    """Monitor GPIO button presses in a background thread."""
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        logger.warning("RPi.GPIO not available - button monitoring disabled")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    logger.info("Button monitoring started on GPIO %d", GPIO_PIN)

    while not stop_event.is_set():
        if GPIO.input(GPIO_PIN) == 0:
            press_start = time.time()
            while GPIO.input(GPIO_PIN) == 0 and not stop_event.is_set():
                time.sleep(0.001)
            duration = time.time() - press_start

            if duration < 0.03:
                logger.info("Short press detected (%.0fms)", duration * 1000)
                execute_action(button_short)
            elif duration < 0.05:
                logger.info("Long press detected (%.0fms)", duration * 1000)
                execute_action(button_long)
            else:
                logger.debug("Ignored press (%.0fms)", duration * 1000)

        stop_event.wait(0.01)

    GPIO.cleanup(GPIO_PIN)


def main():
    parser = argparse.ArgumentParser(description="Argon Neo 5 Fan Control")
    parser.add_argument("--fan-mode", default="auto", choices=["auto", "manual", "off"])
    parser.add_argument("--temp-low", type=int, default=45)
    parser.add_argument("--temp-high", type=int, default=65)
    parser.add_argument("--manual-speed", type=int, default=50)
    parser.add_argument("--update-interval", type=int, default=10)
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
    logger.info("Mode: %s | Temp range: %d-%d°C | Interval: %ds",
                args.fan_mode, args.temp_low, args.temp_high, args.update_interval)

    try:
        from smbus2 import SMBus
        bus = SMBus(I2C_BUS)
    except Exception as e:
        logger.error("Failed to open I2C bus %d: %s", I2C_BUS, e)
        logger.error("Make sure I2C is enabled and /dev/i2c-1 is accessible")
        sys.exit(1)

    stop_event = threading.Event()

    # Graceful shutdown: turn off fan
    def shutdown_handler(signum, frame):
        logger.info("Shutting down - setting fan to 0%%")
        try:
            set_fan_speed(bus, 0)
        except Exception:
            pass
        stop_event.set()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    # Start button monitoring thread
    if args.button_short != "none" or args.button_long != "none":
        button_thread = threading.Thread(
            target=monitor_button,
            args=(args.button_short, args.button_long, stop_event),
            daemon=True,
        )
        button_thread.start()

    # Main fan control loop
    last_speed = -1
    while not stop_event.is_set():
        temp = get_cpu_temp()
        if temp is None:
            stop_event.wait(args.update_interval)
            continue

        if args.fan_mode == "auto":
            speed = calculate_auto_speed(temp, args.temp_low, args.temp_high)
        elif args.fan_mode == "manual":
            speed = args.manual_speed
        else:
            speed = 0

        if speed != last_speed:
            logger.info("CPU: %.1f°C → Fan: %d%%", temp, speed)
            set_fan_speed(bus, speed)
            last_speed = speed
        else:
            logger.debug("CPU: %.1f°C → Fan: %d%% (unchanged)", temp, speed)

        stop_event.wait(args.update_interval)

    bus.close()
    logger.info("Daemon stopped")


if __name__ == "__main__":
    main()
