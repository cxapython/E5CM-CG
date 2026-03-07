#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E5CM-CG 项目编译脚本
使用 PyInstaller 将 main.py 编译为独立的 exe 文件
"""

import os
import sys
import subprocess
import shutil

def 编译项目():
    """编译项目为 exe"""
    项目根目录 = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(项目根目录, "main.py")
    输出目录 = os.path.join(项目根目录, "dist")
    build_dir = os.path.join(项目根目录, "build")
    
    if not os.path.exists(main_py):
        print(f"❌ 错误: 找不到 {main_py}")
        return False
    
    print("=" * 60)
    print("🎮 E5CM-CG 项目编译开始")
    print("=" * 60)
    print(f"📍 项目根目录: {项目根目录}")
    print(f"📄 主入口: {main_py}")
    print(f"📦 输出目录: {输出目录}")
    print()
    
    # 构建 PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 生成单个 exe 文件
        "--windowed",  # 无控制台窗口（Pygame 图形应用）
        "--name=e舞成名",  # exe 文件名
        "--icon=./UI-img/大模式选择界面/按钮/花式模式按钮.png",  # 图标（可选）
        f"--distpath={输出目录}",  # 输出目录
        f"--buildpath={build_dir}",  # 构建临时目录
        "--add-data=json;json",  # 添加 json 目录
        "--add-data=冷资源;冷资源",  # 添加资源目录
        "--add-data=UI-img;UI-img",  # 添加 UI 图片
        "--add-data=songs;songs",  # 添加歌曲目录
        "--add-data=backmovies;backmovies",  # 添加视频目录
        "--add-data=scenes;scenes",  # 添加场景代码
        "--add-data=core;core",  # 添加核心代码
        "--add-data=ui;ui",  # 添加 UI 代码
        # 隐藏导入（可选，加快编译速度）
        "--hidden-import=pygame",
        "--hidden-import=cv2",
        "--collect-all=pygame",
        main_py,
    ]
    
    print("📝 编译命令:")
    print(" ".join(cmd))
    print()
    
    try:
        print("⏳ 编译中，请稍候（可能需要几分钟）...")
        result = subprocess.run(cmd, cwd=项目根目录, check=True)
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("✅ 编译成功！")
            print("=" * 60)
            exe_path = os.path.join(输出目录, "e舞成名.exe")
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📦 生成文件: {exe_path}")
                print(f"📊 文件大小: {size_mb:.1f} MB")
                print()
                print("🚀 你可以直接运行生成的 exe 文件")
                print("💡 提示: exe 文件可以在没有安装 Python 的电脑上运行")
            return True
        else:
            print(f"❌ 编译失败 (返回码: {result.returncode})")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 编译出错: {e}")
        return False
    except Exception as e:
        print(f"❌ 异常: {type(e).__name__}: {e}")
        return False

def 清理编译文件():
    """清理编译生成的临时文件（可选）"""
    项目根目录 = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(项目根目录, "build")
    spec_file = os.path.join(项目根目录, "e舞成名.spec")
    
    print()
    清理 = input("是否清理编译临时文件? (y/n): ").lower()
    if 清理 == "y":
        try:
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
                print(f"✓ 删除 {build_dir}")
            if os.path.exists(spec_file):
                os.remove(spec_file)
                print(f"✓ 删除 {spec_file}")
            print("✓ 清理完成")
        except Exception as e:
            print(f"⚠ 清理失败: {e}")

if __name__ == "__main__":
    success = 编译项目()
    if success:
        清理编译文件()
        sys.exit(0)
    else:
        input("按 Enter 退出...")
        sys.exit(1)
