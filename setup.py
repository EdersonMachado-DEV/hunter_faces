from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_options = {
    "packages": ["cv2", "deepface", "customtkinter", "pymysql", "numpy", "PIL", "os", "datetime", "matplotlib"],
    "excludes": [],
    "include_files": [],
}

executables = [
    Executable("faces.py", base=base, target_name="FaceCounterApp"),
    Executable("app.py", base=base, target_name="FaceCounterDashboard")
]

setup(
    name="Hunter Faces",
    version="1.0",
    description="Aplicativo de contagem facial",
    options={"build_exe": build_options},
    executables=executables
)