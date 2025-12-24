@echo off
echo Installing Video Merger Dependencies...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install PyQt5
echo Installing PyQt5...
python -m pip install PyQt5

REM Install MoviePy with all dependencies
echo Installing MoviePy and dependencies...
python -m pip install imageio
python -m pip install imageio-ffmpeg
python -m pip install decorator
python -m pip install tqdm
python -m pip install proglog
python -m pip install moviepy

REM Test installation
echo.
echo Testing installations...
python -c "import PyQt5; print('PyQt5: OK')"
python -c "import moviepy; print('MoviePy: OK')"

echo.
echo Installation complete! You can now run: python main.py
pause