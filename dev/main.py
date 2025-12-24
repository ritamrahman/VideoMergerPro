"""
🎬 Pro Video Merger
A modern desktop GUI application for merging multiple video files with smart splitting
Built with PyQt5 and MoviePy
"""

import sys
import os
import time
from typing import List, Optional
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QLinearGradient, QBrush
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QPushButton, QListWidget, QProgressBar,
                           QFileDialog, QMessageBox, QCheckBox, QSpinBox, QFrame,
                           QListWidgetItem, QAbstractItemView, QSizePolicy, QScrollArea,
                           QLineEdit, QDialog)
from PyQt5.QtCore import Qt, QTimer, QSize
import ctypes
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

try:
    myappid = 'antigravity.ultimatevideomerger.2.3.0' # Unique ID
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

from video_merger_robust import RobustVideoMerger
from worker_thread import VideoMergerWorker, VideoInfoWorker, UpdateCheckerWorker

CURRENT_VERSION = "2.3.0"
UPDATE_URL = "https://raw.githubusercontent.com/YourUsername/VideoMerger/main/version.json" # Placeholder

class ProjectTitleDialog(QDialog):
    """Custom professional dialog for title input"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Configuration")
        self.setFixedWidth(500)
        self.setStyleSheet("background-color: #1e1e1e; color: #fff;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Give your project a name")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d4;")
        layout.addWidget(header)
        
        desc = QLabel("This title will be used for the final filenames.")
        desc.setStyleSheet("color: #888; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Vacation 2023, Gaming Highlights...")
        self.title_input.setMinimumHeight(45)
        self.title_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 10px;
                color: #fff;
                font-size: 15px;
            }
            QLineEdit:focus { border-color: #0078d4; }
        """)
        layout.addWidget(self.title_input)
        
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setStyleSheet("background-color: #333; color: #fff; border-radius: 5px;")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("Start Merge")
        self.ok_btn.setMinimumHeight(40)
        self.ok_btn.setStyleSheet("background-color: #0078d4; color: #fff; font-weight: bold; border-radius: 5px;")
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)

class ModernDarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.Window, QColor(30, 30, 30))
        self.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.setColor(QPalette.Base, QColor(25, 25, 25))
        self.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        self.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        self.setColor(QPalette.Text, QColor(255, 255, 255))
        self.setColor(QPalette.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        self.setColor(QPalette.BrightText, QColor(255, 0, 0))
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        self.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

class VideoMergerApp(QMainWindow):
    """
    Main application window for the Video Merger tool
    Modern dark interface with smart splitting capabilities
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize video processing components
        self.video_files = []
        self.video_durations = {}  # Map path -> duration in seconds
        self.video_merger = RobustVideoMerger()
        self.worker_thread = None
        # Adaptive performance detection for low-end hardware
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total_ram_gb = stat.ullTotalPhys / (1024**3)
            
            # Log diagnostics
            with open("crash_report.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- Startup Log v{CURRENT_VERSION} ---\n")
                f.write(f"OS: {platform.platform()}\n")
                f.write(f"Detected RAM: {total_ram_gb:.2f} GB\n")

            if total_ram_gb < 2.5: # 2.5GB to safely catch 1GB/2GB RDP machines
                self.video_merger.optimize_for_low_end(2) # Level 2: Ultimate Stability
            elif total_ram_gb < 5.0: # 4GB machines
                self.video_merger.optimize_for_low_end(1) # Level 1: Standard Potato
        except Exception as e:
            # Silently log startup issues
            with open("crash_report.log", "a", encoding="utf-8") as f:
                f.write(f"Startup RAM Check Fail: {e}\n")
        
        self.worker_thread = None
        self.info_worker = None
        self.update_worker = None
        self.start_time = None
        self.is_calculating_info = False
        # Loading animation components
        self.anim_step = 0
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate_loading_text)
        
        # Timer for updating elapsed time
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_time_display)
        
        self.init_ui()
        self.apply_styling()
        
        # Drag and Drop support
        self.setAcceptDrops(True)
        
        # Check for updates on startup
        self.check_for_updates()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm')
        valid_files = [f for f in files if f.lower().endswith(video_extensions)]
        
        if valid_files:
            self.handle_files_addition(valid_files)
    def init_ui(self):
        """Create a clean, modern UI layout"""
        self.setWindowTitle("Ultimate Video Merger")
        self.setWindowIcon(QIcon(resource_path("app_icon.ico")))
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left Panel (Preview Only)
        left_panel = QFrame()
        left_panel.setFixedWidth(380)
        left_panel.setStyleSheet("background-color: #252526; border-right: 1px solid #3e3e42;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(15, 30, 15, 20)
        
        # App Title
        title = QLabel("Video Merger")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #ffffff;")
        left_layout.addWidget(title)
        
        subtitle = QLabel("Ultimate Edition")
        subtitle.setStyleSheet("font-size: 13px; color: #0078d4; margin-top: -15px; margin-bottom: 20px;")
        left_layout.addWidget(subtitle)
        
        # Expanded Split Preview in Sidebar (PRIORITY)
        preview_header = QLabel("Merge Schedule Details")
        preview_header.setStyleSheet("color: #0078d4; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        left_layout.addWidget(preview_header)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setStyleSheet("border: 1px solid #333; border-radius: 8px; background-color: #1a1a1c;")
        
        self.preview_label = QLabel("<div style='color: #444; text-align: center; margin-top: 150px;'>Merge plan will appear here...</div>")
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignTop)
        
        self.preview_scroll.setWidget(self.preview_label)
        left_layout.addWidget(self.preview_scroll)
        left_layout.setStretchFactor(self.preview_scroll, 1) # Large stretch factor
        
        left_layout.addSpacing(20)
        
        # Apps Controls (Smart Split) - ULTRA Minimalist
        self.controls_group = QFrame()
        self.controls_group.setStyleSheet("background-color: transparent; border: none; padding: 0px; margin-top: 5px;")
        controls_layout = QVBoxLayout(self.controls_group)
        controls_layout.setSpacing(5)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.smart_split_cb = QCheckBox("Enable clipping")
        self.smart_split_cb.setChecked(True)
        self.smart_split_cb.setStyleSheet("font-weight: bold; color: #555; font-size: 11px;")
        self.smart_split_cb.toggled.connect(self.toggle_split_options)
        self.smart_split_cb.toggled.connect(self.update_split_preview)
        controls_layout.addWidget(self.smart_split_cb)

        # Config Row
        config_row = QHBoxLayout()
        config_row.setSpacing(5)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 1200)
        self.duration_spin.setValue(10)
        self.duration_spin.setSuffix("m")
        self.duration_spin.setFixedWidth(60)
        self.duration_spin.valueChanged.connect(self.update_split_preview)
        
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 1000)
        self.count_spin.setValue(10)
        self.count_spin.setSuffix("c")
        self.count_spin.setFixedWidth(60)
        self.count_spin.setVisible(False)
        self.count_spin.valueChanged.connect(self.update_split_preview)

        self.split_duration_btn = QPushButton("T")
        self.split_duration_btn.setToolTip("Split by Duration")
        self.split_duration_btn.setCheckable(True)
        self.split_duration_btn.setChecked(True)
        self.split_duration_btn.setFixedWidth(25)
        self.split_count_btn = QPushButton("C")
        self.split_count_btn.setToolTip("Split by Clip Count")
        self.split_count_btn.setCheckable(True)
        self.split_count_btn.setFixedWidth(25)
        
        self.split_duration_btn.clicked.connect(lambda: self.set_split_mode("duration"))
        self.split_count_btn.clicked.connect(lambda: self.set_split_mode("count"))

        config_row.addWidget(self.split_duration_btn)
        config_row.addWidget(self.split_count_btn)
        config_row.addWidget(self.duration_spin)
        config_row.addWidget(self.count_spin)

        self.auto_naming_cb = QCheckBox("Name")
        self.auto_naming_cb.setChecked(True)
        self.auto_naming_cb.setStyleSheet("color: #666; font-size: 10px;")
        self.auto_naming_cb.toggled.connect(self.update_split_preview)
        
        self.auto_save_cb = QCheckBox("Save")
        self.auto_save_cb.setChecked(True)
        self.auto_save_cb.setStyleSheet("color: #666; font-size: 10px;")
        
        self.standalone_cb = QCheckBox("Auto-Standalone (60s)")
        self.standalone_cb.setChecked(True)
        self.standalone_cb.setStyleSheet("color: #0078d4; font-size: 10px; font-weight: bold;")
        self.standalone_cb.toggled.connect(self.update_split_preview)
        
        config_row.addWidget(self.auto_naming_cb)
        config_row.addWidget(self.auto_save_cb)
        config_row.addWidget(self.standalone_cb)
        config_row.addStretch()
        controls_layout.addLayout(config_row)

        left_layout.addWidget(self.controls_group)
        left_layout.addSpacing(5)
        
        # Bottom Left Status
        left_layout.addStretch() # Push everything up
        self.total_duration_label = QLabel("Total Duration: 00:00")
        self.total_duration_label.setStyleSheet("color: #888; font-size: 14px;")
        left_layout.addWidget(self.total_duration_label)
        
        display_version = f"v{CURRENT_VERSION} • GPU Enabled" if self.video_merger.use_gpu else f"v{CURRENT_VERSION} • CPU Mode"
        if self.video_merger.performance_level == 2:
            display_version += " • 🛡️ Ultimate Stability Active"
        elif self.video_merger.performance_level == 1:
            display_version += " • 🥔 Battery Saver Active"
        else:
            display_version += " • 🚀 High Performance"
            
        version_label = QLabel(display_version)
        version_label.setStyleSheet("color: #0078d4; font-size: 11px; font-weight: bold;")
        left_layout.addWidget(version_label)
        
        main_layout.addWidget(left_panel)
        
        # Right Panel (File List & Actions)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(20)
        
        # File List Header
        list_header = QHBoxLayout()
        header_lbl = QLabel("Videos to Merge")
        header_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        list_header.addWidget(header_lbl)
        
        list_header.addStretch()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setCursor(Qt.PointingHandCursor)
        self.select_all_btn.setFixedWidth(100)
        self.select_all_btn.clicked.connect(self.select_all_videos)
        list_header.addWidget(self.select_all_btn)
        
        list_header.addSpacing(10)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setFixedWidth(100)
        self.clear_btn.clicked.connect(self.clear_videos)
        list_header.addWidget(self.clear_btn)
        
        right_layout.addLayout(list_header)

        # File List - MUCH LARGER
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.file_list.setMinimumHeight(350) # Very prominent list
        right_layout.addWidget(self.file_list)
        
        # Add Button (Drop Area - MASSIVE & CLEAN)
        self.add_btn = QPushButton("☁\nDROP VIDEOS HERE")
        self.add_btn.setObjectName("add_btn") 
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setMinimumHeight(150) # Very prominent drop area
        self.add_btn.clicked.connect(self.add_videos)
        right_layout.addWidget(self.add_btn)
        
        # Progress Section
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 16px; color: #ddd;")
        right_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3e3e42;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 5px;
            }
        """)
        right_layout.addWidget(self.progress_bar)
        
        self.detailed_status = QLabel("")
        self.detailed_status.setStyleSheet("color: #888; font-size: 13px;")
        right_layout.addWidget(self.detailed_status)
        
        # Compilation Title with Gradient Border
        self.comp_title_lbl = QLabel("Compilation Title (Used for filename):")
        self.comp_title_lbl.setStyleSheet("color: #ddd; font-size: 14px; font-weight: bold; margin-top: 10px;")
        right_layout.addWidget(self.comp_title_lbl)
        
        # Frame for Gradient Border effect
        self.title_border = QFrame()
        self.title_border.setMinimumHeight(60)
        self.title_border.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d4, stop:0.5 #00bbff, stop:1 #0078d4);
                border-radius: 10px;
                padding: 2px;
            }
        """)
        title_border_layout = QVBoxLayout(self.title_border)
        title_border_layout.setContentsMargins(0,0,0,0)
        
        self.comp_title_edit = QLineEdit()
        self.comp_title_edit.setPlaceholderText("Enter Project Name (e.g. My Compilation)...")
        self.comp_title_edit.setMinimumHeight(56)
        self.comp_title_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit:focus { 
                background-color: #222;
            }
        """)
        self.comp_title_edit.textChanged.connect(self.update_split_preview)
        title_border_layout.addWidget(self.comp_title_edit)
        right_layout.addWidget(self.title_border)
        
        # Merge Button
        self.merge_btn = QPushButton("MERGE VIDEOS")
        self.merge_btn.setCursor(Qt.PointingHandCursor)
        self.merge_btn.setMinimumHeight(60)
        self.merge_btn.setEnabled(False)
        self.merge_btn.clicked.connect(self.merge_videos)
        right_layout.addWidget(self.merge_btn)
        
        main_layout.addWidget(right_panel)
        
    def apply_styling(self):
        """Apply global stylesheet"""
        # Set dark palette for standard widgets not covered by sheets
        QApplication.setStyle("Fusion")
        QApplication.setPalette(ModernDarkPalette())
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; font-family: 'Segoe UI', sans-serif; }
            QListWidget {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 5px;
                color: #ddd;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #303030; }
            QListWidget::item:selected { background-color: #094771; }
            QListWidget::item:hover { background-color: #2a2d2e; }
            
            QPushButton {
                background-color: #3e3e42;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #4e4e52; }
            QPushButton:pressed { background-color: #2d2d30; }
            
            QPushButton#add_btn {
                border: 2px dashed #444;
                background-color: #2a2a2e;
                color: #888;
                font-size: 20px;
                font-weight: bold;
                padding: 20px;
            }
            QPushButton#add_btn:hover {
                border-color: #0078d4;
                color: #0078d4;
                background-color: #1a1a1f;
            }
            
            QPushButton:disabled {
                background-color: #333;
                color: #555;
            }
        """)
        
        # Primary Action Button Style
        self.merge_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-size: 18px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #2d2d30; color: #555; }
        """)
        self.merge_btn.setObjectName("merge_btn")
        self.add_btn.setObjectName("add_btn")

    def toggle_split_options(self, checked):
        # In the minimalist redesign, we only hide/show the specific inputs
        isVisible = checked
        self.duration_spin.setVisible(isVisible and self.split_duration_btn.isChecked())
        self.count_spin.setVisible(isVisible and self.split_count_btn.isChecked())
        self.split_duration_btn.setVisible(isVisible)
        self.split_count_btn.setVisible(isVisible)
        self.auto_naming_cb.setVisible(isVisible)
        self.auto_save_cb.setVisible(isVisible)
        self.standalone_cb.setVisible(isVisible)
        self.preview_scroll.setVisible(isVisible)
        if isVisible:
            mode = "duration" if self.split_duration_btn.isChecked() else "count"
            self.set_split_mode(mode)

    def set_split_mode(self, mode):
        """Switch between duration and count based splitting"""
        if mode == "duration":
            self.split_duration_btn.setChecked(True)
            self.split_count_btn.setChecked(False)
            self.duration_spin.setVisible(True)
            self.count_spin.setVisible(False)
        else:
            self.split_duration_btn.setChecked(False)
            self.split_count_btn.setChecked(True)
            self.duration_spin.setVisible(False)
            self.count_spin.setVisible(True)
        
        self.update_split_preview()

    def add_videos(self):
        """Add video files to the list via dialog"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Videos", "", 
            "Video files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm)"
        )
        
        if files:
            self.handle_files_addition(files)

    def handle_files_addition(self, files: List[str]):
        """Shared logic for adding files from any source (dialog or drop)"""
        new_files = []
        for f in files:
            if f not in self.video_files:
                self.video_files.append(f)
                new_files.append(f)
                item = QListWidgetItem(os.path.basename(f))
                item.setData(Qt.UserRole, f) # Store full path
                item.setText(f"{os.path.basename(f)} (Calculating...)")
                self.file_list.addItem(item)
        
        if new_files:
            self.is_calculating_info = True
            self.anim_timer.start(500)
            self.fetch_metadata(new_files)
            
        self.update_ui_state()

    def fetch_metadata(self, files):
        """Start worker to fetch duration for new files"""
        self.info_worker = VideoInfoWorker(files, self.video_merger)
        self.info_worker.info_ready.connect(self.update_file_info)
        self.info_worker.info_failed.connect(self.handle_info_failed)
        self.info_worker.start()

    def handle_info_failed(self, path, error):
        """Handle cases where video info cannot be fetched"""
        print(f"Failed to get info for {path}: {error}")
        self.video_durations[path] = 0 # Mark as known but zero duration
        self.update_file_info_post(path)

    def update_file_info(self, path, info):
        """Update list item with actual duration"""
        duration = info.get('duration', 0)
        self.video_durations[path] = duration
        
        # Find item in list
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.data(Qt.UserRole) == path:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                item.setText(f"{info['filename']} - {minutes}:{seconds:02d}")
                break
        
        self.update_file_info_post(path)

    def update_file_info_post(self, path):
        """Common logic after file info is received or failed"""
        # Check if all done
        if all(f in self.video_durations for f in self.video_files):
            self.is_calculating_info = False
            self.anim_timer.stop()
            self.update_split_preview()

        self.update_total_duration()
        self.update_ui_state()

    def animate_loading_text(self):
        """Simple animation step for loading indicators"""
        self.anim_step = (self.anim_step + 1) % 4
        dots = "." * self.anim_step
        
        if self.is_calculating_info:
            self.update_status(f"Calculating Video Info{dots}")
            self.update_split_preview()
            self.update_ui_state()

    def update_total_duration(self):
        """Calculate and display total duration of all selected videos"""
        total_sec = sum(self.video_durations.get(f, 0) for f in self.video_files)
        mins = int(total_sec // 60)
        secs = int(total_sec % 60)
        hours = 0
        if mins >= 60:
            hours = mins // 60
            mins = mins % 60
            self.total_duration_label.setText(f"Total Duration: {hours}h {mins}m {secs}s")
        else:
            self.total_duration_label.setText(f"Total Duration: {mins}m {secs}s")
            
        # Also update split preview
        self.update_split_preview()

    def update_split_preview(self):
        """Update the text preview of how videos will be split with a high-end visual look"""
        if not self.video_files:
            self.preview_label.setText("<div style='color: #555; font-size: 13px; text-align: center; margin-top: 50px;'>Add videos to see split preview...</div>")
            return

        if not self.smart_split_cb.isChecked():
            self.preview_label.setText("<div style='color: #0078d4; font-size: 14px; font-weight: bold; text-align: center; margin-top: 50px;'>Smart Split Disabled<br><span style='font-weight: normal; color: #888;'>1 single part will be created</span></div>")
            return

        max_dur = 0
        max_count = 0
        standalone_thresh = 60 if self.standalone_cb.isChecked() else 0
        
        if self.split_duration_btn.isChecked():
            max_dur = self.duration_spin.value() * 60
        else:
            max_count = self.count_spin.value()
        
        durations_ready = all(f in self.video_durations for f in self.video_files)
        batches = self.video_merger.calculate_batches(
            self.video_files, 
            max_duration_sec=max_dur, 
            max_clip_count=max_count,
            cached_durations=self.video_durations,
            standalone_threshold_sec=standalone_thresh
        )
        
        if not durations_ready and max_dur > 0:
            dots = "." * self.anim_step
            self.preview_label.setText(f"<div style='color: #0078d4; text-align: center; margin-top: 100px; font-size: 16px;'><b>Analyzing Clips{dots}</b><br><span style='color: #666; font-size: 12px;'>Preparing your compilation cards</span></div>")
            return

        total_clips = len(self.video_files)
        total_parts = len(batches)
        split_mode_str = f"Max {self.duration_spin.value()}m" if self.split_duration_btn.isChecked() else f"Max {self.count_spin.value()} clips"
        
        output_folder = "N/A"
        if self.video_files:
            output_folder = "Merge/" if self.auto_save_cb.isChecked() else "Manual"

        preview_text = f"""
            <div style='background-color: #252526; border: 1px solid #3e3e42; border-radius: 8px; padding: 12px; margin-bottom: 20px;'>
                <div style='color: #0078d4; font-weight: bold; font-size: 15px;'>Project Summary</div>
                <div style='color: #aaa; font-size: 12px; margin-top: 5px;'>
                    📦 Total: {total_clips} clips<br>
                    🎞 Parts: {total_parts} batches<br>
                    ⏱ Split: {split_mode_str}<br>
                    📂 Folder: <span style='color: #0078d4;'>{output_folder}</span>
                </div>
            </div>
            <div style='margin-bottom: 15px; color: #ffffff; font-size: 14px;'><b>Merge Execution Plan:</b></div>
        """
        
        title_val = self.comp_title_edit.text().strip()
        safe_title = "".join([c for c in title_val if c.isalnum() or c in (' ', '-', '_')]).strip()
        if not safe_title: safe_title = "Project"

        for i, batch in enumerate(batches):
            # Same logic as VideoMergerWorker for consistency
            if total_parts > 1 and self.auto_naming_cb.isChecked():
                start_num = self.video_files.index(batch[0]) + 1
                end_num = self.video_files.index(batch[-1]) + 1
                filename = f"{safe_title} clip-{start_num}-{end_num} merge {i+1}.mp4"
            elif total_parts > 1:
                filename = f"{safe_title}_part{i+1}.mp4"
            else:
                filename = f"{safe_title}.mp4"
            start_num = self.video_files.index(batch[0]) + 1
            end_num = self.video_files.index(batch[-1]) + 1
            batch_dur = sum(self.video_durations.get(f, 0) for f in batch)
            bm, bs = int(batch_dur // 60), int(batch_dur % 60)
            
            # Progress Bar for duration (relative to max_dur or default 10m)
            limit_sec = max_dur if max_dur > 0 else 600
            usage_percent = min(100, int((batch_dur / limit_sec) * 100))
            bar_color = "#0078d4" if usage_percent < 90 else "#d47800"
            
            # Card styling
            preview_text += f"""
            <div style='background-color: #1e1e20; border: 1px solid #333; border-radius: 8px; padding: 12px; margin-bottom: 15px; border-left: 5px solid {bar_color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <span style='color: {bar_color}; font-weight: bold; font-size: 14px;'>PART {i+1}</span>
                    <span style='background: #333; color: #aaa; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;'>{bm}:{bs:02d}</span>
                </div>
                
                <div style='margin-top: 8px; background-color: #111; height: 4px; border-radius: 2px;'>
                    <div style='background-color: {bar_color}; width: {usage_percent}%; height: 100%; border-radius: 2px;'></div>
                </div>

                <div style='color: #eee; font-size: 11px; margin-top: 8px; font-family: monospace;'>{filename}</div>
                
                <div style='margin-top: 10px; border-top: 1px solid #2a2a2a; padding-top: 8px;'>
            """
            
            # List more files (up to 15)
            for j, f in enumerate(batch):
                # Sync part number back to main list (optional but very helpful)
                # We'll do this in a separate loop for performance or just here
                pass

                if j >= 10:
                    preview_text += f"<div style='color: #555; padding-left: 10px; font-size: 10px;'>... and {len(batch)-10} more clips</div>"
                    break
                
                fname = os.path.basename(f)
                if len(fname) > 35: fname = fname[:32] + "..."
                
                f_dur = self.video_durations.get(f, 0)
                fm, fs = int(f_dur // 60), int(f_dur % 60)
                
                # File row with duration
                preview_text += f"""
                <div style='color: #888; font-size: 10px; margin-bottom: 3px; display: flex; justify-content: space-between;'>
                    <span style='color: #0078d4;'>•</span> <span style='flex-grow: 1; margin-left: 5px;'>{fname}</span>
                    <span style='color: #444;'>[{fm}:{fs:02d}]</span>
                </div>
                """
            
            preview_text += "</div></div>"
            
        self.preview_label.setText(preview_text)
        
        # Update Main List with Part Numbers
        self.sync_part_numbers_to_list(batches)

    def sync_part_numbers_to_list(self, batches):
        """Update the main QListWidget items to show which part they belong to"""
        file_to_part = {}
        for i, batch in enumerate(batches):
            for f in batch:
                file_to_part[f] = i + 1
                
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            path = item.data(Qt.UserRole)
            part_num = file_to_part.get(path, "?")
            
            # Get clean filename and duration
            f_dur = self.video_durations.get(path, 0)
            fm, fs = int(f_dur // 60), int(f_dur % 60)
            fname = os.path.basename(path)
            
            # Update text with Part marker
            # Color indicator via background or prefix
            prefix = f"[PART {part_num}] "
            item.setText(f"{prefix} {fname} - {fm}:{fs:02d}")
            
            # Subtly color code parts
            colors = ["#1e1e20", "#252526"]
            item.setBackground(QColor(colors[part_num % 2]))

    def select_all_videos(self):
        """Selected all items in the video list"""
        self.file_list.selectAll()

    def clear_videos(self):
        self.video_files.clear()
        self.video_durations.clear()
        self.file_list.clear()
        self.update_total_duration()
        self.update_ui_state()

    def update_ui_state(self):
        has_videos = len(self.video_files) > 0
        is_processing = self.is_processing()
        is_calculating = self.is_calculating_info
        
        self.merge_btn.setEnabled(has_videos and not is_processing and not is_calculating)
        self.clear_btn.setEnabled(has_videos and not is_processing)
        self.select_all_btn.setEnabled(has_videos and not is_processing)
        self.add_btn.setEnabled(not is_processing)
        
        if is_calculating:
            dots = "." * self.anim_step
            self.merge_btn.setText(f"PREPARING VIDEOS{dots}")
        elif is_processing:
            self.merge_btn.setText("PROCESSING...")
        else:
            self.merge_btn.setText("MERGE VIDEOS")

    def is_processing(self):
        return self.worker_thread is not None and self.worker_thread.isRunning()

    def merge_videos(self):
        if len(self.video_files) < 1:
            QMessageBox.warning(self, "Warning", "Please select at least 1 video file.")
            return

        # Title Validation Logic
        title = self.comp_title_edit.text().strip()
        if not title:
            # If title is empty, force user to provide one with professional dialog
            dialog = ProjectTitleDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                title = dialog.title_input.text().strip()
                if not title: title = "My Compilation" # Fallback
                self.comp_title_edit.setText(title)
            else:
                return # User cancelled

        if self.auto_save_cb.isChecked():
            # Auto-save logic
            first_file = self.video_files[0]
            parent_dir = os.path.dirname(first_file)
            merge_dir = os.path.join(parent_dir, "Merge")
            
            if not os.path.exists(merge_dir):
                try:
                    os.makedirs(merge_dir)
                except Exception as e:
                    QMessageBox.warning(self, "Folder Error", f"Could not create 'Merge' folder: {e}")
                    # Fallback to dialog
                    output_path = self.get_output_path_from_dialog()
                    if not output_path: return
                    self.start_merge_process(output_path)
                    return
            
            safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
            if not safe_title: safe_title = "merged_video"
            
            output_path = os.path.join(merge_dir, f"{safe_title}.mp4")
            self.start_merge_process(output_path)
        else:
            # Manual save logic
            output_path = self.get_output_path_from_dialog()
            if output_path:
                self.start_merge_process(output_path)

    def get_output_path_from_dialog(self):
        title = self.comp_title_edit.text().strip()
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
        if not safe_title: safe_title = "merged_video"
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Merged Video", 
            f"{safe_title}.mp4",
            "Video files (*.mp4)"
        )
        return output_path

    def start_merge_process(self, output_path):
        self.start_time = time.time()
        self.progress_timer.start(1000)
        
        max_dur = 0
        max_count = 0
        standalone_thresh = 60 if self.standalone_cb.isChecked() else 0
        if self.smart_split_cb.isChecked():
            if self.split_duration_btn.isChecked():
                max_dur = self.duration_spin.value() * 60 # Convert mins to secs
            else:
                max_count = self.count_spin.value()
            
        self.worker_thread = VideoMergerWorker(
            self.video_files, 
            output_path, 
            self.video_merger, 
            max_duration=max_dur,
            max_clip_count=max_count,
            auto_naming=self.auto_naming_cb.isChecked(),
            comp_title=self.comp_title_edit.text(),
            standalone_threshold=standalone_thresh
        )
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.status_updated.connect(self.update_status)
        self.worker_thread.merge_completed.connect(self.on_merge_completed)
        self.worker_thread.merge_failed.connect(self.on_merge_failed)
        
        self.worker_thread.start()
        self.update_ui_state()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def update_time_display(self):
        if self.start_time is None: return
        elapsed = time.time() - self.start_time
        elapsed_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"
        self.detailed_status.setText(f"Elapsed: {elapsed_str}")

    def on_merge_completed(self, result_msg):
        self.progress_timer.stop()
        self.worker_thread = None
        self.progress_bar.setValue(100)
        self.status_label.setText("Completed Successfully!")
        self.detailed_status.setText("All tasks finished.")
        self.update_ui_state()
        
        QMessageBox.information(self, "Success", f"Video processing complete!\n\nOutput:\n{result_msg}")

    def on_merge_failed(self, error_message):
        self.progress_timer.stop()
        self.worker_thread = None
        self.progress_bar.setValue(0)
        self.status_label.setText("Failed")
        self.detailed_status.setText("Error occurred")
        self.update_ui_state()
        QMessageBox.critical(self, "Error", f"Failed to merge videos:\n{error_message}")

    def closeEvent(self, event):
        if self.is_processing():
            reply = QMessageBox.question(self, "Exit", "Processing in progress. Cancel and exit?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker_thread.cancel()
                self.worker_thread.wait(2000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def check_for_updates(self):
        """Start thread to check for updates from remote URL"""
        self.update_worker = UpdateCheckerWorker(UPDATE_URL)
        self.update_worker.update_available.connect(self.on_update_found)
        self.update_worker.start()

    def on_update_found(self, new_version, download_url, message):
        """Handle when a new version is detected"""
        if new_version != CURRENT_VERSION:
            # Simple notification to user
            msg = f"A new version (v{new_version}) is available!\n\n"
            if message:
                msg += f"What's new:\n{message}\n\n"
            msg += "Would you like to visit the download page?"
            
            res = QMessageBox.information(self, "Update Available", msg, 
                                        QMessageBox.Yes | QMessageBox.No)
            if res == QMessageBox.Yes:
                import webbrowser
                webbrowser.open(download_url)

def main():
    app = QApplication(sys.argv)
    window = VideoMergerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()