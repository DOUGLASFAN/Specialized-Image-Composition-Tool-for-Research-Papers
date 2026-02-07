"""
科研论文图片组合工具 - 测试脚本
用于测试各个模块的基本功能
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_process import ImageProcessor
from config import ConfigManager


def create_test_images(output_dir="test_images", num_images=4):
    """
    创建测试用的示例图片
    
    Args:
        output_dir: 输出目录
        num_images: 创建图片数量
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    colors = [
        (255, 100, 100),  # 红色
        (100, 255, 100),  # 绿色
        (100, 100, 255),  # 蓝色
        (255, 255, 100),  # 黄色
        (255, 100, 255),  # 紫色
        (100, 255, 255),  # 青色
    ]
    
    for i in range(num_images):
        # 创建图片
        img = Image.new('RGB', (400, 300), colors[i % len(colors)])
        draw = ImageDraw.Draw(img)
        
        # 添加文字
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = f"Test {i+1}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((400 - text_width) // 2, (300 - text_height) // 2)
        draw.text(position, text, fill=(0, 0, 0), font=font)
        
        # 保存图片
        img_path = os.path.join(output_dir, f"test_image_{i+1}.png")
        img.save(img_path)
        print(f"创建测试图片: {img_path}")


def test_image_processor():
    """测试图像处理模块"""
    print("\n" + "="*50)
    print("测试图像处理模块")
    print("="*50)
    
    # 创建测试图片
    create_test_images()
    
    # 加载图片
    processor = ImageProcessor()
    test_dir = "test_images"
    
    if not os.path.exists(test_dir):
        print("错误: 测试图片目录不存在")
        return False
    
    # 获取测试图片
    image_files = sorted([f for f in os.listdir(test_dir) if f.endswith('.png')])
    images = []
    for img_file in image_files[:4]:  # 使用前4张图片
        img_path = os.path.join(test_dir, img_file)
        img = Image.open(img_path)
        images.append(img)
        print(f"加载图片: {img_file}")
    
    # 测试缩放
    print("\n测试缩放功能...")
    scaled_images = []
    for img in images:
        scaled = processor.scale_image(img, "longest_edge", 300, "free")
        scaled_images.append(scaled)
        print(f"  缩放后尺寸: {scaled.size}")
    
    # 测试组合
    print("\n测试图片组合功能...")
    config = {
        "rows": 2,
        "cols": 2,
        "horizontal_spacing": 20,
        "vertical_spacing": 20,
        "background": "white",
        "canvas_margin": 10
    }
    
    combined = processor.combine_images(scaled_images, config)
    print(f"组合图尺寸: {combined.size}")
    
    # 测试添加标签
    print("\n测试添加标签功能...")
    label_config = {
        "format": "(a)(b)(c)",
        "position": "top_left",
        "font": "Arial",
        "size": 20,
        "color": "black",
        "margin": 10
    }
    
    labeled = processor.add_labels(combined, scaled_images, config, label_config)
    
    # 保存结果
    output_path = "test_output.png"
    labeled.save(output_path)
    print(f"保存结果: {output_path}")
    
    return True


def test_config_manager():
    """测试配置管理模块"""
    print("\n" + "="*50)
    print("测试配置管理模块")
    print("="*50)
    
    config_manager = ConfigManager()
    
    # 获取默认配置
    print("\n获取默认配置...")
    default_config = config_manager.get_default_config()
    print(f"默认配置: {default_config}")
    
    # 更新配置
    print("\n更新配置...")
    new_config = {
        "layout": {"rows": 3, "cols": 3},
        "spacing": {"horizontal": 30, "vertical": 30}
    }
    config_manager.update_config(new_config)
    print(f"更新后配置: {config_manager.config}")
    
    # 保存配置
    print("\n保存配置...")
    config_file = "test_config.json"
    config_manager.save_config(config_file)
    print(f"配置已保存到: {config_file}")
    
    # 加载配置
    print("\n加载配置...")
    loaded_config = config_manager.load_config(config_file)
    print(f"加载的配置: {loaded_config}")
    
    # 验证配置
    print("\n验证配置...")
    is_valid = config_manager.validate_config(loaded_config)
    print(f"配置验证结果: {'有效' if is_valid else '无效'}")
    
    # 重置配置
    print("\n重置配置...")
    config_manager.reset_config()
    print(f"重置后配置: {config_manager.config}")
    
    return True


def test_spacing_conversion():
    """测试间距单位转换"""
    print("\n" + "="*50)
    print("测试间距单位转换")
    print("="*50)
    
    config_manager = ConfigManager()
    
    # 像素转厘米
    print("\n像素转厘米:")
    pixels = 100
    cm = config_manager.pixel_to_cm(pixels)
    print(f"  {pixels} 像素 = {cm:.2f} 厘米")
    
    # 厘米转像素
    print("\n厘米转像素:")
    cm_value = 2.54
    pixels = config_manager.cm_to_pixel(cm_value)
    print(f"  {cm_value} 厘米 = {pixels:.2f} 像素")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*50)
    print("科研论文图片组合工具 - 测试套件")
    print("="*50)
    
    tests = [
        ("图像处理模块", test_image_processor),
        ("配置管理模块", test_config_manager),
        ("间距单位转换", test_spacing_conversion),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n✓ {test_name} 测试通过")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n✗ {test_name} 测试失败: {str(e)}")
    
    # 输出测试结果摘要
    print("\n" + "="*50)
    print("测试结果摘要")
    print("="*50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n所有测试通过！✓")
    else:
        print(f"\n有 {total - passed} 个测试失败，请检查错误信息。")


if __name__ == "__main__":
    run_all_tests()