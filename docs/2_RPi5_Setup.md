# 2. Raspberry Pi 5 HAOS Setup

Configuration guide for Raspberry Pi 5 with Argon Neo 5 case and Home Assistant monitoring.

## System Monitor Integration

**System Monitor** provides sensors for CPU temperature, memory usage, disk space, and network traffic.

### Installation

1. **Settings** → **Devices & Services** → **+ Add Integration**
2. Search for **System Monitor**
3. Click **Create**
4. No additional configuration needed

### Enable Sensors

1. Go to **Settings** → **Devices & Services** → **System Monitor**
2. Click on the device
3. Enable the sensors you want:
   - **Processor temperature** — CPU temperature (essential for fan monitoring)
   - **Memory usage** — RAM usage percentage
   - **Disk usage** — Storage usage percentage
   - **Network in/out** — Network traffic per interface (wlan0, end0)
   - **pwmfan fan speed** — Argon Neo 5 fan RPM (if available)

## Network Configuration

RPi5 HAOS supports:
- **wlan0** — WiFi
- **end0** — Ethernet (Gigabit)

### Static IP (Recommended)

1. Go to **Settings** → **System** → **Network**
2. Click your network interface (WiFi or Ethernet)
3. Configure:
   - IPv4 method: **Static**
   - Address: `192.168.1.132` (or your preferred IP)
   - Gateway: `192.168.1.1` (your router's IP)
   - DNS: `8.8.8.8, 8.8.4.4`
4. Click **Save**

## Fan Control

The Argon Neo 5 fan is controlled automatically by HAOS kernel thermal daemon:
- **Auto-enabled** — no configuration needed
- Fan connects directly to RPi5 PWM header
- Fan spins up as CPU temperature rises
- Runs at 0% RPM when CPU is cool (under ~45°C)

No manual configuration required — the fan works out of the box.

## Troubleshooting

**System Monitor sensors show "unavailable":**
- Restart Home Assistant: **Settings** → **System** → **Restart Home Assistant**
- Wait 2-3 minutes for sensors to initialize
- Ensure integration is properly enabled

**Network not connecting:**
- Check cable connection (if using Ethernet)
- Restart network: **Settings** → **System** → **Network** → **Restart networking**
- Verify SSID and password if using WiFi

**High temperature:**
- Ensure fan cable is properly connected to RPi5 PWM header
- Check airflow around the case
- Clean dust from case vents
- Temperature above 80°C may trigger CPU throttling

**Fan not spinning:**
- Verify cable is firmly connected to PWM header
- Check System Monitor → **pwmfan fan speed** for current RPM
- If 0 RPM at high temp, check cable or pwmfan hardware issue
