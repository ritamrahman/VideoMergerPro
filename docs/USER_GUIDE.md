# 📘 Ultimate Video Merger (v2.5.0) - User Guide

Welcome to **Ultimate Video Merger**, the high-performance tool designed for everyone—from high-end editors to "Potato PC" users.

## 🚀 Getting Started

### Installation
No installation is required!
1. Locate the file `VideoMergerPro v2.5.0.exe`.
2. Move it to any folder on your computer (e.g., Desktop).
3. Double-click to run.

---

### 🥔 Dynamic Performance Optimization (Potato Mode)
The application automatically detects your hardware and adjusts settings:

1. **Rocket Mode (High Performance)**: Full speed, parallel processing for PCs with **>5GB RAM**.
2. **Potato Mode (Battery Saver) (< 5GB RAM)**: Uses faster encoding presets and smaller batch sizes to save memory.
3. **Ultimate Stability Mode (< 2.5GB RAM)**: 
    - **Single-Threaded**: Strictly uses one CPU core to keep your system responsive.
    - **Micro-Batching**: Merges only 2 clips at once.
    - **I/O Buffering**: Optimized for slow "Third Grade" HDDs.
    - **Crash Logging**: Automatically generates `crash_report.log` if an error occurs.

Look at the **bottom-left corner** of the app window to see your active mode.

---

## 🛠️ Features Guide

### 1. Smart Split
Instead of one giant 10-hour video, use Smart Split to keep things manageable.
- **Duration Limit (T)**: Example: *"Split every 10 minutes"*. Perfect for YouTube uploads.
- **Clip Count (C)**: Example: *"Split every 5 videos"*.
- **Visual Tracking**: Watch the sidebar! The **Battery Bars** show exactly how full each "Part" is.

### 2. Output Mode (Resolution Control)
New in v2.5.0, you can force the output aspect ratio regardless of input:
- **Auto Detect**: Automatically detects if a batch is entirely vertical.
- **Horizontal (16:9)**: Standard widescreen format.
- **Vertical (9:16)**: Perfect for TikTok, Reels, and Shorts (1080x1920).
- **Square (1:1)**: Ideal for Instagram posts.
Non-conforming clips are automatically padded with black bars to fit the target resolution.

### 3. Smart Auto-Standalone
Videos longer than **60 seconds** are treated as standalone features. They use **Fast Copy** technology, which preserves 100% of the original quality and finishes in seconds.

### 4. Drag & Drop
- Drag folders or hundreds of files at once onto the giant Cloud icon.

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Analyzing..." is stuck** | Please wait. Complex files take longer. If it takes >1 minute for 5 files, one might be corrupt. |
| **App won't open** | Ensure you have at least 400MB free RAM. Try running as Administrator. |
| **Video output is large** | Use the standard 'Auto' resolution or Horizontal mode for best compatibility. |

---

## 💻 System Requirements

**Minimum (Ultimate Stability Mode):**
- Windows 10/11
- 4GB RAM (Supports as low as 2GB)
- Dual-Core CPU

**Recommended (Rocket Mode):**
- 8GB+ RAM
- NVIDIA GPU (GTX 1050 or higher) for hardware-accelerated merging.
