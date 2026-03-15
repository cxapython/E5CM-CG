import json
import os
import sys
from typing import Dict, List

from core.常量与路径 import (
    取运行根目录 as _公共取运行根目录,
    取资源根目录 as _公共取资源根目录,
    取songs根目录 as _公共取songs根目录,
)
from core.sqlite_store import (
    SCOPE_SONG_RECORDS as _歌曲记录存储作用域,
    read_scope as _读取存储作用域,
    replace_scope as _替换存储作用域,
)


def _规范路径(路径: str) -> str:
    try:
        return os.path.abspath(str(路径 or "").strip())
    except Exception:
        return ""


def _去重路径列表(路径列表: List[str]) -> List[str]:
    结果: List[str] = []
    已见 = set()
    for 路径 in 路径列表:
        规范后 = _规范路径(路径)
        if (not 规范后) or (规范后 in 已见):
            continue
        已见.add(规范后)
        结果.append(规范后)
    return 结果


def _向上查找目录(起点: str, 判定函数, 最大层数: int = 10) -> str:
    当前 = _规范路径(起点)
    if not 当前:
        return ""

    for _ in range(max(1, int(最大层数))):
        try:
            if 判定函数(当前):
                return 当前
        except Exception:
            pass

        上级 = os.path.dirname(当前)
        if 上级 == 当前:
            break
        当前 = 上级

    return ""


def _取运行根目录(项目根: str = "") -> str:
    if 项目根:
        规范项目根 = _规范路径(项目根)
        if 规范项目根 and os.path.isdir(规范项目根):
            return 规范项目根
    return _公共取运行根目录()


def _取资源根目录(项目根: str = "") -> str:
    if 项目根:
        规范项目根 = _规范路径(项目根)
        if 规范项目根 and os.path.isdir(规范项目根):
            return 规范项目根
    return _公共取资源根目录()


def _取歌曲目录(项目根: str) -> str:
    资源根 = _取资源根目录(项目根)
    return _公共取songs根目录(资源={"根": 资源根})


def _取用户数据根目录(项目根: str) -> str:
    return _取运行根目录(项目根)


def _主索引路径(项目根: str) -> str:
    数据根目录 = _取用户数据根目录(项目根)
    return os.path.join(数据根目录, "json", "歌曲记录索引.json")


def _兼容索引路径列表(项目根: str) -> List[str]:
    return [_主索引路径(项目根)]


def _读取json文件(路径: str):
    if (not 路径) or (not os.path.isfile(路径)):
        return None

    for 编码 in ("utf-8-sig", "utf-8", "gbk"):
        try:
            with open(路径, "r", encoding=编码) as 文件:
                return json.load(文件)
        except Exception:
            continue
    return None


def _写入json文件(路径: str, 数据):
    目录 = os.path.dirname(_规范路径(路径))
    if not 目录:
        raise ValueError(f"无效的写入路径: {路径}")

    os.makedirs(目录, exist_ok=True)

    临时路径 = 路径 + ".tmp"
    with open(临时路径, "w", encoding="utf-8") as 文件:
        json.dump(数据, 文件, ensure_ascii=False, indent=2)

    os.replace(临时路径, 路径)


def _索引路径(项目根: str) -> str:
    return _主索引路径(项目根)


def _提取歌曲相对路径(sm路径: str, 项目根: str) -> str:
    文本 = str(sm路径 or "").strip()
    if not 文本:
        return ""

    文本 = 文本.replace("\\", "/")

    if "/songs/" in 文本:
        return "songs/" + 文本.split("/songs/", 1)[1].lstrip("/")

    if 文本.startswith("songs/"):
        return 文本

    歌曲目录 = _取歌曲目录(项目根)
    规范sm路径 = _规范路径(sm路径)
    规范歌曲目录 = _规范路径(歌曲目录)

    if 规范sm路径 and 规范歌曲目录:
        try:
            相对路径 = os.path.relpath(规范sm路径, 规范歌曲目录).replace("\\", "/")
            if not 相对路径.startswith("../"):
                return "songs/" + 相对路径.lstrip("/")
        except Exception:
            pass

    文本 = 文本.lstrip("./").lstrip("/")
    if not 文本:
        return ""
    return "songs/" + 文本


def _歌曲键(sm路径: str, 项目根: str) -> str:
    return _提取歌曲相对路径(sm路径, 项目根)


def 取歌曲记录键(sm路径: str, 项目根: str) -> str:
    return _歌曲键(sm路径, 项目根)


def _规范歌曲记录项(项, 歌名: str = "", sm路径: str = "") -> dict:
    结果 = dict(项) if isinstance(项, dict) else {}

    try:
        结果["最高分"] = int(max(0, int(结果.get("最高分", 0) or 0)))
    except Exception:
        结果["最高分"] = 0

    try:
        结果["游玩次数"] = int(max(0, int(结果.get("游玩次数", 0) or 0)))
    except Exception:
        结果["游玩次数"] = 0

    if str(结果.get("歌名", "") or "") == "" and 歌名:
        结果["歌名"] = str(歌名 or "")

    if sm路径:
        结果["sm路径"] = str(sm路径 or "")
    elif str(结果.get("sm路径", "") or "") == "":
        结果["sm路径"] = ""

    return 结果


def _合并歌曲记录项(旧项: dict, 新项: dict, 项目根: str, 默认键: str = "") -> dict:
    旧项 = _规范歌曲记录项(
        旧项,
        歌名=str((旧项 or {}).get("歌名", "") or ""),
        sm路径=str((旧项 or {}).get("sm路径", "") or ""),
    )
    新项 = _规范歌曲记录项(
        新项,
        歌名=str((新项 or {}).get("歌名", "") or ""),
        sm路径=str((新项 or {}).get("sm路径", "") or ""),
    )

    try:
        最高分 = max(
            int(旧项.get("最高分", 0) or 0),
            int(新项.get("最高分", 0) or 0),
        )
    except Exception:
        最高分 = 0

    try:
        游玩次数 = int(max(0, int(旧项.get("游玩次数", 0) or 0))) + int(
            max(0, int(新项.get("游玩次数", 0) or 0))
        )
    except Exception:
        游玩次数 = int(max(0, int(旧项.get("游玩次数", 0) or 0)))

    歌名 = str(新项.get("歌名", "") or 旧项.get("歌名", "") or "")
    sm路径 = str(新项.get("sm路径", "") or 旧项.get("sm路径", "") or "")

    if (not sm路径) and 默认键:
        sm路径 = 默认键

    return {
        "最高分": int(max(0, 最高分)),
        "游玩次数": int(max(0, 游玩次数)),
        "歌名": 歌名,
        "sm路径": sm路径,
    }


def 读取歌曲记录索引(项目根: str) -> Dict[str, dict]:
    数据 = _读取存储作用域(_歌曲记录存储作用域, 根目录=项目根)

    if not isinstance(数据, dict):
        return {}

    是否已修正 = False
    结果: Dict[str, dict] = {}

    for 原键, 原项 in 数据.items():
        项 = dict(原项) if isinstance(原项, dict) else {}
        原sm路径 = str(项.get("sm路径", "") or "").strip()
        候选sm路径 = 原sm路径 or str(原键 or "").strip()

        新键 = _歌曲键(候选sm路径, 项目根)
        if not 新键:
            新键 = str(原键 or "").replace("\\", "/")

        新项 = _规范歌曲记录项(
            项,
            歌名=str(项.get("歌名", "") or ""),
            sm路径=原sm路径 or 候选sm路径,
        )

        if str(原键 or "") != 新键:
            是否已修正 = True

        if 新键 in 结果:
            结果[新键] = _合并歌曲记录项(结果[新键], 新项, 项目根, 默认键=新键)
            是否已修正 = True
        else:
            结果[新键] = dict(新项)

    if 是否已修正:
        保存歌曲记录索引(项目根, 结果)

    return 结果


def 保存歌曲记录索引(项目根: str, 数据: Dict[str, dict]):
    结果: Dict[str, dict] = {}

    for 键, 项 in dict(数据 or {}).items():
        原项 = dict(项) if isinstance(项, dict) else {}
        原sm路径 = str(原项.get("sm路径", "") or "").strip()
        候选sm路径 = 原sm路径 or str(键 or "").strip()

        新键 = _歌曲键(候选sm路径, 项目根)
        if not 新键:
            新键 = str(键 or "").replace("\\", "/")

        新项 = _规范歌曲记录项(
            原项,
            歌名=str(原项.get("歌名", "") or ""),
            sm路径=原sm路径 or 候选sm路径,
        )

        if 新键 in 结果:
            结果[新键] = _合并歌曲记录项(结果[新键], 新项, 项目根, 默认键=新键)
        else:
            结果[新键] = dict(新项)

    try:
        _替换存储作用域(_歌曲记录存储作用域, 结果, 根目录=项目根)
    except Exception:
        主路径 = _主索引路径(项目根)
        _写入json文件(主路径, 结果)


def 取歌曲记录(项目根: str, sm路径: str, 歌名: str = "") -> dict:
    索引 = 读取歌曲记录索引(项目根)
    键 = _歌曲键(sm路径, 项目根)

    if not 键:
        return _规范歌曲记录项({}, 歌名=str(歌名 or ""), sm路径=str(sm路径 or ""))

    项 = 索引.get(键)
    if not isinstance(项, dict):
        项 = _规范歌曲记录项({}, 歌名=str(歌名 or ""), sm路径=str(sm路径 or ""))
        索引[键] = dict(项)
        保存歌曲记录索引(项目根, 索引)
    else:
        原项 = dict(项)
        项 = _规范歌曲记录项(项, 歌名=str(歌名 or ""), sm路径=str(sm路径 or ""))
        if 项 != 原项:
            索引[键] = dict(项)
            保存歌曲记录索引(项目根, 索引)

    return dict(项)


def 更新歌曲最高分(项目根: str, sm路径: str, 歌名: str, 分数: int) -> dict:
    索引 = 读取歌曲记录索引(项目根)
    键 = _歌曲键(sm路径, 项目根)

    if not 键:
        return {
            "是否新纪录": False,
            "最高分": int(max(0, int(分数 or 0))),
            "旧最高分": 0,
            "游玩次数": 1,
        }

    项 = 索引.get(键)
    if not isinstance(项, dict):
        项 = _规范歌曲记录项({}, 歌名=str(歌名 or ""), sm路径=str(sm路径 or ""))
    else:
        项 = _规范歌曲记录项(项, 歌名=str(歌名 or ""), sm路径=str(sm路径 or ""))

    try:
        旧最高分 = int(max(0, int(项.get("最高分", 0) or 0)))
    except Exception:
        旧最高分 = 0

    try:
        旧游玩次数 = int(max(0, int(项.get("游玩次数", 0) or 0)))
    except Exception:
        旧游玩次数 = 0

    新分数 = int(max(0, int(分数 or 0)))
    是否新纪录 = bool(新分数 > 旧最高分)

    项["游玩次数"] = int(旧游玩次数 + 1)
    项["歌名"] = str(歌名 or 项.get("歌名", "") or "")
    项["sm路径"] = str(sm路径 or 项.get("sm路径", "") or "")

    if 是否新纪录:
        项["最高分"] = 新分数

    索引[键] = dict(项)
    保存歌曲记录索引(项目根, 索引)

    return {
        "是否新纪录": 是否新纪录,
        "最高分": int(max(旧最高分, 新分数)),
        "旧最高分": int(旧最高分),
        "游玩次数": int(项.get("游玩次数", 0) or 0),
    }
