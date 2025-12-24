"""
Robust Video Merger Engine
Handles diverse video formats and properties with maximum compatibility
"""

import os
import subprocess
import time
import json
import shutil
import platform
import re
from typing import List, Callable, Optional
import imageio_ffmpeg


class RobustVideoMerger:
    """
    Robust video processing engine using FFmpeg backend
    Handles videos with different formats, resolutions, and frame rates
    """
    
    def __init__(self):
        """Initialize the video merger with default settings"""
        self.target_width = 1920
        self.target_height = 1080
        self.target_fps = 30
        self.codec = 'libx264'
        self.audio_codec = 'aac'
        self.use_gpu = False
        self.gpu_codec = 'h264_nvenc'  # NVIDIA hardware encoder
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.performance_level = 0 # 0=Normal, 1=Potato (<4GB), 2=Poverty (<1.5GB)
        self.potato_mode = False
        self.block_size = 10 # Default batch size
        self.max_threads = 0 # 0 means auto
        self.check_gpu_support()
    
    def optimize_for_low_end(self, level: int):
        """
        Enable settings for systems with low RAM/CPU
        level 1: < 4GB RAM (Standard Potato)
        level 2: < 1.5GB RAM (Extreme Potato)
        """
        self.performance_level = level
        self.potato_mode = level > 0
        
        if level >= 1:
            self.block_size = 4
            print(f"Engine: Potato Mode Active (Level {level})")
        
        if level >= 2:
            self.block_size = 2 # Process only 2 clips at once
            self.max_threads = 1 # Force single-thread to save RAM
            print("Engine: Extreme Poverty Mode Active (Single-threaded processing enabled)")
    
    def calculate_batches(self, video_files: List[str], max_duration_sec: float = 0, max_clip_count: int = 0, 
                          cached_durations: dict = None, standalone_threshold_sec: float = 0) -> List[List[str]]:
        """
        Group video files into batches based on duration or clip count.
        [NEW] Supports standalone_threshold_sec to force long videos into their own batch.
        
        Args:
            video_files: List of video file paths
            max_duration_sec: Maximum duration in seconds per batch (0 to disable)
            max_clip_count: Maximum number of clips per batch (0 to disable)
            cached_durations: Optional dict of path -> duration to skip ffprobe
            standalone_threshold_sec: Videos longer than this will be standalone (0 to disable)
            
        Returns:
            List of batches (each batch is a list of file paths)
        """
        if not video_files:
            return []
            
        if max_clip_count > 0 and standalone_threshold_sec <= 0:
            return self.calculate_batches_by_count(video_files, max_clip_count)
            
        batches = []
        current_batch = []
        current_duration = 0.0
        
        for file in video_files:
            try:
                # CRITICAL: If cached_durations is provided, we MUST NOT perform slow I/O on the main thread
                if cached_durations is not None:
                    duration = cached_durations.get(file, 0)
                else:
                    # Only fallback to slow fetch if no cache was provided (usually for command line usage)
                    info = self.get_video_info(file)
                    duration = info.get('duration', 0)
                
                # [NEW] Logic for Auto-Standalone
                is_standalone = standalone_threshold_sec > 0 and duration >= standalone_threshold_sec
                
                if is_standalone:
                    # Finalize current batch if not empty
                    if current_batch:
                        batches.append(current_batch)
                    # Create a standalone batch for this file
                    batches.append([file])
                    current_batch = []
                    current_duration = 0.0
                    continue

                # Standard batching logic
                if max_clip_count > 0 and len(current_batch) >= max_clip_count:
                    batches.append(current_batch)
                    current_batch = [file]
                    current_duration = duration
                elif max_duration_sec > 0 and current_batch and (current_duration + duration > max_duration_sec):
                    batches.append(current_batch)
                    current_batch = [file]
                    current_duration = duration
                else:
                    current_batch.append(file)
                    current_duration += duration
                    
            except Exception as e:
                # Silently handle missing info - UI will show "Analyzing" state anyway
                current_batch.append(file)
        
        # Add the last batch if it exists
        if current_batch:
            batches.append(current_batch)
            
        return batches

    def calculate_batches_by_count(self, video_files: List[str], max_clip_count: int) -> List[List[str]]:
        """
        Group video files into batches where each batch has at most max_clip_count files.
        """
        if not video_files:
            return []
        
        if max_clip_count <= 0:
            return [video_files]
            
        batches = []
        for i in range(0, len(video_files), max_clip_count):
            batches.append(video_files[i : i + max_clip_count])
        return batches
    
    def _get_startupinfo(self):
        """Helper to suppress console window on Windows and set priority"""
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            if self.potato_mode:
                # 0x00004000 = BELOW_NORMAL_PRIORITY_CLASS
                startupinfo.dwFlags |= 0x00004000 
            return startupinfo
        return None

    def check_gpu_support(self):
        """Check if NVIDIA GPU acceleration is available"""
        si = self._get_startupinfo()
        try:
            # Check if nvidia-smi is available (indicates NVIDIA GPU)
            result = subprocess.run(['nvidia-smi'], capture_output=True, check=True, startupinfo=si)
            if result.returncode == 0:
                # Check if FFmpeg supports h264_nvenc
                result = subprocess.run([self.ffmpeg_path, '-hide_banner', '-encoders'], 
                                      capture_output=True, text=True, check=True, startupinfo=si)
                if 'h264_nvenc' in result.stdout:
                    self.use_gpu = True
                    self.gpu_codec = 'h264_nvenc'
                    print("GPU acceleration enabled (NVIDIA RTX detected)")
                elif 'hevc_nvenc' in result.stdout:
                    self.use_gpu = True
                    self.gpu_codec = 'hevc_nvenc'
                    print("GPU acceleration enabled with HEVC (NVIDIA RTX detected)")
                else:
                    print("NVIDIA GPU detected but hardware encoding not available in FFmpeg")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("GPU acceleration not available - using CPU encoding")
            self.use_gpu = False
    
    def merge_videos(self, 
                    video_files: List[str], 
                    output_path: str,
                    progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """
        Merge multiple video files into a single output video.
        Uses a multi-stage FFmpeg process for reliability.
        [NEW] Optimization: If only 1 file, just copy it to save time/quality.
        """
        if not video_files: return False
        
        # Optimization: If only one file, just copy it (fast, no quality loss)
        if len(video_files) == 1:
            if progress_callback:
                progress_callback(50, "Standalone video detected. Using Fast Copy (Preserving Original Quality)...")
            try:
                if os.path.abspath(video_files[0]) == os.path.abspath(output_path):
                    # Already the same file, nothing to do
                    return True
                shutil.copy2(video_files[0], output_path)
                if progress_callback: progress_callback(100, "Fast Copy Complete!")
                return True
            except Exception as copy_e:
                print(f"Fast Copy failed: {copy_e}. Falling back to standard merge...")
                # Fall through to standard merge just in case, though it will fail len < 2
                pass

        temp_files = []
        si = self._get_startupinfo()
        try:
            # Check if FFmpeg is available
            subprocess.run([self.ffmpeg_path, '-version'], capture_output=True, check=True, startupinfo=si)
            
            # Process in blocks to stay stable and avoid command length limits
            BLOCK_SIZE = self.block_size
            
            # Step 1: Merge into intermediate blocks
            total_blocks = (len(video_files) + BLOCK_SIZE - 1) // BLOCK_SIZE
            
            for i in range(0, len(video_files), BLOCK_SIZE):
                block_files = video_files[i : i + BLOCK_SIZE]
                block_num = (i // BLOCK_SIZE) + 1
                
                temp_output = f"temp_block_{block_num}_{int(time.time())}.mp4"
                temp_files.append(temp_output)
                
                if progress_callback:
                    progress_callback(int((block_num-1)/total_blocks * 80), 
                                     f"Merging Batch {block_num}/{total_blocks}...")
                
                # Use faster settings for intermediate blocks
                self._ffmpeg_merge_block(block_files, temp_output, preset='ultrafast', crf=23)
            
            # Step 2: Merge the intermediate blocks into the final result
            if progress_callback:
                progress_callback(90, "Finalizing output (Optimizing Size)...")
            
            # Final merge uses 'medium' preset and higher CRF for best size-to-quality ratio
            self._ffmpeg_merge_block(temp_files, output_path, preset='medium', crf=28)
            
            if progress_callback:
                progress_callback(100, "Success!")
            return True

        except Exception as e:
            # Fallback
            print(f"FFmpeg failed with: {e}")
            try:
                if self.performance_level >= 2:
                    raise Exception("Internal fallback (MoviePy) disabled in Maximum Stability mode to save RAM.")
                
                if progress_callback:
                    progress_callback(0, "Primary engine failed. Using safe fallback...")
                return self._merge_with_moviepy(video_files, output_path, progress_callback)
            except Exception as mp_e:
                raise Exception(f"Merge failed on both engines.\nFFmpeg: {e}\nInternal: {mp_e}")
        finally:
            # Cleanup ALWAYS
            for f in temp_files:
                if os.path.exists(f): 
                    try: os.remove(f)
                    except: pass

    def _ffmpeg_merge_block(self, files: List[str], out: str, preset: str = 'ultrafast', crf: int = 23):
        """
        Merges a small list of files using Decoded Concat (Complex Filter)
        Now supports compression tuning.
        """
        inputs = []
        filter_parts = []
        
        for i, file in enumerate(files):
            inputs.extend(['-i', file])
            
            info = self.get_video_info(file)
            duration = info.get('duration', 1.0)
            has_audio = self._has_audio(file)
            
            v_filter = (f"[{i}:v]scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=decrease,"
                        f"pad={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
            filter_parts.append(v_filter)
            
            if has_audio:
                a_filter = f"[{i}:a]aresample=44100,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{i}]"
            else:
                a_filter = f"anullsrc=channel_layout=stereo:sample_rate=44100:d={duration}[a{i}]"
            
            filter_parts.append(a_filter)

        concat_in = "".join([f"[v{j}][a{j}]" for j in range(len(files))])
        concat_cmd = f"{concat_in}concat=n={len(files)}:v=1:a=1[vout][aout]"
        filter_parts.append(concat_cmd)
        
        full_filter = ";".join(filter_parts)
        
        # Final encoding settings
        final_preset = 'ultrafast' if self.potato_mode else preset
        
        # Level 2+ Poverty Optimizations
        thread_args = ['-threads', str(self.max_threads)] if self.max_threads > 0 else []
        io_args = ['-max_muxing_queue_size', '1024'] if self.performance_level >= 2 else []
        
        cmd = [self.ffmpeg_path, '-y', '-hide_banner'] + thread_args + inputs + [
            '-filter_complex', full_filter,
            '-map', '[vout]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', final_preset, '-crf', str(crf), 
            '-c:a', 'aac', '-b:a', '128k',
            *io_args,
            '-movflags', '+faststart',
            out
        ]
        
        si = self._get_startupinfo()
        res = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si)
        if res.returncode != 0:
            # Provide more helpful debug info in the exception
            error_details = f"FFmpeg Block Failed (Exit {res.returncode}).\nError: {res.stderr}"
            self._log_error(error_details)
            raise Exception(error_details)

    def _log_error(self, message: str):
        """Append error to a local log file for user troubleshooting"""
        try:
            with open("crash_report.log", "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n" + "-"*30 + "\n")
        except:
            pass

    def _has_audio(self, path: str) -> bool:
        """Robustly check if file contains an audio stream using ffprobe"""
        try:
            si = self._get_startupinfo()
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', path]
            res = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si)
            # If output contains 'audio', it has an audio stream
            return "audio" in res.stdout.strip().lower()
        except:
            return False

    def _merge_with_moviepy(self, video_files: List[str], output_path: str,
                           progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """
        Fallback merge using MoviePy with improved robustness
        """
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        try:
            from moviepy.audio.AudioClip import AudioClip
            from moviepy.editor import CompositeVideoClip
        except ImportError:
            pass

        clips = []
        total_files = len(video_files)
        
        try:
            if progress_callback:
                progress_callback(10, "Loading videos with Internal Engine...")
            
            # Load and process each video
            for i, video_path in enumerate(video_files):
                if progress_callback:
                    progress = 10 + int((i / total_files) * 60)
                    progress_callback(progress, f"Processing video {i+1}/{total_files} (internal engine)")
                
                if not os.path.exists(video_path):
                    raise FileNotFoundError(f"Video file not found: {video_path}")
                
                # Load video clip
                clip = VideoFileClip(video_path)
                
                # 1. HANDLE DIMENSIONS
                if clip.w != self.target_width or clip.h != self.target_height:
                    scale = min(self.target_width / clip.w, self.target_height / clip.h)
                    new_w, new_h = int(clip.w * scale), int(clip.h * scale)
                    clip = clip.resize((new_w, new_h))
                    clip = CompositeVideoClip([clip.set_position("center")], 
                                            size=(self.target_width, self.target_height),
                                            bg_color=(0,0,0))
                
                # 2. HANDLE FPS
                clip = clip.set_fps(self.target_fps)

                # 3. HANDLE AUDIO
                if clip.audio is None:
                    # Fix: MoviePy AudioClip needs a duration and a make_frame
                    from moviepy.audio.AudioClip import AudioArrayClip
                    import numpy as np
                    # Create 1 second of silence then clip it to video duration
                    silent_data = np.zeros((int(clip.duration * 44100), 2))
                    silent_audio = AudioArrayClip(silent_data, fps=44100)
                    clip = clip.set_audio(silent_audio)
                
                clips.append(clip)
            
            if progress_callback:
                progress_callback(80, "Merging videos...")
            
            final_video = concatenate_videoclips(clips, method="compose")
            
            if progress_callback:
                progress_callback(90, "Encoding final video...")
            
            final_video.write_videofile(
                output_path,
                codec=self.codec,
                audio_codec=self.audio_codec,
                fps=self.target_fps,
                verbose=False,
                logger=None,
                threads=4
            )
            
            for clip in clips: clip.close()
            final_video.close()
            return True
            
        except Exception as e:
            for clip in clips:
                try: clip.close()
                except: pass
            raise e

    def validate_video_files(self, video_files: List[str]) -> List[str]:
        invalid_files = []
        for video_path in video_files:
            if not os.path.exists(video_path):
                invalid_files.append(f"{video_path} (not found)")
        return invalid_files

    def get_video_info(self, video_path: str) -> dict:
        if not os.path.exists(video_path): raise FileNotFoundError(video_path)
        try:
                si = self._get_startupinfo()
                thread_args = ['-threads', '1'] if self.performance_level >= 2 else []
                # Fallback to ffmpeg -i parsing if ffprobe is missing
                ffprobe_path = os.path.join(os.path.dirname(self.ffmpeg_path), 'ffprobe.exe')
                
                if os.path.exists(ffprobe_path):
                    cmd = [ffprobe_path, '-v', 'quiet', '-print_format', 'json'] + thread_args + ['-show_format', '-show_streams', video_path]
                    res = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si)
                    data = json.loads(res.stdout)
                    v_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), {})
                    return {
                        'filename': os.path.basename(video_path),
                        'duration': float(data['format'].get('duration', 0)),
                        'fps': eval(v_stream.get('r_frame_rate', '0/1')),
                        'width': int(v_stream.get('width', 0)),
                        'height': int(v_stream.get('height', 0)),
                        'file_size': int(data['format'].get('size', 0))
                    }
                else:
                    return self._get_video_info_via_ffmpeg(video_path)
        except Exception as e:
            # Fallback to moviepy only if not Level 2
            if self.performance_level < 2:
                from moviepy.editor import VideoFileClip
                clip = VideoFileClip(video_path)
                info = {'filename': os.path.basename(video_path), 'duration': clip.duration, 'width': clip.w, 'height': clip.h, 'file_size': os.path.getsize(video_path)}
                clip.close()
                return info
            else:
                raise e

    def _get_video_info_via_ffmpeg(self, video_path: str) -> dict:
        """Fallback info parser using ffmpeg -i (No ffprobe required)"""
        si = self._get_startupinfo()
        cmd = [self.ffmpeg_path, '-i', video_path]
        res = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si)
        output = res.stderr # ffmpeg outputs info to stderr
        
        info = {'filename': os.path.basename(video_path), 'duration': 0, 'width': 1920, 'height': 1080}
        
        # Duration match
        dur_match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", output)
        if dur_match:
            h, m, s = map(float, dur_match.groups())
            info['duration'] = h * 3600 + m * 60 + s
            
        # Resolution match
        res_match = re.search(r"Video:.*?\s(\d+)x(\d+)", output)
        if res_match:
            info['width'] = int(res_match.group(1))
            info['height'] = int(res_match.group(2))
            
        info['file_size'] = os.path.getsize(video_path)
        return info