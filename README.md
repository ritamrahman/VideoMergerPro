# 🎬 Ultimate Video Merger v2.5.0

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, modern desktop application designed for high-efficiency video merging and smart clip management. Built with **PyQt5** and powered by **FFmpeg**, it offers a professional-grade experience for content creators.

---

## ✨ Key Features

- **🚀 Smart Auto-Standalone**: Automatically identifies videos 1 minute or longer and treats them as individual files with **Fast Copy** (Zero quality loss).
- **📐 Dynamic Aspect Ratio**: Automatically detects vertical video batches and adjusts output accordingly.
- **⚙️ Manual Resolution Control**: Force Horizontal (16:9), Vertical (9:16), or Square (1:1) output modes.
- **📊 Advanced Batching**: Group videos by duration or clip count with a real-time sidebar preview.
- **⚡ Hardware Acceleration**: Support for **NVIDIA NVENC** (RTX/GTX) for lightning-fast encoding.
- **🥔 Potato Mode**: Adaptive performance levels that protect low-RAM systems from crashing.
- **🎨 Modern Dark UI**: Sleek, glassmorphism-inspired interface with interactive "Merge Schedule" cards.

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- NVIDIA Drivers (Optional, for GPU speed)

### Run from Source
1. **Clone and Install**:
   ```bash
   git clone https://github.com/ritamrahman/VideoMergerPro.git
   pip install -r dev/requirements.txt
   ```

2. **Launch**:
   ```bash
   python dev/main.py
   ```

---

## 🏗️ Building the Executable

```bash
pyinstaller dev/VideoMergerPro.spec --noconfirm
```
Output: `dist/Ultimate Video Merger v2.5.0.exe`

---

## 📂 Project Structure

- `dev/`: Core source code (GUI & Engine).
- `docs/`: User and Developer guides.

---

## 📜 License
MIT License. Developed by [ritamrahman](https://github.com/ritamrahman).
