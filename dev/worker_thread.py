"""
Worker Thread for Video Processing
Handles video merging in a separate thread to keep the UI responsive
Provides progress updates and error handling
"""

from PyQt5.QtCore import QThread, pyqtSignal
import os
import json
import urllib.request
import traceback
from typing import List

from video_merger_robust import RobustVideoMerger


class VideoMergerWorker(QThread):
    """
    Worker thread for handling video merge operations
    Runs video processing in background to prevent UI freezing
    """
    
    # Signals for communicating with the main thread
    progress_updated = pyqtSignal(int)  # Progress percentage (0-100)
    status_updated = pyqtSignal(str)    # Status message
    merge_completed = pyqtSignal(str)   # Output file path on success
    merge_failed = pyqtSignal(str)      # Error message on failure
    
    def __init__(self, video_files: List[str], output_path: str, video_merger: RobustVideoMerger, 
                 max_duration: float = 0, max_clip_count: int = 0, auto_naming: bool = True,
                 comp_title: str = "Merge", standalone_threshold: float = 0):
        """
        Initialize the worker thread
        
        Args:
            video_files: List of input video file paths
            output_path: Path for the output merged video
            video_merger: VideoMerger instance for processing
            max_duration: Max duration per output video (in seconds). 0 to disable splitting.
            max_clip_count: Max clips per output video. 0 to disable splitting.
            auto_naming: Whether to use the clip-X-Y naming format.
            comp_title: Custom title for the compilation.
            standalone_threshold: Videos longer than this will be standalone (in seconds).
        """
        super().__init__()
        
        self.video_files = video_files
        self.output_path = output_path
        self.video_merger = video_merger
        self.max_duration = max_duration
        self.max_clip_count = max_clip_count
        self.auto_naming = auto_naming
        self.comp_title = comp_title
        self.standalone_threshold = standalone_threshold
        self._is_cancelled = False
    
    def run(self):
        """
        Main thread execution method
        Performs video validation and merging with progress updates
        """
        
        try:
            # Emit initial status
            self.status_updated.emit("Validating video files...")
            self.progress_updated.emit(0)
            
            # Validate all video files before processing
            invalid_files = self.video_merger.validate_video_files(self.video_files)
            
            if invalid_files:
                error_msg = "Invalid video files found:\n" + "\n".join(invalid_files)
                self.merge_failed.emit(error_msg)
                return
            
            if self._is_cancelled:
                return
            
            # Step 1: Calculate batches if splitting is enabled
            batches = []
            if self.max_duration > 0 or self.max_clip_count > 0 or self.standalone_threshold > 0:
                self.status_updated.emit("Calculating batches...")
                batches = self.video_merger.calculate_batches(
                    self.video_files, 
                    max_duration_sec=self.max_duration, 
                    max_clip_count=self.max_clip_count,
                    standalone_threshold_sec=self.standalone_threshold
                )
            else:
                batches = [self.video_files]
            
            total_batches = len(batches)
            
            # If only 1 batch, just use original output path
            # If multiple, key them _part1, _part2, etc.
            
            generated_files = []
            
            for index, batch_files in enumerate(batches):
                if self._is_cancelled:
                    return

                # Determine output filename for this batch
                current_output_path = self.output_path
                if total_batches > 1:
                    base, ext = os.path.splitext(self.output_path)
                    folder = os.path.dirname(self.output_path)
                    filename = os.path.basename(self.output_path)
                    
                    if self.auto_naming:
                        # Find the range of clips in this batch relative to original list
                        start_idx = self.video_files.index(batch_files[0]) + 1
                        end_idx = self.video_files.index(batch_files[-1]) + 1
                        
                        # [Title] clip-1-40 merge 1.mp4
                        safe_title = "".join([c for c in self.comp_title if c.isalnum() or c in (' ', '-', '_')]).strip()
                        if not safe_title: safe_title = "Project"
                        new_name = f"{safe_title} clip-{start_idx}-{end_idx} merge {index+1}{ext}"
                        current_output_path = os.path.join(folder, new_name)
                    else:
                        current_output_path = f"{base}_part{index+1}{ext}"
                
                batch_number = index + 1
                
                # Update status
                if total_batches > 1:
                    self.status_updated.emit(f"Processing Part {batch_number}/{total_batches} ({len(batch_files)} clips)...")
                else:
                    self.status_updated.emit("Starting video merge process...")
                
                # Define progress callback function specifically for this batch
                def progress_callback(prog: int, status: str):
                    if not self._is_cancelled:
                        # Map 0-100 of this batch to overall progress
                        # e.g. Batch 1 is 0-50%, Batch 2 is 50-100%
                        overall_progress = int(((index + (prog / 100)) / total_batches) * 100)
                        self.progress_updated.emit(overall_progress)
                        
                        # Use detailed status if multiple batches
                        if total_batches > 1:
                            self.status_updated.emit(f"[Part {batch_number}/{total_batches}] {status}")
                        else:
                            self.status_updated.emit(status)
                
                # Start the video merge process for this batch
                success = self.video_merger.merge_videos(
                    video_files=batch_files,
                    output_path=current_output_path,
                    progress_callback=progress_callback
                )
                
                if not success:
                    self.merge_failed.emit(f"Failed to process part {batch_number}")
                    return
                
                generated_files.append(current_output_path)
            
            if self._is_cancelled:
                return
            
            # Emit completion signal with the main output path (or list description)
            if total_batches > 1:
                self.merge_completed.emit(f"{total_batches} parts created starting with:\n{generated_files[0]}")
            else:
                self.merge_completed.emit(self.output_path)
                
        except Exception as e:
            # Handle any unexpected errors
            error_msg = f"An error occurred during video processing:\n\n{str(e)}"
            
            # Include traceback for debugging if needed
            if hasattr(e, '__traceback__'):
                error_msg += f"\n\nTechnical details:\n{traceback.format_exc()}"
            
            self.merge_failed.emit(error_msg)
    
    def cancel(self):
        """
        Cancel the current video processing operation
        """
        self._is_cancelled = True
        self.status_updated.emit("Cancelling video merge...")
    
    def is_cancelled(self) -> bool:
        """
        Check if the operation has been cancelled
        """
        return self._is_cancelled


class VideoInfoWorker(QThread):
    """
    Worker thread for getting video file information including duration
    """
    
    # Signals for communicating with the main thread
    info_ready = pyqtSignal(str, dict)    # file_path, video_info
    info_failed = pyqtSignal(str, str)    # file_path, error_message
    
    def __init__(self, video_files: List[str], video_merger: RobustVideoMerger):
        """
        Initialize the video info worker
        """
        super().__init__()
        self.video_files = video_files
        self.video_merger = video_merger
    
    def run(self):
        """
        Main thread execution method
        Gets information for each video file
        """
        for video_path in self.video_files:
            try:
                # Get video information
                video_info = self.video_merger.get_video_info(video_path)
                self.info_ready.emit(video_path, video_info)
                
            except Exception as e:
                # Emit error for this specific file
                self.info_failed.emit(video_path, str(e))


class UpdateCheckerWorker(QThread):
    """
    Worker thread for checking software updates remotely
    """
    update_available = pyqtSignal(str, str, str) # version, url, message
    
    def __init__(self, check_url: str):
        super().__init__()
        self.check_url = check_url
    
    def run(self):
        try:
            # Use urllib to avoid external dependencies like 'requests'
            with urllib.request.urlopen(self.check_url, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    version = data.get('version')
                    url = data.get('download_url')
                    message = data.get('message', '')
                    
                    if version and url:
                        self.update_available.emit(version, url, message)
        except Exception:
            return  # Fail silently for placeholder URLs
