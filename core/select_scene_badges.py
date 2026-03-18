from __future__ import annotations

from typing import Callable, Optional

import pygame


FontGetter = Callable[..., pygame.font.Font]


def draw_mv_badge(
    screen: pygame.Surface,
    cover_rect: pygame.Rect,
    anchor_rect: pygame.Rect,
    is_large: bool,
    get_font: FontGetter,
    sequence_label_rect: Optional[pygame.Rect] = None,
):
    if not isinstance(screen, pygame.Surface):
        return
    if (not isinstance(cover_rect, pygame.Rect)) or cover_rect.w <= 2 or cover_rect.h <= 2:
        return
    if not isinstance(anchor_rect, pygame.Rect):
        anchor_rect = cover_rect

    if is_large:
        font_size = max(16, int(cover_rect.h * 0.042))
        badge_h = max(26, int(anchor_rect.h * 0.052))
        if isinstance(sequence_label_rect, pygame.Rect):
            badge_x = int(sequence_label_rect.right + max(12, int(anchor_rect.w * 0.012)))
            badge_y = int(
                sequence_label_rect.top
                + max(18, int(sequence_label_rect.h * 0.56))
            )
        else:
            badge_x = int(cover_rect.x + max(18, int(anchor_rect.w * 0.020)))
            badge_y = int(cover_rect.y + max(22, int(anchor_rect.h * 0.120)))
        side_padding = max(10, int(badge_h * 0.40))
        icon_size = max(10, int(badge_h * 0.38))
    else:
        font_size = max(12, int(anchor_rect.h * 0.076))
        badge_h = max(18, int(anchor_rect.h * 0.086))
        if isinstance(sequence_label_rect, pygame.Rect):
            badge_x = int(sequence_label_rect.right + 1)
            badge_y = int(
                max(
                    cover_rect.y + 1,
                    sequence_label_rect.top + max(1, int(sequence_label_rect.h * 0.06)),
                )
            )
        else:
            badge_x = int(cover_rect.x + max(28, int(anchor_rect.w * 0.160)))
            badge_y = int(cover_rect.y + max(4, int(anchor_rect.h * 0.010)))
        side_padding = max(7, int(badge_h * 0.34))
        icon_size = max(7, int(badge_h * 0.34))

    font = get_font(font_size, 是否粗体=True)
    text_surface = font.render("MV", True, (236, 244, 255))
    text_w = int(text_surface.get_width())
    text_h = int(text_surface.get_height())
    gap = max(5, int(badge_h * 0.18))
    badge_w = max(26, side_padding * 2 + icon_size + gap + text_w)

    badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)
    inset = max(3, int(badge_h * 0.18))
    if badge_rect.right > cover_rect.right - 4:
        badge_rect.right = cover_rect.right - 4
    if badge_rect.bottom > cover_rect.bottom - 4:
        badge_rect.bottom = cover_rect.bottom - 4
    min_left = cover_rect.x + 4
    min_top = cover_rect.y + 4
    if badge_rect.x < min_left:
        badge_rect.x = min_left
    if badge_rect.y < min_top:
        badge_rect.y = min_top

    shadow_rect = badge_rect.move(0, 2)
    shadow_layer = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
    pygame.draw.rect(
        shadow_layer,
        (6, 10, 22, 78),
        pygame.Rect(0, 0, shadow_rect.w, shadow_rect.h),
        border_radius=max(10, int(shadow_rect.h * 0.48)),
    )
    screen.blit(shadow_layer, shadow_rect.topleft)

    body = pygame.Surface((badge_rect.w, badge_rect.h), pygame.SRCALPHA)
    full_rect = body.get_rect()
    inner_rect = full_rect.inflate(-2, -2)
    radius = max(10, int(full_rect.h * 0.48))

    pygame.draw.rect(
        body,
        (14, 18, 34, 206),
        full_rect,
        border_radius=radius,
    )
    pygame.draw.rect(
        body,
        (108, 224, 255, 210),
        inner_rect,
        width=2,
        border_radius=max(8, radius - 2),
    )

    accent_w = max(4, int(full_rect.w * 0.08))
    pygame.draw.rect(
        body,
        (255, 82, 166, 214),
        pygame.Rect(0, 0, accent_w, full_rect.h),
        border_top_left_radius=radius,
        border_bottom_left_radius=radius,
    )

    gloss = [
        (accent_w + inset, inset),
        (full_rect.w - inset, inset),
        (full_rect.w - max(10, int(full_rect.w * 0.22)), max(inset + 1, int(full_rect.h * 0.48))),
        (accent_w + max(8, int(full_rect.w * 0.10)), max(inset + 1, int(full_rect.h * 0.48))),
    ]
    pygame.draw.polygon(body, (255, 255, 255, 24), gloss)

    icon_cx = accent_w + side_padding + icon_size // 2
    icon_cy = full_rect.centery
    triangle = [
        (icon_cx - icon_size // 3, icon_cy - icon_size // 2),
        (icon_cx - icon_size // 3, icon_cy + icon_size // 2),
        (icon_cx + icon_size // 2, icon_cy),
    ]
    pygame.draw.polygon(body, (118, 236, 255, 240), triangle)

    text_x = accent_w + side_padding + icon_size + gap
    text_y = full_rect.centery - text_h // 2 - 1
    body.blit(text_surface, (text_x, text_y))

    mini_bar_w = max(10, int(full_rect.w * 0.18))
    mini_bar_rect = pygame.Rect(
        full_rect.right - mini_bar_w - inset,
        full_rect.bottom - max(4, int(full_rect.h * 0.22)),
        mini_bar_w,
        2,
    )
    pygame.draw.rect(body, (132, 226, 255, 150), mini_bar_rect, border_radius=2)

    screen.blit(body, badge_rect.topleft)
