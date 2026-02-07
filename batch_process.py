"""
科研论文专用图片组合工具 - 批量处理模块
功能：批量处理多个文件夹的图片，自动生成组合图
"""

import os
from typing import List, Tuple
from PyQt5.QtWidgets import QProgressDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

from image_process import ImageProcessor
from config import ConfigManager


class BatchProcessor(QThread):
    """批量处理线程"""
    
    progress_updated = pyqtSignal(int, int, str)  # (当前, 总数, 当前文件名)
    finished = pyqtSignal(bool, str)  # (是否成功, 消息)
    
    def __init__(self, folders: List[str], config: dict, output_dir: str):
        super().__init__()
        self.folders = folders
        self.config = config
        self.output_dir = output_dir
    
    def run(self):
        """执行批量处理"""
        try:
            total_folders = len(self.folders)
            processed = 0
            
            for folder in self.folders:
                # 获取文件夹名称
                folder_name = os.path.basename(folder)
                
                # 发送进度更新
                self.progress_updated.emit(processed, total_folders, folder_name)
                
                # 处理该文件夹
                success, message = self.process_folder(folder, folder_name)
                
                if not success:
                    self.finished.emit(False, f"处理文件夹 {folder_name} 失败: {message}")
                    return
                
                processed += 1
            
            self.finished.emit(True, f"批量处理完成！共处理 {processed} 个文件夹")
            
        except Exception as e:
            self.finished.emit(False, f"批量处理出错: {str(e)}")
    
    def process_folder(self, folder: str, folder_name: str) -> Tuple[bool, str]:
        """
        处理单个文件夹
        :param folder: 文件夹路径
        :param folder_name: 文件夹名称
        :return: (是否成功, 消息)
        """
        try:
            # 获取文件夹中的所有图片
            image_files = []
            for file in os.listdir(folder):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.eps')):
                    image_files.append(os.path.join(folder, file))
            
            if not image_files:
                return False, "文件夹中没有找到图片文件"
            
            # 加载图片
            processor = ImageProcessor()
            success, message = processor.load_images(image_files)
            if not success:
                return False, message
            
            # 应用配置
            rows = self.config['rows']
            cols = self.config['cols']
            
            # 缩放图片
            aspect_ratio = self.config['aspect_ratio']
            resized_images = []
            for img in processor.images:
                resized = processor.resize_image(
                    img, 
                    self.config['resize_mode'], 
                    self.config['image_size'], 
                    aspect_ratio
                )
                resized_images.append(resized)
            processor.images = resized_images
            
            # 获取间距
            h_spacing = self.config['h_spacing']
            v_spacing = self.config['v_spacing']
            if self.config['spacing_unit'] == 'cm':
                config_manager = ConfigManager()
                h_spacing = config_manager.get_spacing_in_pixels(h_spacing, 'cm')
                v_spacing = config_manager.get_spacing_in_pixels(v_spacing, 'cm')
            
            # 创建组合图片
            combined = processor.create_combined_image(
                rows, cols,
                h_spacing, v_spacing,
                self.config['bg_color'],
                self.config['canvas_margin'],
                self.config['align']
            )
            
            # 添加标签
            combined = processor.add_labels(
                combined, rows, cols,
                self.config['label_format'],
                self.config['label_position'],
                self.config['label_font'],
                self.config['label_font_size'],
                self.config['label_color'],
                self.config['label_margin'],
                h_spacing, v_spacing,
                self.config['canvas_margin'],
                self.config['align']
            )
            
            # 保存图片
            output_format = self.config['output_format'].lower()
            output_filename = f"{folder_name}_combined.{output_format}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            success, message = processor.save_image(
                combined,
                output_path,
                self.config['dpi'],
                self.config['output_format']
            )
            
            if success:
                return True, message
            else:
                return False, message
            
        except Exception as e:
            return False, str(e)