"""
科研论文专用图片组合工具 - GUI主界面模块
功能：图形化界面，包含图片导入、布局设置、精细化配置、预览、输出等功能
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSpinBox, QComboBox, QGroupBox,
                             QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                             QSlider, QCheckBox, QColorDialog, QSplitter, QFrame,
                             QDoubleSpinBox, QScrollArea, QStatusBar, QProgressBar,
                             QGridLayout, QTabWidget, QRadioButton, QButtonGroup,
                             QProgressDialog)
from PyQt5.QtCore import Qt, QMimeData, QSize, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QPixmap, QImage, QIcon, QDrag, QPainter, QColor, QPalette
from PIL import Image
import io

from image_process import ImageProcessor
from config import ConfigManager
from batch_process import BatchProcessor


class DraggableListWidget(QListWidget):
    """支持拖拽排序的列表控件"""
    
    item_reordered = pyqtSignal(list)  # 发送重新排序后的索引列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
    
    def dropEvent(self, event):
        """处理拖放事件"""
        super().dropEvent(event)
        # 获取新的顺序
        new_order = []
        for i in range(self.count()):
            item = self.item(i)
            if item:
                new_order.append(item.data(Qt.UserRole))
        self.item_reordered.emit(new_order)


class ImageListWidget(QListWidget):
    """图片列表控件，支持拖拽导入"""
    
    files_dropped = pyqtSignal(list)  # 发送拖入的文件路径列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)
        self.setIconSize(QSize(100, 100))
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(10)
    
    def dragEnterEvent(self, event):
        """处理拖入事件"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """处理拖动事件"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """处理放下事件"""
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.eps'))]
            if image_files:
                self.files_dropped.emit(image_files)
        event.accept()


class PhotoDealToolGUI(QMainWindow):
    """科研论文图片组合工具主界面"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化处理器
        self.image_processor = ImageProcessor()
        self.config_manager = ConfigManager()
        self.batch_processor = None
        
        # 当前预览图片
        self.current_preview = None
        
        # 初始化界面
        self.init_ui()
        
        # 连接信号
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('科研论文专用图片组合工具 v1.0')
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板（图片导入+布局设置）
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 中间面板（预览区）
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # 右侧面板（精细化配置+输出）
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 600, 350])
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')
    
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 图片导入区
        import_group = QGroupBox('图片导入')
        import_layout = QVBoxLayout()
        
        self.image_list = ImageListWidget()
        import_layout.addWidget(self.image_list)
        
        btn_layout = QHBoxLayout()
        self.btn_import = QPushButton('导入图片')
        self.btn_import.clicked.connect(self.import_images)
        self.btn_clear = QPushButton('清空列表')
        self.btn_clear.clicked.connect(self.clear_images)
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(self.btn_clear)
        import_layout.addLayout(btn_layout)
        
        # 批量处理按钮
        self.btn_batch = QPushButton('批量处理')
        self.btn_batch.clicked.connect(self.batch_process)
        self.btn_batch.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold;')
        import_layout.addWidget(self.btn_batch)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # 布局设置区
        layout_group = QGroupBox('布局设置')
        layout_layout = QGridLayout()
        
        layout_layout.addWidget(QLabel('行数:'), 0, 0)
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 10)
        self.spin_rows.setValue(2)
        layout_layout.addWidget(self.spin_rows, 0, 1)
        
        layout_layout.addWidget(QLabel('列数:'), 1, 0)
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 10)
        self.spin_cols.setValue(2)
        layout_layout.addWidget(self.spin_cols, 1, 1)
        
        layout_layout.addWidget(QLabel('缩放模式:'), 2, 0)
        self.combo_resize = QComboBox()
        self.combo_resize.addItems(['使用原始分辨率', '最长边', '最短边', '自定义尺寸', '居中裁剪'])
        layout_layout.addWidget(self.combo_resize, 2, 1)
        
        layout_layout.addWidget(QLabel('图片尺寸:'), 3, 0)
        self.spin_size = QSpinBox()
        self.spin_size.setRange(100, 20000)
        self.spin_size.setValue(800)
        layout_layout.addWidget(self.spin_size, 3, 1)
        
        layout_layout.addWidget(QLabel('宽高比:'), 4, 0)
        self.combo_aspect = QComboBox()
        self.combo_aspect.addItems(['自由比例', '1:1', '4:3', '16:9'])
        layout_layout.addWidget(self.combo_aspect, 4, 1)
        
        layout_group.setLayout(layout_layout)
        layout.addWidget(layout_group)
        
        # 对齐方式
        align_group = QGroupBox('对齐方式')
        align_layout = QHBoxLayout()
        self.radio_center = QRadioButton('居中')
        self.radio_left = QRadioButton('左对齐')
        self.radio_right = QRadioButton('右对齐')
        self.radio_center.setChecked(True)
        align_layout.addWidget(self.radio_center)
        align_layout.addWidget(self.radio_left)
        align_layout.addWidget(self.radio_right)
        align_group.setLayout(align_layout)
        layout.addWidget(align_group)
        
        layout.addStretch()
        
        return panel
    
    def create_center_panel(self) -> QWidget:
        """创建中间预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 预览区
        preview_group = QGroupBox('实时预览')
        preview_layout = QVBoxLayout()
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setBackgroundRole(QPalette.Base)
        
        # 预览标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setStyleSheet('background-color: #f0f0f0; border: 1px solid #ccc;')
        scroll.setWidget(self.preview_label)
        
        preview_layout.addWidget(scroll)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton('刷新预览')
        self.btn_preview.clicked.connect(self.update_preview)
        self.btn_output = QPushButton('输出图片')
        self.btn_output.clicked.connect(self.output_image)
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_output)
        layout.addLayout(btn_layout)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """创建右侧配置面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 间距设置
        spacing_group = QGroupBox('间距设置')
        spacing_layout = QGridLayout()
        
        spacing_layout.addWidget(QLabel('水平间距:'), 0, 0)
        self.spin_h_spacing = QSpinBox()
        self.spin_h_spacing.setRange(0, 200)
        self.spin_h_spacing.setValue(20)
        spacing_layout.addWidget(self.spin_h_spacing, 0, 1)
        
        spacing_layout.addWidget(QLabel('垂直间距:'), 1, 0)
        self.spin_v_spacing = QSpinBox()
        self.spin_v_spacing.setRange(0, 200)
        self.spin_v_spacing.setValue(20)
        spacing_layout.addWidget(self.spin_v_spacing, 1, 1)
        
        spacing_layout.addWidget(QLabel('单位:'), 2, 0)
        self.combo_spacing_unit = QComboBox()
        self.combo_spacing_unit.addItems(['像素(px)', '厘米(cm)'])
        spacing_layout.addWidget(self.combo_spacing_unit, 2, 1)
        
        spacing_group.setLayout(spacing_layout)
        layout.addWidget(spacing_group)
        
        # 标签设置
        label_group = QGroupBox('子图标签')
        label_layout = QGridLayout()
        
        label_layout.addWidget(QLabel('标签格式:'), 0, 0)
        self.combo_label_format = QComboBox()
        self.combo_label_format.addItems(['(a)(b)(c)', 'a/b/c/', 'Fig1a/Fig1b'])
        label_layout.addWidget(self.combo_label_format, 0, 1)
        
        label_layout.addWidget(QLabel('标签位置:'), 1, 0)
        self.combo_label_pos = QComboBox()
        self.combo_label_pos.addItems(['左上角', '右上角', '左下角', '右下角'])
        label_layout.addWidget(self.combo_label_pos, 1, 1)
        
        label_layout.addWidget(QLabel('字体:'), 2, 0)
        self.combo_font = QComboBox()
        self.combo_font.addItems(['Arial', '宋体', '黑体', 'Times New Roman'])
        label_layout.addWidget(self.combo_font, 2, 1)
        
        label_layout.addWidget(QLabel('字号:'), 3, 0)
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(1, 1000)
        self.spin_font_size.setValue(12)
        label_layout.addWidget(self.spin_font_size, 3, 1)
        
        label_layout.addWidget(QLabel('颜色:'), 4, 0)
        self.combo_label_color = QComboBox()
        self.combo_label_color.addItems(['黑色', '白色'])
        label_layout.addWidget(self.combo_label_color, 4, 1)
        
        label_layout.addWidget(QLabel('标签边距:'), 5, 0)
        self.spin_label_margin = QSpinBox()
        self.spin_label_margin.setRange(0, 1000)
        self.spin_label_margin.setValue(10)
        label_layout.addWidget(self.spin_label_margin, 5, 1)
        
        label_group.setLayout(label_layout)
        layout.addWidget(label_group)
        
        # 画布设置
        canvas_group = QGroupBox('画布设置')
        canvas_layout = QGridLayout()
        
        canvas_layout.addWidget(QLabel('背景色:'), 0, 0)
        self.combo_bg_color = QComboBox()
        self.combo_bg_color.addItems(['白色', '透明', '黑色'])
        canvas_layout.addWidget(self.combo_bg_color, 0, 1)
        
        canvas_layout.addWidget(QLabel('画布边距:'), 1, 0)
        self.spin_canvas_margin = QSpinBox()
        self.spin_canvas_margin.setRange(0, 100)
        self.spin_canvas_margin.setValue(10)
        canvas_layout.addWidget(self.spin_canvas_margin, 1, 1)
        
        canvas_group.setLayout(canvas_layout)
        layout.addWidget(canvas_group)
        
        # 输出设置
        output_group = QGroupBox('输出设置')
        output_layout = QGridLayout()
        
        output_layout.addWidget(QLabel('输出格式:'), 0, 0)
        self.combo_output_format = QComboBox()
        self.combo_output_format.addItems(['PNG', 'TIFF', 'PDF', 'EPS'])
        output_layout.addWidget(self.combo_output_format, 0, 1)
        
        output_layout.addWidget(QLabel('分辨率(DPI):'), 1, 0)
        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(72, 1200)
        self.spin_dpi.setValue(300)
        self.spin_dpi.setSingleStep(50)
        output_layout.addWidget(self.spin_dpi, 1, 1)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 配置管理
        config_group = QGroupBox('配置管理')
        config_layout = QHBoxLayout()
        self.btn_save_config = QPushButton('保存配置')
        self.btn_save_config.clicked.connect(self.save_config)
        self.btn_load_config = QPushButton('加载配置')
        self.btn_load_config.clicked.connect(self.load_config)
        config_layout.addWidget(self.btn_save_config)
        config_layout.addWidget(self.btn_load_config)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        return panel
    
    def connect_signals(self):
        """连接信号和槽"""
        # 图片列表信号
        self.image_list.files_dropped.connect(self.handle_dropped_files)
        
        # 预览更新定时器（用于节流）
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._delayed_update_preview)
        self.preview_update_delay = 200  # 延迟200ms
        
        # 实时预览信号
        self.spin_rows.valueChanged.connect(self._schedule_preview_update)
        self.spin_cols.valueChanged.connect(self._schedule_preview_update)
        self.combo_resize.currentIndexChanged.connect(self._schedule_preview_update)
        self.spin_size.valueChanged.connect(self._schedule_preview_update)
        self.combo_aspect.currentIndexChanged.connect(self._schedule_preview_update)
        self.spin_h_spacing.valueChanged.connect(self._schedule_preview_update)
        self.spin_v_spacing.valueChanged.connect(self._schedule_preview_update)
        self.combo_spacing_unit.currentIndexChanged.connect(self._schedule_preview_update)
        self.combo_label_format.currentIndexChanged.connect(self._schedule_preview_update)
        self.combo_label_pos.currentIndexChanged.connect(self._schedule_preview_update)
        self.combo_font.currentIndexChanged.connect(self._schedule_preview_update)
        self.spin_font_size.valueChanged.connect(self._schedule_preview_update)
        self.combo_label_color.currentIndexChanged.connect(self._schedule_preview_update)
        self.spin_label_margin.valueChanged.connect(self._schedule_preview_update)
        self.combo_bg_color.currentIndexChanged.connect(self._schedule_preview_update)
        self.spin_canvas_margin.valueChanged.connect(self._schedule_preview_update)
        self.radio_center.toggled.connect(self._schedule_preview_update)
        self.radio_left.toggled.connect(self._schedule_preview_update)
        self.radio_right.toggled.connect(self._schedule_preview_update)
    
    def _schedule_preview_update(self):
        """安排预览更新（节流）"""
        self.preview_timer.start(self.preview_update_delay)
    
    def _delayed_update_preview(self):
        """延迟执行预览更新"""
        self.update_preview()
    
    def import_images(self):
        """导入图片"""
        files, _ = QFileDialog.getOpenFileNames(
            self, '选择图片', '',
            '图片文件 (*.png *.jpg *.jpeg *.tiff *.tif *.eps);;所有文件 (*.*)'
        )
        
        if files:
            self.load_images(files)
    
    def handle_dropped_files(self, files):
        """处理拖入的文件"""
        self.load_images(files)
    
    def load_images(self, files):
        """加载图片文件"""
        success, message = self.image_processor.load_images(files)
        
        if success:
            self.update_image_list()
            self.status_bar.showMessage(message)
            self.update_preview()
        else:
            QMessageBox.warning(self, '加载失败', message)
    
    def update_image_list(self):
        """更新图片列表显示"""
        self.image_list.clear()
        
        for i, (img, path) in enumerate(zip(self.image_processor.images, 
                                            self.image_processor.image_paths)):
            # 创建缩略图
            thumb = img.copy()
            thumb.thumbnail((100, 100), Image.LANCZOS)
            
            # 转换为QPixmap
            if thumb.mode == 'RGBA':
                thumb = thumb.convert('RGB')
            qimg = QImage(thumb.tobytes(), thumb.width, thumb.height, 
                         QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            # 创建列表项
            item = QListWidgetItem(QIcon(pixmap), os.path.basename(path))
            item.setData(Qt.UserRole, i)
            self.image_list.addItem(item)
        
        self.status_bar.showMessage(f'已加载 {len(self.image_processor.images)} 张图片')
    
    def clear_images(self):
        """清空图片列表"""
        self.image_processor.clear_images()
        self.image_list.clear()
        self.preview_label.clear()
        self.current_preview = None
        self.status_bar.showMessage('已清空所有图片')
    
    def update_preview(self):
        """更新预览"""
        if not self.image_processor.images:
            self.preview_label.setText('请先导入图片')
            return
        
        try:
            # 获取配置参数
            rows = self.spin_rows.value()
            cols = self.spin_cols.value()
            
            # 检查图片数量
            if len(self.image_processor.images) > rows * cols:
                self.status_bar.showMessage(f'警告: 图片数量({len(self.image_processor.images)})超过布局容量({rows*cols})')
            
            # 缩放图片
            resize_mode_map = {
                '使用原始分辨率': 'original',
                '最长边': 'longest_edge',
                '最短边': 'shortest_edge',
                '自定义尺寸': 'custom',
                '居中裁剪': 'crop'
            }
            resize_mode = resize_mode_map[self.combo_resize.currentText()]
            size = self.spin_size.value()
            
            aspect_map = {
                '自由比例': None,
                '1:1': (1, 1),
                '4:3': (4, 3),
                '16:9': (16, 9)
            }
            aspect_ratio = aspect_map[self.combo_aspect.currentText()]
            
            # 缩放所有图片
            resized_images = []
            for img in self.image_processor.images:
                resized = self.image_processor.resize_image(img, resize_mode, size, aspect_ratio, fast=True)
                resized_images.append(resized)
            
            # 临时替换图片
            original_images = self.image_processor.images
            self.image_processor.images = resized_images
            
            # 获取间距
            h_spacing = self.spin_h_spacing.value()
            v_spacing = self.spin_v_spacing.value()
            if self.combo_spacing_unit.currentText() == '厘米(cm)':
                h_spacing = self.config_manager.get_spacing_in_pixels(h_spacing, 'cm')
                v_spacing = self.config_manager.get_spacing_in_pixels(v_spacing, 'cm')
            
            # 获取背景色
            bg_color_map = {
                '白色': 'white',
                '透明': 'transparent',
                '黑色': 'black'
            }
            bg_color = bg_color_map[self.combo_bg_color.currentText()]
            
            # 获取对齐方式
            align_map = {
                '居中': 'center',
                '左对齐': 'left',
                '右对齐': 'right'
            }
            align = align_map['居中'] if self.radio_center.isChecked() else \
                   align_map['左对齐'] if self.radio_left.isChecked() else \
                   align_map['右对齐']
            
            # 创建组合图片
            combined = self.image_processor.create_combined_image(
                rows, cols, h_spacing, v_spacing, bg_color,
                self.spin_canvas_margin.value(), align
            )
            
            # 添加标签
            label_format_map = {
                '(a)(b)(c)': '(a)',
                'a/b/c/': 'a/',
                'Fig1a/Fig1b': 'Fig1a'
            }
            label_format = label_format_map[self.combo_label_format.currentText()]
            
            label_pos_map = {
                '左上角': 'top_left',
                '右上角': 'top_right',
                '左下角': 'bottom_left',
                '右下角': 'bottom_right'
            }
            label_position = label_pos_map[self.combo_label_pos.currentText()]
            
            label_color_map = {
                '黑色': 'black',
                '白色': 'white'
            }
            label_color = label_color_map[self.combo_label_color.currentText()]
            
            combined = self.image_processor.add_labels(
                combined, rows, cols, label_format, label_position,
                self.combo_font.currentText(), self.spin_font_size.value(),
                label_color, self.spin_label_margin.value(),
                h_spacing, v_spacing, self.spin_canvas_margin.value(), align
            )
            
            # 恢复原始图片
            self.image_processor.images = original_images
            
            # 显示预览
            self.current_preview = combined
            
            # 缩放预览图片以适应显示区域
            preview_size = self.preview_label.size()
            if combined.width > preview_size.width() or combined.height > preview_size.height():
                ratio = min(preview_size.width() / combined.width, 
                           preview_size.height() / combined.height)
                new_width = int(combined.width * ratio)
                new_height = int(combined.height * ratio)
                combined = combined.resize((new_width, new_height), Image.LANCZOS)
            
            # 转换为QPixmap
            if combined.mode == 'RGBA':
                combined = combined.convert('RGB')
            qimg = QImage(combined.tobytes(), combined.width, combined.height, 
                         QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            self.preview_label.setPixmap(pixmap)
            self.status_bar.showMessage(f'预览已更新 - {rows}行×{cols}列')
            
        except Exception as e:
            QMessageBox.critical(self, '预览错误', f'生成预览失败: {str(e)}')
    
    def output_image(self):
        """输出图片"""
        if not self.current_preview:
            QMessageBox.warning(self, '警告', '请先生成预览')
            return
        
        # 获取输出格式
        output_format = self.combo_output_format.currentText()
        dpi = self.spin_dpi.value()
        
        # 选择保存路径
        default_name = f'combined_image.{output_format.lower()}'
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存图片', default_name,
            f'{output_format}文件 (*.{output_format.lower()});;所有文件 (*.*)'
        )
        
        if file_path:
            # 使用原始高分辨率图片重新生成组合图
            try:
                # 获取配置参数
                rows = self.spin_rows.value()
                cols = self.spin_cols.value()
                
                # 缩放图片
                resize_mode_map = {
                    '使用原始分辨率': 'original',
                    '最长边': 'longest_edge',
                    '最短边': 'shortest_edge',
                    '自定义尺寸': 'custom',
                    '居中裁剪': 'crop'
                }
                resize_mode = resize_mode_map[self.combo_resize.currentText()]
                size = self.spin_size.value()
                
                aspect_map = {
                    '自由比例': None,
                    '1:1': (1, 1),
                    '4:3': (4, 3),
                    '16:9': (16, 9)
                }
                aspect_ratio = aspect_map[self.combo_aspect.currentText()]
                
                # 从原始文件路径重新加载图片（避免二次缩放）
                resized_images = []
                for img_path in self.image_processor.image_paths:
                    # 重新加载原始图片
                    original_img = Image.open(img_path)
                    
                    # 处理EXIF方向
                    try:
                        from PIL import ImageOps
                        original_img = ImageOps.exif_transpose(original_img)
                    except:
                        pass
                    
                    # 对原始图片进行缩放
                    resized = self.image_processor.resize_image(original_img, resize_mode, size, aspect_ratio)
                    resized_images.append(resized)
                
                # 临时替换图片
                original_images = self.image_processor.images
                self.image_processor.images = resized_images
                
                # 获取间距
                h_spacing = self.spin_h_spacing.value()
                v_spacing = self.spin_v_spacing.value()
                if self.combo_spacing_unit.currentText() == '厘米(cm)':
                    h_spacing = self.config_manager.get_spacing_in_pixels(h_spacing, 'cm')
                    v_spacing = self.config_manager.get_spacing_in_pixels(v_spacing, 'cm')
                
                # 获取背景色
                bg_color_map = {
                    '白色': 'white',
                    '透明': 'transparent',
                    '黑色': 'black'
                }
                bg_color = bg_color_map[self.combo_bg_color.currentText()]
                
                # 获取对齐方式
                align_map = {
                    '居中': 'center',
                    '左对齐': 'left',
                    '右对齐': 'right'
                }
                align = align_map['居中'] if self.radio_center.isChecked() else \
                       align_map['左对齐'] if self.radio_left.isChecked() else \
                       align_map['右对齐']
                
                # 创建组合图片
                combined = self.image_processor.create_combined_image(
                    rows, cols, h_spacing, v_spacing, bg_color,
                    self.spin_canvas_margin.value(), align
                )
                
                # 添加标签
                label_format_map = {
                    '(a)(b)(c)': '(a)',
                    'a/b/c/': 'a/',
                    'Fig1a/Fig1b': 'Fig1a'
                }
                label_format = label_format_map[self.combo_label_format.currentText()]
                
                label_pos_map = {
                    '左上角': 'top_left',
                    '右上角': 'top_right',
                    '左下角': 'bottom_left',
                    '右下角': 'bottom_right'
                }
                label_position = label_pos_map[self.combo_label_pos.currentText()]
                
                label_color_map = {
                    '黑色': 'black',
                    '白色': 'white'
                }
                label_color = label_color_map[self.combo_label_color.currentText()]
                
                combined = self.image_processor.add_labels(
                    combined, rows, cols, label_format, label_position,
                    self.combo_font.currentText(), self.spin_font_size.value(),
                    label_color, self.spin_label_margin.value(),
                    h_spacing, v_spacing, self.spin_canvas_margin.value(), align
                )
                
                # 恢复原始图片
                self.image_processor.images = original_images
                
                # 保存图片
                success, message = self.image_processor.save_image(
                    combined, file_path, dpi, output_format
                )
                
                if success:
                    QMessageBox.information(self, '成功', message)
                    self.status_bar.showMessage(message)
                else:
                    QMessageBox.critical(self, '失败', message)
                    
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存图片失败: {str(e)}')
    
    def save_config(self):
        """保存配置"""
        # 更新配置
        self.config_manager.update_config(
            rows=self.spin_rows.value(),
            cols=self.spin_cols.value(),
            resize_mode=['longest_edge', 'shortest_edge', 'custom', 'crop'][self.combo_resize.currentIndex()],
            image_size=self.spin_size.value(),
            aspect_ratio=[None, (1, 1), (4, 3), (16, 9)][self.combo_aspect.currentIndex()],
            h_spacing=self.spin_h_spacing.value(),
            v_spacing=self.spin_v_spacing.value(),
            spacing_unit='px' if self.combo_spacing_unit.currentIndex() == 0 else 'cm',
            label_format=['(a)', 'a/', 'Fig1a'][self.combo_label_format.currentIndex()],
            label_position=['top_left', 'top_right'][self.combo_label_pos.currentIndex()],
            label_font=self.combo_font.currentText(),
            label_font_size=self.spin_font_size.value(),
            label_color=['black', 'white'][self.combo_label_color.currentIndex()],
            label_margin=self.spin_label_margin.value(),
            bg_color=['white', 'transparent', 'black'][self.combo_bg_color.currentIndex()],
            canvas_margin=self.spin_canvas_margin.value(),
            align='center' if self.radio_center.isChecked() else 'left' if self.radio_left.isChecked() else 'right',
            output_format=self.combo_output_format.currentText(),
            dpi=self.spin_dpi.value()
        )
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存配置', 'config.json',
            'JSON文件 (*.json);;所有文件 (*.*)'
        )
        
        if file_path:
            success, message = self.config_manager.save_config(file_path)
            if success:
                QMessageBox.information(self, '成功', message)
            else:
                QMessageBox.critical(self, '失败', message)
    
    def load_config(self):
        """加载配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '加载配置', '',
            'JSON文件 (*.json);;所有文件 (*.*)'
        )
        
        if file_path:
            success, message = self.config_manager.load_config(file_path)
            if success:
                self.apply_config()
                QMessageBox.information(self, '成功', message)
            else:
                QMessageBox.critical(self, '失败', message)
    
    def apply_config(self):
        """应用配置到界面"""
        config = self.config_manager.get_config()
        
        self.spin_rows.setValue(config['rows'])
        self.spin_cols.setValue(config['cols'])
        
        resize_mode_map = {
            'original': 0,
            'longest_edge': 1,
            'shortest_edge': 2,
            'custom': 3,
            'crop': 4
        }
        self.combo_resize.setCurrentIndex(resize_mode_map.get(config['resize_mode'], 0))
        
        self.spin_size.setValue(config['image_size'])
        
        aspect_map = {
            None: 0,
            (1, 1): 1,
            (4, 3): 2,
            (16, 9): 3
        }
        self.combo_aspect.setCurrentIndex(aspect_map.get(config['aspect_ratio'], 0))
        
        self.spin_h_spacing.setValue(config['h_spacing'])
        self.spin_v_spacing.setValue(config['v_spacing'])
        self.combo_spacing_unit.setCurrentIndex(0 if config['spacing_unit'] == 'px' else 1)
        
        label_format_map = {
            '(a)': 0,
            'a/': 1,
            'Fig1a': 2
        }
        self.combo_label_format.setCurrentIndex(label_format_map.get(config['label_format'], 0))
        
        label_pos_map = {
            'top_left': 0,
            'top_right': 1,
            'bottom_left': 2,
            'bottom_right': 3
        }
        self.combo_label_pos.setCurrentIndex(label_pos_map.get(config['label_position'], 0))
        
        font_index = self.combo_font.findText(config['label_font'])
        if font_index >= 0:
            self.combo_font.setCurrentIndex(font_index)
        
        self.spin_font_size.setValue(config['label_font_size'])
        self.combo_label_color.setCurrentIndex(0 if config['label_color'] == 'black' else 1)
        self.spin_label_margin.setValue(config['label_margin'])
        
        bg_color_map = {
            'white': 0,
            'transparent': 1,
            'black': 2
        }
        self.combo_bg_color.setCurrentIndex(bg_color_map.get(config['bg_color'], 0))
        
        self.spin_canvas_margin.setValue(config['canvas_margin'])
        
        if config['align'] == 'center':
            self.radio_center.setChecked(True)
        elif config['align'] == 'left':
            self.radio_left.setChecked(True)
        else:
            self.radio_right.setChecked(True)
        
        format_index = self.combo_output_format.findText(config['output_format'])
        if format_index >= 0:
            self.combo_output_format.setCurrentIndex(format_index)
        
        self.spin_dpi.setValue(config['dpi'])
        
        self.update_preview()
    
    def batch_process(self):
        """批量处理多个文件夹"""
        # 选择文件夹
        folders = QFileDialog.getExistingDirectoryUrl(
            self, '选择包含图片的文件夹',
            QUrl.fromLocalFile(os.path.expanduser('~')),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not folders.isEmpty():
            folder_path = folders.toLocalFile()
            
            # 创建批量处理器
            self.batch_processor = BatchProcessor(
                self.image_processor,
                self.config_manager
            )
            
            # 创建进度对话框
            progress_dialog = QProgressDialog('正在批量处理...', '取消', 0, 100, self)
            progress_dialog.setWindowTitle('批量处理')
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setMinimumDuration(100)
            
            # 获取当前配置
            self.config_manager.update_config(
                rows=self.spin_rows.value(),
                cols=self.spin_cols.value(),
                resize_mode=['original', 'longest_edge', 'shortest_edge', 'custom', 'crop'][self.combo_resize.currentIndex()],
                image_size=self.spin_size.value(),
                aspect_ratio=[None, (1, 1), (4, 3), (16, 9)][self.combo_aspect.currentIndex()],
                h_spacing=self.spin_h_spacing.value(),
                v_spacing=self.spin_v_spacing.value(),
                spacing_unit='px' if self.combo_spacing_unit.currentIndex() == 0 else 'cm',
                label_format=['(a)', 'a/', 'Fig1a'][self.combo_label_format.currentIndex()],
                label_position=['top_left', 'top_right'][self.combo_label_pos.currentIndex()],
                label_font=self.combo_font.currentText(),
                label_font_size=self.spin_font_size.value(),
                label_color=['black', 'white'][self.combo_label_color.currentIndex()],
                label_margin=self.spin_label_margin.value(),
                bg_color=['white', 'transparent', 'black'][self.combo_bg_color.currentIndex()],
                canvas_margin=self.spin_canvas_margin.value(),
                align='center' if self.radio_center.isChecked() else 'left' if self.radio_left.isChecked() else 'right',
                output_format=self.combo_output_format.currentText(),
                dpi=self.spin_dpi.value()
            )
            
            # 选择输出目录
            output_dir = QFileDialog.getExistingDirectory(
                self, '选择输出目录',
                os.path.expanduser('~')
            )
            
            if not output_dir:
                return
            
            # 启动批量处理线程
            import threading
            
            def process_thread():
                try:
                    success_count, fail_count, results = self.batch_processor.process_folder(
                        folder_path,
                        output_dir,
                        progress_callback=lambda current, total, message: self.update_progress(
                            progress_dialog, current, total, message
                        )
                    )
                    
                    # 在主线程中显示结果
                    QTimer.singleShot(0, lambda: self.show_batch_results(
                        success_count, fail_count, results
                    ))
                    
                except Exception as e:
                    QTimer.singleShot(0, lambda: QMessageBox.critical(
                        self, '批量处理错误', f'批量处理失败: {str(e)}'
                    ))
            
            # 启动线程
            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()
    
    def update_progress(self, progress_dialog, current, total, message):
        """更新进度对话框"""
        progress = int((current / total) * 100) if total > 0 else 0
        progress_dialog.setValue(progress)
        progress_dialog.setLabelText(message)
        
        # 检查是否取消
        if progress_dialog.wasCanceled():
            if self.batch_processor:
                self.batch_processor.stop()
    
    def show_batch_results(self, success_count, fail_count, results):
        """显示批量处理结果"""
        message = f'批量处理完成！\n\n'
        message += f'成功: {success_count} 个\n'
        message += f'失败: {fail_count} 个\n'
        
        if fail_count > 0 and results:
            message += '\n失败的文件夹:\n'
            for result in results:
                if not result['success']:
                    message += f"- {result['folder']}: {result['message']}\n"
        
        QMessageBox.information(self, '批量处理完成', message)
        self.status_bar.showMessage(f'批量处理完成 - 成功: {success_count}, 失败: {fail_count}')


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = PhotoDealToolGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()