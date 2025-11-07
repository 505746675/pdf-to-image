import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QProgressBar,
                             QComboBox, QSpinBox, QCheckBox, QFileDialog,
                             QMessageBox, QListWidget, QGroupBox, QTextEdit,
                             QSplitter, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from pdf_converter import PDFConverter

class ConversionThread(QThread):
    """转换线程，避免界面冻结"""
    progress = pyqtSignal(int, int)  # 当前页，总页数
    finished = pyqtSignal(list)      # 保存的文件列表
    error = pyqtSignal(str)         # 错误信息
    
    def __init__(self, pdf_path, output_dir, format, dpi, prefix):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.format = format
        self.dpi = dpi
        self.prefix = prefix
        self.converter = PDFConverter()
    
    def run(self):
        try:
            saved_files = self.converter.convert_pdf_to_images(
                self.pdf_path, self.output_dir, self.format, 
                self.dpi, self.prefix, self.progress.emit
            )
            self.finished.emit(saved_files)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converter = PDFConverter()
        self.current_pdf_path = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("PDF转图片工具 v1.0")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 单文件转换标签页
        single_tab = QWidget()
        self.setup_single_tab(single_tab)
        tab_widget.addTab(single_tab, "单文件转换")
        
        # 批量转换标签页
        batch_tab = QWidget()
        self.setup_batch_tab(batch_tab)
        tab_widget.addTab(batch_tab, "批量转换")
        
        # 日志显示
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
    
    def setup_single_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 文件选择区域
        file_group = QGroupBox("PDF文件选择")
        file_layout = QHBoxLayout()
        
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("选择PDF文件...")
        file_layout.addWidget(self.file_path)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_pdf_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # PDF信息显示
        info_group = QGroupBox("文件信息")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("请选择PDF文件")
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 转换设置
        settings_group = QGroupBox("转换设置")
        settings_layout = QVBoxLayout()
        
        # 输出目录
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:"))
        self.output_dir = QLineEdit()
        self.output_dir.setText("output")
        output_layout.addWidget(self.output_dir)
        output_browse_btn = QPushButton("浏览...")
        output_browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_browse_btn)
        settings_layout.addLayout(output_layout)
        
        # 格式和DPI设置
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(self.converter.supported_formats)
        self.format_combo.setCurrentText('PNG')
        format_layout.addWidget(self.format_combo)
        
        format_layout.addWidget(QLabel("DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(200)
        format_layout.addWidget(self.dpi_spin)
        
        format_layout.addStretch()
        settings_layout.addLayout(format_layout)
        
        # 文件前缀
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("文件前缀:"))
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("留空使用PDF文件名")
        prefix_layout.addWidget(self.prefix_edit)
        settings_layout.addLayout(prefix_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        layout.addWidget(self.convert_btn)
        
        layout.addStretch()
    
    def setup_batch_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 文件列表区域
        list_group = QGroupBox("PDF文件列表")
        list_layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        list_layout.addWidget(self.file_list)
        
        list_buttons_layout = QHBoxLayout()
        add_files_btn = QPushButton("添加文件")
        add_files_btn.clicked.connect(self.add_batch_files)
        list_buttons_layout.addWidget(add_files_btn)
        
        add_folder_btn = QPushButton("添加文件夹")
        add_folder_btn.clicked.connect(self.add_batch_folder)
        list_buttons_layout.addWidget(add_folder_btn)
        
        remove_btn = QPushButton("移除选中")
        remove_btn.clicked.connect(self.remove_selected_files)
        list_buttons_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("清空列表")
        clear_btn.clicked.connect(self.clear_file_list)
        list_buttons_layout.addWidget(clear_btn)
        
        list_buttons_layout.addStretch()
        list_layout.addLayout(list_buttons_layout)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 批量转换设置
        batch_settings_group = QGroupBox("批量转换设置")
        batch_settings_layout = QVBoxLayout()
        
        batch_output_layout = QHBoxLayout()
        batch_output_layout.addWidget(QLabel("输出目录:"))
        self.batch_output_dir = QLineEdit()
        self.batch_output_dir.setText("batch_output")
        batch_output_layout.addWidget(self.batch_output_dir)
        batch_output_browse_btn = QPushButton("浏览...")
        batch_output_browse_btn.clicked.connect(self.browse_batch_output_dir)
        batch_output_layout.addWidget(batch_output_browse_btn)
        batch_settings_layout.addLayout(batch_output_layout)
        
        batch_format_layout = QHBoxLayout()
        batch_format_layout.addWidget(QLabel("输出格式:"))
        self.batch_format_combo = QComboBox()
        self.batch_format_combo.addItems(self.converter.supported_formats)
        self.batch_format_combo.setCurrentText('PNG')
        batch_format_layout.addWidget(self.batch_format_combo)
        
        batch_format_layout.addWidget(QLabel("DPI:"))
        self.batch_dpi_spin = QSpinBox()
        self.batch_dpi_spin.setRange(72, 600)
        self.batch_dpi_spin.setValue(200)
        batch_format_layout.addWidget(self.batch_dpi_spin)
        
        batch_format_layout.addStretch()
        batch_settings_layout.addLayout(batch_format_layout)
        
        batch_settings_group.setLayout(batch_settings_layout)
        layout.addWidget(batch_settings_group)
        
        # 批量转换按钮
        self.batch_convert_btn = QPushButton("开始批量转换")
        self.batch_convert_btn.clicked.connect(self.start_batch_conversion)
        self.batch_convert_btn.setEnabled(False)
        layout.addWidget(self.batch_convert_btn)
        
        layout.addStretch()
    
    def browse_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.file_path.setText(file_path)
            self.current_pdf_path = file_path
            self.update_file_info(file_path)
            self.convert_btn.setEnabled(True)
    
    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir.setText(dir_path)
    
    def browse_batch_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择批量输出目录")
        if dir_path:
            self.batch_output_dir.setText(dir_path)
    
    def update_file_info(self, pdf_path):
        try:
            info = self.converter.get_pdf_info(pdf_path)
            if info:
                info_text = (f"页数: {info['page_count']} | "
                           f"标题: {info['title']} | "
                           f"作者: {info['author']} | "
                           f"文件大小: {info['file_size'] / 1024:.1f} KB")
                self.info_label.setText(info_text)
                self.log_message(f"已加载PDF文件: {Path(pdf_path).name}")
            else:
                self.info_label.setText("无法读取PDF信息")
        except Exception as e:
            self.info_label.setText(f"读取PDF信息失败: {e}")
    
    def start_conversion(self):
        if not self.current_pdf_path:
            QMessageBox.warning(self, "警告", "请先选择PDF文件")
            return
        
        output_dir = self.output_dir.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "警告", "请设置输出目录")
            return
        
        # 创建转换线程
        self.conversion_thread = ConversionThread(
            self.current_pdf_path,
            output_dir,
            self.format_combo.currentText(),
            self.dpi_spin.value(),
            self.prefix_edit.text().strip() or None
        )
        
        # 连接信号
        self.conversion_thread.progress.connect(self.update_progress)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.error.connect(self.conversion_error)
        
        # 更新UI状态
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 开始转换
        self.conversion_thread.start()
        self.log_message("开始转换PDF文件...")
    
    def update_progress(self, current, total):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.log_message(f"转换进度: {current}/{total} 页")
    
    def conversion_finished(self, saved_files):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        msg = f"转换完成！共生成 {len(saved_files)} 个图片文件"
        QMessageBox.information(self, "完成", msg)
        self.log_message(msg)
        
        # 打开输出目录
        output_dir = self.output_dir.text().strip()
        if os.path.exists(output_dir):
            os.startfile(output_dir)  # Windows系统打开文件夹
    
    def conversion_error(self, error_msg):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(self, "错误", f"转换失败:\n{error_msg}")
        self.log_message(f"转换失败: {error_msg}")
    
    def add_batch_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        for file_path in files:
            if file_path not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                self.file_list.addItem(file_path)
        self.update_batch_convert_button()
    
    def add_batch_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择包含PDF文件的文件夹")
        if folder_path:
            pdf_files = list(Path(folder_path).glob("*.pdf"))
            for pdf_file in pdf_files:
                if str(pdf_file) not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                    self.file_list.addItem(str(pdf_file))
            self.update_batch_convert_button()
    
    def remove_selected_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self.update_batch_convert_button()
    
    def clear_file_list(self):
        self.file_list.clear()
        self.update_batch_convert_button()
    
    def update_batch_convert_button(self):
        self.batch_convert_btn.setEnabled(self.file_list.count() > 0)
    
    def start_batch_conversion(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "警告", "请添加要转换的PDF文件")
            return
        
        output_dir = self.batch_output_dir.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "警告", "请设置输出目录")
            return
        
        # 获取文件列表
        pdf_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        
        # 执行批量转换
        try:
            results = self.converter.batch_convert(
                pdf_files,
                output_dir,
                self.batch_format_combo.currentText(),
                self.batch_dpi_spin.value()
            )
            
            # 统计结果
            success_count = sum(1 for r in results if r['status'] == 'success')
            failed_count = len(results) - success_count
            
            msg = f"批量转换完成！成功: {success_count}, 失败: {failed_count}"
            QMessageBox.information(self, "完成", msg)
            self.log_message(msg)
            
            # 显示失败的文件
            if failed_count > 0:
                failed_files = [r['input_file'] for r in results if r['status'] == 'failed']
                self.log_message("失败文件:\n" + "\n".join(failed_files))
            
            # 打开输出目录
            if os.path.exists(output_dir):
                os.startfile(output_dir)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量转换失败:\n{str(e)}")
            self.log_message(f"批量转换失败: {str(e)}")
    
    def log_message(self, message):
        self.log_text.append(f"[{self.get_current_time()}] {message}")
    
    def get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")