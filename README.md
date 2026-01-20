# Screen Dimmer 📱

A powerful and user-friendly screen dimming application for Windows with blue light filtering, scheduled dimming, blink reminders, and multi-display support.

## ✨ Features

- **🔆 Screen Dimming** - Reduce screen brightness to protect your eyes
- **🔵 Blue Light Filter** - Warm orange tint to reduce eye strain and improve sleep
- **⏰ Scheduled Dimming** - Automatically dim your screen at specific times
- **✨ Blink Reminder** - Get reminded to blink and rest your eyes
- **🖥️ Multi-Display Support** - Control dimming for multiple monitors independently
- **⌨️ Keyboard Shortcuts** - Quick access with hotkeys
- **💾 Custom Profiles** - Save your favorite dimming settings
- **🔔 System Tray Integration** - Runs quietly in the background

---

## 📋 Requirements

- **Operating System**: Windows 10 or later

### For EXE File (Standalone):
- **No additional requirements!** Just download and run
- No Python installation needed
- No package installation needed
- Everything is bundled in the EXE file

### For PYW/PY Files:
- **Python**: Python 3.7 or higher
- **Required Python Packages**:
  - `PyQt5` - For the user interface
  - `keyboard` (optional) - For global hotkeys (works without it, but hotkeys will only work when the app window is focused)

---

## 🚀 Installation

### Step 1: Install Python

If you don't have Python installed:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Complete the installation

### Step 2: Install Required Packages (Only for PYW/PY files)

**Skip this step if you're using the EXE file!**

If you're using `dimmer.pyw` or `dimmer.py`, open Command Prompt or PowerShell and run:

```bash
pip install PyQt5 keyboard
```

**Note**: If you don't install `keyboard`, the app will still work, but global hotkeys (Alt+D, Alt+R, Alt+G) will only work when the app window is focused.

### Step 3: Download the Application

You have **three options** to run Screen Dimmer:

**Option A: Standalone EXE (Easiest - No Python Required!)**
- Download `ScreenDimmer.exe` 
- **No Python installation needed!**
- Just double-click and run
- Perfect for users who don't want to install Python

**Option B: Python Script (PYW) - Great for System Tray!**
- Download `dimmer.pyw` 
- Runs without showing a command window (perfect for background use)
- Easy to keep running in system tray
- Requires Python installed (see Step 1)
- Double-click to run silently - perfect for auto-starting
- Best choice if you want it running all the time in the background

**Option C: Python Script (PY)**
- Download `dimmer.py`
- Requires Python installed (see Step 1)
- Shows command window when running
- Best for debugging

**Recommendations**:
- **EXE file** - Simplest if you don't want to install Python
- **PYW file** - Best for system tray and background use (easy after installing dependencies once)
- **PY file** - Best for debugging or seeing console output

---

## 🎮 How to Run

### Method 1: Standalone EXE (Recommended - No Python Needed!)

1. Download `ScreenDimmer.exe`
2. Double-click `ScreenDimmer.exe`
3. That's it! The app will start immediately
4. **No Python installation required!**

**Note**: Windows may show a security warning the first time you run it. Click "More info" → "Run anyway" if you trust the file.

### Method 2: Python Windowless Script (PYW) - Perfect for System Tray!

1. Download `dimmer.pyw`
2. Make sure Python is installed (see Installation Step 1)
3. Install dependencies: `pip install PyQt5 keyboard` (see Installation Step 2)
4. Double-click `dimmer.pyw`
5. The app runs silently without showing a command window
6. **Perfect for keeping it running in the system tray!**
7. You can add it to Windows startup for automatic launch

**Tip**: After installing dependencies once, PYW files are very easy to use - just double-click and it runs in the background!

### Method 3: Python Script (PY)

1. Download `dimmer.py`
2. Make sure Python is installed (see Installation Step 1)
3. Install dependencies: `pip install PyQt5 keyboard` (see Installation Step 2)
4. Double-click `dimmer.py` or run from command line: `python dimmer.py`
5. Shows command window (useful for debugging)

### Method 4: Command Line (For PY/PYW files)

1. Open Command Prompt or PowerShell
2. Navigate to the folder: `cd C:\ScreenDimmer` (or your folder path)
3. Run: 
   - For `.py`: `python dimmer.py`
   - For `.pyw`: `pythonw dimmer.pyw` (no window)

### Method 5: Create a Shortcut (For EXE/PYW/PY files)

**For EXE file:**
1. Right-click `ScreenDimmer.exe`
2. Select "Create shortcut"
3. Double-click the shortcut anytime to run!

**For PYW/PY files:**
1. Right-click `dimmer.pyw` or `dimmer.py`
2. Select "Create shortcut"
3. Right-click the shortcut → Properties
4. In "Target", add `python` or `pythonw` before the path:
   - For `.py`: `python "C:\ScreenDimmer\dimmer.py"`
   - For `.pyw`: `pythonw "C:\ScreenDimmer\dimmer.pyw"`
5. Click OK
6. Double-click the shortcut anytime to run!

---

## 📖 User Guide

### First Launch

When you first open Screen Dimmer:
- The app window will appear
- An icon will appear in your system tray (bottom-right corner)
- The app runs in the background - you can minimize it!

### Main Window Tabs

The app has 4 main tabs:

1. **⚡ Main** - Basic dimming controls
2. **🕐 Schedule** - Automatic scheduled dimming
3. **✨ Blinker** - Eye rest reminders
4. **🖥️ 2nd Display** - Control additional monitors

---

## ⚡ Main Tab - Basic Controls

### Enable/Disable Dimmer

1. Click the **"⚡ Enable Dimmer"** button (turns green when active)
2. Or press **Alt+D** anywhere on your computer (if keyboard module is installed)

### Adjust Dimming Level

- Use the **brightness slider** (0-95%)
- Lower = darker screen
- Higher = lighter screen
- Try the preset buttons: **25%**, **50%**, **75%**, **95%**

### Blue Light Filter

**What is it?**
- Adds a warm orange tint to your screen
- Reduces blue light that can cause eye strain
- Helps you sleep better at night

**How to use:**
1. Check the **"🔵 Enable Blue Light Filter"** checkbox
2. Adjust the **intensity slider** (0-100%)
   - 0% = No tint (completely clear)
   - 50% = Moderate warm tint
   - 100% = Strong warm orange tint
3. Works great for evening/night use!

### Profiles

**Save your favorite settings:**
1. Adjust dimming level and blue light to your liking
2. Click **"💾 Save Profile"**
3. Enter a name (e.g., "Night Reading")
4. Click OK

**Load a saved profile:**
- Click any profile button (Night Mode, Reading, Gaming, Movie)
- Or select from the dropdown and click "Load Profile"

**Delete a profile:**
- Select the profile from dropdown
- Click "🗑️ Delete Profile"

---

## 🕐 Schedule Tab - Automatic Dimming

Set your screen to automatically dim at specific times!

### Quick Setup (Presets)

**All Day (6 AM - 6 PM)**
- Click **"🌅 All Day"** button
- Screen dims during daytime hours
- Click **"🚀 Enable Schedule"** to activate

**All Night (6 PM - 6 AM)**
- Click **"🌙 All Night"** button
- Screen dims during nighttime hours
- Click **"🚀 Enable Schedule"** to activate

**Custom Schedule**
- Click **"⚙️ Custom"** button
- Set your **Start Time** (when dimming begins)
- Set your **End Time** (when dimming ends)
- Adjust **Dim Level** (how dark it gets)
- Click **"🚀 Enable Schedule"** to activate

### How It Works

- When the schedule is **active** and it's within your time range, the screen automatically dims
- When it's outside the time range, dimming turns off automatically
- The schedule display shows when it will start/end

### Enable/Disable Schedule

- Click **"🚀 Enable Schedule"** to turn it on
- Click **"⏹️ Disable Schedule"** to turn it off
- The status will show "Enabled" or "Disabled"

---

## ✨ Blinker Tab - Eye Rest Reminders

Get reminded to blink and rest your eyes!

### Setup

1. **Set Interval** - How often you want reminders (in minutes)
   - Default: 10 minutes
   - Recommended: 10-20 minutes for regular use

2. **Set Duration** - How long the reminder lasts (in seconds)
   - Default: 7 seconds
   - Recommended: 5-10 seconds

3. **Choose Reminder Type:**
   - ✅ **Text Reminders** - Shows "Blink" messages (recommended)
   - ✅ **Emoji Reminders** - Shows eye emojis (optional)

4. Click **"🚀 Enable Blinker"** to start

### How It Works

- Every X minutes (your interval), a reminder appears on your screen
- Emojis or text messages float down your screen
- This reminds you to blink and rest your eyes
- After the duration, it disappears automatically

### Keyboard Shortcut

- Press **Alt+R** anywhere to toggle blinker on/off

---

## 🖥️ 2nd Display Tab - Multiple Monitors

Control dimming for additional monitors separately!

### Enable 2nd Display Dimming

1. Check **"Enable 2nd Display Dimming"**
2. Adjust the **brightness slider** for your second monitor
3. Use preset buttons: **25%**, **50%**, **75%**, **95%**

### Blue Light Filter for 2nd Display

1. Check **"Enable Blue Light Filter"** (must enable dimming first)
2. Adjust the **intensity slider** (0-100%)
3. Works independently from your main display

### Tips

- Each display can have different settings
- Perfect for setups with multiple monitors
- Main display and 2nd display work independently

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Alt+D** | Toggle dimmer on/off |
| **Alt+R** | Toggle blinker on/off |
| **Alt+G** | Temporarily hide overlay (for gestures) |

**Note**: Global hotkeys (work anywhere) require the `keyboard` package. Without it, shortcuts only work when the app window is focused.

---

## 🔔 System Tray

The app runs in your system tray (bottom-right corner):

- **Left-click** the tray icon → Shows/hides the main window
- **Right-click** the tray icon → Shows menu:
  - Show/Hide window
  - Quit application

**Tips**: 
- You can close the window and the app keeps running in the tray!
- **PYW files are perfect for this** - they run silently without any windows
- Add PYW to Windows startup folder to auto-launch on boot
- The app remembers your settings and restores them when you reopen it

---

## 💡 Tips & Best Practices

### For Eye Health

- **Use blue light filter** in the evening (50-80% intensity)
- **Set a schedule** for automatic dimming at night
- **Enable blinker** to remind yourself to rest your eyes
- **Lower dimming levels** (25-50%) are usually enough for most people

### For Different Activities

- **Reading**: Dim 50-70% + Blue light 60-80%
- **Gaming**: Dim 30-50% + Blue light off
- **Movies**: Dim 60-80% + Blue light 40-60%
- **Night work**: Dim 70-85% + Blue light 70-100%

### Performance Tips

- The app is lightweight and won't slow down your computer
- You can minimize it to the tray - it keeps working!
- Profiles save your settings automatically

---

## ❓ Troubleshooting

### App Won't Start

**Problem**: Double-clicking does nothing
- **Solution**: Make sure Python is installed and added to PATH
- Try running from command line: `python dimmer.py`

**Problem**: "Module not found" error
- **Solution**: Install required packages: `pip install PyQt5 keyboard`

### Dimming Not Working

**Problem**: Screen doesn't dim when enabled
- **Solution**: 
  - Make sure the dimmer is actually enabled (button should be green)
  - Try adjusting the slider - very low values might not be visible
  - Check if another app is blocking overlays

**Problem**: Can't see anything when dimmed
- **Solution**: 
  - Lower the dimming level (try 25-50%)
  - Disable dimmer temporarily: Press Alt+D or click the button

### Blue Light Filter Issues

**Problem**: Blue light filter makes screen too orange
- **Solution**: Lower the intensity slider (try 30-50%)

**Problem**: Can't read text with blue light on
- **Solution**: 
  - Lower the intensity to 0-30%
  - Make sure dimming level isn't too high
  - Blue light filter should be subtle, not overwhelming

### Hotkeys Not Working

**Problem**: Alt+D, Alt+R don't work
- **Solution**: 
  - Install keyboard package: `pip install keyboard`
  - Restart the app
  - Make sure no other app is using those shortcuts

### Schedule Not Working

**Problem**: Schedule doesn't activate automatically
- **Solution**: 
  - Make sure "Enable Schedule" button is clicked (should say "Disable Schedule")
  - Check that you've selected a preset or set custom times
  - Verify your system time is correct

### Blinker Not Showing

**Problem**: Blinker reminders don't appear
- **Solution**: 
  - Make sure blinker is enabled (button should say "Disable Blinker")
  - Check that at least one reminder type is checked (Text or Emoji)
  - Wait for the interval time to pass

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the Troubleshooting section** above
2. **Restart the application** - Close completely and reopen
3. **Check system tray** - Make sure the app is running (icon visible)
4. **Verify Python version** - Run `python --version` (should be 3.7+)

---

## 📝 Technical Details

- **Version**: 1.1
- **Language**: Python 3
- **Framework**: PyQt5
- **Platform**: Windows 10+
- **License**: Free to use

### Files Created

The app creates these files in the same folder:
- `dimmer_profiles.json` - Your saved profiles
- `dimmer_stats.json` - Your current dimmer state and settings
- Settings are saved automatically

### Available File Formats

- **`ScreenDimmer.exe`** - Standalone executable (no Python needed)
- **`dimmer.pyw`** - Python windowless script (no command window)
- **`dimmer.py`** - Python script (shows command window)

---

## 🎯 Quick Start Checklist

### For EXE Users (Easiest):
- [ ] Download `ScreenDimmer.exe`
- [ ] Double-click to run
- [ ] Try enabling dimmer with Alt+D or the button
- [ ] Adjust brightness slider
- [ ] Try blue light filter
- [ ] Minimize to system tray
- [ ] Set up a schedule (optional)
- [ ] Enable blinker (optional)

### For PYW Users (Great for System Tray!):
- [ ] Install Python 3.7+
- [ ] Install PyQt5: `pip install PyQt5`
- [ ] (Optional) Install keyboard: `pip install keyboard`
- [ ] Run `dimmer.pyw` - it runs silently in background!
- [ ] Try enabling dimmer with Alt+D or the button
- [ ] Adjust brightness slider
- [ ] Try blue light filter
- [ ] Minimize to system tray - perfect for keeping it running!
- [ ] (Optional) Add to Windows startup for auto-launch
- [ ] Set up a schedule (optional)
- [ ] Enable blinker (optional)

### For PY Users:
- [ ] Install Python 3.7+
- [ ] Install PyQt5: `pip install PyQt5`
- [ ] (Optional) Install keyboard: `pip install keyboard`
- [ ] Run `dimmer.py` from command line or double-click
- [ ] Try enabling dimmer with Alt+D or the button
- [ ] Adjust brightness slider
- [ ] Try blue light filter
- [ ] Minimize to system tray
- [ ] Set up a schedule (optional)
- [ ] Enable blinker (optional)

---

## 🙏 Thank You!

Thank you for using Screen Dimmer! We hope it helps protect your eyes and improve your screen viewing experience.

**Enjoy your dimmed, eye-friendly screen!** 👀✨

---

*Last updated: Version 1.1*
