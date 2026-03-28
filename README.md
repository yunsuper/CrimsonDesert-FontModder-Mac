# Crimson Desert Font Modder for macOS (Native/Steam)

![macOS Support](https://img.shields.io/badge/Platform-macOS%20(Native/Steam)-000000?style=flat&logo=apple)
![Apple Silicon Optimized](https://img.shields.io/badge/Optimized%20for-Apple%20Silicon%20(M1/M2/M3/M4)-007AFF?style=flat)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A standalone Python-based GUI tool specifically designed for the **macOS Native/Steam version** of Crimson Desert. It automates the process of patching all 16 internal font slots while providing a clear guide to bypass macOS security restrictions (SIP/Quarantine).

---

## 📖 Introduction
While Windows users have various patching options, Mac users often face unique challenges due to system security (SIP/Quarantine). This tool simplifies the process for the Mac community, ensuring a seamless font customization experience without manually tinkering with deep system files.

## ✨ Key Features
* **Full Font Overwrite:** Patches all 16 internal font slots (Korean, English, Japanese, etc.) with your custom `.ttf` or `.otf` file.
* **macOS Native Support:** Specifically targets the file structure found in the Mac version (e.g., `basefont/*.ttf`).
* **High-Performance Patching:** Optimized logic using **LZ4 compression** to match original file budgets perfectly on macOS.

## 🛠 Requirements (First-time only)
You must have Python and the necessary libraries installed. Run these commands in your **Terminal**:

### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"
```

### 2. Install Python-tk and LZ4 library
```bash
brew install python-tk@3.12
pip3 install lz4
```

## 🚀 How to Use
#### Step 1. Permissions
Go to System Settings > Privacy & Security > Full Disk Access and enable Terminal. (Please restart your Terminal after this step!)

#### Step 2. Run the Tool
Navigate to the tool's folder in Terminal and run:
```Bash
python3 CrimsonDesertFontModGUI_Mac.py
```

#### Step 3. Patching
Click <b>[Browse]</b> to select your custom font file.

Click <b>[Force Patch Fonts]</b> to begin the process.

#### Step 4. Final Step (Bypass Quarantine)
Run this command in Terminal to ensure the game launches without security errors:
```bash
sudo xattr -rd com.apple.quarantine "/Users/$(whoami)/Library/Application Support/Steam/steamapps/common/Crimson Desert/CrimsonDesert_Steam.app"
```
> [!NOTE]
If the game updates and the font resets, simply run the tool again.

---

## 📜 Credits & Ethics
Inspired by the font patching methods found in various Windows mods on Nexus Mods.

This tool is an original Python implementation developed specifically for macOS by yunsuper.

Nexus Mods Page: [Mod#115](https://www.nexusmods.com/crimsondesert/mods/115)

---

## ⚖️ License
Distributed under the MIT License. See LICENSE for more information.

Created by: yunsuper (GitHub) / yunsuper1 (NexusMods)