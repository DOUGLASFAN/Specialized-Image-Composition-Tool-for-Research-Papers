"""
科研论文专用图片组合工具 - 核心图像处理模块
功能：图片加载、缩放、裁剪、拼接、标签添加、格式输出
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import os
from typing import List, Tuple, Optional, Dict
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg


class ImageProcessor:
    """图像处理核心类"""
    
    def __init__(self):
        self.images = []  # 存储加载的图片
        self.image_paths = []  # 存储图片路径
        
    def clear(self):
        """
        释放图片资源
        """
        # 清空图片列表，释放内存
        self.images.clear()
        self.image_paths.clear()
        # 强制垃圾回收
        import gc
        gc.collect()
        
    def load_images(self, paths: List[str]) -> Tuple[bool, str]:
        """
        加载图片列表
        :param paths: 图片路径列表
        :return: (是否成功, 错误信息)
        """
        try:
            errors = []
            added_count = 0
            skipped_count = 0
            
            for path in paths:
                try:
                    # 检查文件是否已存在
                    if path in self.image_paths:
                        skipped_count += 1
                        continue
                    
                    if not os.path.exists(path):
                        errors.append(f"文件不存在: {path}")
                        continue
                        
                    # 根据文件扩展名选择加载方式
                    ext = os.path.splitext(path)[1].lower()
                    
                    if ext == '.eps':
                        # EPS格式使用matplotlib加载
                        img = self._load_eps(path)
                    else:
                        # 其他格式使用PIL加载
                        img = Image.open(path)
                        # 处理EXIF方向信息
                        try:
                            from PIL import ImageOps
                            img = ImageOps.exif_transpose(img)
                        except:
                            pass
                        # 转换为RGB模式（如果是RGBA则保留透明度）
                        if img.mode == 'RGBA':
                            pass  # 保持RGBA模式
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                    
                    # 创建缩略图用于预览，减少内存使用
                    # 保留原始图片尺寸信息，但存储缩略图
                    thumbnail = img.copy()
                    # 对于大图，创建合理大小的缩略图
                    max_size = 1024  # 最大边长
                    if max(thumbnail.width, thumbnail.height) > max_size:
                        thumbnail.thumbnail((max_size, max_size), Image.LANCZOS)
                    
                    self.images.append(thumbnail)
                    self.image_paths.append(path)
                    added_count += 1
                    
                except Exception as e:
                    errors.append(f"加载失败 {path}: {str(e)}")
            
            if errors:
                return False, "\n".join(errors)
            
            message = f"成功加载 {added_count} 张图片"
            if skipped_count > 0:
                message += f"，跳过 {skipped_count} 张重复图片"
            return True, message
        except Exception as e:
            return False, f"加载图片时发生错误: {str(e)}"
    
    def _load_eps(self, path: str) -> Image.Image:
        """
        加载EPS格式图片
        :param path: EPS文件路径
        :return: PIL Image对象
        """
        try:
            # 使用matplotlib加载EPS
            fig = plt.figure(figsize=(8, 8), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1], frameon=False)
            ax.axis('off')
            ax.imshow(plt.imread(path))
            
            canvas = FigureCanvasAgg(fig)
            canvas.draw()
            img_array = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
            img_array = img_array.reshape(canvas.get_width_height()[::-1] + (3,))
            
            plt.close(fig)
            return Image.fromarray(img_array)
        except:
            # 如果matplotlib加载失败，尝试使用PIL
            return Image.open(path)
    
    def resize_image(self, img: Image.Image, mode: str = 'longest_edge', 
                     size: int = 800, aspect_ratio: Optional[Tuple[int, int]] = None, 
                     fast: bool = False) -> Image.Image:
        """
        调整图片尺寸
        :param img: 原始图片
        :param mode: 缩放模式 ('original', 'longest_edge', 'shortest_edge', 'custom', 'crop')
        :param size: 目标尺寸
        :param aspect_ratio: 固定宽高比 (width, height)
        :param fast: 是否使用快速缩放算法（用于预览）
        :return: 调整后的图片
        """
        try:
            # 使用原始分辨率模式
            if mode == 'original':
                return img
            
            # 选择缩放算法
            resize_algorithm = Image.Resampling.NEAREST if fast else Image.Resampling.LANCZOS
            
            if aspect_ratio:
                # 强制固定宽高比
                target_ratio = aspect_ratio[0] / aspect_ratio[1]
                current_ratio = img.width / img.height
                
                if current_ratio > target_ratio:
                    # 图片更宽，按宽度缩放
                    new_width = size
                    new_height = int(size / target_ratio)
                else:
                    # 图片更高，按高度缩放
                    new_height = size
                    new_width = int(size * target_ratio)
                
                img = img.resize((new_width, new_height), resize_algorithm)
                
                # 裁剪到固定比例
                if current_ratio != target_ratio:
                    if current_ratio > target_ratio:
                        # 裁剪宽度
                        left = (img.width - int(img.height * target_ratio)) // 2
                        img = img.crop((left, 0, left + int(img.height * target_ratio), img.height))
                    else:
                        # 裁剪高度
                        top = (img.height - int(img.width / target_ratio)) // 2
                        img = img.crop((0, top, img.width, top + int(img.width / target_ratio)))
                
                return img
            
            if mode == 'longest_edge':
                # 按最长边缩放
                ratio = size / max(img.width, img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                return img.resize(new_size, resize_algorithm)
            
            elif mode == 'shortest_edge':
                # 按最短边缩放
                ratio = size / min(img.width, img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                return img.resize(new_size, resize_algorithm)
            
            elif mode == 'custom':
                # 自定义尺寸（保持比例）
                ratio = size / min(img.width, img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                return img.resize(new_size, resize_algorithm)
            
            elif mode == 'crop':
                # 居中裁剪到正方形
                min_side = min(img.width, img.height)
                left = (img.width - min_side) // 2
                top = (img.height - min_side) // 2
                img = img.crop((left, top, left + min_side, top + min_side))
                return img.resize((size, size), resize_algorithm)
            
            return img
        except Exception as e:
            print(f"调整图片尺寸时发生错误: {str(e)}")
            return img
    
    def create_combined_image(self, rows: int, cols: int, 
                             h_spacing: int = 20, v_spacing: int = 20,
                             bg_color: str = 'white',
                             margin: int = 10,
                             align: str = 'center') -> Optional[Image.Image]:
        """
        创建组合图片
        :param rows: 行数
        :param cols: 列数
        :param h_spacing: 水平间距（像素）
        :param v_spacing: 垂直间距（像素）
        :param bg_color: 背景颜色
        :param margin: 画布边距
        :param align: 对齐方式 ('center', 'left', 'right')
        :return: 组合后的图片
        """
        try:
            if not self.images:
                return None
            
            # 计算每行每列的最大宽度和高度
            row_heights = []
            col_widths = []
            
            for r in range(rows):
                max_height = 0
                for c in range(cols):
                    idx = r * cols + c
                    if idx < len(self.images):
                        max_height = max(max_height, self.images[idx].height)
                row_heights.append(max_height)
            
            for c in range(cols):
                max_width = 0
                for r in range(rows):
                    idx = r * cols + c
                    if idx < len(self.images):
                        max_width = max(max_width, self.images[idx].width)
                col_widths.append(max_width)
            
            # 计算画布总尺寸
            total_width = sum(col_widths) + (cols - 1) * h_spacing + 2 * margin
            total_height = sum(row_heights) + (rows - 1) * v_spacing + 2 * margin
            
            # 限制画布尺寸，防止内存不足
            max_canvas_size = 16384  # 16K
            if total_width > max_canvas_size or total_height > max_canvas_size:
                print(f"画布尺寸过大: {total_width}x{total_height}，已限制")
                scale = max_canvas_size / max(total_width, total_height)
                total_width = int(total_width * scale)
                total_height = int(total_height * scale)
            
            # 创建画布
            if bg_color == 'transparent':
                combined = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
            else:
                combined = Image.new('RGB', (total_width, total_height), bg_color)
            
            # 粘贴图片
            y_offset = margin
            for r in range(rows):
                x_offset = margin
                for c in range(cols):
                    idx = r * cols + c
                    if idx < len(self.images):
                        img = self.images[idx]
                        
                        # 计算对齐位置
                        if align == 'center':
                            x = x_offset + (col_widths[c] - img.width) // 2
                            y = y_offset + (row_heights[r] - img.height) // 2
                        elif align == 'left':
                            x = x_offset
                            y = y_offset + (row_heights[r] - img.height) // 2
                        else:  # right
                            x = x_offset + col_widths[c] - img.width
                            y = y_offset + (row_heights[r] - img.height) // 2
                        
                        # 处理透明图片
                        if img.mode == 'RGBA':
                            combined.paste(img, (x, y), img)
                        else:
                            combined.paste(img, (x, y))
                    
                    x_offset += col_widths[c] + h_spacing
                y_offset += row_heights[r] + v_spacing
            
            return combined
        except Exception as e:
            print(f"创建组合图片时发生错误: {str(e)}")
            return None
    
    def add_labels(self, combined: Image.Image, rows: int, cols: int,
                   label_format: str = '(a)', label_position: str = 'top_left',
                   font_name: str = 'Arial', font_size: int = 12,
                   label_color: str = 'black', label_margin: int = 10,
                   h_spacing: int = 20, v_spacing: int = 20,
                   margin: int = 10, align: str = 'center') -> Image.Image:
        """
        添加子图标签
        :param combined: 组合图片
        :param rows: 行数
        :param cols: 列数
        :param label_format: 标签格式 ('(a)', 'a/', 'Fig1a')
        :param label_position: 标签位置 ('top_left', 'top_right', 'bottom_left', 'bottom_right')
        :param font_name: 字体名称
        :param font_size: 字体大小
        :param label_color: 标签颜色
        :param label_margin: 标签边距
        :param h_spacing: 水平间距
        :param v_spacing: 垂直间距
        :param margin: 画布边距
        :param align: 对齐方式
        :return: 添加标签后的图片
        """
        try:
            # 转换为RGBA以支持透明度
            if combined.mode != 'RGBA':
                combined = combined.convert('RGBA')
            
            draw = ImageDraw.Draw(combined)
            
            # 尝试加载字体
            try:
                font = ImageFont.truetype(font_name, font_size)
            except:
                try:
                    # 尝试使用系统字体
                    if font_name == '宋体':
                        font = ImageFont.truetype('simsun.ttc', font_size)
                    elif font_name == '黑体':
                        font = ImageFont.truetype('simhei.ttf', font_size)
                    elif font_name == 'Times New Roman':
                        font = ImageFont.truetype('times.ttf', font_size)
                    else:
                        # 尝试常见的Arial字体路径
                        font_paths = ['arial.ttf', 'ARIAL.TTF', 'C:/Windows/Fonts/arial.ttf', '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf']
                        for path in font_paths:
                            try:
                                font = ImageFont.truetype(path, font_size)
                                break
                            except:
                                continue
                        else:
                            # 所有尝试都失败，使用默认字体
                            font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
            
            # 计算每行每列的最大宽度和高度
            row_heights = []
            col_widths = []
            
            for r in range(rows):
                max_height = 0
                for c in range(cols):
                    idx = r * cols + c
                    if idx < len(self.images):
                        max_height = max(max_height, self.images[idx].height)
                row_heights.append(max_height)
            
            for c in range(cols):
                max_width = 0
                for r in range(rows):
                    idx = r * cols + c
                    if idx < len(self.images):
                        max_width = max(max_width, self.images[idx].width)
                col_widths.append(max_width)
            
            # 添加标签
            y_offset = margin
            for r in range(rows):
                x_offset = margin
                for c in range(cols):
                    idx = r * cols + c
                    if idx < len(self.images):
                        # 生成标签文本
                        label_idx = idx
                        if label_format == '(a)':
                            label_text = f"({chr(97 + label_idx)})"
                        elif label_format == 'a/':
                            label_text = f"{chr(97 + label_idx)}/"
                        else:  # Fig1a
                            label_text = f"Fig1{chr(97 + label_idx)}"
                        
                        # 计算标签位置
                        img = self.images[idx]
                        
                        if align == 'center':
                            img_x = x_offset + (col_widths[c] - img.width) // 2
                            img_y = y_offset + (row_heights[r] - img.height) // 2
                        elif align == 'left':
                            img_x = x_offset
                            img_y = y_offset + (row_heights[r] - img.height) // 2
                        else:  # right
                            img_x = x_offset + col_widths[c] - img.width
                            img_y = y_offset + (row_heights[r] - img.height) // 2
                        
                        # 标签位置
                        if label_position == 'top_left':
                            text_x = img_x + label_margin
                            text_y = img_y + label_margin
                        elif label_position == 'top_right':
                            # 获取文本宽度
                            bbox = draw.textbbox((0, 0), label_text, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_x = img_x + img.width - text_width - label_margin
                            text_y = img_y + label_margin
                        elif label_position == 'bottom_left':
                            # 获取文本高度
                            bbox = draw.textbbox((0, 0), label_text, font=font)
                            text_height = bbox[3] - bbox[1]
                            text_x = img_x + label_margin
                            text_y = img_y + img.height - text_height - label_margin
                        else:  # bottom_right
                            # 获取文本宽度和高度
                            bbox = draw.textbbox((0, 0), label_text, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            text_x = img_x + img.width - text_width - label_margin
                            text_y = img_y + img.height - text_height - label_margin
                        
                        # 绘制标签
                        draw.text((text_x, text_y), label_text, fill=label_color, font=font)
                    
                    x_offset += col_widths[c] + h_spacing
                y_offset += row_heights[r] + v_spacing
            
            return combined
        except Exception as e:
            print(f"添加标签时发生错误: {str(e)}")
            return combined
    
    def save_image(self, img: Image.Image, output_path: str, 
                   dpi: int = 300, format: str = 'PNG') -> Tuple[bool, str]:
        """
        保存图片
        :param img: 图片对象
        :param output_path: 输出路径
        :param dpi: 分辨率
        :param format: 输出格式
        :return: (是否成功, 消息)
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            if format.upper() in ['PDF', 'EPS']:
                # 矢量格式使用matplotlib保存
                fig = plt.figure(figsize=(img.width / dpi, img.height / dpi), dpi=dpi)
                ax = fig.add_axes([0, 0, 1, 1], frameon=False)
                ax.axis('off')
                ax.imshow(np.array(img))
                
                if format.upper() == 'PDF':
                    fig.savefig(output_path, format='pdf', dpi=dpi, bbox_inches='tight', pad_inches=0)
                else:  # EPS
                    fig.savefig(output_path, format='eps', dpi=dpi, bbox_inches='tight', pad_inches=0)
                
                plt.close(fig)
            else:
                # 位图格式使用PIL保存
                if format.upper() == 'TIFF':
                    img.save(output_path, format='TIFF', dpi=(dpi, dpi), compression='tiff_lzw')
                else:  # PNG
                    if img.mode == 'RGBA':
                        img.save(output_path, format='PNG', dpi=(dpi, dpi))
                    else:
                        img.save(output_path, format='PNG', dpi=(dpi, dpi))
            
            return True, f"图片已保存到: {output_path}"
        except Exception as e:
            return False, f"保存失败: {str(e)}"
    
    def reorder_images(self, new_order: List[int]) -> None:
        """
        重新排序图片
        :param new_order: 新的顺序索引列表
        """
        if len(new_order) == len(self.images):
            self.images = [self.images[i] for i in new_order]
            self.image_paths = [self.image_paths[i] for i in new_order]
    
    def get_image_count(self) -> int:
        """获取当前图片数量"""
        return len(self.images)
    
    def clear_images(self) -> None:
        """清空所有图片"""
        self.clear()