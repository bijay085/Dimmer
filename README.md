# 🖥️ Screen Dimmer

A powerful and user-friendly screen dimming application for Windows with blue light filtering, scheduled dimming, blink reminders, and multi-display support.

![Version](https://img.shields.io/badge/version-1.1-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2B-lightgrey)
![Python](https://img.shields.io/badge/python-3.7%2B-green)
![License](https://img.shields.io/badge/license-Free-brightgreen)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔆 **Screen Dimming** | Reduce screen brightness to protect your eyes |
| 🔵 **Blue Light Filter** | Warm orange tint to reduce eye strain and improve sleep |
| ⏰ **Scheduled Dimming** | Automatically dim your screen at specific times |
| ✨ **Blink Reminder** | Get reminded to blink and rest your eyes |
| 🖥️ **Multi-Display Support** | Control dimming for multiple monitors independently |
| ⌨️ **Keyboard Shortcuts** | Quick access with global hotkeys |
| 💾 **Custom Profiles** | Save your favorite dimming settings |
| 🔔 **System Tray** | Runs quietly in the background |

---

## 📋 Requirements

| Requirement | Details |
|-------------|---------|
| **OS** | Windows 10 or later |
| **Python** | 3.7+ (only for .py/.pyw files) |
| **Dependencies** | PyQt5, keyboard (optional) |

---

## 🚀 Installation

### Method 1: Git Clone (Recommended for Developers)

```bash
# Clone the repository
git clone https://github.com/bijay085/Dimmer.git

# Navigate to the directory
cd Dimmer

# Install dependencies (for .py/.pyw files)
pip install PyQt5 keyboard
```

### Method 2: Direct Download

1. Go to [https://github.com/bijay085/Dimmer](https://github.com/bijay085/Dimmer)
2. Click the green **Code** button
3. Select **Download ZIP**
4. Extract the ZIP file to your desired location

---

## 📦 Available File Formats

| File | Python Required | Console Window | Best For |
|------|-----------------|----------------|----------|
| `ScreenDimmer.exe` | ❌ No | ❌ No | General users - just download and run |
| `dimmer.pyw` | ✅ Yes | ❌ No | System tray & background use |
| `dimmer.py` | ✅ Yes | ✅ Yes | Debugging & development |

---

## 🎮 How to Run

### Option A: Standalone EXE (Easiest - No Python Needed)

```
1. Download ScreenDimmer.exe from the repository
2. Double-click ScreenDimmer.exe
3. Done! The app starts immediately
```

> ⚠️ **Note**: Windows may show a security warning. Click **More info** → **Run anyway**

### Option B: Python Script (.pyw) - Perfect for System Tray

```bash
# First, install dependencies (one-time setup)
pip install PyQt5 keyboard

# Run the application (no console window)
pythonw dimmer.pyw

# Or simply double-click dimmer.pyw in File Explorer
```

### Option C: Python Script (.py) - For Debugging

```bash
# Install dependencies
pip install PyQt5 keyboard

# Run with console output
python dimmer.py
```

---

## ⚙️ First-Time Setup

### Step 1: Install Python (Skip if using EXE)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Important**: Check ✅ "Add Python to PATH" during installation
3. Complete the installation

### Step 2: Install Dependencies (Skip if using EXE)

Open Command Prompt or PowerShell:

```bash
pip install PyQt5 keyboard
```

> 💡 **Tip**: The `keyboard` package enables global hotkeys. Without it, shortcuts only work when the app is focused.

### Step 3: Verify Installation

```bash
# Check Python version
python --version

# Should show: Python 3.7.x or higher
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Alt+D** | Toggle dimmer on/off |
| **Alt+R** | Toggle blinker on/off |
| **Alt+G** | Temporarily hide overlay (for gestures) |

> 🔑 Global hotkeys require the `keyboard` package

---

## 📖 User Guide

### Main Tab - Basic Controls

**Enable/Disable Dimmer**
- Click the **⚡ Enable Dimmer** button
- Or press **Alt+D** anywhere

**Adjust Brightness**
- Use the slider (0-95%)
- Quick presets: 15%, 30%, 50%, 80%

**Blue Light Filter**
1. Check **Enable Blue Light Filter**
2. Adjust intensity (0-100%)
3. Higher = warmer orange tint

### Schedule Tab - Automatic Dimming

**Presets Available:**
- ☀️ **All Day**: 6 AM - 6 PM
- 🌙 **All Night**: 6 PM - 6 AM
- ⚙️ **Custom**: Set your own times
- ⏱️ **Timer**: Quick countdown timer

**How to Use:**
1. Click a preset button
2. Click **🚀 Enable Schedule**
3. Dimmer activates automatically at scheduled time

### Blinker Tab - Eye Rest Reminders

**Setup:**
1. Set interval (1-60 minutes)
2. Set duration (1-30 seconds)
3. Enable emoji/text reminders
4. Click **🚀 Enable Blinker**

### 2nd Display Tab

**For Multi-Monitor Setups:**
1. Check **Enable 2nd Display Dimming**
2. Adjust brightness independently
3. Enable separate blue light filter

---

## 💡 Recommended Settings

| Activity | Dimming | Blue Light |
|----------|---------|------------|
| Reading | 50-70% | 60-80% |
| Gaming | 30-50% | Off |
| Movies | 60-80% | 40-60% |
| Night Work | 70-85% | 70-100% |

---

## 🔧 Auto-Start on Windows Boot

### For EXE File:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a shortcut to `ScreenDimmer.exe` in this folder

### For PYW File:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a shortcut with target: `pythonw "C:\path\to\dimmer.pyw"`

---

## 🔔 System Tray Usage

- **Left-click** tray icon → Show/Hide window
- **Right-click** tray icon → Context menu
- Close window → App keeps running in tray

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Ensure Python is in PATH. Run `python dimmer.py` to see errors |
| "Module not found" | Run `pip install PyQt5 keyboard` |
| Screen doesn't dim | Check if dimmer is enabled (button should be green) |
| Hotkeys not working | Install keyboard package: `pip install keyboard` |
| Blue light too orange | Lower intensity to 30-50% |
| Schedule not activating | Ensure "Enable Schedule" is clicked after selecting preset |

---

## 📁 Files Created by App

| File | Purpose |
|------|---------|
| `dimmer_profiles.json` | Saved profiles |
| `dimmer_stats.json` | Current settings & state |

---

## 🛠️ Development

### Project Structure

```
Dimmer/
├── ScreenDimmer.exe    # Standalone executable
├── dimmer.py           # Python script (with console)
├── dimmer.pyw          # Python script (no console)
├── README.md           # This file
├── dimmer_profiles.json # User profiles (auto-generated)
└── dimmer_stats.json   # App state (auto-generated)
```

### Building EXE from Source

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ScreenDimmer dimmer.py
```

---

## 📝 Changelog

### v1.1
- Added multi-display support
- Added blink reminder with rain effects
- Added scheduled dimming presets
- Improved blue light filter
- Added global hotkeys
- Performance optimizations

---

## 👨‍💻 Author

**Bijay Koirala**

- 🌐 Website: [bijaykoirala0.com.np](https://bijaykoirala0.com.np)
- 📱 Telegram: [@flamemodparadise](https://t.me/flamemodparadise)
- 🐙 GitHub: [bijay085](https://github.com/bijay085)

---

## 📄 License

Free to use for personal and commercial purposes.

---

## ⚠️ Disclaimer

This tool provides screen dimming and blue light filtering for eye comfort only. It is not a medical device. Use responsibly and take regular breaks from screens.

---

**Enjoy your dimmed, eye-friendly screen!** 👀✨
