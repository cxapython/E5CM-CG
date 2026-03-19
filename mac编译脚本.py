# -*- coding: utf-8 -*-
"""
E5CM-CG macOS 打包脚本
使用 PyInstaller 打包成 macOS 应用程序
"""
from __future__ import annotations

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path


版本文件名 = "客户端版本.json"
默认版本号 = "v1.0.0"
SONGS目录骨架清单文件名 = "_目录骨架清单.txt"
DIY导入教程文件名 = "DIY导入教程.txt"
运行态数据库文件名 = "runtime_state.sqlite3"
SONGS骨架顶级目录 = ("diy", "花式", "竞速")
SONGS骨架来源目录 = ("花式", "竞速")
PyInstaller隐藏导入模块 = (
    "ui.谱面渲染器",
    "ui.谱面GPU渲染器",
    "ui.调试_谱面渲染器_渲染控件",
    "ui.圆环频谱叠加",
    "ui.准备动画",
)


def 获取项目根目录() -> Path:
    return Path(__file__).resolve().parent


def 获取编译结果目录(项目根目录: Path) -> Path:
    return 项目根目录 / "dist"


def 获取程序输出目录(项目根目录: Path) -> Path:
    return 获取编译结果目录(项目根目录) / "E5CM-CG.app"


def 获取主程序路径(项目根目录: Path) -> Path:
    return 项目根目录 / "main.py"


def 获取版本文件路径列表(项目根目录: Path) -> list[Path]:
    return [
        项目根目录 / "config" / "app" / 版本文件名,
    ]


def 读取版本配置(文件路径: Path) -> dict:
    try:
        if 文件路径.exists():
            with open(文件路径, "r", encoding="utf-8") as 文件:
                对象 = json.load(文件)
            if isinstance(对象, dict):
                return dict(对象)
    except Exception:
        pass
    return {}


def 确认并写入当前版本号(项目根目录: Path) -> str:
    版本文件路径列表 = 获取版本文件路径列表(项目根目录)

    当前版本号 = ""
    for 文件路径 in 版本文件路径列表:
        当前版本号 = str(读取版本配置(文件路径).get("version", "") or "").strip()
        if 当前版本号:
            break
    if not 当前版本号:
        当前版本号 = 默认版本号

    print("=" * 60)
    print("[STEP] 确认当前版本号")
    print("=" * 60)
    print(f"当前版本号: {当前版本号}")
    print("请输入本次版本号（直接回车保留当前值）: ", end="")
    try:
        用户输入 = input()
    except EOFError:
        用户输入 = ""
    新版本号 = str(用户输入 or "").strip() or 当前版本号

    if not 新版本号:
        raise ValueError("版本号不能为空")

    for 文件路径 in 版本文件路径列表:
        旧配置 = 读取版本配置(文件路径)
        新配置 = dict(旧配置)
        新配置["version"] = 新版本号
        文件路径.parent.mkdir(parents=True, exist_ok=True)
        with open(文件路径, "w", encoding="utf-8") as 文件:
            json.dump(新配置, 文件, ensure_ascii=False, indent=2)
        print(f"[OK] 已写入版本号: {文件路径}")

    print()
    return 新版本号


def 检查依赖():
    print("=" * 60)
    print("[STEP] 检查编译依赖")
    print("=" * 60)

    依赖映射 = {
        "pygame": "pygame",
        "cv2": "opencv-python",
        "PyInstaller": "pyinstaller",
    }

    缺失包列表 = []

    for 模块名, 包名 in 依赖映射.items():
        try:
            __import__(模块名)
            print(f"[OK] {模块名} 已安装")
        except ImportError:
            print(f"[FAIL] {模块名} 未安装")
            缺失包列表.append(包名)

    if 缺失包列表:
        print("\n需要安装以下依赖：")
        for 包名 in 缺失包列表:
            print(f"  - {包名}")

        print("\n是否现在安装？(y/n): ", end="")
        try:
            用户输入 = input().strip().lower()
        except EOFError:
            用户输入 = "y"
        if 用户输入 != "y":
            print("[FAIL] 编译中止")
            sys.exit(1)

        for 包名 in 缺失包列表:
            print(f"\n正在安装 {包名}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 包名])

        print("\n[OK] 依赖安装完成")

    print()


def 检查macOS环境():
    """检查是否在 macOS 上运行"""
    print("=" * 60)
    print("[STEP] 检查 macOS 环境")
    print("=" * 60)

    if sys.platform != "darwin":
        print("[WARN] 当前不是 macOS 系统，打包可能失败")
        print(f"       当前系统: {sys.platform}")
    else:
        print(f"[OK] macOS 系统: {platform.mac_ver()[0]}")

    # 检查架构
    架构 = platform.machine()
    print(f"[OK] CPU 架构: {架构}")

    if 架构 == "arm64":
        print("[INFO] Apple Silicon (M1/M2/M3) 架构")
        print("       打包的应用将仅能在 Apple Silicon Mac 上运行")
    elif 架构 == "x86_64":
        print("[INFO] Intel 架构")
        print("       打包的应用将仅能在 Intel Mac 上运行")

    print()


def 清理目录(路径对象: Path):
    if not 路径对象.exists():
        return

    if 路径对象.is_dir():
        shutil.rmtree(路径对象)
    else:
        路径对象.unlink()


def 清理旧文件(项目根目录: Path):
    print("[STEP] 清理旧的编译文件")

    # 首先检查并删除已存在的 .app 应用
    app路径 = 获取编译结果目录(项目根目录) / "E5CM-CG.app"
    if app路径.exists():
        print(f"  [INFO] 发现已存在的应用: {app路径}")
        try:
            shutil.rmtree(app路径)
            print(f"  [OK] 已删除旧应用: {app路径}")
        except Exception as e:
            print(f"  [WARN] 删除旧应用失败: {e}")

    待清理列表 = [
        获取编译结果目录(项目根目录),
        项目根目录 / "build",
        项目根目录 / "E5CM-CG.spec",
        项目根目录 / "__pycache__",
    ]

    for 路径对象 in 待清理列表:
        if 路径对象.exists():
            清理目录(路径对象)
            print(f"  [OK] 已删除: {路径对象}")

    print()


def 获取需要复制的目录列表(项目根目录: Path) -> list[tuple[Path, str]]:
    """
    获取需要复制到 .app/Contents/Resources 的目录列表
    """
    目录名列表 = [
        "config",
        "core",
        "scenes",
        "ui",
        "UI-img",
        "冷资源",
        "backmovies",
        "songs",  # 包含实际歌曲文件
    ]

    复制列表: list[tuple[Path, str]] = []

    for 目录名 in 目录名列表:
        源目录 = 项目根目录 / 目录名
        if 源目录.exists():
            复制列表.append((源目录, 目录名))
        else:
            print(f"[WARN] 缺少目录，稍后跳过: {源目录}")

    return 复制列表


def 显示复制计划(复制列表: list[tuple[Path, str]]):
    print("[STEP] 复制计划")
    if not 复制列表:
        print("  [WARN] 没有任何可复制目录")
        print()
        return

    for 源目录, 目标目录名 in 复制列表:
        print(f"  [OK] {源目录.name} -> Resources/{目标目录名}")
    print()


def _目录相对路径排序键(相对路径: str) -> tuple[int, tuple[str, ...]]:
    文本 = str(相对路径 or "").replace("\\", "/").strip("/")
    片段 = tuple(文本.split("/")) if 文本 else tuple()
    return (len(片段), 片段)


def 收集songs目录骨架(项目根目录: Path) -> list[str]:
    songs源目录 = 项目根目录 / "songs"
    结果集合: set[str] = set(SONGS骨架顶级目录)

    if not songs源目录.exists():
        print(f"[WARN] 未找到 songs 目录，将仅创建顶级目录: {songs源目录}")
        return sorted(结果集合, key=_目录相对路径排序键)

    for 顶级目录名 in SONGS骨架来源目录:
        顶级目录 = songs源目录 / 顶级目录名
        if not 顶级目录.exists():
            print(f"[WARN] songs 子目录缺失，已跳过: {顶级目录}")
            continue

        结果集合.add(顶级目录名)
        for 当前目录 in 顶级目录.rglob("*"):
            if not 当前目录.is_dir():
                continue
            try:
                相对路径 = 当前目录.relative_to(songs源目录).as_posix()
            except Exception:
                continue
            if not 相对路径:
                continue
            if len(Path(相对路径).parts) <= 3:
                结果集合.add(相对路径)

    return sorted(结果集合, key=_目录相对路径排序键)


def 生成DIY导入教程内容() -> str:
    return "\n".join(
        [
            "DIY 歌曲导入教程",
            "",
            "1. 打开 E5CM-CG.app/Contents/Resources/songs/diy 文件夹。",
            "2. 在里面新建一个你的曲包文件夹，例如：songs/diy/Kpop。",
            "3. 把你下载好的整包歌曲文件夹放进这个曲包文件夹里。",
            "   正确示例：songs/diy/Kpop/A-Cha/A-Cha.ssc",
            "   也可以是：songs/diy/Kpop/A-Cha/A-Cha.sm",
            "4. 不要把 .ssc / .sm / .sma 文件直接丢在 songs/diy 根目录。",
            "5. 一首歌通常应该和它的音频放在同一个歌曲文件夹里。",
            "   常见音频格式：.ogg  .mp3  .wav",
            "6. 导入完成后，重启游戏，再进入 DIY 模式刷新列表。",
            "",
            "当前 DIY 支持的谱面格式：.json  .ssc  .sm  .sma",
            "",
            "如果你下载的是整包压缩包：",
            "- 先解压",
            "- 确认不是「文件夹套文件夹」",
            "- 看到歌曲文件夹里有 .ssc / .sm / .sma 和音频文件就对了",
            "",
            "示例目录结构：",
            "songs/diy",
            "└─ Kpop",
            "   ├─ A-Cha",
            "   │  ├─ A-Cha.ssc",
            "   │  └─ audio.ogg",
            "   └─ Trouble maker",
            "      ├─ Hyunaaaaaaaaaaaaaa S2.sm",
            "      └─ music.mp3",
            "",
        ]
    )


def 生成songs目录骨架(项目根目录: Path, resources目录: Path):
    songs输出目录 = resources目录 / "songs"

    if songs输出目录.exists():
        shutil.rmtree(songs输出目录)
    songs输出目录.mkdir(parents=True, exist_ok=True)

    目录骨架列表 = 收集songs目录骨架(项目根目录)
    for 相对路径 in 目录骨架列表:
        (songs输出目录 / Path(相对路径)).mkdir(parents=True, exist_ok=True)

    骨架清单路径 = songs输出目录 / SONGS目录骨架清单文件名
    骨架清单路径.write_text("\n".join(目录骨架列表) + "\n", encoding="utf-8")

    教程路径 = songs输出目录 / "diy" / DIY导入教程文件名
    教程路径.write_text(生成DIY导入教程内容(), encoding="utf-8")

    print(f"  [OK] 已生成 songs 目录骨架: {songs输出目录}")
    print(f"  [OK] 已写入 DIY 导入教程: {教程路径}")
    print(f"  [OK] 已写入目录骨架清单: {骨架清单路径}")
    print()


import random


def 随机选择保留歌曲文件夹(songs输出目录: Path):
    """
    随机选择竞速/疯狂目录下的两个文件夹保留，删除其他歌曲文件夹以减小体积
    """
    疯狂目录 = songs输出目录 / "竞速" / "疯狂"
    if not 疯狂目录.exists():
        print(f"  [INFO] 未找到疯狂目录，跳过随机选择")
        return

    所有文件夹 = [p for p in 疯狂目录.iterdir() if p.is_dir()]
    if len(所有文件夹) <= 2:
        print(f"  [INFO] 疯狂目录下只有 {len(所有文件夹)} 个文件夹，无需随机选择")
        return

    # 随机选择两个文件夹保留
    保留文件夹 = random.sample(所有文件夹, 2)
    保留名称 = [f.name for f in 保留文件夹]

    print(f"  [STEP] 随机选择保留的歌曲文件夹")
    print(f"  [OK] 保留: {保留名称[0]}")
    print(f"  [OK] 保留: {保留名称[1]}")

    # 删除其他文件夹
    删除计数 = 0
    for 文件夹 in 所有文件夹:
        if 文件夹 not in 保留文件夹:
            try:
                shutil.rmtree(文件夹)
                删除计数 += 1
            except Exception as e:
                print(f"  [WARN] 删除失败: {文件夹.name} - {e}")

    print(f"  [OK] 已删除 {删除计数} 个文件夹以减小应用体积")


def 确保songs目录结构完整(项目根目录: Path, resources目录: Path):
    """
    确保 songs 目录结构完整（保留已复制的歌曲文件，添加必要的 diy 目录和教程）
    """
    songs输出目录 = resources目录 / "songs"

    # 随机选择只保留两个歌曲文件夹
    随机选择保留歌曲文件夹(songs输出目录)

    # 确保 diy 目录存在
    diy目录 = songs输出目录 / "diy"
    diy目录.mkdir(parents=True, exist_ok=True)

    # 写入 DIY 导入教程
    教程路径 = diy目录 / DIY导入教程文件名
    教程路径.write_text(生成DIY导入教程内容(), encoding="utf-8")

    # 写入目录骨架清单（基于实际存在的目录）
    目录骨架列表 = []
    if songs输出目录.exists():
        for 路径 in songs输出目录.iterdir():
            if 路径.is_dir():
                目录骨架列表.append(路径.name)
                # 递归收集子目录
                for 子路径 in 路径.rglob("*"):
                    if 子路径.is_dir():
                        try:
                            相对路径 = 子路径.relative_to(songs输出目录).as_posix()
                            if 相对路径 and 相对路径 not in 目录骨架列表:
                                目录骨架列表.append(相对路径)
                        except Exception:
                            pass

    骨架清单路径 = songs输出目录 / SONGS目录骨架清单文件名
    骨架清单路径.write_text("\n".join(sorted(目录骨架列表)) + "\n", encoding="utf-8")

    print(f"  [OK] 已确保 songs 目录结构完整: {songs输出目录}")
    print(f"  [OK] 已写入 DIY 导入教程: {教程路径}")
    print(f"  [OK] 已写入目录骨架清单: {骨架清单路径}")
    print()


def _构建后备默认模式进度() -> dict:
    return {"等级": 1, "经验": 0.0, "累计歌曲": 0, "累计首数": 0}


def 构建默认个人资料() -> dict:
    try:
        from core.等级经验 import 构建默认模式进度, 经验数据版本

        默认花式进度 = dict(构建默认模式进度())
        默认竞速进度 = dict(构建默认模式进度())
        默认经验版本 = int(经验数据版本)
    except Exception:
        默认花式进度 = _构建后备默认模式进度()
        默认竞速进度 = _构建后备默认模式进度()
        默认经验版本 = 2

    return {
        "昵称": "玩家昵称",
        "头像文件": "UI-img/个人中心-个人资料/默认头像.png",
        "统计": {
            "游玩时长分钟": 0,
            "累计评价S数": 0,
            "最大Combo": 0,
            "最大Combo曲目": "",
            "最高分": 0,
            "最高分曲目": "",
        },
        "进度": {
            "最大等级": 70,
            "经验版本": int(默认经验版本),
            "段位": "UI-img/个人中心-个人资料/等级/1.png",
            "花式": 默认花式进度,
            "竞速": 默认竞速进度,
        },
    }


def 初始化默认运行态数据库(数据库路径: Path):
    import sqlite3

    数据库路径.parent.mkdir(parents=True, exist_ok=True)
    连接 = sqlite3.connect(str(数据库路径))
    try:
        连接.execute(
            """
            CREATE TABLE IF NOT EXISTS store_kv (
                scope TEXT NOT NULL,
                key TEXT NOT NULL,
                value_json TEXT NOT NULL,
                updated_at REAL NOT NULL,
                PRIMARY KEY (scope, key)
            )
            """
        )
        连接.commit()
    finally:
        连接.close()


def 生成默认运行态(项目根目录: Path, resources目录: Path):
    print("[STEP] 生成默认运行态（不复制开发机状态）")

    if not resources目录.exists():
        raise FileNotFoundError(f"未找到 Resources 目录: {resources目录}")

    状态目录 = resources目录 / "state"
    用户目录 = resources目录 / "userdata"
    个人资料目录 = 用户目录 / "profile"
    头像目录 = 个人资料目录 / "avatars"
    个人资料路径 = 个人资料目录 / "个人资料.json"
    数据库路径 = 状态目录 / 运行态数据库文件名

    状态目录.mkdir(parents=True, exist_ok=True)
    头像目录.mkdir(parents=True, exist_ok=True)

    默认个人资料 = 构建默认个人资料()
    个人资料路径.write_text(
        json.dumps(默认个人资料, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    初始化默认运行态数据库(数据库路径)

    print(f"  [OK] 已生成状态目录: {状态目录}")
    print(f"  [OK] 已初始化状态数据库: {数据库路径}")
    print(f"  [OK] 已生成个人资料: {个人资料路径}")
    print(f"  [OK] 已生成头像目录: {头像目录}")
    print()


def 构建_pyinstaller命令(项目根目录: Path) -> list[str]:
    主程序路径 = 获取主程序路径(项目根目录)
    编译结果目录 = 获取编译结果目录(项目根目录)
    构建目录 = 项目根目录 / "build"

    if not 主程序路径.exists():
        raise FileNotFoundError(f"未找到主程序文件: {主程序路径}")

    # macOS 使用 .icns 图标（如果存在），否则不指定图标
    图标路径 = 项目根目录 / "UI-img" / "app.icns"
    图标参数 = []
    if 图标路径.exists():
        图标参数 = [f"--icon={图标路径}"]
        print(f"[OK] 使用图标: {图标路径}")
    else:
        # 尝试从 .ico 转换或跳过图标
        print(f"[WARN] 未找到 .icns 图标文件，将使用默认图标")

    命令列表 = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=E5CM-CG",
        "--onedir",
        "--windowed",  # macOS 上创建 .app bundle
        "--clean",
        "--noconfirm",
        f"--distpath={编译结果目录}",
        f"--workpath={构建目录}",
        f"--specpath={项目根目录}",
        *图标参数,
    ]

    # 添加隐藏导入
    for 模块名 in PyInstaller隐藏导入模块:
        命令列表.append(f"--hidden-import={模块名}")

    # macOS 特定参数
    命令列表.append("--osx-bundle-identifier=com.e5cm.cg")

    命令列表.append(str(主程序路径))
    return 命令列表


def 运行编译(命令列表: list[str]) -> bool:
    print("=" * 60)
    print("[STEP] 开始编译 main.py (PyInstaller)")
    print("=" * 60)
    print("说明：本次采用 onedir 模式，生成 macOS .app 应用包")
    print()

    try:
        结果对象 = subprocess.run(命令列表, check=False)
    except Exception as 异常对象:
        print(f"[FAIL] 编译过程异常: {异常对象}")
        return False

    if 结果对象.returncode == 0:
        print("\n[OK] 编译成功")
        return True

    print(f"\n[FAIL] 编译失败，返回码: {结果对象.returncode}")
    return False


def 复制目录(源目录: Path, 目标目录: Path):
    if 目标目录.exists():
        shutil.rmtree(目标目录)
    shutil.copytree(源目录, 目标目录)


def 复制文件(源文件: Path, 目标文件: Path):
    目标文件.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(源文件, 目标文件)


def 获取app_resources目录(项目根目录: Path) -> Path:
    """
    获取 .app 内的 Resources 目录路径
    PyInstaller 在 macOS 上会将数据放在 .app/Contents/Resources/
    """
    app路径 = 获取编译结果目录(项目根目录) / "E5CM-CG.app"
    resources路径 = app路径 / "Contents" / "Resources"

    # 检查是否存在，如果不存在尝试其他可能的位置
    if resources路径.exists():
        return resources路径

    # 某些 PyInstaller 版本可能直接放在 .app 旁边
    备选路径 = 获取编译结果目录(项目根目录) / "E5CM-CG"
    if 备选路径.exists():
        return 备选路径

    return resources路径


def 复制外部目录到输出目录(项目根目录: Path, 复制列表: list[tuple[Path, str]]):
    print("[STEP] 复制外部目录到 .app/Contents/Resources")

    resources目录 = 获取app_resources目录(项目根目录)

    if not resources目录.exists():
        # 如果 PyInstaller 没有创建 Resources 目录，创建它
        resources目录.mkdir(parents=True, exist_ok=True)
        print(f"  [INFO] 创建 Resources 目录: {resources目录}")

    for 源目录, 目标目录名 in 复制列表:
        if not 源目录.exists():
            print(f"  [FAIL] 不存在，跳过: {源目录}")
            continue

        目标目录 = resources目录 / 目标目录名
        try:
            复制目录(源目录, 目标目录)
            print(f"  [OK] 复制目录: {源目录} -> {目标目录}")
        except Exception as 异常对象:
            print(f"  [FAIL] 复制失败: {源目录} -> {异常对象}")

    print()


def 复制说明文件(项目根目录: Path):
    resources目录 = 获取app_resources目录(项目根目录)
    说明文件路径 = resources目录 / "启动说明.txt"

    内容 = "\n".join(
        [
            "E5CM-CG macOS 打包结果说明",
            "",
            "1. 双击 E5CM-CG.app 启动游戏",
            "2. 如果提示「无法验证开发者」，请在系统偏好设置 > 安全性与隐私中允许运行",
            "3. 右键点击 .app 选择「打开」也可以绕过验证",
            "4. songs 文件夹位于 .app/Contents/Resources/songs/",
            "5. 若仍有路径错误，请优先检查项目代码里是否写死了路径",
            "",
            "DIY 歌曲导入：",
            "- 右键点击 E5CM-CG.app，选择「显示包内容」",
            "- 导航到 Contents/Resources/songs/diy/ 目录",
            "- 将歌曲文件夹放入 diy 目录下",
            "",
        ]
    )

    说明文件路径.write_text(内容, encoding="utf-8")


def 验证编译结果(项目根目录: Path, 复制列表: list[tuple[Path, str]]) -> bool:
    print("[STEP] 验证编译结果")

    app路径 = 获取编译结果目录(项目根目录) / "E5CM-CG.app"
    resources目录 = 获取app_resources目录(项目根目录)

    全部正常 = True

    if app路径.exists():
        print(f"  [OK] 应用包存在: {app路径}")
    else:
        print(f"  [FAIL] 应用包缺失: {app路径}")
        全部正常 = False

    # 检查可执行文件
    可执行文件路径 = app路径 / "Contents" / "MacOS" / "E5CM-CG"
    if 可执行文件路径.exists():
        print(f"  [OK] 可执行文件存在: {可执行文件路径}")
    else:
        print(f"  [FAIL] 可执行文件缺失: {可执行文件路径}")
        全部正常 = False

    for _, 目标目录名 in 复制列表:
        目标目录 = resources目录 / 目标目录名
        if 目标目录.exists():
            print(f"  [OK] 目录存在: {目标目录}")
        else:
            print(f"  [FAIL] 目录缺失: {目标目录}")
            全部正常 = False

    songs目录 = resources目录 / "songs"
    diy目录 = songs目录 / "diy"
    教程路径 = diy目录 / DIY导入教程文件名
    骨架清单路径 = songs目录 / SONGS目录骨架清单文件名

    if songs目录.exists():
        print(f"  [OK] 目录存在: {songs目录}")
    else:
        print(f"  [FAIL] 目录缺失: {songs目录}")
        全部正常 = False

    if diy目录.exists():
        print(f"  [OK] 目录存在: {diy目录}")
    else:
        print(f"  [FAIL] 目录缺失: {diy目录}")
        全部正常 = False

    if 教程路径.exists():
        print(f"  [OK] 文件存在: {教程路径}")
    else:
        print(f"  [FAIL] 文件缺失: {教程路径}")
        全部正常 = False

    if 骨架清单路径.exists():
        print(f"  [OK] 文件存在: {骨架清单路径}")
    else:
        print(f"  [FAIL] 文件缺失: {骨架清单路径}")
        全部正常 = False

    print()
    return 全部正常


def 清理临时编译文件(项目根目录: Path):
    print("[STEP] 清理临时文件")

    待清理列表 = [
        项目根目录 / "build",
        项目根目录 / "E5CM-CG.spec",
        项目根目录 / "__pycache__",
    ]

    for 路径对象 in 待清理列表:
        if not 路径对象.exists():
            continue

        try:
            清理目录(路径对象)
            print(f"  [OK] 删除: {路径对象}")
        except Exception as 异常对象:
            print(f"  [WARN] 删除失败: {路径对象} -> {异常对象}")

    print()


def 创建dmg(项目根目录: Path, 版本号: str):
    """
    可选：创建 DMG 安装包
    需要 macOS 环境和 hdiutil 工具
    """
    print("=" * 60)
    print("[STEP] 创建 DMG 安装包（可选）")
    print("=" * 60)

    app路径 = 获取编译结果目录(项目根目录) / "E5CM-CG.app"
    if not app路径.exists():
        print("[FAIL] .app 不存在，跳过 DMG 创建")
        return False

    dmg名称 = f"E5CM-CG-{版本号}.dmg"
    dmg路径 = 获取编译结果目录(项目根目录) / dmg名称
    临时dmg目录 = 获取编译结果目录(项目根目录) / "dmg_temp"

    # 清理旧的 DMG
    if dmg路径.exists():
        try:
            dmg路径.unlink()
        except Exception:
            pass

    # 创建临时目录
    if 临时dmg目录.exists():
        shutil.rmtree(临时dmg目录)
    临时dmg目录.mkdir(parents=True)

    try:
        # 复制 .app 到临时目录
        目标App = 临时dmg目录 / "E5CM-CG.app"
        shutil.copytree(app路径, 目标App)

        # 创建应用程序快捷方式
        应用程序别名 = 临时dmg目录 / "Applications"
        应用程序别名.mkdir()

        # 使用 hdiutil 创建 DMG
        print(f"  [INFO] 正在创建 {dmg名称}...")
        结果 = subprocess.run(
            [
                "hdiutil", "create",
                "-volname", "E5CM-CG",
                "-srcfolder", str(临时dmg目录),
                "-ov", "-format", "UDZO",
                str(dmg路径)
            ],
            capture_output=True,
            text=True
        )

        if 结果.returncode == 0:
            print(f"  [OK] DMG 创建成功: {dmg路径}")
        else:
            print(f"  [FAIL] DMG 创建失败: {结果.stderr}")
            return False

    finally:
        # 清理临时目录
        if 临时dmg目录.exists():
            shutil.rmtree(临时dmg目录)

    print()
    return True


def 主程序():
    项目根目录 = 获取项目根目录()
    编译结果目录 = 获取编译结果目录(项目根目录)

    print()
    print("=" * 60)
    print("[STEP] E5CM-CG macOS 打包脚本")
    print("=" * 60)
    print(f"项目根目录: {项目根目录}")
    print(f"输出目录: {编译结果目录}")
    print()

    检查macOS环境()
    确认并写入当前版本号(项目根目录)
    检查依赖()
    清理旧文件(项目根目录)

    复制列表 = 获取需要复制的目录列表(项目根目录)
    显示复制计划(复制列表)

    命令列表 = 构建_pyinstaller命令(项目根目录)
    是否成功 = 运行编译(命令列表)
    if not 是否成功:
        print("\n[FAIL] 编译失败，请先看 PyInstaller 上面的真实报错")
        sys.exit(1)

    复制外部目录到输出目录(项目根目录, 复制列表)

    resources目录 = 获取app_resources目录(项目根目录)
    确保songs目录结构完整(项目根目录, resources目录)
    生成默认运行态(项目根目录, resources目录)
    复制说明文件(项目根目录)

    验证通过 = 验证编译结果(项目根目录, 复制列表)
    if not 验证通过:
        print("\n[WARN] 编译完成，但结果不完整，请检查缺失目录")
        sys.exit(1)

    清理临时编译文件(项目根目录)

    # 询问是否创建 DMG
    print("是否创建 DMG 安装包？(y/n): ", end="")
    try:
        用户输入 = input().strip().lower()
    except EOFError:
        用户输入 = "n"

    if 用户输入 == "y":
        版本号 = 读取版本配置((项目根目录 / "config" / "app" / 版本文件名)).get("version", 默认版本号)
        创建dmg(项目根目录, 版本号)

    print("=" * 60)
    print("[DONE] 打包成功")
    print("=" * 60)
    print(f"应用位置: {编译结果目录 / 'E5CM-CG.app'}")
    print()
    print("使用说明：")
    print("1. 双击 E5CM-CG.app 启动游戏")
    print("2. 如果提示无法验证，请在系统偏好设置中允许运行")
    print("3. 歌曲文件放在 .app/Contents/Resources/songs/ 目录下")
    print()


if __name__ == "__main__":
    try:
        主程序()
    except KeyboardInterrupt:
        print("\n[WARN] 编译被中止")
        sys.exit(1)
    except Exception as 异常对象:
        print(f"\n[FAIL] 发生错误: {异常对象}")
        import traceback
        traceback.print_exc()
        sys.exit(1)