import os
import tempfile
from pathlib import Path
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class PDFConverter:
    def __init__(self):
        self.supported_formats = ['PNG', 'JPEG', 'BMP', 'TIFF']
    
    def get_pdf_info(self, pdf_path):
        """获取PDF文件信息"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                page_count = len(reader.pages)
                
                # 获取文档信息
                info = reader.metadata
                title = info.get('/Title', '未知标题')
                author = info.get('/Author', '未知作者')
                
                return {
                    'page_count': page_count,
                    'title': title,
                    'author': author,
                    'file_size': os.path.getsize(pdf_path)
                }
        except Exception as e:
            logger.error(f"获取PDF信息失败: {e}")
            return None
    
    def convert_pdf_to_images(self, pdf_path, output_dir, format='PNG', dpi=200, 
                             output_prefix=None, progress_callback=None):
        """将PDF转换为图片"""
        try:
            # 验证输入文件
            if not os.path.isfile(pdf_path):
                raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 设置输出文件名前缀
            if output_prefix is None:
                output_prefix = Path(pdf_path).stem
            
            # 转换PDF为图片
            logger.info(f"开始转换PDF: {pdf_path}")
            images = convert_from_path(pdf_path, dpi=dpi)
            
            saved_files = []
            total_pages = len(images)
            
            for i, image in enumerate(images):
                # 生成输出文件名
                output_filename = f"{output_prefix}_page_{i+1:03d}.{format.lower()}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片
                if format.upper() == 'JPEG':
                    image = image.convert('RGB')  # JPEG需要RGB模式
                
                image.save(output_path, format=format)
                saved_files.append(output_path)
                
                # 更新进度
                if progress_callback:
                    progress_callback(i + 1, total_pages)
                
                logger.info(f"已保存第 {i+1} 页: {output_path}")
            
            logger.info(f"转换完成，共 {total_pages} 页")
            return saved_files
            
        except Exception as e:
            logger.error(f"PDF转换失败: {e}")
            raise
    
    def batch_convert(self, pdf_files, output_dir, format='PNG', dpi=200):
        """批量转换多个PDF文件"""
        results = []
        total_files = len(pdf_files)
        
        for i, pdf_file in enumerate(pdf_files):
            try:
                logger.info(f"处理文件 {i+1}/{total_files}: {pdf_file}")
                output_subdir = os.path.join(output_dir, Path(pdf_file).stem)
                saved_files = self.convert_pdf_to_images(
                    pdf_file, output_subdir, format, dpi
                )
                results.append({
                    'input_file': pdf_file,
                    'output_files': saved_files,
                    'status': 'success'
                })
            except Exception as e:
                logger.error(f"处理文件失败 {pdf_file}: {e}")
                results.append({
                    'input_file': pdf_file,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results