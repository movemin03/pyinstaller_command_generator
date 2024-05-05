# PyInstaller Command Generator (English description)

PyInstaller Command Generator is a user-friendly tool designed to facilitate the generation of PyInstaller commands with ease. It provides a graphical interface for creating PyInstaller commands effortlessly.

## Requirements:
```cmd
pip install tkinter
```

## Usage:
1. Run the `pyinstaller_command_generator.py` script.
2. Enter the necessary details and configurations in the GUI.
3. Click the "Generate Command" button to generate the PyInstaller command.
4. Copy the generated command and use it to convert your Python script into an executable.

## PyInstaller Command:
To export this script using PyInstaller, use the following command:
```cmd
pyinstaller pyinstaller_command_generator.py --onefile --hidden-import os --hidden-import tkinter --hidden-import ast --hidden-import subprocess
```
---
---

# PyInstaller Command Generator (한국어 설명)

PyInstaller 명령 생성기는 사용자 편의를 위해 설계된 사용하기 쉬운 도구로, PyInstaller 명령을 손쉽게 생성할 수 있도록 도와줍니다. 이 도구는 직관적인 인터페이스를 제공하여 PyInstaller 명령을 간편하게 생성할 수 있습니다.

## 요구 사항:
```cmd
pip install tkinter
```

## 사용법:
pyinstaller_command_generator.py 스크립트를 실행합니다.
GUI에서 필요한 세부 정보와 설정을 입력합니다.
"명령 생성" 버튼을 클릭하여 PyInstaller 명령을 생성합니다.
생성된 명령을 복사하여 Python 스크립트를 실행 파일로 변환하는 데 사용합니다.

## PyInstaller 명령:
이 스크립트를 PyInstaller를 사용하여 내보내려면 다음 명령을 사용하세요:
```cmd
pyinstaller pyinstaller_command_generator.py --onefile --hidden-import os --hidden-import tkinter --hidden-import ast --hidden-import subprocess
```
