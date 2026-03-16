import json
import os
import re

from core.常量与路径 import 取应用配置路径, 取运行根目录


版本文件名 = "客户端版本.json"
默认版本号 = "v1.0.0"


def 获取版本文件路径(根目录: str | None = None) -> str:
    目标根目录 = str(根目录 or "").strip() or 取运行根目录()
    return 取应用配置路径(版本文件名, 根目录=os.path.abspath(目标根目录))


def 规范版本号(值: object, 默认值: str = "") -> str:
    文本 = str(值 or "").strip()
    if 文本:
        return 文本
    return str(默认值 or "").strip()


def 规范版本比较值(值: object) -> str:
    文本 = 规范版本号(值).replace(" ", "").lower()
    if 文本.startswith("v"):
        文本 = 文本[1:]
    return 文本


def _解析版本比较片段(值: object) -> tuple[list[int], tuple[int, str, int]]:
    文本 = 规范版本比较值(值)
    if not 文本:
        return [], (999, "", 0)

    主体文本 = str(文本.split("+", 1)[0] or "").strip()
    数字主体文本 = ""
    后缀文本 = ""
    匹配 = re.match(r"^(\d+(?:[._-]\d+)*)(.*)$", 主体文本)
    if 匹配:
        数字主体文本 = str(匹配.group(1) or "").strip()
        后缀文本 = str(匹配.group(2) or "").strip("._- ")
    if (not 后缀文本) and re.search(r"[a-z]", 主体文本):
        尾部匹配 = re.search(r"([a-z][a-z0-9._-]*)$", 主体文本)
        if 尾部匹配:
            后缀文本 = str(尾部匹配.group(1) or "").strip("._- ")
            前缀文本 = 主体文本[: 尾部匹配.start()].strip("._- ")
            if 前缀文本:
                数字主体文本 = 前缀文本

    数字片段 = re.findall(r"\d+", 数字主体文本)
    数字段 = [int(x) for x in 数字片段]

    if not 后缀文本:
        return 数字段, (999, "", 0)

    标签匹配 = re.match(r"([a-z]+)(\d*)", 后缀文本)
    标签 = str(标签匹配.group(1) or "").strip().lower() if 标签匹配 else 后缀文本
    try:
        序号 = int(标签匹配.group(2) or 0) if 标签匹配 else 0
    except Exception:
        序号 = 0

    权重表 = {
        "dev": 10,
        "alpha": 20,
        "a": 20,
        "beta": 30,
        "b": 30,
        "pre": 40,
        "preview": 40,
        "rc": 50,
    }
    return 数字段, (int(权重表.get(标签, 60)), 标签, int(序号))


def 比较版本号(左值: object, 右值: object) -> int:
    左数字段, 左后缀 = _解析版本比较片段(左值)
    右数字段, 右后缀 = _解析版本比较片段(右值)

    最大长度 = max(len(左数字段), len(右数字段))
    for 索引 in range(最大长度):
        左段 = int(左数字段[索引]) if 索引 < len(左数字段) else 0
        右段 = int(右数字段[索引]) if 索引 < len(右数字段) else 0
        if 左段 > 右段:
            return 1
        if 左段 < 右段:
            return -1

    if 左后缀 > 右后缀:
        return 1
    if 左后缀 < 右后缀:
        return -1
    return 0


def 读取版本信息(根目录: str | None = None) -> dict:
    路径 = 获取版本文件路径(根目录)
    默认数据 = {"version": 默认版本号}

    try:
        if os.path.isfile(路径):
            with open(路径, "r", encoding="utf-8") as 文件:
                对象 = json.load(文件)
            if isinstance(对象, dict):
                结果 = dict(默认数据)
                结果.update(对象)
                return 结果
    except Exception:
        pass

    return dict(默认数据)


def 读取当前版本号(根目录: str | None = None, 默认值: str = 默认版本号) -> str:
    数据 = 读取版本信息(根目录)
    return 规范版本号(数据.get("version"), 默认值)


def 读取当前版本展示文本(
    根目录: str | None = None,
    软件名: str = "e舞成名重构版",
) -> str:
    版本号 = 读取当前版本号(根目录=根目录, 默认值=默认版本号)
    if not 版本号:
        return str(软件名 or "").strip()
    return f"{str(软件名 or '').strip()}{版本号}"
