import os
import shutil
from pathlib import Path

def validate_pdf_file(file_path):
    """验证PDF文件是否有效"""
    if not os.path.isfile(file_path):
        return False, "文件不存在"
    
    if not file_path.lower().endswith('.pdf'):
        return False, "文件不是PDF格式"
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return False, "文件为空"
    
    if file_size > 100 * 1024 * 1024:  # 100MB限制
        return False, "文件过大（超过100MB）"
    
    return True, "文件有效"

def get_available_disk_space(path):
    """获取指定路径的可用磁盘空间"""
    try:
        total, used, free = shutil.disk_usage(path)
        return free
    except:
        return 0

def format_file_size(size_bytes):
    """格式化文件大小显示"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"