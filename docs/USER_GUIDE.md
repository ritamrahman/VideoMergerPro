# 📘 Video Merger Pro (v2.2.1) - User Guide

Welcome to **Video Merger Pro**, the high-performance tool designed for everyone—from high-end editors to "Potato PC" users.

## 🚀 Getting Started

### Installation
No installation is required!
1. Locate the file `VideoMergerPro.exe`.
2. Move it to any folder on your computer (e.g., Desktop).
3. Double-click to run.

---

### 🥔 Dynamic Performance Optimization (Potato Mode)
The application automatically detects your hardware and adjusts settings:

1. **Standard Mode**: Full speed, parallel processing.
2. **Potato Mode (< 5GB RAM)**: Uses faster encoding presets and smaller batch sizes to save memory.
3. **Ultimate Stability Mode (< 2.5GB RAM)**: 
    - **Single-Threaded**: Strictly uses one CPU core to keep your system responsive.
    - **Micro-Batching**: Merges only 2 clips at once.
    - **I/O Buffering**: Optimized for slow "Third Grade" HDDs.
    - **Crash Logging**: Automatically generates `crash_report.log` if an error occurs.
Look at the **bottom-left corner** of the app window:
- **🚀 High Performance**: You have a powerful PC (>5GB RAM). Usage is maximized for speed.
- **🥔 Battery Saver Active**: You have a low-end PC (<5GB RAM). Safety measures are active.
- **🛡️ Ultimate Stability Active**: You have an extremely low-end PC (<2.5GB RAM). Maximum safety is prioritized over speed.
    - **Optimization**: Prioritizes stability to prevent crashes.
    - **Responsiveness**: Keeps your mouse/keyboard smooth while merging.
    - **Ultrafast Encoding**: sacrificing a tiny bit of quality for massive speed gains.

---

## 🛠️ Features Guide

### 1. Smart Split (The Key Feature)
Instead of one giant 10-hour video, use Smart Split to keep things manageable.
- **Duration Limit (T)**: Example: *"Split every 10 minutes"*. Perfect for YouTube uploads.
- **Clip Count (C)**: Example: *"Split every 5 videos"*.
- **Visual Tracking**: Watch the sidebar! The **Battery Bars** show exactly how full each "Part" is.

### 2. Dual-Layer Tracking
- **Main List**: Every video shows `[PART 1]`, `[PART 2]`, etc. so you know where it belongs.
- **Sidebar**: Detailed schedule showing total time per part.

### 3. Drag & Drop
- Drag folders or hundreds of files at once onto the giant Cloud icon.
- **Note**: If you drag 100+ files, give it a moment to analyze. The "Analyzing..." animation will guide you.

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Analyzing..." is stuck** | Please wait. Complex files take longer. If it takes >1 minute for 5 files, one might be corrupt. |
| **App won't open** | Ensure you have at least 400MB free RAM. Try running as Administrator. |
| **Video output is large** | This is normal for high-quality merges. Use a handbrake tool to compress later if needed. |
| **Taskbar Icon Missing** | This is fixed in v2.2.0. Ensure you are running the latest `.exe` build. |

---

## 💻 System Requirements

**Minimum (Potato Mode):**
- Windows 10/11
- 4GB RAM
- Dual-Core CPU

**Recommended (Rocket Mode):**
- 8GB+ RAM
- NVIDIA GPU (GTX 1050 or higher) for 5x faster merging.
