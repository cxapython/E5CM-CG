import os
import re
from typing import Dict, Any, List, Optional

import pygame

# =========================
# 设置页布局常量（实际值固化）
# =========================

设置页_面板宽占比 = 0.88
设置页_面板高占比 = 0.78
设置页_面板整体缩放 = 1.0
设置页_面板_x偏移 = 0
设置页_面板_y偏移 = 0

# 左侧“设置列表”大组
设置页_左区_x占比 = 0.14924242424242423
设置页_左区_y占比 = 0.10846953937592868
设置页_左区_宽占比 = 0.1315390346452523
设置页_左区_行高占比 = 0.06712049972167135
设置页_左区_行间距像素 = 22

# 每一行单独微调
设置页_左区_行偏移覆盖 = {
    "调速": (8, 0),
    "变速": (-33, -1),
    "变速类型": (-52, -4),
    "隐藏": (-56, -9),
    "轨迹": (-54, -11),
    "方向": (-37, -15),
    "大小": (-19, -18),
}

# 右侧“背景选择”大组
设置页_右区_x占比 = 0.32089994079336887
设置页_右区_y占比 = 0.0
设置页_右区_宽占比 = 0.6111426879810539
设置页_右区_高占比 = 0.6
设置页_右区_额外偏移 = (0, 0)

# 右侧预览图边距 / 预览框 / 大箭头
设置页_右区_预览内边距 = 20
设置页_右区_预览框_偏移 = (-10, 118)
设置页_右区_预览框_宽缩放 = 0.88
设置页_右区_预览框_高缩放 = 0.9
设置页_右区_左大箭头_偏移 = (25, 85)
设置页_右区_右大箭头_偏移 = (8, 146)
设置页_右区_左大箭头_缩放 = 1.0
设置页_右区_右大箭头_缩放 = 1.0

# 左下箭头预览框
设置页_箭头预览_x占比 = 0.2030787448194198
设置页_箭头预览_y占比 = 0.7458703939008895
设置页_箭头预览_宽占比 = 0.07282415630550622
设置页_箭头预览_高占比 = 0.13595933926302414
设置页_箭头预览_额外偏移 = (0, 0)
设置页_箭头预览_内边距 = 0


# def 计算设置页布局(屏幕宽: int, 屏幕高: int) -> Dict[str, Any]:
#     try:
#         屏幕宽 = int(屏幕宽)
#     except Exception:
#         屏幕宽 = 1280

#     try:
#         屏幕高 = int(屏幕高)
#     except Exception:
#         屏幕高 = 720

#     屏幕宽 = max(320, 屏幕宽)
#     屏幕高 = max(240, 屏幕高)

#     面板宽 = int(屏幕宽 * float(设置页_面板宽占比) * float(设置页_面板整体缩放))
#     面板高 = int(屏幕高 * float(设置页_面板高占比) * float(设置页_面板整体缩放))

#     面板宽 = max(700, min(面板宽, 屏幕宽 - 40))
#     面板高 = max(420, min(面板高, 屏幕高 - 40))

#     中心x = 屏幕宽 // 2 + int(设置页_面板_x偏移)
#     中心y = 屏幕高 // 2 + int(设置页_面板_y偏移)

#     面板基础矩形 = pygame.Rect(0, 0, 面板宽, 面板高)
#     面板基础矩形.center = (中心x, 中心y)

#     局部面板 = pygame.Rect(0, 0, 面板宽, 面板高)

#     # 左侧列表区域
#     左起x = int(局部面板.w * float(设置页_左区_x占比))
#     左起y = int(局部面板.h * float(设置页_左区_y占比))
#     左宽 = int(局部面板.w * float(设置页_左区_宽占比))
#     行高 = max(32, int(局部面板.h * float(设置页_左区_行高占比)))
#     行间距 = int(设置页_左区_行间距像素)

#     行矩形表: Dict[str, pygame.Rect] = {}
#     当前y = 左起y
#     for 行键 in list(设置菜单行键列表()):
#         dx, dy = 设置页_左区_行偏移覆盖.get(行键, (0, 0))
#         行矩形 = pygame.Rect(左起x + int(dx), 当前y + int(dy), 左宽, 行高)
#         行矩形表[行键] = 行矩形
#         当前y += 行高 + 行间距

#     控件矩形表: Dict[str, Dict[str, pygame.Rect]] = {}
#     for 行键, 行矩形 in 行矩形表.items():
#         小箭边长 = max(18, int(行矩形.h * 0.68))
#         左箭 = pygame.Rect(
#             行矩形.x,
#             行矩形.centery - 小箭边长 // 2,
#             小箭边长,
#             小箭边长,
#         )
#         右箭 = pygame.Rect(
#             行矩形.right - 小箭边长,
#             行矩形.centery - 小箭边长 // 2,
#             小箭边长,
#             小箭边长,
#         )
#         内容 = pygame.Rect(
#             左箭.right + 8,
#             行矩形.y,
#             行矩形.w - 小箭边长 * 2 - 16,
#             行矩形.h,
#         )
#         控件矩形表[行键] = {
#             "左": 左箭,
#             "右": 右箭,
#             "内容": 内容,
#         }

#     # 左下箭头预览框
#     try:
#         箭头预览宽 = max(60, int(局部面板.w * float(设置页_箭头预览_宽占比)))
#         箭头预览高 = max(60, int(局部面板.h * float(设置页_箭头预览_高占比)))
#         箭头预览x = int(局部面板.w * float(设置页_箭头预览_x占比)) + int(
#             设置页_箭头预览_额外偏移[0]
#         )
#         箭头预览y = int(局部面板.h * float(设置页_箭头预览_y占比)) + int(
#             设置页_箭头预览_额外偏移[1]
#         )

#         列表底 = max([矩形.bottom for 矩形 in 行矩形表.values()] + [0])
#         箭头预览y = max(箭头预览y, 列表底 + max(6, int(局部面板.h * 0.01)))

#         箭头预览矩形 = pygame.Rect(
#             箭头预览x,
#             箭头预览y,
#             箭头预览宽,
#             箭头预览高,
#         ).clip(局部面板.inflate(-10, -10))

#         if 箭头预览矩形.w < 30 or 箭头预览矩形.h < 30:
#             箭头预览矩形 = pygame.Rect(
#                 箭头预览x,
#                 箭头预览y,
#                 max(30, 箭头预览宽),
#                 max(30, 箭头预览高),
#             ).clip(局部面板.inflate(-10, -10))
#     except Exception:
#         箭头预览矩形 = pygame.Rect(0, 0, 10, 10)

#     try:
#         预览框 = 箭头预览矩形
#         箭边长 = max(34, int(预览框.h * 0.62))
#         箭边长 = min(箭边长, max(34, int(预览框.w * 0.45)))
#         间距 = max(8, int(箭边长 * 0.18))

#         左箭x = 预览框.x - 间距 - 箭边长
#         右箭x = 预览框.right + 间距

#         if 左箭x < 0:
#             左箭x = 预览框.x + 6
#         if (右箭x + 箭边长) > 局部面板.w:
#             右箭x = max(0, 预览框.right - 箭边长 - 6)

#         箭头预览左箭 = pygame.Rect(
#             左箭x,
#             预览框.centery - 箭边长 // 2,
#             箭边长,
#             箭边长,
#         )
#         箭头预览右箭 = pygame.Rect(
#             右箭x,
#             预览框.centery - 箭边长 // 2,
#             箭边长,
#             箭边长,
#         )

#         箭头预览左箭 = 箭头预览左箭.clip(局部面板.inflate(-2, -2))
#         箭头预览右箭 = 箭头预览右箭.clip(局部面板.inflate(-2, -2))

#         if 箭头预览左箭.w < 10 or 箭头预览左箭.h < 10:
#             箭头预览左箭 = pygame.Rect(
#                 预览框.x + 6,
#                 预览框.centery - 18,
#                 36,
#                 36,
#             ).clip(局部面板.inflate(-2, -2))

#         if 箭头预览右箭.w < 10 or 箭头预览右箭.h < 10:
#             箭头预览右箭 = pygame.Rect(
#                 预览框.right - 42,
#                 预览框.centery - 18,
#                 36,
#                 36,
#             ).clip(局部面板.inflate(-2, -2))

#         箭头预览控件矩形 = {
#             "左": 箭头预览左箭,
#             "右": 箭头预览右箭,
#         }
#     except Exception:
#         箭头预览控件矩形 = {
#             "左": pygame.Rect(0, 0, 1, 1),
#             "右": pygame.Rect(0, 0, 1, 1),
#         }

#     # 右侧背景区域
#     右起x = int(局部面板.w * float(设置页_右区_x占比)) + int(设置页_右区_额外偏移[0])
#     右起y = int(局部面板.h * float(设置页_右区_y占比)) + int(设置页_右区_额外偏移[1])
#     右宽 = int(局部面板.w * float(设置页_右区_宽占比))
#     右高 = int(局部面板.h * float(设置页_右区_高占比))
#     背景区矩形 = pygame.Rect(右起x, 右起y, 右宽, 右高)

#     大箭边长基准 = max(26, int(背景区矩形.h * 0.18))
#     左箭缩放 = float(max(0.3, min(3.0, float(设置页_右区_左大箭头_缩放))))
#     右箭缩放 = float(max(0.3, min(3.0, float(设置页_右区_右大箭头_缩放))))
#     左箭边长 = max(16, int(round(float(大箭边长基准) * 左箭缩放)))
#     右箭边长 = max(16, int(round(float(大箭边长基准) * 右箭缩放)))

#     背景左大箭 = pygame.Rect(
#         int(背景区矩形.x + int(设置页_右区_左大箭头_偏移[0])),
#         int(背景区矩形.centery - 左箭边长 // 2 + int(设置页_右区_左大箭头_偏移[1])),
#         int(左箭边长),
#         int(左箭边长),
#     )
#     背景右大箭 = pygame.Rect(
#         int(背景区矩形.right - 右箭边长 + int(设置页_右区_右大箭头_偏移[0])),
#         int(背景区矩形.centery - 右箭边长 // 2 + int(设置页_右区_右大箭头_偏移[1])),
#         int(右箭边长),
#         int(右箭边长),
#     )

#     内边距 = int(设置页_右区_预览内边距)
#     预览基准区 = pygame.Rect(
#         int(背景左大箭.right + 10),
#         int(背景区矩形.y + 内边距),
#         int(max(10, 背景区矩形.w - 背景左大箭.w - 背景右大箭.w - 20)),
#         int(max(10, 背景区矩形.h - 内边距 * 2)),
#     )

#     预览宽缩放 = float(max(0.2, min(3.0, float(设置页_右区_预览框_宽缩放))))
#     预览高缩放 = float(max(0.2, min(3.0, float(设置页_右区_预览框_高缩放))))
#     背景预览矩形 = pygame.Rect(
#         0,
#         0,
#         int(max(10, round(float(预览基准区.w) * 预览宽缩放))),
#         int(max(10, round(float(预览基准区.h) * 预览高缩放))),
#     )
#     背景预览矩形.center = (
#         int(预览基准区.centerx + int(设置页_右区_预览框_偏移[0])),
#         int(预览基准区.centery + int(设置页_右区_预览框_偏移[1])),
#     )

#     背景控件矩形 = {
#         "左": 背景左大箭,
#         "右": 背景右大箭,
#         "预览": 背景预览矩形,
#     }

#     return {
#         "面板基础矩形": 面板基础矩形,
#         "行矩形表": 行矩形表,
#         "控件矩形表": 控件矩形表,
#         "背景区矩形": 背景区矩形,
#         "背景控件矩形": 背景控件矩形,
#         "箭头预览矩形": 箭头预览矩形,
#         "箭头预览控件矩形": 箭头预览控件矩形,
#     }


def 计算设置页布局(屏幕宽: int, 屏幕高: int) -> Dict[str, Any]:
    try:
        屏幕宽 = int(屏幕宽)
    except Exception:
        屏幕宽 = 1280

    try:
        屏幕高 = int(屏幕高)
    except Exception:
        屏幕高 = 720

    屏幕宽 = max(320, 屏幕宽)
    屏幕高 = max(240, 屏幕高)

    # 以你当前调好的测试窗口 1400x860 作为设置页布局基准
    基准屏宽 = 1400
    基准屏高 = 860
    布局缩放 = min(float(屏幕宽) / float(基准屏宽), float(屏幕高) / float(基准屏高))
    布局缩放 = max(0.68, min(1.15, 布局缩放))

    def _缩放像素(值: int, 最小值: int | None = None, 最大值: int | None = None) -> int:
        try:
            新值 = int(round(float(值) * float(布局缩放)))
        except Exception:
            新值 = int(值)
        if 最小值 is not None:
            新值 = max(int(最小值), 新值)
        if 最大值 is not None:
            新值 = min(int(最大值), 新值)
        return 新值

    def _缩放点(点值) -> tuple[int, int]:
        try:
            return (
                _缩放像素(int(点值[0])),
                _缩放像素(int(点值[1])),
            )
        except Exception:
            return (0, 0)

    def _缩放行偏移覆盖(原表: Dict[str, tuple[int, int]]) -> Dict[str, tuple[int, int]]:
        新表: Dict[str, tuple[int, int]] = {}
        for 行键, 偏移 in dict(原表 or {}).items():
            新表[str(行键)] = _缩放点(偏移)
        return 新表

    面板宽 = int(屏幕宽 * float(设置页_面板宽占比) * float(设置页_面板整体缩放))
    面板高 = int(屏幕高 * float(设置页_面板高占比) * float(设置页_面板整体缩放))

    # 小屏时允许更小，别卡死 700/420
    最小面板宽 = _缩放像素(700, 最小值=460)
    最小面板高 = _缩放像素(420, 最小值=300)
    边缘留白 = _缩放像素(40, 最小值=20)

    面板宽 = max(最小面板宽, min(面板宽, 屏幕宽 - 边缘留白))
    面板高 = max(最小面板高, min(面板高, 屏幕高 - 边缘留白))

    中心x = 屏幕宽 // 2 + _缩放像素(int(设置页_面板_x偏移))
    中心y = 屏幕高 // 2 + _缩放像素(int(设置页_面板_y偏移))

    面板基础矩形 = pygame.Rect(0, 0, 面板宽, 面板高)
    面板基础矩形.center = (中心x, 中心y)

    局部面板 = pygame.Rect(0, 0, 面板宽, 面板高)

    # 左侧列表区域
    左起x = int(局部面板.w * float(设置页_左区_x占比))
    左起y = int(局部面板.h * float(设置页_左区_y占比))
    左宽 = int(局部面板.w * float(设置页_左区_宽占比))
    行高 = max(_缩放像素(32, 最小值=24), int(局部面板.h * float(设置页_左区_行高占比)))
    行间距 = _缩放像素(int(设置页_左区_行间距像素), 最小值=8)

    行偏移覆盖 = _缩放行偏移覆盖(设置页_左区_行偏移覆盖)

    行矩形表: Dict[str, pygame.Rect] = {}
    当前y = 左起y
    for 行键 in list(设置菜单行键列表()):
        dx, dy = 行偏移覆盖.get(行键, (0, 0))
        行矩形 = pygame.Rect(左起x + int(dx), 当前y + int(dy), 左宽, 行高)
        行矩形表[行键] = 行矩形
        当前y += 行高 + 行间距

    控件矩形表: Dict[str, Dict[str, pygame.Rect]] = {}
    左右内容间距 = _缩放像素(8, 最小值=4)
    for 行键, 行矩形 in 行矩形表.items():
        小箭边长 = max(_缩放像素(18, 最小值=14), int(行矩形.h * 0.68))
        左箭 = pygame.Rect(
            行矩形.x,
            行矩形.centery - 小箭边长 // 2,
            小箭边长,
            小箭边长,
        )
        右箭 = pygame.Rect(
            行矩形.right - 小箭边长,
            行矩形.centery - 小箭边长 // 2,
            小箭边长,
            小箭边长,
        )
        内容 = pygame.Rect(
            左箭.right + 左右内容间距,
            行矩形.y,
            行矩形.w - 小箭边长 * 2 - 左右内容间距 * 2,
            行矩形.h,
        )
        控件矩形表[行键] = {
            "左": 左箭,
            "右": 右箭,
            "内容": 内容,
        }

    # 左下箭头预览框
    try:
        箭头预览宽 = max(
            _缩放像素(60, 最小值=42), int(局部面板.w * float(设置页_箭头预览_宽占比))
        )
        箭头预览高 = max(
            _缩放像素(60, 最小值=42), int(局部面板.h * float(设置页_箭头预览_高占比))
        )
        箭头预览额外偏移 = _缩放点(设置页_箭头预览_额外偏移)
        箭头预览x = int(局部面板.w * float(设置页_箭头预览_x占比)) + int(
            箭头预览额外偏移[0]
        )
        箭头预览y = int(局部面板.h * float(设置页_箭头预览_y占比)) + int(
            箭头预览额外偏移[1]
        )

        列表底 = max([矩形.bottom for 矩形 in 行矩形表.values()] + [0])
        箭头预览y = max(
            箭头预览y, 列表底 + max(_缩放像素(6, 最小值=4), int(局部面板.h * 0.01))
        )

        箭头预览矩形 = pygame.Rect(
            箭头预览x,
            箭头预览y,
            箭头预览宽,
            箭头预览高,
        ).clip(局部面板.inflate(-_缩放像素(10, 最小值=6), -_缩放像素(10, 最小值=6)))

        if 箭头预览矩形.w < 24 or 箭头预览矩形.h < 24:
            箭头预览矩形 = pygame.Rect(
                箭头预览x,
                箭头预览y,
                max(_缩放像素(30, 最小值=24), 箭头预览宽),
                max(_缩放像素(30, 最小值=24), 箭头预览高),
            ).clip(局部面板.inflate(-_缩放像素(10, 最小值=6), -_缩放像素(10, 最小值=6)))
    except Exception:
        箭头预览矩形 = pygame.Rect(0, 0, 10, 10)

    try:
        预览框 = 箭头预览矩形
        箭边长 = max(_缩放像素(34, 最小值=22), int(预览框.h * 0.62))
        箭边长 = min(箭边长, max(_缩放像素(34, 最小值=22), int(预览框.w * 0.45)))
        间距 = max(_缩放像素(8, 最小值=4), int(箭边长 * 0.18))

        左箭x = 预览框.x - 间距 - 箭边长
        右箭x = 预览框.right + 间距

        if 左箭x < 0:
            左箭x = 预览框.x + _缩放像素(6, 最小值=4)
        if (右箭x + 箭边长) > 局部面板.w:
            右箭x = max(0, 预览框.right - 箭边长 - _缩放像素(6, 最小值=4))

        箭头预览左箭 = pygame.Rect(
            左箭x,
            预览框.centery - 箭边长 // 2,
            箭边长,
            箭边长,
        )
        箭头预览右箭 = pygame.Rect(
            右箭x,
            预览框.centery - 箭边长 // 2,
            箭边长,
            箭边长,
        )

        箭头预览左箭 = 箭头预览左箭.clip(
            局部面板.inflate(-_缩放像素(2, 最小值=1), -_缩放像素(2, 最小值=1))
        )
        箭头预览右箭 = 箭头预览右箭.clip(
            局部面板.inflate(-_缩放像素(2, 最小值=1), -_缩放像素(2, 最小值=1))
        )

        if 箭头预览左箭.w < 10 or 箭头预览左箭.h < 10:
            箭头预览左箭 = pygame.Rect(
                预览框.x + _缩放像素(6, 最小值=4),
                预览框.centery - _缩放像素(18, 最小值=12),
                _缩放像素(36, 最小值=24),
                _缩放像素(36, 最小值=24),
            ).clip(局部面板.inflate(-_缩放像素(2, 最小值=1), -_缩放像素(2, 最小值=1)))

        if 箭头预览右箭.w < 10 or 箭头预览右箭.h < 10:
            箭头预览右箭 = pygame.Rect(
                预览框.right - _缩放像素(42, 最小值=28),
                预览框.centery - _缩放像素(18, 最小值=12),
                _缩放像素(36, 最小值=24),
                _缩放像素(36, 最小值=24),
            ).clip(局部面板.inflate(-_缩放像素(2, 最小值=1), -_缩放像素(2, 最小值=1)))

        箭头预览控件矩形 = {
            "左": 箭头预览左箭,
            "右": 箭头预览右箭,
        }
    except Exception:
        箭头预览控件矩形 = {
            "左": pygame.Rect(0, 0, 1, 1),
            "右": pygame.Rect(0, 0, 1, 1),
        }

    # 右侧背景区域
    右区额外偏移 = _缩放点(设置页_右区_额外偏移)
    右起x = int(局部面板.w * float(设置页_右区_x占比)) + int(右区额外偏移[0])
    右起y = int(局部面板.h * float(设置页_右区_y占比)) + int(右区额外偏移[1])
    右宽 = int(局部面板.w * float(设置页_右区_宽占比))
    右高 = int(局部面板.h * float(设置页_右区_高占比))
    背景区矩形 = pygame.Rect(右起x, 右起y, 右宽, 右高)

    大箭边长基准 = max(_缩放像素(26, 最小值=18), int(背景区矩形.h * 0.18))
    左箭缩放 = float(max(0.3, min(3.0, float(设置页_右区_左大箭头_缩放))))
    右箭缩放 = float(max(0.3, min(3.0, float(设置页_右区_右大箭头_缩放))))
    左箭边长 = max(_缩放像素(16, 最小值=12), int(round(float(大箭边长基准) * 左箭缩放)))
    右箭边长 = max(_缩放像素(16, 最小值=12), int(round(float(大箭边长基准) * 右箭缩放)))

    左大箭头偏移 = _缩放点(设置页_右区_左大箭头_偏移)
    右大箭头偏移 = _缩放点(设置页_右区_右大箭头_偏移)

    背景左大箭 = pygame.Rect(
        int(背景区矩形.x + int(左大箭头偏移[0])),
        int(背景区矩形.centery - 左箭边长 // 2 + int(左大箭头偏移[1])),
        int(左箭边长),
        int(左箭边长),
    )
    背景右大箭 = pygame.Rect(
        int(背景区矩形.right - 右箭边长 + int(右大箭头偏移[0])),
        int(背景区矩形.centery - 右箭边长 // 2 + int(右大箭头偏移[1])),
        int(右箭边长),
        int(右箭边长),
    )

    内边距 = _缩放像素(int(设置页_右区_预览内边距), 最小值=8)
    预览基准区 = pygame.Rect(
        int(背景左大箭.right + _缩放像素(10, 最小值=6)),
        int(背景区矩形.y + 内边距),
        int(
            max(
                10,
                背景区矩形.w - 背景左大箭.w - 背景右大箭.w - _缩放像素(20, 最小值=12),
            )
        ),
        int(max(10, 背景区矩形.h - 内边距 * 2)),
    )

    预览宽缩放 = float(max(0.2, min(3.0, float(设置页_右区_预览框_宽缩放))))
    预览高缩放 = float(max(0.2, min(3.0, float(设置页_右区_预览框_高缩放))))
    背景预览矩形 = pygame.Rect(
        0,
        0,
        int(max(10, round(float(预览基准区.w) * 预览宽缩放))),
        int(max(10, round(float(预览基准区.h) * 预览高缩放))),
    )

    预览框偏移 = _缩放点(设置页_右区_预览框_偏移)
    背景预览矩形.center = (
        int(预览基准区.centerx + int(预览框偏移[0])),
        int(预览基准区.centery + int(预览框偏移[1])),
    )

    背景控件矩形 = {
        "左": 背景左大箭,
        "右": 背景右大箭,
        "预览": 背景预览矩形,
    }

    return {
        "布局缩放": float(布局缩放),
        "面板基础矩形": 面板基础矩形,
        "行矩形表": 行矩形表,
        "控件矩形表": 控件矩形表,
        "背景区矩形": 背景区矩形,
        "背景控件矩形": 背景控件矩形,
        "箭头预览矩形": 箭头预览矩形,
        "箭头预览控件矩形": 箭头预览控件矩形,
    }


def 设置菜单行键列表() -> List[str]:
    """
    选歌设置菜单左侧可调行（保留旧布局顺序，兼容旧 json 偏移）。
    """
    return ["调速", "变速", "变速类型", "隐藏", "轨迹", "方向", "大小"]


def 设置菜单默认调速选项() -> List[str]:
    # 固定档位：3.0 ~ 7.0（步进 0.5）
    return ["3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0", "6.5", "7.0"]


def 设置菜单行显示名(行键: str) -> str:
    键 = str(行键 or "")
    if 键 == "变速":
        return "背景"
    if 键 == "变速类型":
        return "谱面"
    return 键


def 设置菜单行值(
    行键: str,
    设置参数: Optional[Dict[str, str]] = None,
) -> str:
    参数 = dict(设置参数 or {})
    键 = str(行键 or "")
    if 键 == "变速":
        return str(参数.get("背景模式", "图片") or "图片")
    if 键 == "变速类型":
        return str(参数.get("谱面", "正常") or "正常")
    if 键 == "隐藏":
        return str(参数.get("隐藏", "关闭") or "关闭")
    if 键 == "轨迹":
        return str(参数.get("轨迹", "正常") or "正常")
    if 键 == "方向":
        return str(参数.get("方向", "关闭") or "关闭")
    if 键 == "大小":
        return str(参数.get("大小", "正常") or "正常")
    if 键 == "调速":
        return str(参数.get("调速", "X4.0") or "X4.0")
    return ""


def 设置参数文本提取值(参数文本: str, 键名: str) -> str:
    try:
        文本 = str(参数文本 or "")
        m = re.search(rf"{re.escape(str(键名))}\s*=\s*([^\s]+)", 文本)
        if not m:
            return ""
        return str(m.group(1)).strip()
    except Exception:
        return ""


def 构建设置参数文本(
    设置参数: Optional[Dict[str, object]] = None,
    背景文件名: str = "",
    箭头文件名: str = "",
) -> str:
    参数 = dict(设置参数 or {})
    参数片段: List[str] = []
    顺序键 = ["调速", "背景模式", "谱面", "隐藏", "轨迹", "方向", "大小"]
    if ("背景模式" not in 参数) and ("变速" in 参数):
        参数["背景模式"] = 参数.get("变速")

    try:
        for 键 in 顺序键:
            if 键 in 参数:
                参数片段.append(f"{键}={参数.get(键)}")
        for 键, 值 in 参数.items():
            if 键 in 顺序键:
                continue
            参数片段.append(f"{键}={值}")
    except Exception:
        参数片段 = []

    if 背景文件名:
        参数片段.append(f"背景={背景文件名}")
    if 箭头文件名:
        参数片段.append(f"箭头={箭头文件名}")
    return "设置参数：" + ("  ".join(参数片段) if 参数片段 else "默认")


def 取非透明裁切矩形(图: pygame.Surface) -> pygame.Rect:
    """
    返回图像 alpha>0 的最小包围盒；若无 alpha 或找不到，则返回整图。
    """
    try:
        w, h = 图.get_size()
    except Exception:
        return pygame.Rect(0, 0, 1, 1)
    if w <= 0 or h <= 0:
        return pygame.Rect(0, 0, 1, 1)

    try:
        mask = pygame.mask.from_surface(图, threshold=1)
        bbox = mask.get_bounding_rects()
        if bbox:
            # 合并所有 rect，避免多块分离导致裁切不全
            out = bbox[0].copy()
            for r in bbox[1:]:
                out = out.union(r)
            if out.w > 0 and out.h > 0:
                return out
    except Exception:
        pass
    return pygame.Rect(0, 0, int(w), int(h))


def 绘制_cover裁切预览(
    目标面: pygame.Surface,
    原图: Optional[pygame.Surface],
    目标区域: pygame.Rect,
) -> bool:
    """
    在目标区域内按 cover 方式绘制并裁切，保证超出部分不外溢。
    """
    if 原图 is None or (not isinstance(目标区域, pygame.Rect)):
        return False
    if 目标区域.w <= 0 or 目标区域.h <= 0:
        return False

    try:
        裁切源 = 取非透明裁切矩形(原图)
        ow, oh = int(裁切源.w), int(裁切源.h)
    except Exception:
        return False
    if ow <= 0 or oh <= 0:
        return False

    比例 = max(float(目标区域.w) / float(ow), float(目标区域.h) / float(oh))
    nw = max(1, int(round(float(ow) * 比例)))
    nh = max(1, int(round(float(oh) * 比例)))

    try:
        源图 = 原图.subsurface(裁切源).copy().convert_alpha()
        图 = pygame.transform.smoothscale(源图, (nw, nh)).convert_alpha()
    except Exception:
        try:
            源图 = 原图.subsurface(裁切源).copy().convert_alpha()
            图 = pygame.transform.scale(源图, (nw, nh)).convert_alpha()
        except Exception:
            return False

    src_x = max(0, (nw - 目标区域.w) // 2)
    src_y = max(0, (nh - 目标区域.h) // 2)
    src = pygame.Rect(src_x, src_y, int(目标区域.w), int(目标区域.h))
    src = src.clip(pygame.Rect(0, 0, nw, nh))

    try:
        目标面.blit(图, 目标区域.topleft, area=src)
        return True
    except Exception:
        return False
