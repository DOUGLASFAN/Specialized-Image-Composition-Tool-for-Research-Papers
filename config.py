"""
科研论文专用图片组合工具 - 配置管理模块
功能：保存和加载排版配置参数
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """配置管理类"""
    
    def __init__(self):
        self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        :return: 默认配置字典
        """
        return {
            # 布局设置
            'rows': 2,
            'cols': 2,
            
            # 图片缩放设置
            'resize_mode': 'longest_edge',  # longest_edge, shortest_edge, custom, crop
            'image_size': 800,
            'aspect_ratio': None,  # None, (1, 1), (4, 3), (16, 9)
            
            # 间距设置
            'h_spacing': 20,  # 像素
            'v_spacing': 20,  # 像素
            'spacing_unit': 'px',  # px, cm
            
            # 标签设置
            'label_format': '(a)',  # (a), a/, Fig1a
            'label_position': 'top_left',  # top_left, top_right
            'label_font': 'Arial',  # Arial, 宋体, 黑体, Times New Roman
            'label_font_size': 12,
            'label_color': 'black',  # black, white
            'label_margin': 10,
            
            # 画布设置
            'bg_color': 'white',  # white, transparent, black
            'canvas_margin': 10,
            'align': 'center',  # center, left, right
            
            # 输出设置
            'output_format': 'PNG',  # PNG, TIFF, PDF, EPS
            'dpi': 300,
            'output_path': '',
        }
    
    def update_config(self, **kwargs) -> None:
        """
        更新配置
        :param kwargs: 配置参数键值对
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        :return: 配置字典
        """
        return self.config.copy()
    
    def save_config(self, file_path: str) -> tuple:
        """
        保存配置到文件
        :param file_path: 配置文件路径
        :return: (是否成功, 消息)
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
            
            # 保存为JSON格式
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            return True, f"配置已保存到: {file_path}"
        except Exception as e:
            return False, f"保存配置失败: {str(e)}"
    
    def load_config(self, file_path: str) -> tuple:
        """
        从文件加载配置
        :param file_path: 配置文件路径
        :return: (是否成功, 消息)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"配置文件不存在: {file_path}"
            
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # 更新配置（只更新存在的键）
            for key, value in loaded_config.items():
                if key in self.config:
                    self.config[key] = value
            
            return True, f"配置已从 {file_path} 加载"
        except Exception as e:
            return False, f"加载配置失败: {str(e)}"
    
    def reset_config(self) -> None:
        """重置为默认配置"""
        self.config = self._get_default_config()
    
    def get_spacing_in_pixels(self, spacing: float, unit: str) -> int:
        """
        将间距转换为像素
        :param spacing: 间距值
        :param unit: 单位 (px, cm)
        :return: 像素值
        """
        if unit == 'cm':
            # 1 cm ≈ 37.8 像素 (在96 DPI下)
            return int(spacing * 37.8)
        else:
            return int(spacing)
    
    def validate_config(self) -> tuple:
        """
        验证配置参数
        :return: (是否有效, 错误信息)
        """
        errors = []
        
        # 验证行列数
        if self.config['rows'] < 1 or self.config['cols'] < 1:
            errors.append("行数和列数必须大于0")
        
        # 验证图片尺寸
        if self.config['image_size'] < 100:
            errors.append("图片尺寸不能小于100像素")
        
        # 验证间距
        if self.config['h_spacing'] < 0 or self.config['v_spacing'] < 0:
            errors.append("间距不能为负数")
        
        # 验证字体大小
        if self.config['label_font_size'] < 8 or self.config['label_font_size'] > 72:
            errors.append("字体大小应在8-72之间")
        
        # 验证DPI
        if self.config['dpi'] < 72 or self.config['dpi'] > 1200:
            errors.append("DPI应在72-1200之间")
        
        if errors:
            return False, "\n".join(errors)
        return True, "配置验证通过"