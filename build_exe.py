# build_exe.py - 用于打包exe的脚本
"""
使用PyInstaller打包图像生成器为exe文件

使用步骤:
1. 安装依赖: pip install -r requirements.txt
2. 运行打包: python build_exe.py
"""

import os
import subprocess
import sys

def install_dependencies():
    """安装所需依赖"""
    dependencies = [
        'volcengine',
        'tkinter',  # 通常Python自带
        'requests',
        'pyinstaller'
    ]
    
    print("正在安装依赖...")
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} 安装成功")
        except subprocess.CalledProcessError:
            if dep == 'tkinter':
                print(f"⚠ {dep} 安装失败，但通常Python自带此库")
            else:
                print(f"✗ {dep} 安装失败")
                return False
    return True

def build_exe():
    """使用PyInstaller打包exe"""
    print("\n开始打包exe文件...")
    
    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',                    # 打包成单个exe文件
        '--windowed',                   # 不显示控制台窗口
        '--name=AI图像生成器',           # exe文件名
        '--icon=icon.ico',              # 图标文件（如果有的话）
        '--add-data=*.py;.',           # 添加所有Python文件
        '--hidden-import=volcengine',   # 确保包含volcengine库
        '--hidden-import=tkinter',      # 确保包含tkinter库
        'image_generator_gui.py'        # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists('icon.ico'):
        cmd = [item for item in cmd if not item.startswith('--icon')]
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ 打包成功！")
        print("exe文件位置: dist/AI图像生成器.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 打包失败: {e}")
        return False

def main():
    print("=== AI图像生成器打包工具 ===\n")
    
    # 检查主程序文件是否存在
    if not os.path.exists('image_generator_gui.py'):
        print("✗ 找不到主程序文件 image_generator_gui.py")
        print("请确保该文件与此打包脚本在同一目录下")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("\n依赖安装失败，无法继续打包")
        return
    
    # 打包exe
    if build_exe():
        print("\n打包完成！可以在dist目录下找到生成的exe文件")
        print("\n注意事项:")
        print("1. 首次运行exe时，杀毒软件可能会报警，这是正常现象")
        print("2. 请确保目标电脑已安装Visual C++ Redistributable")
        print("3. exe文件较大是正常的，因为包含了完整的Python运行环境")
    else:
        print("\n打包失败，请检查错误信息")

if __name__ == '__main__':
    main()