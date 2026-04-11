# 1. Installation Guide

## Option A: Manual Installation (Recommended)

Add the repository directly to Home Assistant without HACS.

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Click **⋯** (top right) → **Repositories**
3. Enter:
   ```
   https://github.com/mmhantea/ha-addons
   ```
4. Click **Add** → **Close**
5. Find the add-on in the store and click **Install**
6. Configure and **Start**

## Option B: Via HACS

Use HACS (Home Assistant Community Store) for automatic updates and easy management.

### Prerequisites

HACS must be installed first. If you don't have it:

1. Go to **Settings** → **Apps** → **Install app**
2. Search for **Get HACS** → **Install**
3. Follow the setup instructions in the app logs
4. Restart Home Assistant when done

### Adding This Repository

1. Open HACS (left sidebar)
2. Click **Add-ons** → **⋯** → **Custom repositories**
3. Enter:
   ```
   https://github.com/mmhantea/ha-addons
   ```
4. Select category: **Add-ons** → **Add**
5. Find "Argon Neo 5 Monitor" → **Install**
6. Configure and **Start**

## Troubleshooting

**Add-on not appearing:**
- Refresh the page (F5)
- Check the URL is correct
- Restart Home Assistant if needed

**Installation fails:**
- Check **Settings** → **System** → **Logs** for errors
- Ensure you have enough disk space
- Try uninstalling and reinstalling

**HACS not found after install:**
- Restart Home Assistant completely
- Clear browser cache (Ctrl+Shift+Delete)
