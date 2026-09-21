uv run pyinstaller --onefile --name lazyopen --clean -i ./face.ico main.py
if exist "build" rmdir /s /q "build"