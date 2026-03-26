from __future__ import annotations

import re
from typing import Callable, Optional

import pygame


def _format_song_display_name(song_name: str) -> str:
    text = str(song_name or "").strip().replace("_", " ")
    if not text:
        return ""
    text = re.sub(r"\s*[#＃]\s*\d+\s*$", "", text).strip()
    return text


def _style_float(style: Optional[dict], key: str, fallback: float) -> float:
    if not isinstance(style, dict):
        return float(fallback)
    try:
        return float(style.get(key, fallback))
    except Exception:
        return float(fallback)


def build_song_card_cache_key(
    song,
    frame_rect: pygame.Rect,
    layout_version: float,
    cover_ready: bool,
    play_count: int,
) -> tuple[object, ...]:
    return (
        int(frame_rect.w),
        int(frame_rect.h),
        float(layout_version),
        str(getattr(song, "sm路径", "") or ""),
        str(getattr(song, "封面路径", "") or ""),
        bool(cover_ready),
        int(getattr(song, "星级", 0) or 0),
        int(getattr(song, "序号", 0) or 0),
        _format_song_display_name(str(getattr(song, "歌名", "") or "")),
        str(getattr(song, "bpm", "") or ""),
        int(play_count),
        bool(getattr(song, "是否VIP", False)),
        bool(getattr(song, "是否HOT", False)),
        bool(getattr(song, "是否NEW", False)),
        bool(getattr(song, "是否带MV", False)),
    )


def render_song_card_static_surface(
    song,
    frame_rect: pygame.Rect,
    local_frame_rect: pygame.Rect,
    local_cover_rect: pygame.Rect,
    local_cover_visible_rect: pygame.Rect,
    local_info_rect: pygame.Rect,
    local_star_rect: pygame.Rect,
    local_play_rect: pygame.Rect,
    local_bpm_rect: pygame.Rect,
    cover_surface: Optional[pygame.Surface],
    play_count: int,
    frame_path: str,
    small_star_path: str,
    vip_path: str,
    hot_path: str,
    new_path: str,
    get_font: Callable[..., pygame.font.Font],
    render_compact_text: Callable[..., pygame.Surface],
    get_play_count_color: Callable[[int], tuple[int, int, int]],
    get_ui_container_image: Callable[..., Optional[pygame.Surface]],
    get_ui_image: Callable[..., Optional[pygame.Surface]],
    scale_to_height: Callable[..., Optional[pygame.Surface]],
    draw_star_row: Callable[..., None],
    draw_index_badge: Callable[..., None],
    draw_mv_badge: Callable[..., None],
    text_style: Optional[dict] = None,
) -> pygame.Surface:
    surface = pygame.Surface((frame_rect.w, frame_rect.h), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    if cover_surface is not None:
        previous_clip = surface.get_clip()
        try:
            surface.set_clip(local_cover_visible_rect)
            surface.blit(cover_surface, local_cover_rect.topleft)
        finally:
            surface.set_clip(previous_clip)
    else:
        pygame.draw.rect(surface, (30, 30, 40), local_cover_visible_rect)

    info_bar = pygame.Surface((local_info_rect.w, local_info_rect.h), pygame.SRCALPHA)
    info_bar.fill((0, 0, 0, 118))
    surface.blit(info_bar, local_info_rect.topleft)

    draw_star_row(
        屏幕=surface,
        区域=local_star_rect,
        星数=int(getattr(song, "星级", 0) or 0),
        星星路径=small_star_path,
        星星缩放倍数=0.42,
        每行最大=10,
    )

    style = dict(text_style) if isinstance(text_style, dict) else {}
    play_label_ratio = max(0.05, min(0.80, _style_float(style, "游玩次数标签字号占信息条高比", 0.16)))
    play_number_ratio = max(0.05, min(0.80, _style_float(style, "游玩次数数字字号占信息条高比", 0.18)))
    bpm_ratio = max(0.05, min(0.80, _style_float(style, "BPM字号占信息条高比", 0.20)))
    play_min = max(6, int(round(_style_float(style, "游玩次数最小字号", 7))))
    bpm_min = max(6, int(round(_style_float(style, "BPM最小字号", 8))))

    play_label_size = max(play_min, int(local_info_rect.h * play_label_ratio))
    play_number_size = max(play_min, int(local_info_rect.h * play_number_ratio))
    bpm_size = max(bpm_min, int(local_info_rect.h * bpm_ratio))

    song_name = _format_song_display_name(str(getattr(song, "歌名", "") or ""))
    if song_name:
        title_padding_x = max(6, int(local_info_rect.w * 0.06))
        min_top = int(local_star_rect.bottom + max(1, int(local_info_rect.h * 0.01)))
        title_bottom = int(local_play_rect.y - max(1, int(local_info_rect.h * 0.015)))
        title_height = max(12, int(local_info_rect.h * 0.26))
        title_top = int(title_bottom - title_height)
        if title_top < min_top:
            title_top = min_top

        title_rect = pygame.Rect(
            int(local_info_rect.x + title_padding_x),
            int(title_top),
            int(max(12, local_info_rect.w - title_padding_x * 2)),
            int(max(8, title_bottom - title_top)),
        )
        if title_rect.bottom > local_play_rect.y - 1:
            title_rect.bottom = local_play_rect.y - 1

        if title_rect.w >= 20 and title_rect.h >= 8:
            try:
                title_frame_ratio = max(
                    0.04,
                    min(0.50, _style_float(style, "歌名字号占框高比", 0.10)),
                )
                title_min_size = max(
                    8, int(round(_style_float(style, "歌名最小字号", 8)))
                )
                title_vs_bpm_delta = int(
                    round(_style_float(style, "歌名字号相对BPM增量", 2))
                )
                title_font_size = max(
                    int(bpm_size + title_vs_bpm_delta),
                    min(
                        int(title_rect.h * 0.95),
                        int(frame_rect.h * title_frame_ratio),
                    ),
                )
                title_font = get_font(int(title_font_size), 是否粗体=False)
                while (
                    title_font.get_height() > title_rect.h
                    and title_font_size > title_min_size
                ):
                    title_font_size -= 1
                    title_font = get_font(int(title_font_size), 是否粗体=False)

                title_surface = title_font.render(song_name, True, (248, 250, 255))
                shadow_surface = title_font.render(song_name, True, (0, 0, 0))
                title_x = int(title_rect.centerx - title_surface.get_width() // 2)
                title_y = int(title_rect.centery - title_surface.get_height() // 2)
                shadow_offset = max(1, int(title_rect.h * 0.10))

                previous_clip = surface.get_clip()
                try:
                    surface.set_clip(title_rect)
                    surface.blit(shadow_surface, (title_x, title_y + shadow_offset))
                    surface.blit(title_surface, (title_x, title_y))
                finally:
                    surface.set_clip(previous_clip)

            except Exception:
                pass

    bpm_text = f"BPM:{getattr(song, 'bpm', '')}" if getattr(song, "bpm", None) else "BPM:?"
    play_color = get_play_count_color(int(play_count))

    try:
        play_label_font = get_font(play_label_size, 是否粗体=True)
        play_number_font = get_font(play_number_size, 是否粗体=True)
        bpm_font = get_font(bpm_size, 是否粗体=True)

        play_label_surface = render_compact_text(
            "游玩次数:",
            play_label_font,
            play_color,
            字符间距=-1,
        )
        play_number_surface = render_compact_text(
            str(int(play_count)),
            play_number_font,
            play_color,
            字符间距=0,
        )
        bpm_surface = bpm_font.render(bpm_text, True, (255, 255, 255))

        play_block_width = int(play_label_surface.get_width()) + 2 + int(
            play_number_surface.get_width()
        )
        play_x = local_play_rect.x
        play_y = local_play_rect.centery - max(
            play_label_surface.get_height(),
            play_number_surface.get_height(),
        ) // 2

        bpm_x = local_bpm_rect.right - bpm_surface.get_width()
        bpm_y = local_bpm_rect.centery - bpm_surface.get_height() // 2

        if play_x + play_block_width > bpm_x - 6:
            compression_delta = (play_x + play_block_width) - (bpm_x - 6)
            bpm_x += max(0, compression_delta)

        surface.blit(play_label_surface, (play_x, play_y))
        surface.blit(
            play_number_surface,
            (play_x + int(play_label_surface.get_width()) + 2, play_y),
        )
        surface.blit(bpm_surface, (bpm_x, bpm_y))
    except Exception:
        pass

    frame_surface = get_ui_container_image(
        frame_path,
        frame_rect.w,
        frame_rect.h,
        缩放模式="stretch",
        透明=True,
    )
    if frame_surface is not None:
        surface.blit(frame_surface, (0, 0))

    draw_index_badge(
        屏幕=surface,
        锚点矩形=local_frame_rect,
        内部序号从0=int(getattr(song, "序号", 0) or 0),
        是否大图=False,
    )

    if bool(getattr(song, "是否带MV", False)):
        draw_mv_badge(
            surface,
            local_cover_rect,
            local_frame_rect,
            是否大图=False,
        )

    if bool(getattr(song, "是否VIP", False)):
        vip_original = get_ui_image(vip_path, 透明=True)
        if vip_original is not None:
            vip_height = max(10, int(frame_rect.h * 0.15))
            vip_surface = scale_to_height(vip_original, vip_height)
            if vip_surface is not None:
                vip_width, vip_height = vip_surface.get_size()
                vip_x = local_frame_rect.right - vip_width - max(2, int(vip_width * 0.06))
                vip_y = local_frame_rect.top - max(2, int(vip_height * -0.020))
                surface.blit(vip_surface, (vip_x, vip_y))

    hot_reserved_width = 0
    try:
        if bool(getattr(song, "是否HOT", False)):
            hot_original = get_ui_image(hot_path, 透明=True)
            if hot_original is not None:
                hot_height = max(14, int(frame_rect.h * 0.34))
                hot_surface = scale_to_height(hot_original, hot_height)
                if hot_surface is not None:
                    hot_width, hot_height = hot_surface.get_size()
                    hot_x = local_frame_rect.right - hot_width - max(4, int(hot_height * -0.50))
                    hot_y = local_frame_rect.bottom - hot_height - max(4, int(hot_height * 0.10))
                    hot_reserved_width = hot_width + max(6, int(hot_height * 0.14))
                    surface.blit(hot_surface, (hot_x, hot_y))
    except Exception:
        pass

    try:
        if bool(getattr(song, "是否NEW", False)):
            new_original = get_ui_image(new_path, 透明=True)
            if new_original is not None:
                new_height = max(12, int(frame_rect.h * 0.30))
                new_surface = scale_to_height(new_original, new_height)
                if new_surface is not None:
                    new_width, new_height = new_surface.get_size()
                    new_x = local_frame_rect.right - new_width - max(4, int(new_height * 0.0))
                    if hot_reserved_width > 0:
                        new_x -= hot_reserved_width
                    new_y = local_frame_rect.bottom - new_height - max(4, int(new_height * 0.10))
                    surface.blit(new_surface, (new_x, new_y))
    except Exception:
        pass

    return surface
