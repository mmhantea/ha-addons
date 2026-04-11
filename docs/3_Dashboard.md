# 3. Create Monitoring Dashboard

Set up a comprehensive dashboard for monitoring your Raspberry Pi 5 and Argon Neo 5.

## Prerequisites

- System Monitor integration installed and enabled (see [2_RPi5_Setup.md](2_RPi5_Setup.md))
- At least these sensors activated:
  - `sensor.system_monitor_processor_temperature`
  - `sensor.system_monitor_memory_usage`
  - `sensor.system_monitor_disk_usage`
  - `sensor.system_monitor_network_in_wlan0`
  - `sensor.system_monitor_network_out_wlan0`
  - `sensor.system_monitor_pwmfan_fan_speed` (optional)

## Creating the Dashboard

### Step 1: Create New Dashboard

1. **Dashboards** → **Create Dashboard**
2. Give it a name: `RPi5 Monitor`
3. Click **Create**

### Step 2: Add Configuration

1. Click the **✏️ (edit)** button (top right)
2. Click **≡ (menu)** → **Edit Dashboard**
3. Click **Raw configuration editor**
4. Copy and paste this YAML:

```yaml
title: RPi5 Monitor
views:
  - path: default
    title: System
    cards:
      - type: entities
        title: CPU & Temperature
        entities:
          - entity: sensor.system_monitor_processor_temperature
            name: CPU Temperature

      - type: entities
        title: Memory & Disk
        entities:
          - entity: sensor.system_monitor_memory_usage
            name: Memory Usage
          - entity: sensor.system_monitor_disk_usage
            name: Disk Usage

      - type: entities
        title: Network (WiFi)
        entities:
          - entity: sensor.system_monitor_network_in_wlan0
            name: In
          - entity: sensor.system_monitor_network_out_wlan0
            name: Out

      - type: entities
        title: Network (Ethernet)
        entities:
          - entity: sensor.system_monitor_network_in_end0
            name: In
          - entity: sensor.system_monitor_network_out_end0
            name: Out

      - type: entities
        title: Fan
        entities:
          - entity: sensor.system_monitor_pwmfan_fan_speed
            name: Speed
```

### Step 3: Save

1. Click **Save** (top right)
2. Click **Close** (top right)
3. Dashboard is now live!

## Customization

### Add More Sensors

Edit dashboard in raw mode and add entities under any card:

```yaml
      - type: entities
        title: Custom Section
        entities:
          - entity: sensor.some_sensor
            name: Label
          - entity: sensor.another_sensor
            name: Another Label
```

### Change Card Type

Replace `type: entities` with:
- `type: gauge` — circular gauge (good for percentages)
- `type: history-stats` — historical graph
- `type: mini-graph-card` — time-series chart (requires card)

Example gauge card for memory:
```yaml
      - type: gauge
        title: Memory Usage
        min: 0
        max: 100
        unit_of_measurement: "%"
        entity: sensor.system_monitor_memory_usage
```

## Finding All Available Sensors

1. Go to **Developer Tools** → **States**
2. Filter by `sensor.system_monitor_`
3. See all available sensors with current values
4. Use entity IDs in your dashboard YAML

## Tips

- **Refresh rate**: Entities update every 60 seconds by default
- **Mobile**: Dashboard adapts to mobile screens automatically
- **Automations**: Use these sensors in automations (e.g., notify if CPU > 85°C)
- **History**: Click on any sensor card to see historical data and trends
