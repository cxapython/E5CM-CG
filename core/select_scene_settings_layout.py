import json
import os
import re
from typing import Callable, Dict, List, Optional, Tuple

import pygame

from core.select_speed_settings import format_select_scroll_speed, get_select_scroll_speed_options


def get_select_menu_row_keys() -> List[str]:
    return ["调速", "变速", "变速类型", "隐藏", "轨迹", "方向", "大小"]


def get_default_select_menu_speed_options() -> List[str]:
    return get_select_scroll_speed_options()


def get_select_menu_row_label(row_key: str) -> str:
    key = str(row_key or "")
    if key == "变速":
        return "背景"
    if key == "变速类型":
        return "谱面"
    return key


def get_select_menu_row_value(
    row_key: str,
    settings_params: Optional[Dict[str, str]] = None,
) -> str:
    params = dict(settings_params or {})
    key = str(row_key or "")
    if key == "变速":
        value = str(params.get("背景模式", params.get("变速", "图片")) or "图片").strip()
        if value == "视频":
            return "视频"
        if value == "动态背景":
            return "动态背景"
        return "图片"
    if key == "变速类型":
        return str(params.get("谱面", "正常") or "正常")
    if key == "隐藏":
        return str(params.get("隐藏", "关闭") or "关闭")
    if key == "轨迹":
        return str(params.get("轨迹", "正常") or "正常")
    if key == "方向":
        return str(params.get("方向", "关闭") or "关闭")
    if key == "大小":
        return str(params.get("大小", "正常") or "正常")
    if key == "调速":
        return format_select_scroll_speed(params.get("调速", ""), prefix="X")
    return ""


def extract_select_settings_param_value(param_text: str, key_name: str) -> str:
    try:
        text = str(param_text or "")
        match = re.search(rf"{re.escape(str(key_name))}\s*=\s*([^\s]+)", text)
        if not match:
            return ""
        return str(match.group(1)).strip()
    except Exception:
        return ""


def build_select_settings_param_text(
    settings_params: Optional[Dict[str, object]] = None,
    background_filename: str = "",
    arrow_filename: str = "",
) -> str:
    params = dict(settings_params or {})
    parts: List[str] = []
    ordered_keys = ["调速", "背景模式", "谱面", "隐藏", "轨迹", "方向", "大小"]
    if ("背景模式" not in params) and ("变速" in params):
        params["背景模式"] = params.get("变速")

    try:
        for key in ordered_keys:
            if key in params:
                parts.append(f"{key}={params.get(key)}")
        for key, value in params.items():
            if key in ordered_keys:
                continue
            parts.append(f"{key}={value}")
    except Exception:
        parts = []

    if background_filename:
        parts.append(f"背景={background_filename}")
    if arrow_filename:
        parts.append(f"箭头={arrow_filename}")
    return "设置参数：" + ("  ".join(parts) if parts else "默认")


def get_nontransparent_crop_rect(image: pygame.Surface) -> pygame.Rect:
    try:
        width, height = image.get_size()
    except Exception:
        return pygame.Rect(0, 0, 1, 1)
    if width <= 0 or height <= 0:
        return pygame.Rect(0, 0, 1, 1)

    try:
        mask = pygame.mask.from_surface(image, threshold=1)
        boxes = mask.get_bounding_rects()
        if boxes:
            merged = boxes[0].copy()
            for rect in boxes[1:]:
                merged = merged.union(rect)
            if merged.w > 0 and merged.h > 0:
                return merged
    except Exception:
        pass
    return pygame.Rect(0, 0, int(width), int(height))


def draw_cover_crop_preview(
    target_surface: pygame.Surface,
    source_image: Optional[pygame.Surface],
    target_rect: pygame.Rect,
) -> bool:
    if source_image is None or (not isinstance(target_rect, pygame.Rect)):
        return False
    if target_rect.w <= 0 or target_rect.h <= 0:
        return False

    try:
        crop_rect = get_nontransparent_crop_rect(source_image)
        original_width = int(crop_rect.w)
        original_height = int(crop_rect.h)
    except Exception:
        return False
    if original_width <= 0 or original_height <= 0:
        return False

    scale_ratio = max(
        float(target_rect.w) / float(original_width),
        float(target_rect.h) / float(original_height),
    )
    scaled_width = max(1, int(round(float(original_width) * scale_ratio)))
    scaled_height = max(1, int(round(float(original_height) * scale_ratio)))

    try:
        source = source_image.subsurface(crop_rect).copy().convert_alpha()
        scaled = pygame.transform.smoothscale(source, (scaled_width, scaled_height)).convert_alpha()
    except Exception:
        try:
            source = source_image.subsurface(crop_rect).copy().convert_alpha()
            scaled = pygame.transform.scale(source, (scaled_width, scaled_height)).convert_alpha()
        except Exception:
            return False

    src_x = max(0, (scaled_width - target_rect.w) // 2)
    src_y = max(0, (scaled_height - target_rect.h) // 2)
    src_rect = pygame.Rect(src_x, src_y, int(target_rect.w), int(target_rect.h))
    src_rect = src_rect.clip(pygame.Rect(0, 0, scaled_width, scaled_height))

    try:
        target_surface.blit(scaled, target_rect.topleft, area=src_rect)
        return True
    except Exception:
        return False


class SettingsLayoutDebugger:
    def __init__(self, save_path: str, get_font: Callable):
        self.save_path = str(save_path or "")
        self._get_font = get_font
        self.enabled = False
        self.selected_key: str = ""
        self.hover_key: str = ""
        self.dragging = False
        self.drag_start_local = (0, 0)
        self.drag_start_rect = pygame.Rect(0, 0, 0, 0)
        self.current_rects: Dict[str, pygame.Rect] = {}
        self.override_data: Dict[str, dict] = {}
        self.text_scale_data: Dict[str, float] = {}
        self._load_saved_data()

    @property
    def 是否启用(self) -> bool:
        return bool(self.enabled)

    def 切换启用(self):
        self.enabled = not bool(self.enabled)
        self.dragging = False
        self.hover_key = ""

    def _load_saved_data(self):
        if (not self.save_path) or (not os.path.isfile(self.save_path)):
            self.override_data = {}
            self.text_scale_data = {}
            return
        for encoding in ("utf-8-sig", "utf-8", "gbk"):
            try:
                with open(self.save_path, "r", encoding=encoding) as file:
                    data = json.load(file)
                if isinstance(data, dict):
                    components = data.get("组件", {})
                    text_scale = data.get("文字缩放", {})
                    self.override_data = dict(components) if isinstance(components, dict) else {}
                    self.text_scale_data = dict(text_scale) if isinstance(text_scale, dict) else {}
                    return
            except Exception:
                continue
        self.override_data = {}
        self.text_scale_data = {}

    def 保存到文件(self, panel_width: int, panel_height: int) -> bool:
        try:
            panel_width = max(1, int(panel_width))
            panel_height = max(1, int(panel_height))
        except Exception:
            return False

        output: Dict[str, dict] = {}
        for key_name, rect in self.current_rects.items():
            if not isinstance(rect, pygame.Rect):
                continue
            output[str(key_name)] = {
                "x": float(rect.x) / float(panel_width),
                "y": float(rect.y) / float(panel_height),
                "w": float(rect.w) / float(panel_width),
                "h": float(rect.h) / float(panel_height),
            }

        data = {
            "版本": 2,
            "基准": "设置背景图.png",
            "组件": output,
            "文字缩放": dict(self.text_scale_data or {}),
        }

        try:
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            with open(self.save_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            self.override_data = dict(output)
            return True
        except Exception:
            return False

    def _record_to_rect(
        self, record: dict, panel_width: int, panel_height: int
    ) -> Optional[pygame.Rect]:
        if not isinstance(record, dict):
            return None
        try:
            x = int(round(float(record.get("x", 0.0)) * float(panel_width)))
            y = int(round(float(record.get("y", 0.0)) * float(panel_height)))
            w = int(round(float(record.get("w", 0.0)) * float(panel_width)))
            h = int(round(float(record.get("h", 0.0)) * float(panel_height)))
        except Exception:
            return None
        return pygame.Rect(x, y, max(1, w), max(1, h))

    def _get_row_owner(self, component_key: str) -> str:
        key = str(component_key or "")
        if key.startswith("行:"):
            return key.split(":", 1)[1]
        if key.startswith("控件:"):
            parts = key.split(":")
            if len(parts) >= 3:
                return str(parts[1])
        return ""

    def 取行文字缩放(self, row_key: str) -> float:
        try:
            value = float((self.text_scale_data or {}).get(str(row_key or ""), 1.0) or 1.0)
        except Exception:
            value = 1.0
        return max(0.50, min(3.00, value))

    def _adjust_selected_text_scale(self, wheel_direction: int):
        if not self.selected_key:
            return
        row_key = self._get_row_owner(self.selected_key)
        if not row_key:
            return
        current_value = self.取行文字缩放(row_key)
        new_value = current_value + (0.05 if int(wheel_direction) > 0 else -0.05)
        self.text_scale_data[str(row_key)] = float(round(max(0.50, min(3.00, new_value)), 2))

    def _collect_current_components(self, host):
        components: Dict[str, pygame.Rect] = {}
        try:
            for row_key, rect in dict(getattr(host, "_设置页_行矩形表", {}) or {}).items():
                if isinstance(rect, pygame.Rect):
                    components[f"行:{row_key}"] = rect.copy()
        except Exception:
            pass

        try:
            for row_key, control_dict in dict(getattr(host, "_设置页_控件矩形表", {}) or {}).items():
                if not isinstance(control_dict, dict):
                    continue
                for sub_key in ("左", "右", "内容"):
                    rect = control_dict.get(sub_key)
                    if isinstance(rect, pygame.Rect):
                        components[f"控件:{row_key}:{sub_key}"] = rect.copy()
        except Exception:
            pass

        try:
            background_rect = getattr(host, "_设置页_背景区矩形", None)
            if isinstance(background_rect, pygame.Rect):
                components["背景区"] = background_rect.copy()
        except Exception:
            pass

        try:
            background_controls = dict(getattr(host, "_设置页_背景控件矩形", {}) or {})
            for sub_key in ("左", "右", "预览"):
                rect = background_controls.get(sub_key)
                if isinstance(rect, pygame.Rect):
                    components[f"背景控件:{sub_key}"] = rect.copy()
        except Exception:
            pass

        try:
            arrow_preview_rect = getattr(host, "_设置页_箭头预览矩形", None)
            if isinstance(arrow_preview_rect, pygame.Rect):
                components["箭头预览区"] = arrow_preview_rect.copy()
        except Exception:
            pass

        try:
            arrow_preview_controls = dict(getattr(host, "_设置页_箭头预览控件矩形", {}) or {})
            for sub_key in ("左", "右"):
                rect = arrow_preview_controls.get(sub_key)
                if isinstance(rect, pygame.Rect):
                    components[f"箭头预览控件:{sub_key}"] = rect.copy()
        except Exception:
            pass

        self.current_rects = components

    def _write_back_to_host(self, host):
        for key_name, rect in self.current_rects.items():
            if not isinstance(rect, pygame.Rect):
                continue
            if str(key_name).startswith("行:"):
                row_key = str(key_name).split(":", 1)[1]
                if row_key in getattr(host, "_设置页_行矩形表", {}):
                    host._设置页_行矩形表[row_key] = rect.copy()
                continue
            if str(key_name).startswith("控件:"):
                _, row_key, sub_key = str(key_name).split(":", 2)
                control_table = getattr(host, "_设置页_控件矩形表", {})
                if row_key in control_table and isinstance(control_table.get(row_key), dict):
                    control_table[row_key][sub_key] = rect.copy()
                continue
            if key_name == "背景区":
                host._设置页_背景区矩形 = rect.copy()
                continue
            if str(key_name).startswith("背景控件:"):
                sub_key = str(key_name).split(":", 1)[1]
                host._设置页_背景控件矩形[sub_key] = rect.copy()
                continue
            if key_name == "箭头预览区":
                host._设置页_箭头预览矩形 = rect.copy()
                continue
            if str(key_name).startswith("箭头预览控件:"):
                sub_key = str(key_name).split(":", 1)[1]
                host._设置页_箭头预览控件矩形[sub_key] = rect.copy()

    def _screen_to_panel_local(self, host, screen_point) -> Tuple[int, int]:
        panel_draw_rect = getattr(host, "_设置页_面板绘制矩形", pygame.Rect(0, 0, 1, 1))
        current_scale = max(0.001, float(getattr(host, "_设置页_最后缩放", 1.0) or 1.0))
        local_x = int((screen_point[0] - panel_draw_rect.x) / current_scale)
        local_y = int((screen_point[1] - panel_draw_rect.y) / current_scale)
        return (local_x, local_y)

    def _hit_test(self, local_point) -> str:
        candidates = []
        for key_name, rect in self.current_rects.items():
            if isinstance(rect, pygame.Rect) and rect.collidepoint(local_point):
                candidates.append((rect.w * rect.h, str(key_name)))
        if not candidates:
            return ""
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    def _move_selected_rect(self, host, dx: int, dy: int):
        if not self.selected_key or self.selected_key not in self.current_rects:
            return
        new_rect = self.current_rects[self.selected_key].copy()
        new_rect.x += int(dx)
        new_rect.y += int(dy)
        self.current_rects[self.selected_key] = _clamp_rect_to_panel(host, new_rect)
        self._write_back_to_host(host)

    def _resize_selected_rect(self, host, wheel_direction: int, adjust_width: bool, adjust_height: bool):
        if not self.selected_key or self.selected_key not in self.current_rects:
            return
        old_rect = self.current_rects[self.selected_key].copy()
        scale_factor = 1.05 if int(wheel_direction) > 0 else 0.95
        new_width = int(round(float(old_rect.w) * scale_factor))
        new_height = int(round(float(old_rect.h) * scale_factor))
        if adjust_width and (not adjust_height):
            new_height = old_rect.h
        elif adjust_height and (not adjust_width):
            new_width = old_rect.w
        new_rect = pygame.Rect(0, 0, max(8, new_width), max(8, new_height))
        new_rect.center = old_rect.center
        self.current_rects[self.selected_key] = _clamp_rect_to_panel(host, new_rect)
        self._write_back_to_host(host)

    def 应用保存覆盖(self, host):
        self._collect_current_components(host)
        try:
            panel_rect = getattr(host, "_设置页_面板基础矩形", pygame.Rect(0, 0, 1, 1))
            panel_width = max(1, int(panel_rect.w))
            panel_height = max(1, int(panel_rect.h))
        except Exception:
            panel_width = 1
            panel_height = 1
        for key_name, record in dict(self.override_data or {}).items():
            if key_name not in self.current_rects:
                continue
            new_rect = self._record_to_rect(record, panel_width, panel_height)
            if isinstance(new_rect, pygame.Rect):
                self.current_rects[key_name] = _clamp_rect_to_panel(host, new_rect)
        self._write_back_to_host(host)

    def 处理事件(self, host, event) -> bool:
        if not bool(self.enabled):
            return False
        self._collect_current_components(host)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                try:
                    panel_rect = getattr(host, "_设置页_面板基础矩形", pygame.Rect(0, 0, 1, 1))
                    save_ok = self.保存到文件(int(panel_rect.w), int(panel_rect.h))
                    if save_ok and hasattr(host, "显示消息提示"):
                        host.显示消息提示("设置页调试器：布局已保存", 持续秒=1.6)
                except Exception:
                    pass
                return True
            if event.key == pygame.K_UP:
                self._move_selected_rect(host, 0, -1)
                return True
            if event.key == pygame.K_DOWN:
                self._move_selected_rect(host, 0, 1)
                return True
            if event.key == pygame.K_LEFT:
                self._move_selected_rect(host, -1, 0)
                return True
            if event.key == pygame.K_RIGHT:
                self._move_selected_rect(host, 1, 0)
                return True
        if event.type == pygame.MOUSEMOTION:
            local_point = self._screen_to_panel_local(host, event.pos)
            self.hover_key = self._hit_test(local_point)
            if self.dragging and self.selected_key in self.current_rects:
                dx = int(local_point[0] - self.drag_start_local[0])
                dy = int(local_point[1] - self.drag_start_local[1])
                new_rect = self.drag_start_rect.copy()
                new_rect.x += dx
                new_rect.y += dy
                self.current_rects[self.selected_key] = _clamp_rect_to_panel(host, new_rect)
                self._write_back_to_host(host)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            local_point = self._screen_to_panel_local(host, event.pos)
            hit_key = self._hit_test(local_point)
            self.selected_key = str(hit_key or "")
            if self.selected_key and self.selected_key in self.current_rects:
                self.dragging = True
                self.drag_start_local = (int(local_point[0]), int(local_point[1]))
                self.drag_start_rect = self.current_rects[self.selected_key].copy()
            else:
                self.dragging = False
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            local_point = self._screen_to_panel_local(host, event.pos)
            hit_key = self._hit_test(local_point)
            if hit_key:
                self.selected_key = str(hit_key)
            if not self.selected_key:
                return True
            wheel_direction = 1 if int(event.button) == 4 else -1
            key_mods = pygame.key.get_mods()
            if bool(key_mods & pygame.KMOD_ALT):
                self._adjust_selected_text_scale(wheel_direction)
                return True
            if bool(key_mods & pygame.KMOD_CTRL):
                self._resize_selected_rect(host, wheel_direction, adjust_width=False, adjust_height=True)
            elif bool(key_mods & pygame.KMOD_SHIFT):
                self._resize_selected_rect(host, wheel_direction, adjust_width=True, adjust_height=False)
            else:
                self._resize_selected_rect(host, wheel_direction, adjust_width=True, adjust_height=True)
            return True
        return False

    def 绘制覆盖(self, host, panel_surface: pygame.Surface):
        if not bool(self.enabled):
            return
        self._collect_current_components(host)
        try:
            font = self._get_font(18, 是否粗体=True)
            small_font = self._get_font(14, 是否粗体=False)
        except Exception:
            return
        for key_name, rect in self.current_rects.items():
            if not isinstance(rect, pygame.Rect):
                continue
            if str(key_name) == str(self.selected_key):
                border_color, fill_color = (255, 120, 80, 255), (255, 120, 80, 28)
            elif str(key_name) == str(self.hover_key):
                border_color, fill_color = (80, 220, 255, 255), (80, 220, 255, 20)
            else:
                border_color, fill_color = (120, 255, 140, 170), (120, 255, 140, 10)
            try:
                fill_surface = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                fill_surface.fill(fill_color)
                panel_surface.blit(fill_surface, rect.topleft)
                pygame.draw.rect(panel_surface, border_color, rect, width=1, border_radius=2)
            except Exception:
                pass
            try:
                if str(key_name) == str(self.selected_key) or str(key_name) == str(self.hover_key):
                    label_surface = font.render(str(key_name), True, (255, 255, 255))
                    label_bg = pygame.Surface((label_surface.get_width() + 8, label_surface.get_height() + 4), pygame.SRCALPHA)
                    label_bg.fill((0, 0, 0, 150))
                    label_x = max(0, rect.x)
                    label_y = max(0, rect.y - label_bg.get_height())
                    panel_surface.blit(label_bg, (label_x, label_y))
                    panel_surface.blit(label_surface, (label_x + 4, label_y + 2))
            except Exception:
                pass
        try:
            help_text = "F6开关调试 | 拖动移动 | 滚轮等比缩放 | Ctrl+滚轮改高 | Shift+滚轮改宽 | Alt+滚轮改字 | 方向键1px微调 | Ctrl+S保存"
            help_surface = small_font.render(help_text, True, (255, 255, 255))
            help_bg = pygame.Surface((help_surface.get_width() + 12, help_surface.get_height() + 8), pygame.SRCALPHA)
            help_bg.fill((0, 0, 0, 170))
            panel_surface.blit(help_bg, (8, 8))
            panel_surface.blit(help_surface, (14, 12))
        except Exception:
            pass


def get_select_settings_layout_config() -> dict:
    return {
        "设计宽": 2048, "设计高": 1152, "布局缩放最小": 0.68, "布局缩放最大": 1.18,
        "面板宽占比": 0.82, "面板高占比": 0.76, "面板最小边距": 24,
        "面板最大宽": 1540, "面板最大高": 860, "面板最小宽": 1160, "面板最小高": 640,
        "内容左边距": 64, "内容右边距": 58, "内容上边距": 56, "内容下边距": 42,
        "左右列间距": 72, "左列宽占比": 0.34, "左列上偏移": 18, "左列行区高占比": 0.64,
        "行列表": get_select_menu_row_keys(), "行间距": 16, "行高最小": 54, "行高最大": 86,
        "行内左右边距": 8, "小箭头宽": 28, "小箭头高占行高": 0.54, "内容左右内边距": 12,
        "右列顶部预留": 6, "右列上下分区间距": 28, "右列上区高占比": 0.58,
        "背景区左右箭头宽": 60, "背景区左右箭头高": 118, "背景区箭头与预览间距": 18,
        "背景区预览上下内边距": 20, "背景区左右内边距": 12,
        "箭头预览左右箭头宽": 56, "箭头预览左右箭头高": 108, "箭头预览箭头间距": 18,
        "箭头预览上下内边距": 10, "箭头预览底部文字间距": 18,
        "箭头预览底部保护边距": 6, "箭头预览内边距": 0,
        "标签字号占行高": 0.44, "选项字号占行高": 0.48, "小字字号占行高": 0.31, "名称下移": 1,
    }


def compute_select_settings_layout(screen_width: int, screen_height: int) -> dict:
    config = get_select_settings_layout_config()
    try:
        screen_width = int(screen_width)
    except Exception:
        screen_width = 1280
    try:
        screen_height = int(screen_height)
    except Exception:
        screen_height = 720
    screen_width = max(960, screen_width)
    screen_height = max(600, screen_height)
    design_width = float(config.get("设计宽", 2048) or 2048)
    design_height = float(config.get("设计高", 1152) or 1152)
    layout_scale = min(float(screen_width) / design_width, float(screen_height) / design_height)
    layout_scale = max(
        float(config.get("布局缩放最小", 0.68) or 0.68),
        min(float(config.get("布局缩放最大", 1.18) or 1.18), float(layout_scale)),
    )

    def clamp_float(value, min_value: float, max_value: float) -> float:
        try:
            value = float(value)
        except Exception:
            value = float(min_value)
        return max(float(min_value), min(float(max_value), value))

    def clamp_int(value, min_value: int, max_value: int) -> int:
        try:
            value = int(round(float(value)))
        except Exception:
            value = int(min_value)
        return max(int(min_value), min(int(max_value), value))

    def scale_px(value) -> int:
        try:
            return int(round(float(value) * float(layout_scale)))
        except Exception:
            return 0

    def local_rect(x: int, y: int, w: int, h: int) -> pygame.Rect:
        return pygame.Rect(int(x), int(y), max(1, int(w)), max(1, int(h)))

    panel_width = int(round(screen_width * clamp_float(config.get("面板宽占比", 0.82), 0.20, 1.20)))
    panel_height = int(round(screen_height * clamp_float(config.get("面板高占比", 0.76), 0.20, 1.20)))
    panel_margin = max(12, scale_px(config.get("面板最小边距", 24)))
    panel_min_width = scale_px(config.get("面板最小宽", 1160))
    panel_min_height = scale_px(config.get("面板最小高", 640))
    panel_max_width = scale_px(config.get("面板最大宽", 1540))
    panel_max_height = scale_px(config.get("面板最大高", 860))
    panel_width = clamp_int(panel_width, panel_min_width, min(max(panel_min_width, screen_width - panel_margin * 2), panel_max_width))
    panel_height = clamp_int(panel_height, panel_min_height, min(max(panel_min_height, screen_height - panel_margin * 2), panel_max_height))
    panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
    panel_rect.center = (screen_width // 2, screen_height // 2)
    if panel_rect.left < panel_margin:
        panel_rect.x = panel_margin
    if panel_rect.top < panel_margin:
        panel_rect.y = panel_margin
    if panel_rect.right > screen_width - panel_margin:
        panel_rect.x = screen_width - panel_margin - panel_rect.w
    if panel_rect.bottom > screen_height - panel_margin:
        panel_rect.y = screen_height - panel_margin - panel_rect.h

    content_rect = pygame.Rect(
        panel_rect.x + scale_px(config.get("内容左边距", 64)),
        panel_rect.y + scale_px(config.get("内容上边距", 56)),
        max(1, panel_rect.w - scale_px(config.get("内容左边距", 64)) - scale_px(config.get("内容右边距", 58))),
        max(1, panel_rect.h - scale_px(config.get("内容上边距", 56)) - scale_px(config.get("内容下边距", 42))),
    )
    gutter = scale_px(config.get("左右列间距", 72))
    left_width = int(round(content_rect.w * clamp_float(config.get("左列宽占比", 0.34), 0.15, 0.70)))
    left_width = max(scale_px(280), min(left_width, content_rect.w - gutter - scale_px(260)))
    right_width = max(1, content_rect.w - left_width - gutter)
    left_rect = pygame.Rect(content_rect.x, content_rect.y + scale_px(config.get("左列上偏移", 18)), left_width, max(1, content_rect.h - scale_px(config.get("左列上偏移", 18))))
    right_rect = pygame.Rect(left_rect.right + gutter, content_rect.y + scale_px(config.get("右列顶部预留", 6)), right_width, max(1, content_rect.h - scale_px(config.get("右列顶部预留", 6))))
    row_keys = list(config.get("行列表", []) or [])
    row_count = max(1, len(row_keys))
    row_gap = max(0, scale_px(config.get("行间距", 16)))
    row_height_min = max(24, scale_px(config.get("行高最小", 54)))
    row_height_max = max(row_height_min, scale_px(config.get("行高最大", 86)))
    left_row_region_height = max(1, int(round(left_rect.h * clamp_float(config.get("左列行区高占比", 0.64), 0.20, 1.00))))
    row_height = max(row_height_min, min(row_height_max, (left_row_region_height - (row_count - 1) * row_gap) // row_count))
    small_arrow_width = max(12, scale_px(config.get("小箭头宽", 28)))
    small_arrow_height = max(18, int(round(float(row_height) * float(config.get("小箭头高占行高", 0.54) or 0.54))))
    row_side_padding = max(4, scale_px(config.get("行内左右边距", 8)))
    content_side_padding = max(4, scale_px(config.get("内容左右内边距", 12)))

    row_rects: Dict[str, pygame.Rect] = {}
    control_rects: Dict[str, Dict[str, pygame.Rect]] = {}
    for row_index, row_key in enumerate(row_keys):
        row_rect = local_rect(left_rect.x, left_rect.y + row_index * (row_height + row_gap), left_rect.w, row_height)
        left_arrow_rect = local_rect(row_rect.x + row_side_padding, row_rect.centery - small_arrow_height // 2, small_arrow_width, small_arrow_height)
        right_arrow_rect = local_rect(row_rect.right - row_side_padding - small_arrow_width, row_rect.centery - small_arrow_height // 2, small_arrow_width, small_arrow_height)
        content_left = left_arrow_rect.right + content_side_padding
        content_right = right_arrow_rect.x - content_side_padding
        row_rects[row_key] = row_rect
        control_rects[row_key] = {"左": left_arrow_rect, "右": right_arrow_rect, "内容": local_rect(content_left, row_rect.y, max(12, content_right - content_left), row_rect.h)}

    right_gap = max(0, scale_px(config.get("右列上下分区间距", 28)))
    background_height = int(round((right_rect.h - right_gap) * clamp_float(config.get("右列上区高占比", 0.58), 0.20, 0.85)))
    background_height = max(scale_px(220), min(background_height, max(1, right_rect.h - right_gap - scale_px(140))))
    arrow_area_height = max(1, right_rect.h - background_height - right_gap)
    background_rect = pygame.Rect(right_rect.x, right_rect.y, right_rect.w, background_height)
    arrow_preview_rect = pygame.Rect(right_rect.x, background_rect.bottom + right_gap, right_rect.w, arrow_area_height)
    background_lr_padding = max(0, scale_px(config.get("背景区左右内边距", 12)))
    background_arrow_width = max(18, scale_px(config.get("背景区左右箭头宽", 60)))
    background_arrow_height = max(28, scale_px(config.get("背景区左右箭头高", 118)))
    background_arrow_gap = max(8, scale_px(config.get("背景区箭头与预览间距", 18)))
    background_tb_padding = max(0, scale_px(config.get("背景区预览上下内边距", 20)))
    background_left_arrow_rect = local_rect(background_rect.x + background_lr_padding, background_rect.centery - background_arrow_height // 2, background_arrow_width, background_arrow_height)
    background_right_arrow_rect = local_rect(background_rect.right - background_lr_padding - background_arrow_width, background_rect.centery - background_arrow_height // 2, background_arrow_width, background_arrow_height)
    background_preview_rect = local_rect(background_left_arrow_rect.right + background_arrow_gap, background_rect.y + background_tb_padding, max(40, background_right_arrow_rect.x - background_arrow_gap - (background_left_arrow_rect.right + background_arrow_gap)), max(40, background_rect.h - background_tb_padding * 2))
    arrow_button_width = max(18, scale_px(config.get("箭头预览左右箭头宽", 56)))
    arrow_button_height = max(28, scale_px(config.get("箭头预览左右箭头高", 108)))
    arrow_button_gap = max(8, scale_px(config.get("箭头预览箭头间距", 18)))
    arrow_tb_padding = max(0, scale_px(config.get("箭头预览上下内边距", 10)))
    arrow_left_rect = local_rect(arrow_preview_rect.x + background_lr_padding, arrow_preview_rect.centery - arrow_button_height // 2, arrow_button_width, arrow_button_height)
    arrow_right_rect = local_rect(arrow_preview_rect.right - background_lr_padding - arrow_button_width, arrow_preview_rect.centery - arrow_button_height // 2, arrow_button_width, arrow_button_height)
    preview_side = min(max(60, arrow_right_rect.x - arrow_button_gap - (arrow_left_rect.right + arrow_button_gap)), max(60, arrow_preview_rect.h - arrow_tb_padding * 2))
    arrow_preview_core_rect = local_rect(arrow_preview_rect.centerx - preview_side // 2, arrow_preview_rect.y + arrow_tb_padding, preview_side, preview_side)
    visual = {
        "标签字号": max(14, int(round(row_height * float(config.get("标签字号占行高", 0.44) or 0.44)))),
        "选项字号": max(16, int(round(row_height * float(config.get("选项字号占行高", 0.48) or 0.48)))),
        "小字字号": max(12, int(round(row_height * float(config.get("小字字号占行高", 0.31) or 0.31)))),
        "内容内边距": max(4, content_side_padding),
        "名称下移": scale_px(config.get("名称下移", 1)),
        "箭头名称上间距": max(6, scale_px(config.get("箭头预览底部文字间距", 18))),
        "底部保护边距": max(4, scale_px(config.get("箭头预览底部保护边距", 6))),
        "箭头预览内边距": max(0, scale_px(config.get("箭头预览内边距", 0))),
    }
    return {"布局缩放": float(layout_scale), "面板基础矩形": panel_rect, "行矩形表": row_rects, "控件矩形表": control_rects, "背景区矩形": background_rect, "背景控件矩形": {"左": background_left_arrow_rect, "右": background_right_arrow_rect, "预览": background_preview_rect}, "箭头预览矩形": arrow_preview_core_rect, "箭头预览控件矩形": {"左": arrow_left_rect, "右": arrow_right_rect}, "视觉参数": visual}


def _clamp_rect_to_panel(host, rect: pygame.Rect) -> pygame.Rect:
    if not isinstance(rect, pygame.Rect):
        return pygame.Rect(0, 0, 1, 1)
    try:
        panel_rect = getattr(host, "_设置页_面板基础矩形", pygame.Rect(0, 0, 1, 1))
        panel_width = max(1, int(panel_rect.w))
        panel_height = max(1, int(panel_rect.h))
    except Exception:
        panel_width = 1
        panel_height = 1
    new_rect = rect.copy()
    new_rect.w = min(panel_width, max(1, int(new_rect.w)))
    new_rect.h = min(panel_height, max(1, int(new_rect.h)))
    new_rect.x = max(0, min(int(new_rect.x), max(0, panel_width - new_rect.w)))
    new_rect.y = max(0, min(int(new_rect.y), max(0, panel_height - new_rect.h)))
    return new_rect


def _normalize_row_button_sizes(host):
    try:
        speed_controls = dict(getattr(host, "_设置页_控件矩形表", {}) or {}).get("调速", {})
    except Exception:
        speed_controls = {}
    standard_left = speed_controls.get("左")
    if not isinstance(standard_left, pygame.Rect):
        return
    standard_width = max(1, int(standard_left.w))
    standard_height = max(1, int(standard_left.h))
    control_table = getattr(host, "_设置页_控件矩形表", {})
    if not isinstance(control_table, dict):
        return
    for row_key in get_select_menu_row_keys():
        row_control = control_table.get(row_key)
        if not isinstance(row_control, dict):
            continue
        for sub_key in ("左", "右"):
            rect = row_control.get(sub_key)
            if isinstance(rect, pygame.Rect):
                new_rect = rect.copy()
                new_rect.size = (standard_width, standard_height)
                new_rect.y = rect.centery - standard_height // 2
                row_control[sub_key] = _clamp_rect_to_panel(host, new_rect)


def _clamp_all_controls_to_panel(host):
    try:
        row_rect_table = getattr(host, "_设置页_行矩形表", {})
        if isinstance(row_rect_table, dict):
            for row_key, rect in list(row_rect_table.items()):
                if isinstance(rect, pygame.Rect):
                    row_rect_table[row_key] = _clamp_rect_to_panel(host, rect)
    except Exception:
        pass
    try:
        control_rect_table = getattr(host, "_设置页_控件矩形表", {})
        if isinstance(control_rect_table, dict):
            for row_key, controls in list(control_rect_table.items()):
                if not isinstance(controls, dict):
                    continue
                for sub_key in ("左", "右", "内容"):
                    rect = controls.get(sub_key)
                    if isinstance(rect, pygame.Rect):
                        controls[sub_key] = _clamp_rect_to_panel(host, rect)
    except Exception:
        pass
    try:
        background_rect = getattr(host, "_设置页_背景区矩形", None)
        if isinstance(background_rect, pygame.Rect):
            host._设置页_背景区矩形 = _clamp_rect_to_panel(host, background_rect)
    except Exception:
        pass
    try:
        background_controls = getattr(host, "_设置页_背景控件矩形", {})
        if isinstance(background_controls, dict):
            for sub_key in ("左", "右", "预览"):
                rect = background_controls.get(sub_key)
                if isinstance(rect, pygame.Rect):
                    background_controls[sub_key] = _clamp_rect_to_panel(host, rect)
    except Exception:
        pass
    try:
        arrow_preview_rect = getattr(host, "_设置页_箭头预览矩形", None)
        if isinstance(arrow_preview_rect, pygame.Rect):
            host._设置页_箭头预览矩形 = _clamp_rect_to_panel(host, arrow_preview_rect)
    except Exception:
        pass
    try:
        arrow_preview_controls = getattr(host, "_设置页_箭头预览控件矩形", {})
        if isinstance(arrow_preview_controls, dict):
            for sub_key in ("左", "右"):
                rect = arrow_preview_controls.get(sub_key)
                if isinstance(rect, pygame.Rect):
                    arrow_preview_controls[sub_key] = _clamp_rect_to_panel(host, rect)
    except Exception:
        pass


def recompute_select_settings_layout(host, force: bool = False, **kwargs):
    legacy_force = kwargs.get("强制", None)
    if legacy_force is not None:
        try:
            force = bool(legacy_force)
        except Exception:
            pass
    host._确保设置页资源()
    try:
        current_size = (int(getattr(host, "宽", 0) or 0), int(getattr(host, "高", 0) or 0))
    except Exception:
        current_size = (0, 0)
    if (not force) and current_size == tuple(getattr(host, "_设置页_上次屏幕尺寸", (0, 0))):
        return
    host._设置页_上次屏幕尺寸 = current_size
    layout = compute_select_settings_layout(max(1, int(current_size[0] or 0)), max(1, int(current_size[1] or 0)))
    host._设置页_布局缩放 = float(layout.get("布局缩放", 1.0) or 1.0)
    host._设置页_面板基础矩形 = layout.get("面板基础矩形", pygame.Rect(0, 0, 10, 10))
    host._设置页_行矩形表 = layout.get("行矩形表", {}) if isinstance(layout.get("行矩形表", {}), dict) else {}
    host._设置页_控件矩形表 = layout.get("控件矩形表", {}) if isinstance(layout.get("控件矩形表", {}), dict) else {}
    host._设置页_背景区矩形 = layout.get("背景区矩形", pygame.Rect(0, 0, 10, 10))
    background_controls = layout.get("背景控件矩形", {}) if isinstance(layout.get("背景控件矩形", {}), dict) else {}
    host._设置页_背景控件矩形 = {"左": background_controls.get("左", pygame.Rect(0, 0, 1, 1)) if isinstance(background_controls.get("左", None), pygame.Rect) else pygame.Rect(0, 0, 1, 1), "右": background_controls.get("右", pygame.Rect(0, 0, 1, 1)) if isinstance(background_controls.get("右", None), pygame.Rect) else pygame.Rect(0, 0, 1, 1), "预览": background_controls.get("预览", pygame.Rect(0, 0, 1, 1)) if isinstance(background_controls.get("预览", None), pygame.Rect) else pygame.Rect(0, 0, 1, 1)}
    host._设置页_箭头预览矩形 = layout.get("箭头预览矩形", pygame.Rect(0, 0, 10, 10))
    arrow_preview_controls = layout.get("箭头预览控件矩形", {}) if isinstance(layout.get("箭头预览控件矩形", {}), dict) else {}
    host._设置页_箭头预览控件矩形 = {"左": arrow_preview_controls.get("左", pygame.Rect(0, 0, 1, 1)) if isinstance(arrow_preview_controls.get("左", None), pygame.Rect) else pygame.Rect(0, 0, 1, 1), "右": arrow_preview_controls.get("右", pygame.Rect(0, 0, 1, 1)) if isinstance(arrow_preview_controls.get("右", None), pygame.Rect) else pygame.Rect(0, 0, 1, 1)}
    host._设置页_视觉参数 = layout.get("视觉参数", {}) if isinstance(layout.get("视觉参数", {}), dict) else {}
    host._设置页_面板绘制矩形 = host._设置页_面板基础矩形.copy()
    try:
        if getattr(host, "_设置页_调试器", None) is not None:
            host._设置页_调试器.应用保存覆盖(host)
    except Exception:
        pass
    try:
        _normalize_row_button_sizes(host)
    except Exception:
        pass
    try:
        _clamp_all_controls_to_panel(host)
    except Exception:
        pass
    return
