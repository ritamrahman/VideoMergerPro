# 🎬 Ultimate Video Merger v2.3.0

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, modern desktop application designed for high-efficiency video merging and smart clip management. Built with **PyQt5** and powered by **FFmpeg**, it offers a professional-grade experience for content creators.

---

## ✨ Key Features

- **🚀 Smart Auto-Standalone**: Automatically identifies videos 1 minute or longer and treats them as individual standalone files (Fast Copy), while merging shorter clips into compilations.
- **📊 Advanced Batching**: Group videos by total duration (e.g., max 10 mins per part) or by specific clip counts.
- **⚡ Hardware Acceleration**: Full support for **NVIDIA RTX GPU acceleration** (NVENC) for lightning-fast encoding.
- **🥔 Potato Mode**: Adaptive performance levels for low-RAM or older systems (automatically detects system memory).
- **🎨 Modern Dark UI**: Sleek, glassmorphism-inspired interface with real-time "Merge Execution Plan" previews.
- **🖱️ Drag & Drop**: Effortlessly add folders or multiple files directly into the workspace.

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg (automatically handled if using the provided environment)

### Run from Source
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ritamrahman/VideoMergerPro.git
   cd VideoMergerPro
   ```

2. **Install dependencies**:
   ```bash
   pip install -r dev/requirements.txt
   ```

3. **Launch the application**:
   ```bash
   python dev/main.py
   ```

---

## 🏗️ Building the Executable

To bundle the application into a single standalone `.exe` for Windows:

```bash
pyinstaller dev/VideoMergerPro.spec --noconfirm
```
The output will be located in the `dist/` directory.

---

## 📂 Project Structure

- `dev/`: Source code including the GUI logic (`main.py`) and robust processing engine (`video_merger_robust.py`).
- `docs/`: In-depth Developer and User guides.
- `dist/`: (Generated) Standalone Windows executable.

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
*Developed by [ritamrahman](https://github.com/ritamrahman)*
