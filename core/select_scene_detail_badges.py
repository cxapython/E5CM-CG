from __future__ import annotations

from typing import Callable, Optional

import pygame


UIImageGetter = Callable[..., Optional[pygame.Surface]]
ScaleToHeight = Callable[..., Optional[pygame.Surface]]
LayoutValueGetter = Callable[[str, object], object]
LayoutPixelGetter = Callable[..., int]
NeedsHotPredicate = Callable[[int], bool]


def render_detail_corner_badges(
    screen: pygame.Surface,
    song,
    panel_rect: pygame.Rect,
    alpha: int,
    play_count: int,
    vip_path: str,
    hot_path: str,
    new_path: str,
    get_ui_image: UIImageGetter,
    scale_to_height: ScaleToHeight,
    get_layout_value: LayoutValueGetter,
    get_layout_pixel: LayoutPixelGetter,
    needs_hot: NeedsHotPredicate,
):
    if not isinstance(screen, pygame.Surface):
        return
    if not isinstance(panel_rect, pygame.Rect) or panel_rect.w <= 10 or panel_rect.h <= 10:
        return

    alpha = max(0, min(255, int(alpha or 255)))
    hot_reserved_width = 0

    if bool(getattr(song, "是否VIP", False)):
        vip_original = get_ui_image(vip_path, 透明=True)
        if isinstance(vip_original, pygame.Surface):
            vip_height_ratio = get_layout_value("详情大图.VIP.高占比", 0.20)
            try:
                vip_height_ratio = float(vip_height_ratio)
            except Exception:
                vip_height_ratio = 0.20
            vip_height_ratio = max(0.02, min(0.90, vip_height_ratio))

            vip_height = max(12, int(panel_rect.h * vip_height_ratio))
            vip_surface = scale_to_height(vip_original, vip_height)
            if isinstance(vip_surface, pygame.Surface):
                try:
                    vip_surface.set_alpha(alpha)
                except Exception:
                    pass

                vip_w, vip_h = vip_surface.get_size()
                vip_x_offset = get_layout_pixel(
                    "详情大图.VIP.x偏移",
                    -int(vip_w * 0.20),
                    最小=-99999,
                    最大=99999,
                )
                vip_y_offset = get_layout_pixel(
                    "详情大图.VIP.y偏移",
                    -int(vip_h * 0.35),
                    最小=-99999,
                    最大=99999,
                )

                vip_x = panel_rect.right - vip_w + int(vip_x_offset)
                vip_y = panel_rect.top + int(vip_y_offset)
                screen.blit(vip_surface, (vip_x, vip_y))

    if needs_hot(int(play_count)):
        hot_original = get_ui_image(hot_path, 透明=True)
        if isinstance(hot_original, pygame.Surface):
            hot_height_ratio = get_layout_value("详情大图.HOT.高占比", 0.34)
            try:
                hot_height_ratio = float(hot_height_ratio)
            except Exception:
                hot_height_ratio = 0.24
            hot_height_ratio = max(0.02, min(0.90, hot_height_ratio))

            hot_height = max(14, int(panel_rect.h * hot_height_ratio))
            hot_surface = scale_to_height(hot_original, hot_height)
            if isinstance(hot_surface, pygame.Surface):
                try:
                    hot_surface.set_alpha(alpha)
                except Exception:
                    pass

                hot_w, hot_h = hot_surface.get_size()
                hot_padding_right = get_layout_pixel(
                    "详情大图.HOT.右内边距",
                    max(6, int(hot_height * 0.10)),
                    最小=-99999,
                    最大=99999,
                )
                hot_padding_bottom = get_layout_pixel(
                    "详情大图.HOT.下内边距",
                    max(6, int(hot_height * 0.10)),
                    最小=-99999,
                    最大=99999,
                )
                hot_x_offset = get_layout_pixel(
                    "详情大图.HOT.x偏移",
                    +int(hot_w * 0.50),
                    最小=-99999,
                    最大=99999,
                )
                hot_y_offset = get_layout_pixel(
                    "详情大图.HOT.y偏移",
                    +int(hot_h * 0.10),
                    最小=-99999,
                    最大=99999,
                )

                hot_x = panel_rect.right - hot_w - int(hot_padding_right) + int(hot_x_offset)
                hot_y = panel_rect.bottom - hot_h - int(hot_padding_bottom) + int(hot_y_offset)
                hot_reserved_width = hot_w + max(8, int(hot_height * 0.14))
                screen.blit(hot_surface, (hot_x, hot_y))

    if bool(getattr(song, "是否NEW", False)):
        new_original = get_ui_image(new_path, 透明=True)
        if isinstance(new_original, pygame.Surface):
            new_height_ratio = get_layout_value("详情大图.NEW.高占比", 0.26)
            try:
                new_height_ratio = float(new_height_ratio)
            except Exception:
                new_height_ratio = 0.26
            new_height_ratio = max(0.02, min(0.90, new_height_ratio))

            new_height = max(14, int(panel_rect.h * new_height_ratio))
            new_surface = scale_to_height(new_original, new_height)
            if isinstance(new_surface, pygame.Surface):
                try:
                    new_surface.set_alpha(alpha)
                except Exception:
                    pass

                new_w, new_h = new_surface.get_size()
                new_padding_right = get_layout_pixel(
                    "详情大图.NEW.右内边距",
                    max(6, int(new_height * 0.10)),
                    最小=-99999,
                    最大=99999,
                )
                new_padding_bottom = get_layout_pixel(
                    "详情大图.NEW.下内边距",
                    max(6, int(new_height * 0.10)),
                    最小=-99999,
                    最大=99999,
                )
                new_x_offset = get_layout_pixel(
                    "详情大图.NEW.x偏移",
                    +int(new_w * 0.15),
                    最小=-99999,
                    最大=99999,
                )
                new_y_offset = get_layout_pixel(
                    "详情大图.NEW.y偏移",
                    +int(new_h * 0.15),
                    最小=-99999,
                    最大=99999,
                )

                new_x = panel_rect.right - new_w - int(new_padding_right) + int(new_x_offset)
                if hot_reserved_width > 0:
                    new_x -= hot_reserved_width
                new_y = panel_rect.bottom - new_h - int(new_padding_bottom) + int(new_y_offset)
                screen.blit(new_surface, (new_x, new_y))
