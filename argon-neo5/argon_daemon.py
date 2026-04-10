#!/usr/bin/env python3
"""Argon Neo 5 fan control daemon for Home Assistant (RPi5 PWM fan)."""

import argparse
import logging
import os
import signal
import subprocess
import sys
import time
import threading

GPIO_PIN = 4
HWMON_BASE = "/sys/class/hwmon"

logger = logging.getLogger("argon-neo5")


def find_pwm_fan():
    """Find the hwmon path for pwmfan dynamically."""
    try:
        for entry in os.listdir(HWMON_BASE):
            name_path = os.path.join(HWMON_BASE, entry, "name")
            try:
                with open(name_path) as f:
                    if f.read().strip() == "pwmfan":
                        return os.path.join(HWMON_BASE, entry)
            except IOError:
                continue
    except OSError:
        pass
    return None


def get_cpu_temp():
    """Read CPU temperature in Celsius."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except (IOError, ValueError):
        logger.error("Failed to read CPU temperature")
        return None


def set_fan_speed(hwmon_path, speed_pct):
    """Set fan speed as percentage (0-100) via PWM."""
    speed_pct = max(0, min(100, int(speed_pct)))
    pwm_value = int(speed_pct / 100 * 255)

    try:
        # Enable manual PWM control
        with open(os.path.join(hwmon_path, "pwm1_enable"), "w") as f:
            f.write("1")
        # Set PWM value
        with open(os.path.join(hwmon_path, "pwm1"), "w") as f:
            f.write(str(pwm_value))
        logger.debug("Fan speed set to %d%% (PWM=%d)", speed_pct, pwm_value)
    except IOError as e:
        logger.error("Failed to set fan speed: %s", e)


def set_fan_auto(hwmon_path):
    """Return fan to automatic kernel control."""
    try:
        with open(os.path.join(hwmon_path, "pwm1_enable"), "w") as f:
            f.write("2")
        logger.info("Fan returned to automatic control")
    except IOError:
        pass


def calculate_auto_speed(temp, temp_low, temp_high):
    """Linear interpolation between temp_low (0%) and temp_high (100%)."""
    if temp <= temp_low:
        return 0
    if temp >= temp_high:
        return 100
    return int((temp - temp_low) / (temp_high - temp_low) * 100)


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
        import lgpio
    except ImportError:
        logger.warning("lgpio not available - button monitoring disabled")
        return

    try:
        h = lgpio.gpiochip_open(4)  # gpiochip4 on RPi5
        lgpio.gpio_claim_input(h, GPIO_PIN)
        logger.info("Button monitoring started on GPIO %d", GPIO_PIN)
    except Exception as e:
        logger.warning("Could not open GPIO: %s - button monitoring disabled", e)
        return

    while not stop_event.is_set():
        try:
            if lgpio.gpio_read(h, GPIO_PIN) == 0:
                press_start = time.time()
                while lgpio.gpio_read(h, GPIO_PIN) == 0 and not stop_event.is_set():
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

    lgpio.gpiochip_close(h)


def main():
    parser = argparse.ArgumentParser(description="Argon Neo 5 Fan Control (RPi5)")
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

    logger.info("Argon Neo 5 daemon starting (RPi5 PWM mode)")
    logger.info("Mode: %s | Temp range: %d-%d°C | Interval: %ds",
                args.fan_mode, args.temp_low, args.temp_high, args.update_interval)

    hwmon_path = find_pwm_fan()
    if not hwmon_path:
        logger.error("PWM fan controller not found in /sys/class/hwmon/")
        logger.error("Make sure the fan is connected to the RPi5 fan header")
        sys.exit(1)

    logger.info("PWM fan found at: %s", hwmon_path)

    stop_event = threading.Event()

    def shutdown_handler(signum, frame):
        logger.info("Shutting down - returning fan to auto control")
        set_fan_auto(hwmon_path)
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
            set_fan_speed(hwmon_path, speed)
            last_speed = speed
        else:
            logger.debug("CPU: %.1f°C → Fan: %d%% (unchanged)", temp, speed)

        stop_event.wait(args.update_interval)

    logger.info("Daemon stopped")


if __name__ == "__main__":
    main()
