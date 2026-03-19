# -*- coding: utf-8 -*-

import sys
import json
import sqlite3
import shutil
import subprocess
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
    return 项目根目录 / "编译结果"


def 获取程序输出目录(项目根目录: Path) -> Path:
    return 获取编译结果目录(项目根目录) / "E5CM-CG"


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
    用户输入 = input()
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
        用户输入 = input().strip().lower()
        if 用户输入 != "y":
            print("[FAIL] 编译中止")
            sys.exit(1)

        for 包名 in 缺失包列表:
            print(f"\n正在安装 {包名}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 包名])

        print("\n[OK] 依赖安装完成")

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

    # 首先检查并删除已存在的输出目录
    程序输出目录 = 获取程序输出目录(项目根目录)
    if 程序输出目录.exists():
        print(f"  [INFO] 发现已存在的编译结果: {程序输出目录}")
        try:
            shutil.rmtree(程序输出目录)
            print(f"  [OK] 已删除旧编译结果: {程序输出目录}")
        except Exception as e:
            print(f"  [WARN] 删除旧编译结果失败: {e}")

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
    这里采用“外部目录整体复制”策略：
    - exe 只负责把 Python 代码编译出来
    - 代码目录、资源目录全部复制到编译结果目录
    - 不打包开发机上的运行态、用户资料、收藏夹、投币数
    - songs 改为在编译结果中生成空目录骨架
    """
    目录名列表 = [
        "config",
        "core",
        "scenes",
        "ui",
        "UI-img",
        "冷资源",
        "backmovies",
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
    print("[STEP] 复制计划（保持开发环境目录结构）")
    if not 复制列表:
        print("  [WARN] 没有任何可复制目录")
        print()
        return

    for 源目录, 目标目录名 in 复制列表:
        print(f"  [OK] {源目录.name} -> 编译结果\\{目标目录名}")
    print("  [OK] 生成 songs 空目录骨架 -> 编译结果\\songs")
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
            "1. 打开 songs\\diy 文件夹。",
            "2. 在里面新建一个你的曲包文件夹，例如：songs\\diy\\Kpop。",
            "3. 把你下载好的整包歌曲文件夹放进这个曲包文件夹里。",
            "   正确示例：songs\\diy\\Kpop\\A-Cha\\A-Cha.ssc",
            "   也可以是：songs\\diy\\Kpop\\A-Cha\\A-Cha.sm",
            "4. 不要把 .ssc / .sm / .sma 文件直接丢在 songs\\diy 根目录。",
            "5. 一首歌通常应该和它的音频放在同一个歌曲文件夹里。",
            "   常见音频格式：.ogg  .mp3  .wav",
            "6. 导入完成后，重启游戏，再进入 DIY 模式刷新列表。",
            "",
            "当前 DIY 支持的谱面格式：.json  .ssc  .sm  .sma",
            "",
            "如果你下载的是整包压缩包：",
            "- 先解压",
            "- 确认不是“文件夹套文件夹”",
            "- 看到歌曲文件夹里有 .ssc / .sm / .sma 和音频文件就对了",
            "",
            "示例目录结构：",
            "songs\\diy",
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


def 生成songs目录骨架(项目根目录: Path):
    程序目录 = 获取程序输出目录(项目根目录)
    songs输出目录 = 程序目录 / "songs"

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


def 生成默认运行态(项目根目录: Path):
    print("[STEP] 生成默认运行态（不复制开发机状态）")

    程序目录 = 获取程序输出目录(项目根目录)
    if not 程序目录.exists():
        raise FileNotFoundError(f"未找到程序输出目录: {程序目录}")

    状态目录 = 程序目录 / "state"
    用户目录 = 程序目录 / "userdata"
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
    图标路径 = 项目根目录 / "UI-img" / "app.ico"
    主程序路径 = 获取主程序路径(项目根目录)
    编译结果目录 = 获取编译结果目录(项目根目录)
    构建目录 = 项目根目录 / "build"

    if not 主程序路径.exists():
        raise FileNotFoundError(f"未找到主程序文件: {主程序路径}")

    命令列表 = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=E5CM-CG",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--distpath={编译结果目录}",
        f"--workpath={构建目录}",
        f"--specpath={项目根目录}",
    ]

    if 图标路径.exists():
        命令列表.append(f"--icon={图标路径}")
        print(f"[OK] 使用图标: {图标路径}")
    else:
        print(f"[WARN] 未找到图标，继续无图标编译: {图标路径}")

    for 模块名 in PyInstaller隐藏导入模块:
        命令列表.append(f"--hidden-import={模块名}")

    命令列表.append(str(主程序路径))
    return 命令列表


def 运行编译(命令列表: list[str]) -> bool:
    print("=" * 60)
    print("[STEP] 开始编译 main.py")
    print("=" * 60)
    print("说明：本次采用 onedir 模式，尽量保持运行环境与开发环境一致")
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


def 复制外部目录到输出目录(项目根目录: Path, 复制列表: list[tuple[Path, str]]):
    print("[STEP] 复制外部目录到编译结果目录")

    程序目录 = 获取程序输出目录(项目根目录)

    if not 程序目录.exists():
        raise FileNotFoundError(f"未找到 PyInstaller 输出目录: {程序目录}")

    for 源目录, 目标目录名 in 复制列表:
        if not 源目录.exists():
            print(f"  [FAIL] 不存在，跳过: {源目录}")
            continue

        目标目录 = 程序目录 / 目标目录名
        try:
            复制目录(源目录, 目标目录)
            print(f"  [OK] 复制目录: {源目录} -> {目标目录}")
        except Exception as 异常对象:
            print(f"  [FAIL] 复制失败: {源目录} -> {异常对象}")

    print()


def 复制说明文件(项目根目录: Path):
    程序目录 = 获取程序输出目录(项目根目录)
    说明文件路径 = 程序目录 / "启动说明.txt"

    内容 = "\n".join(
        [
            "E5CM-CG 打包结果说明",
            "",
            "1. 请从当前目录运行 E5CM-CG.exe",
            "2. 不要单独拿走 exe 文件，需保持整个目录结构完整",
            "3. 本打包方式为 onedir，目的是尽量保持与开发环境一致",
            "4. 安装包不会携带开发机运行态，而是在输出目录生成默认运行态",
            "5. songs\\diy 内附带 DIY 导入教程，请按教程自行导入歌曲",
            "6. 若仍有路径错误，请优先检查项目代码里是否写死了 __file__ / cwd / 根目录推断逻辑",
            "",
        ]
    )

    说明文件路径.write_text(内容, encoding="utf-8")


def 验证编译结果(项目根目录: Path, 复制列表: list[tuple[Path, str]]) -> bool:
    print("[STEP] 验证编译结果")

    程序目录 = 获取程序输出目录(项目根目录)
    主程序路径 = 程序目录 / "E5CM-CG.exe"

    全部正常 = True

    if 主程序路径.exists():
        print(f"  [OK] 主程序存在: {主程序路径}")
    else:
        print(f"  [FAIL] 主程序缺失: {主程序路径}")
        全部正常 = False

    for _, 目标目录名 in 复制列表:
        目标目录 = 程序目录 / 目标目录名
        if 目标目录.exists():
            print(f"  [OK] 目录存在: {目标目录}")
        else:
            print(f"  [FAIL] 目录缺失: {目标目录}")
            全部正常 = False

    songs目录 = 程序目录 / "songs"
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

    状态目录 = 程序目录 / "state"
    状态数据库路径 = 状态目录 / 运行态数据库文件名
    用户目录 = 程序目录 / "userdata"
    个人资料目录 = 用户目录 / "profile"
    头像目录 = 个人资料目录 / "avatars"
    个人资料路径 = 个人资料目录 / "个人资料.json"

    for 路径对象 in (状态目录, 用户目录, 个人资料目录, 头像目录):
        if 路径对象.exists():
            print(f"  [OK] 目录存在: {路径对象}")
        else:
            print(f"  [FAIL] 目录缺失: {路径对象}")
            全部正常 = False

    for 路径对象 in (状态数据库路径, 个人资料路径):
        if 路径对象.exists():
            print(f"  [OK] 文件存在: {路径对象}")
        else:
            print(f"  [FAIL] 文件缺失: {路径对象}")
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


def 主程序():
    项目根目录 = 获取项目根目录()
    编译结果目录 = 获取编译结果目录(项目根目录)

    print()
    print("=" * 60)
    print("[STEP] E5CM-CG 极简一致性打包脚本")
    print("=" * 60)
    print(f"项目根目录: {项目根目录}")
    print(f"输出目录: {编译结果目录}")
    print()

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
    生成songs目录骨架(项目根目录)
    生成默认运行态(项目根目录)
    复制说明文件(项目根目录)

    验证通过 = 验证编译结果(项目根目录, 复制列表)
    if not 验证通过:
        print("\n[WARN] 编译完成，但结果不完整，请检查缺失目录")
        sys.exit(1)

    清理临时编译文件(项目根目录)

    print("=" * 60)
    print("[DONE] 编译成功")
    print("=" * 60)
    print(f"输出位置: {编译结果目录 / 'E5CM-CG'}")
    print(f"启动文件: {编译结果目录 / 'E5CM-CG' / 'E5CM-CG.exe'}")
    print("目录结构已尽量保持与开发环境一致")
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
