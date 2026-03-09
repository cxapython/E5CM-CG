# -*- coding: utf-8 -*-

import sys
import shutil
import subprocess
from pathlib import Path


def 获取项目根目录():
    return Path(__file__).parent.absolute()


def 检查依赖():
    print("=" * 60)
    print("📦 检查编译依赖")
    print("=" * 60)

    依赖映射 = {
        "pygame": "pygame",
        "cv2": "opencv-python",
    }

    缺失包列表 = []

    for 模块名, 包名 in 依赖映射.items():
        try:
            __import__(模块名)
            print(f"✓ {模块名} 已安装")
        except ImportError:
            print(f"✗ {模块名} 未安装")
            缺失包列表.append(包名)

    try:
        import PyInstaller  # noqa: F401

        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装")
        缺失包列表.append("pyinstaller")

    if 缺失包列表:
        print(f"\n需要安装缺失依赖: {', '.join(缺失包列表)}")
        print("是否现在安装？(y/n): ", end="")
        用户输入 = input().strip().lower()
        if 用户输入 != "y":
            print("✗ 编译中止")
            sys.exit(1)

        for 包名 in 缺失包列表:
            print(f"\n正在安装 {包名}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 包名])

        print("✓ 依赖安装完成")

    print()


def 清理旧文件(项目根目录: Path):
    print("🧹 清理旧的编译文件")

    编译结果目录 = 项目根目录 / "编译结果"
    构建目录 = 项目根目录 / "build"
    规格文件 = 项目根目录 / "E5CM-CG.spec"

    for 路径对象 in [编译结果目录, 构建目录]:
        if 路径对象.exists():
            shutil.rmtree(路径对象)
            print(f"  ✓ 删除目录: {路径对象}")

    if 规格文件.exists():
        规格文件.unlink()
        print(f"  ✓ 删除文件: {规格文件}")

    print()


def 清理源目录中不需要打包的文件(项目根目录: Path):
    print("🗑️ 清理源目录中不需要打包的文件")

    待删文件列表 = [
        项目根目录 / "UI-img" / "个人中心-个人资料" / "个人资料.json",
        项目根目录 / "songs" / "歌曲记录索引.json",
    ]

    for 文件路径 in 待删文件列表:
        if 文件路径.exists():
            try:
                文件路径.unlink()
                print(f"  ✓ 删除: {文件路径}")
            except Exception as 异常对象:
                print(f"  ⚠ 删除失败: {文件路径} -> {异常对象}")

    print()


def 准备资源数据(项目根目录: Path):
    print("📁 准备资源数据")

    内嵌资源列表 = []
    外部资源列表 = []

    内嵌资源目录列表 = [

    ]

    for 资源目录名 in 内嵌资源目录列表:
        资源目录路径 = 项目根目录 / 资源目录名
        if 资源目录路径.exists():
            内嵌资源列表.append((str(资源目录路径), 资源目录名))
            print(f"  ✓ 内嵌资源: {资源目录名}")
        else:
            print(f"  ⚠ 缺少内嵌资源目录: {资源目录路径}")

    打包专用歌曲目录 = 项目根目录 / "打包专用songs" / "songs"
    默认歌曲目录 = 项目根目录 / "songs"
    if 打包专用歌曲目录.exists():
        外部资源列表.append((str(打包专用歌曲目录), "songs"))
        print(r"  ✓ 外部资源: 打包专用songs\songs -> 编译结果\songs")
    elif 默认歌曲目录.exists():
        外部资源列表.append((str(默认歌曲目录), "songs"))
        print(r"  ✓ 外部资源: songs -> 编译结果\songs")
    else:
        print(r"  ⚠ 未找到 songs，也未找到 打包专用songs\songs")

    默认配置目录 = 项目根目录 / "json"
    if 默认配置目录.exists():
        外部资源列表.append((str(默认配置目录), "json"))
        print(r"  ✓ 外部资源: json -> 编译结果\json")
    else:
        print(r"  ⚠ 未找到 json 目录")

    print(f"\n共 {len(内嵌资源列表)} 个资源打包到 exe")
    print(f"共 {len(外部资源列表)} 个资源保留在编译结果目录\n")
    return 内嵌资源列表, 外部资源列表


def 构建_pyinstaller命令(项目根目录: Path, 内嵌资源列表: list):
    图标路径 = 项目根目录 / "icon" / "app.ico"
    if 图标路径.exists():
        图标参数列表 = ["--icon=" + str(图标路径)]
        print(f"✓ 使用图标: {图标路径}")
    else:
        图标参数列表 = []
        print(f"⚠ 未找到图标: {图标路径}")

    命令列表 = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=E5CM-CG",
        "--onefile",
        "--windowed",
        "--distpath=" + str(项目根目录 / "编译结果"),
        "--workpath=" + str(项目根目录 / "build"),
        "--specpath=" + str(项目根目录),
        "--add-data=" + str(项目根目录 / "core") + ";core",
        "--add-data=" + str(项目根目录 / "scenes") + ";scenes",
        "--add-data=" + str(项目根目录 / "ui") + ";ui",
    ]

    for 源路径, 目标相对目录 in 内嵌资源列表:
        命令列表.append(f"--add-data={源路径};{目标相对目录}")

    命令列表.extend(图标参数列表)
    命令列表.append(str(项目根目录 / "main.py"))
    return 命令列表


def 运行编译(命令列表: list):
    print("=" * 60)
    print("🏗️ 开始编译")
    print("=" * 60)
    print(f"\n执行命令: {' '.join(命令列表[:6])} ...\n")

    try:
        结果对象 = subprocess.run(命令列表, check=False)
        if 结果对象.returncode == 0:
            print("\n✓ 编译成功")
            return True

        print(f"\n✗ 编译失败，返回码: {结果对象.returncode}")
        return False
    except Exception as 异常对象:
        print(f"\n✗ 编译异常: {异常对象}")
        return False


def 复制目录(源目录: Path, 目标目录: Path):
    if 目标目录.exists():
        shutil.rmtree(目标目录)
    shutil.copytree(源目录, 目标目录)


def 复制外部资源到输出目录(项目根目录: Path, 外部资源列表: list):
    print("📦 复制外部资源到编译结果目录")

    编译结果目录 = 项目根目录 / "编译结果"
    编译结果目录.mkdir(parents=True, exist_ok=True)

    for 源路径字符串, 目标相对目录 in 外部资源列表:
        源路径 = Path(源路径字符串)
        目标路径 = 编译结果目录 / 目标相对目录

        if not 源路径.exists():
            print(f"  ⚠ 资源不存在，跳过: {源路径}")
            continue

        try:
            if 源路径.is_dir():
                复制目录(源路径, 目标路径)
                print(f"  ✓ 复制目录: {源路径} -> {目标路径}")
            else:
                目标路径.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(源路径, 目标路径)
                print(f"  ✓ 复制文件: {源路径} -> {目标路径}")
        except Exception as 异常对象:
            print(f"  ✗ 复制失败: {源路径} -> {异常对象}")

    print()


def 删除编译结果中的个人资料_json(项目根目录: Path):
    print("🗑️ 删除编译结果中的个人资料.json")

    目标文件路径 = 项目根目录 / "编译结果" / "json" / "个人资料.json"
    if 目标文件路径.exists():
        try:
            目标文件路径.unlink()
            print(f"  ✓ 已删除: {目标文件路径}")
        except Exception as 异常对象:
            print(f"  ✗ 删除失败: {目标文件路径} -> {异常对象}")
    else:
        print(f"  ℹ 文件不存在，无需删除: {目标文件路径}")

    print()


def 验证编译结果(项目根目录: Path, 外部资源列表: list):
    print("🔍 验证编译结果")

    编译结果目录 = 项目根目录 / "编译结果"
    主程序路径 = 编译结果目录 / "E5CM-CG.exe"

    全部正常 = True

    if 主程序路径.exists():
        print(f"  ✓ 主程序存在: {主程序路径}")
    else:
        print(f"  ✗ 主程序缺失: {主程序路径}")
        全部正常 = False

    for _, 目标相对目录 in 外部资源列表:
        资源路径 = 编译结果目录 / 目标相对目录
        if 资源路径.exists():
            print(f"  ✓ 外部资源存在: {资源路径}")
        else:
            print(f"  ✗ 外部资源缺失: {资源路径}")
            全部正常 = False

    被删文件路径 = 编译结果目录 / "json" / "个人资料.json"
    if 被删文件路径.exists():
        print(f"  ✗ 个人资料.json 仍存在: {被删文件路径}")
        全部正常 = False
    else:
        print(f"  ✓ 个人资料.json 已删除: {被删文件路径}")

    print("\n✓ 打包到 exe 内的资源: 冷资源, backmovies, UI-img")
    print("✓ 外部资源: songs, json")
    print()
    return 全部正常


def 清理临时编译文件(项目根目录: Path):
    print("🧹 清理临时编译文件")

    待删路径列表 = [
        项目根目录 / "build",
        项目根目录 / "E5CM-CG.spec",
        项目根目录 / "__pycache__",
    ]

    for 路径对象 in 待删路径列表:
        if not 路径对象.exists():
            continue

        try:
            if 路径对象.is_dir():
                shutil.rmtree(路径对象)
            else:
                路径对象.unlink()
            print(f"  ✓ 删除: {路径对象}")
        except Exception as 异常对象:
            print(f"  ⚠ 删除失败: {路径对象} -> {异常对象}")

    print()


def 主程序():
    项目根目录 = 获取项目根目录()
    编译结果目录 = 项目根目录 / "编译结果"

    print()
    print("=" * 60)
    print("🎮 E5CM-CG 编译脚本")
    print("=" * 60)
    print(f"项目根目录: {项目根目录}\n")

    检查依赖()
    清理旧文件(项目根目录)
    清理源目录中不需要打包的文件(项目根目录)

    内嵌资源列表, 外部资源列表 = 准备资源数据(项目根目录)
    命令列表 = 构建_pyinstaller命令(项目根目录, 内嵌资源列表)

    是否成功 = 运行编译(命令列表)
    if not 是否成功:
        print("\n⚠️ 编译失败，请检查报错输出")
        sys.exit(1)

    复制外部资源到输出目录(项目根目录, 外部资源列表)
    删除编译结果中的个人资料_json(项目根目录)

    验证是否通过 = 验证编译结果(项目根目录, 外部资源列表)
    if not 验证是否通过:
        print(f"\n⚠️ 编译完成，但结果不完整，请检查: {编译结果目录}")
        sys.exit(1)

    清理临时编译文件(项目根目录)

    print("=" * 60)
    print("✨ 编译成功")
    print("=" * 60)
    print(f"\n输出位置: {编译结果目录}")
    print(f"主程序: {编译结果目录 / 'E5CM-CG.exe'}")
    print(f"歌曲目录: {编译结果目录 / 'songs'}")
    print(f"配置目录: {编译结果目录 / 'json'}")
    print("已删除: 编译结果\\json\\个人资料.json")
    print()


if __name__ == "__main__":
    try:
        主程序()
    except KeyboardInterrupt:
        print("\n⚠️ 编译被中止")
        sys.exit(1)
    except Exception as 异常对象:
        print(f"\n❌ 发生错误: {异常对象}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
