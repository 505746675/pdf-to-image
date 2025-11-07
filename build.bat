@echo off
echo 正在构建PDF转图片工具...

REM 创建虚拟环境
python -m venv build_env
call build_env\Scripts\activate.bat

REM 安装依赖
pip install -r requirements.txt

REM 构建可执行文件
pyinstaller --name="PDF转图片工具" ^
            --windowed ^
            --icon=assets/icon.ico ^
            --add-data="src;src" ^
            src/main.py

echo 构建完成！
echo 可执行文件位置: dist/PDF转图片工具.exe
pause