# 科研论文图片组合工具 - 打包教程

本教程详细介绍如何将科研论文图片组合工具打包为可执行文件，方便在没有Python环境的电脑上使用。

## 目录

- [Windows打包教程](#windows打包教程)
- [macOS打包教程](#macos打包教程)
- [Linux打包教程](#linux打包教程)
- [常见问题](#常见问题)
- [高级配置](#高级配置)

## Windows打包教程

### 准备工作

1. 确保已安装Python 3.8或更高版本
2. 安装项目依赖：
```bash
pip install -r requirements.txt
```

### 安装PyInstaller

```bash
pip install pyinstaller
```

### 准备图标文件（可选）

1. 准备一个`.ico`格式的图标文件
2. 将图标文件命名为`icon.ico`，放在项目根目录
3. 可以使用在线工具将PNG转换为ICO：https://www.icoconverter.com/

### 方法一：使用批处理脚本打包

1. 创建`build_exe.bat`文件：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo   科研论文图片组合工具 - Windows打包
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
pip show pyqt5 >nul 2>&1
if errorlevel 1 (
    echo [警告] PyQt5未安装，正在安装...
    pip install -r requirements.txt
)

echo [2/5] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /f /q *.spec

echo [3/5] 开始打包...
pyinstaller --name="科研论文图片组合工具" ^
--icon=icon.ico ^
--onefile ^
--windowed ^
--clean ^
--noconfirm ^
--add-data "requirements.txt;." ^
main.py

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo [4/5] 复制配置文件...
if exist dist\*.exe (
    copy /y requirements.txt dist\ >nul
    echo [成功] 配置文件已复制
)

echo [5/5] 打包完成！
echo.
echo ========================================
echo   输出文件位置: dist\科研论文图片组合工具.exe
echo ========================================
echo.
echo 提示:
echo - 可执行文件位于 dist 目录
echo - 可以直接复制到其他Windows电脑使用
echo - 首次运行可能较慢，请耐心等待
echo.

pause
```

2. 双击运行`build_exe.bat`
3. 等待打包完成
4. 在`dist`目录下找到生成的`.exe`文件

### 方法二：使用命令行打包

```bash
pyinstaller --name="科研论文图片组合工具" ^
--icon=icon.ico ^
--onefile ^
--windowed ^
--clean ^
--noconfirm ^
--add-data "requirements.txt;." ^
main.py
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--name` | 设置可执行文件名称 |
| `--icon` | 设置图标文件 |
| `--onefile` | 打包为单个文件 |
| `--windowed` | 不显示控制台窗口 |
| `--clean` | 清理临时文件 |
| `--noconfirm` | 不询问确认 |
| `--add-data` | 添加额外的数据文件 |

### 测试可执行文件

1. 双击运行`dist\科研论文图片组合工具.exe`
2. 测试所有功能是否正常
3. 在另一台没有Python环境的电脑上测试

## macOS打包教程

### 准备工作

1. 确保已安装Python 3.8或更高版本
2. 安装项目依赖：
```bash
pip install -r requirements.txt
```

### 安装PyInstaller

```bash
pip install pyinstaller
```

### 准备图标文件（可选）

1. 准备一个`.icns`格式的图标文件
2. 将图标文件命名为`icon.icns`，放在项目根目录
3. 可以使用在线工具转换：https://cloudconvert.com/png-to-icns

### 方法一：使用Shell脚本打包

1. 创建`build_app.sh`文件：

```bash
#!/bin/bash

echo "========================================"
echo "  科研论文图片组合工具 - macOS打包"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3环境，请先安装Python 3.8+"
    exit 1
fi

echo "[1/5] 检查依赖..."
if ! pip3 show pyqt5 &> /dev/null; then
    echo "[警告] PyQt5未安装，正在安装..."
    pip3 install -r requirements.txt
fi

echo "[2/5] 清理旧的打包文件..."
rm -rf build dist *.spec

echo "[3/5] 开始打包..."
pyinstaller --name="科研论文图片组合工具" \
--icon=icon.icns \
--onefile \
--windowed \
--clean \
--noconfirm \
--add-data "requirements.txt:." \
main.py

if [ $? -ne 0 ]; then
    echo "[错误] 打包失败！"
    exit 1
fi

echo "[4/5] 复制配置文件..."
if [ -f dist/"科研论文图片组合工具" ]; then
    cp requirements.txt dist/
    echo "[成功] 配置文件已复制"
fi

echo "[5/5] 打包完成！"
echo ""
echo "========================================"
echo "  输出文件位置: dist/科研论文图片组合工具"
echo "========================================"
echo ""
echo "提示:"
echo "- 可执行文件位于 dist 目录"
echo "- 可以直接复制到其他Mac电脑使用"
echo "- 首次运行可能需要授予执行权限"
echo ""
```

2. 赋予执行权限：
```bash
chmod +x build_app.sh
```

3. 运行脚本：
```bash
./build_app.sh
```

### 方法二：使用命令行打包

```bash
pyinstaller --name="科研论文图片组合工具" \
--icon=icon.icns \
--onefile \
--windowed \
--clean \
--noconfirm \
--add-data "requirements.txt:." \
main.py
```

### 授予执行权限（如果需要）

```bash
chmod +x dist/科研论文图片组合工具
```

### 测试可执行文件

1. 双击运行`dist/科研论文图片组合工具`
2. 测试所有功能是否正常
3. 在另一台没有Python环境的Mac上测试

## Linux打包教程

### 准备工作

1. 确保已安装Python 3.8或更高版本
2. 安装项目依赖：
```bash
pip install -r requirements.txt
```

### 安装PyInstaller

```bash
pip install pyinstaller
```

### 方法一：使用Shell脚本打包

1. 创建`build_linux.sh`文件：

```bash
#!/bin/bash

echo "========================================"
echo "  科研论文图片组合工具 - Linux打包"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3环境，请先安装Python 3.8+"
    exit 1
fi

echo "[1/5] 检查依赖..."
if ! pip3 show pyqt5 &> /dev/null; then
    echo "[警告] PyQt5未安装，正在安装..."
    pip3 install -r requirements.txt
fi

echo "[2/5] 清理旧的打包文件..."
rm -rf build dist *.spec

echo "[3/5] 开始打包..."
pyinstaller --name="科研论文图片组合工具" \
--onefile \
--windowed \
--clean \
--noconfirm \
--add-data "requirements.txt:." \
main.py

if [ $? -ne 0 ]; then
    echo "[错误] 打包失败！"
    exit 1
fi

echo "[4/5] 复制配置文件..."
if [ -f dist/"科研论文图片组合工具" ]; then
    cp requirements.txt dist/
    echo "[成功] 配置文件已复制"
fi

echo "[5/5] 打包完成！"
echo ""
echo "========================================"
echo "  输出文件位置: dist/科研论文图片组合工具"
echo "========================================"
echo ""
echo "提示:"
echo "- 可执行文件位于 dist 目录"
echo "- 可以直接复制到其他Linux电脑使用"
echo "- 首次运行可能需要授予执行权限"
echo ""
```

2. 赋予执行权限：
```bash
chmod +x build_linux.sh
```

3. 运行脚本：
```bash
./build_linux.sh
```

### 方法二：使用命令行打包

```bash
pyinstaller --name="科研论文图片组合工具" \
--onefile \
--windowed \
--clean \
--noconfirm \
--add-data "requirements.txt:." \
main.py
```

### 授予执行权限

```bash
chmod +x dist/科研论文图片组合工具
```

## 常见问题

### Q1: 打包后文件太大怎么办？

**原因**：`--onefile`模式会将所有依赖打包到一个文件中，导致文件较大。

**解决方案**：
1. 使用`--onedir`模式打包为目录：
```bash
pyinstaller --name="科研论文图片组合工具" --onedir --windowed main.py
```
2. 使用UPX压缩：
```bash
pyinstaller --name="科研论文图片组合工具" --onefile --windowed --upx-dir=/path/to/upx main.py
```

### Q2: 打包后运行报错"找不到模块"？

**原因**：某些隐式依赖没有被自动检测到。

**解决方案**：
1. 手动添加隐藏导入：
```bash
pyinstaller --hidden-import=模块名 main.py
```
2. 创建`.spec`文件手动配置：
```python
# 科研论文图片组合工具.spec
a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('requirements.txt', '.')],
             hiddenimports=['PIL._tkinter_finder'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)
```

### Q3: Windows杀毒软件误报？

**原因**：PyInstaller打包的程序可能被误报为病毒。

**解决方案**：
1. 使用代码签名证书对程序进行签名
2. 提醒用户添加信任
3. 使用虚拟环境打包，减少误报

### Q4: macOS无法打开，提示"已损坏"？

**原因**：macOS的安全机制阻止未签名的应用运行。

**解决方案**：
1. 在终端中运行：
```bash
xattr -cr dist/科研论文图片组合工具.app
```
2. 或在系统偏好设置中允许运行

### Q5: Linux运行报错"libGL.so.1: cannot open shared object file"？

**原因**：缺少OpenGL库。

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install libgl1-mesa-glx

# CentOS/RHEL
sudo yum install mesa-libGL
```

### Q6: 打包后图片加载失败？

**原因**：图片文件路径问题或格式支持库缺失。

**解决方案**：
1. 使用绝对路径
2. 确保所有图片格式支持库已打包
3. 检查`--add-data`参数是否正确

## 高级配置

### 创建自定义.spec文件

1. 生成初始.spec文件：
```bash
pyinstaller --onefile --windowed main.py
```

2. 编辑生成的`.spec`文件

3. 使用.spec文件打包：
```bash
pyinstaller 科研论文图片组合工具.spec
```

### 优化打包大小

1. 排除不需要的模块：
```bash
pyinstaller --exclude-module=tkinter --exclude-module=matplotlib main.py
```

2. 使用虚拟环境打包：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
pyinstaller main.py
```

### 添加版本信息（Windows）

创建`version_info.txt`文件：

```txt
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Your Company'),
          StringStruct(u'FileDescription', u'科研论文图片组合工具'),
          StringStruct(u'FileVersion', u'1.0.0.0'),
          StringStruct(u'InternalName', u'PhotoDealTool'),
          StringStruct(u'LegalCopyright', u'Copyright © 2024'),
          StringStruct(u'OriginalFilename', u'科研论文图片组合工具.exe'),
          StringStruct(u'ProductName', u'科研论文图片组合工具'),
          StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

使用版本信息：
```bash
pyinstaller --version-file=version_info.txt main.py
```

## 分发建议

### Windows
1. 将`.exe`文件压缩为ZIP包
2. 包含`README.md`使用说明
3. 提供系统要求说明

### macOS
1. 创建DMG安装包
2. 包含拖拽安装说明
3. 提供安全设置说明

### Linux
1. 创建AppImage或Flatpak包
2. 提供不同发行版的安装说明
3. 包含依赖安装命令

## 总结

通过本教程，您应该能够成功将科研论文图片组合工具打包为可执行文件。如果在打包过程中遇到问题，请参考常见问题部分或提交Issue。

祝您使用愉快！