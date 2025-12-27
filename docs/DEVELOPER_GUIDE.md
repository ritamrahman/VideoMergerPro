# 👨‍💻 Ultimate Video Merger - Developer Guide

This documentation is intended for developers who wish to modify, debug, or extend the Ultimate Video Merger codebase.

## 🏗️ Project Architecture

The application follows a standard **PyQt5 GUI** architecture with a decoupled "Business Logic" layer handling the video processing.

### Key Files
1.  **`dev/main.py`**
    *   **Role**: Entry point & GUI Controller.
    *   **Class `VideoMergerApp`**: Handles the UI layout, signal slots, and user interaction.
    *   **Key Responsibilities**:
        *   Manages the file list and "Smart Split" configuration.
        *   Updates the sidebar preview (`update_split_preview`).
        *   **Potato Mode** detection happens here in `__init__`.

2.  **`dev/video_merger_robust.py`** (The Engine)
    *   **Role**: Core video processing logic.
    *   **Class `RobustVideoMerger`**: Wraps FFmpeg and MoviePy.
    *   **Key Methods**:
        *   `calculate_batches()`: Determines how to split videos based on duration/count.
        *   `merge_videos()`: Orchestrates the actual merge process. Now includes "Fast Copy" optimization for single-video batches.

3.  **`dev/worker_thread.py`**
    *   **Role**: Background processing to keep the UI responsive.
    *   **Classes**:
        *   `VideoInfoWorker`: Fetches metadata (duration/resolution) using `ffprobe`.
        *   `VideoMergerWorker`: Runs the heavy `merge_videos` function.

---

## ⚡ Performance Concepts

### 1. Dynamic Performance Tiers (Potato Mode)
The code automatically detects system RAM and sets a performance level:
*   **Level 1 (Potato) (< 5GB RAM)**: Reduces `block_size` to 4 and uses `ultrafast` FFmpeg presets.
*   **Level 2 (Ultimate Stability) (< 2.5GB RAM)**: 
    - Forced **Single-Threading** (`-threads 1`) to prevent memory spikes.
    - Micro-batches (`block_size = 2`).
    - **MoviePy Fallback Disabled** to save RAM.
    - **I/O Buffering**: Uses `max_muxing_queue_size` for slow disks.

### 2. Resolution & Aspect Ratio Logic
*   **Auto Detect**: If every video in a merge batch is vertical (height > width), the output is standardized to **1080x1920**.
*   **Manual Mode (New)**: The engine supports `resolution_mode` (Auto, Horizontal, Vertical, Square). It uses the `pad` filter in FFmpeg to ensure non-conforming clips are letterboxed/pillarboxed.

### 3. Smart Auto-Standalone
Implemented in `calculate_batches`, videos exceeding the `standalone_threshold_sec` (default 60s) are isolated into their own batches to utilize the `shutil.copy2` (Fast Copy) path, bypassing heavy re-encoding.

---

## 🛠️ Development Setup

### Dependencies
```bash
pip install -r dev/requirements.txt
```

### Building the EXE
```bash
pyinstaller dev/VideoMergerPro.spec --noconfirm
```
The output will be `VideoMergerPro v2.5.0.exe`.
If you want to add features, here are the best places to start:

*   **Add "Fade Transitions"**:
    *   Modify `video_merger_robust.py` -> `_ffmpeg_merge_block`.
    *   You will need to update the `filter_complex` string to include `xfade` filters between inputs.

*   **Add "Watermarking"**:
    *   Update `video_merger_robust.py`.
    *   Add an image input to the FFmpeg command and use the `overlay` filter in the complex filter chain.

*   **Mac/Linux Support**:
    *   Currently, `ctypes` (used for RAM check and AppID) is Windows-specific.
    *   Wrap these calls in `if platform.system() == "Windows":` checks to make it cross-platform.
