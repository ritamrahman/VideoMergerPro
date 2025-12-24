# 👨‍💻 Video Merger Pro - Developer Guide

This documentation is intended for developers who wish to modify, debug, or extend the Video Merger Pro codebase.

## 🏗️ Project Architecture

The application follows a standard **PyQt5 GUI** architecture with a decoupled "Business Logic" layer handling the video processing.

### Key Files
1.  **`dev/main.py`**
    *   **Role**: Entry point & GUI Controller.
    *   **Class `VideoMergerApp`**: Handles the UI layout, signal slots, and user interaction.
    *   **Key Responsibilities**:
        *   Manages the file list and "Smart Split" configuration.
        *   Updates the sidebar preview (`update_split_preview`).
        *   Note: The **Potato Mode** detection happens here in `__init__`.

2.  **`dev/video_merger_robust.py`** (The Engine)
    *   **Role**: Core video processing logic.
    *   **Class `RobustVideoMerger`**: Wraps FFmpeg and MoviePy.
    *   **Key Methods**:
        *   `calculate_batches()`: Determines how to split videos based on duration/count. **Crucial**: Uses `cached_durations` to avoid main-thread lag.
        *   `merge_videos()`: Orchestrates the actual merge process.

3.  **`dev/worker_thread.py`**
    *   **Role**: Background processing to keep the UI responsive.
    *   **Classes**:
        *   `VideoInfoWorker`: Fetches metadata (duration/resolution) in the background.
        *   `VideoMergerWorker`: Runs the heavy `merge_videos` function in a separate thread.

---

### 📂 Naming Convention
To ensure a consistent user experience, the filename logic is mirrored in `main.py` (for UI preview) and `worker_thread.py` (for actual output).
*   **Pattern**: `[Title] clip-[Start]-[End] merge [PartNumber].mp4`
*   **Standardization**: Both components use a `safe_title` sanitizer that removes non-alphanumeric characters (except spaces, dashes, and underscores).

---

## ⚡ Performance Concepts

### 1. "Potato Mode" (Dynamic Performance Tiers)
The code automatically detects system RAM and sets a performance level (0, 1, or 2).
*   **Implementation**: In `main.py`, we check `GlobalMemoryStatusEx`.
*   **Level 1 (Potato) (< 5GB RAM)**: Reduces `block_size` to 4 and uses `ultrafast` FFmpeg presets.
*   **Level 2 (Ultimate Stability) (< 2.5GB RAM)**: 
    - Forced **Single-Threading** (`-threads 1`) to prevent memory spikes.
    - Micro-batches (`block_size = 2`).
    - **MoviePy Fallback Disabled**: The internal engine is completely bypassed to save RAM.
    - **I/O Buffering**: Uses `max_muxing_queue_size` for slow HDDs.

### 2. Absolute Path Resolution
To avoid `WinError 2` (File Not Found) in bundled environments, the engine uses `imageio_ffmpeg.get_ffmpeg_exe()` to resolve the absolute path of the bundled FFmpeg binary.

### 3. Metadata Fallback (ffprobe-less)
If `ffprobe.exe` is missing from the environment, the engine switches to `_get_video_info_via_ffmpeg`. This calls `ffmpeg -i` and parses the `stderr` output using Regex to extract duration and resolution.

### 4. Main Thread Blocking Prevention
*   **Rule**: NEVER call `ffprobe` or `subprocess` on the Main UI Thread.
*   **Solution**: `calculate_batches` strictly uses a dictionary of cached durations. If a file isn't cached, it is skipped/estimated until the `VideoInfoWorker` fetches it.

---

## 🛠️ Development Setup

### Dependencies
Install the required packages using the `requirements.txt` file:
```bash
pip install -r dev/requirements.txt
```

### Running from Source
```bash
python dev/main.py
```

### Building the EXE
We use **PyInstaller**. The spec file is located in the `dev/` folder.
```bash
# Run from the project root:
pyinstaller dev/VideoMergerPro.spec --noconfirm
```
*   **Note**: Proper taskbar icon behavior relies on the `AppUserModelID` set in `main.py`.

---

## 🚀 Extending the Project (Ideas)

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
