import hashlib
import os
from typing import Dict, Optional, Set, Tuple

import pygame

from core.常量与路径 import 取缓存目录


缓存键 = Tuple[str, int, int, int, str]


def _规范缓存键(
    路径: str,
    目标宽: int,
    目标高: int,
    圆角: int,
    模式: str,
) -> 缓存键:
    try:
        绝对路径 = os.path.abspath(str(路径 or "").strip())
    except Exception:
        绝对路径 = str(路径 or "").strip()
    try:
        宽 = max(1, int(目标宽))
    except Exception:
        宽 = 1
    try:
        高 = max(1, int(目标高))
    except Exception:
        高 = 1
    try:
        圆角值 = max(0, int(圆角))
    except Exception:
        圆角值 = 0
    模式值 = str(模式 or "cover").strip().lower() or "cover"
    return (绝对路径, 宽, 高, 圆角值, 模式值)


class 本地图片缓存:
    def __init__(
        self,
        缓存目录: str = "",
        名称空间: str = "image_cache",
        内存上限: int = 512,
    ):
        基础目录 = str(缓存目录 or "").strip() or 取缓存目录(str(名称空间 or "image_cache"))
        self._缓存目录 = os.path.abspath(基础目录)
        self._内存缓存: Dict[缓存键, pygame.Surface] = {}
        self._访问顺序: list[缓存键] = []
        try:
            self._内存上限 = max(32, int(内存上限))
        except Exception:
            self._内存上限 = 512

    def 获取(
        self,
        路径: str,
        目标宽: int,
        目标高: int,
        圆角: int,
        模式: str,
    ) -> Optional[pygame.Surface]:
        键 = _规范缓存键(路径, 目标宽, 目标高, 圆角, 模式)
        已有 = self._内存缓存.get(键)
        if isinstance(已有, pygame.Surface):
            self._刷新访问顺序(键)
            return 已有

        缓存文件路径 = self._取缓存文件路径(键)
        if self._缓存文件有效(缓存文件路径, 键[0]):
            图 = self._读取磁盘缓存(缓存文件路径)
            if isinstance(图, pygame.Surface):
                self._写入内存缓存(键, 图)
                return 图
        return None

    def 写入(
        self,
        路径: str,
        目标宽: int,
        目标高: int,
        圆角: int,
        模式: str,
        图: pygame.Surface,
    ):
        if not isinstance(图, pygame.Surface):
            return
        键 = _规范缓存键(路径, 目标宽, 目标高, 圆角, 模式)
        self._写入内存缓存(键, 图)
        self._写入磁盘缓存(键, 图)

    def 清理远端(self, 保留key集合: Set[缓存键]):
        保留集合: Set[缓存键] = set()
        for 键 in list(保留key集合 or set()):
            try:
                路径, 目标宽, 目标高, 圆角, 模式 = 键
                保留集合.add(
                    _规范缓存键(路径, 目标宽, 目标高, 圆角, 模式)
                )
            except Exception:
                continue
        删除键列表 = [键 for 键 in list(self._内存缓存.keys()) if 键 not in 保留集合]
        for 键 in 删除键列表:
            self._内存缓存.pop(键, None)
            try:
                self._访问顺序.remove(键)
            except Exception:
                pass

    def 取缓存目录(self) -> str:
        return str(self._缓存目录)

    def _刷新访问顺序(self, 键: 缓存键):
        try:
            self._访问顺序.remove(键)
        except Exception:
            pass
        self._访问顺序.append(键)

    def _写入内存缓存(self, 键: 缓存键, 图: pygame.Surface):
        self._内存缓存[键] = 图
        self._刷新访问顺序(键)
        while len(self._访问顺序) > int(self._内存上限):
            最旧键 = self._访问顺序.pop(0)
            if 最旧键 == 键:
                continue
            self._内存缓存.pop(最旧键, None)

    def _取缓存文件路径(self, 键: 缓存键) -> str:
        路径, 宽, 高, 圆角, 模式 = 键
        哈希输入 = f"{路径}|{宽}|{高}|{圆角}|{模式}".encode("utf-8", errors="ignore")
        摘要 = hashlib.sha1(哈希输入).hexdigest()
        return os.path.join(self._缓存目录, 摘要[:2], f"{摘要}.png")

    def _缓存文件有效(self, 缓存文件路径: str, 源路径: str) -> bool:
        if not 缓存文件路径 or (not os.path.isfile(缓存文件路径)):
            return False
        if not 源路径 or (not os.path.isfile(源路径)):
            return True
        try:
            return float(os.path.getmtime(缓存文件路径)) >= float(os.path.getmtime(源路径))
        except Exception:
            return True

    def _读取磁盘缓存(self, 缓存文件路径: str) -> Optional[pygame.Surface]:
        try:
            图 = pygame.image.load(缓存文件路径)
        except Exception:
            return None
        try:
            return 图.convert_alpha()
        except Exception:
            return 图

    def _写入磁盘缓存(self, 键: 缓存键, 图: pygame.Surface):
        缓存文件路径 = self._取缓存文件路径(键)
        临时文件路径 = 缓存文件路径 + ".tmp.png"
        try:
            os.makedirs(os.path.dirname(缓存文件路径), exist_ok=True)
        except Exception:
            return

        try:
            pygame.image.save(图, 临时文件路径)
            os.replace(临时文件路径, 缓存文件路径)
        except Exception:
            try:
                if os.path.isfile(临时文件路径):
                    os.remove(临时文件路径)
            except Exception:
                pass
