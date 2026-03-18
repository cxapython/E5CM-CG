from __future__ import annotations

from typing import Callable, Optional

import pygame


FontGetter = Callable[..., pygame.font.Font]
PlayCountColorGetter = Callable[[int], tuple[int, int, int]]
UIContainerImageGetter = Callable[..., Optional[pygame.Surface]]
StarRowDrawer = Callable[..., None]
SequenceLabelDrawer = Callable[..., None]
MvBadgeDrawer = Callable[..., None]


def render_detail_panel_content(
    panel_surface: pygame.Surface,
    song,
    frame_path: str,
    content_base_rect: pygame.Rect,
    local_cover_rect: pygame.Rect,
    local_info_rect: pygame.Rect,
    local_star_rect: pygame.Rect,
    local_play_rect: pygame.Rect,
    local_bpm_rect: pygame.Rect,
    ornament_width: int,
    ornament_height: int,
    ornament_draw_x: int,
    ornament_draw_y: int,
    content_offset_x: int,
    content_offset_y: int,
    cover_surface: Optional[pygame.Surface],
    big_star_path: str,
    get_font: FontGetter,
    get_play_count_color: PlayCountColorGetter,
    get_ui_container_image: UIContainerImageGetter,
    draw_star_row: StarRowDrawer,
    draw_sequence_label: SequenceLabelDrawer,
    draw_mv_badge: MvBadgeDrawer,
) -> None:
    if not isinstance(panel_surface, pygame.Surface):
        return
    panel_surface.fill((0, 0, 0, 0))

    cover_draw_rect = pygame.Rect(
        int(local_cover_rect.x + content_offset_x),
        int(local_cover_rect.y + content_offset_y),
        int(local_cover_rect.w),
        int(local_cover_rect.h),
    )
    if isinstance(cover_surface, pygame.Surface):
        panel_surface.blit(cover_surface, cover_draw_rect.topleft)
    else:
        pygame.draw.rect(panel_surface, (18, 18, 24), cover_draw_rect)

    info_draw_rect = pygame.Rect(
        int(local_info_rect.x + content_offset_x),
        int(local_info_rect.y + content_offset_y),
        int(local_info_rect.w),
        int(local_info_rect.h),
    )
    info_bar = pygame.Surface((info_draw_rect.w, info_draw_rect.h), pygame.SRCALPHA)
    info_bar.fill((0, 0, 0, 155))
    panel_surface.blit(info_bar, info_draw_rect.topleft)

    draw_star_row(
        panel_surface,
        pygame.Rect(
            int(local_star_rect.x + content_offset_x),
            int(local_star_rect.y + content_offset_y),
            int(local_star_rect.w),
            int(local_star_rect.h),
        ),
        int(getattr(song, "星级", 0) or 0),
        big_star_path,
        1.65,
        每行最大=10,
        基准高占比=0.34,
        行间距占比=0.02,
    )

    song_name = str(getattr(song, "歌名", "") or "").replace("_", " ")
    song_font_size = max(16, int(local_info_rect.h * 0.22))
    try:
        available_text_width = max(80, int(local_info_rect.w * 0.84))
        current_size = int(song_font_size)
        while current_size > 12:
            test_font = get_font(current_size, 是否粗体=False)
            if test_font.size(song_name)[0] <= available_text_width:
                break
            current_size -= 1
        song_font = get_font(max(12, current_size), 是否粗体=False)
        song_surface = song_font.render(song_name, True, (255, 255, 255))

        song_y = int(local_star_rect.bottom + max(4, int(local_info_rect.h * 0.03)))
        song_rect = song_surface.get_rect(
            centerx=int(local_info_rect.centerx + content_offset_x),
            y=int(song_y + content_offset_y),
        )
        panel_surface.blit(song_surface, song_rect.topleft)

        line_y = int(song_rect.bottom + max(4, int(local_info_rect.h * 0.03)))
        pygame.draw.line(
            panel_surface,
            (165, 165, 165),
            (
                int(local_info_rect.x + content_offset_x + max(12, int(local_info_rect.w * 0.06))),
                line_y,
            ),
            (
                int(local_info_rect.right + content_offset_x - max(12, int(local_info_rect.w * 0.06))),
                line_y,
            ),
            max(1, int(local_info_rect.h * 0.012)),
        )
    except Exception:
        pass

    try:
        play_count = int(max(0, int(getattr(song, "游玩次数", 0) or 0)))
    except Exception:
        play_count = 0
    bpm_text = (
        f"BPM:{getattr(song, 'bpm', '')}"
        if getattr(song, "bpm", None)
        else "BPM:?"
    )
    bottom_font_size = max(12, int(local_info_rect.h * 0.13))
    bottom_font = get_font(bottom_font_size, 是否粗体=True)
    play_color = get_play_count_color(play_count)

    try:
        left_surface = bottom_font.render(f"游玩次数:{play_count}", True, play_color)
        right_surface = bottom_font.render(bpm_text, True, (230, 230, 230))

        left_x = int(local_play_rect.x + content_offset_x)
        left_y = int(local_play_rect.centery + content_offset_y - left_surface.get_height() // 2)
        right_x = int(local_bpm_rect.right + content_offset_x - right_surface.get_width())
        right_y = int(local_bpm_rect.centery + content_offset_y - right_surface.get_height() // 2)

        panel_surface.blit(left_surface, (left_x, left_y))
        panel_surface.blit(right_surface, (right_x, right_y))
    except Exception:
        pass

    frame_surface = get_ui_container_image(
        frame_path,
        ornament_width,
        ornament_height,
        缩放模式="stretch",
        透明=True,
    )
    if isinstance(frame_surface, pygame.Surface):
        panel_surface.blit(frame_surface, (int(ornament_draw_x), int(ornament_draw_y)))

    anchor_rect = pygame.Rect(
        int(content_offset_x),
        int(content_offset_y),
        int(content_base_rect.w),
        int(content_base_rect.h),
    )
    draw_sequence_label(
        屏幕=panel_surface,
        锚点矩形=anchor_rect,
        内部序号从0=int(getattr(song, "序号", 0) or 0),
        是否大图=True,
    )
    if bool(getattr(song, "是否带MV", False)):
        draw_mv_badge(
            panel_surface,
            cover_draw_rect,
            anchor_rect,
            是否大图=True,
        )


def draw_detail_star_gloss(
    screen: pygame.Surface,
    current_frame_rect: pygame.Rect,
    local_star_rect: pygame.Rect,
    content_offset_x: int,
    content_offset_y: int,
    total_width: int,
    total_height: int,
    star_count: int,
    effect_alpha: int,
    big_star_path: str,
    star_effect_path: str,
    draw_star_row: StarRowDrawer,
):
    if (not isinstance(current_frame_rect, pygame.Rect)) or current_frame_rect.w <= 4 or current_frame_rect.h <= 4:
        return
    if int(max(0, int(star_count or 0))) <= 0:
        return

    original_star_rect = pygame.Rect(
        int(local_star_rect.x + content_offset_x),
        int(local_star_rect.y + content_offset_y),
        int(local_star_rect.w),
        int(local_star_rect.h),
    )
    if original_star_rect.w <= 2 or original_star_rect.h <= 2:
        return

    scale_x = float(current_frame_rect.w) / float(max(1, int(total_width)))
    scale_y = float(current_frame_rect.h) / float(max(1, int(total_height)))
    scaled_star_rect = pygame.Rect(
        int(current_frame_rect.left + round(float(original_star_rect.x) * scale_x)),
        int(current_frame_rect.top + round(float(original_star_rect.y) * scale_y)),
        max(1, int(round(float(original_star_rect.w) * scale_x))),
        max(1, int(round(float(original_star_rect.h) * scale_y))),
    )

    draw_star_row(
        屏幕=screen,
        区域=scaled_star_rect,
        星数=int(star_count),
        星星路径=big_star_path,
        星星缩放倍数=1.65,
        每行最大=10,
        动态光效路径=star_effect_path,
        光效周期秒=1.6,
        基准高占比=0.34,
        行间距占比=0.02,
        仅绘制动态光效=True,
        光效透明度=int(max(0, min(255, int(effect_alpha or 0)))),
    )
