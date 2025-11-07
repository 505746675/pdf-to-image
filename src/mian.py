import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_converter.log"),
        logging.StreamHandler()
    ]
)

def main():
    # 创建应用目录
    os.makedirs("output", exist_ok=True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("PDF转图片工具")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()