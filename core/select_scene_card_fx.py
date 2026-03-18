from __future__ import annotations

import pygame


def _hover_palette(pedal_highlight: bool) -> tuple[tuple[int, int, int, int], ...]:
    if pedal_highlight:
        return (
            (255, 192, 96, 42),
            (255, 226, 168, 92),
            (255, 214, 138, 188),
            (255, 250, 236, 56),
        )
    return (
        (20, 36, 64, 34),
        (150, 220, 255, 84),
        (118, 232, 255, 182),
        (255, 255, 255, 48),
    )


def draw_card_hover_underlay(
    target_surface: pygame.Surface,
    frame_rect: pygame.Rect,
    pedal_highlight: bool = False,
):
    shadow_color, rim_color, _accent_color, _sheen_color = _hover_palette(
        bool(pedal_highlight)
    )
    shadow_rect = frame_rect.inflate(18, 16)
    shadow_rect.move_ip(0, 8)
    shadow_layer = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
    outer_radius = max(22, int(min(shadow_rect.w, shadow_rect.h) * 0.18))
    inner_rect = pygame.Rect(8, 6, max(1, shadow_rect.w - 16), max(1, shadow_rect.h - 14))
    inner_radius = max(18, outer_radius - 6)
    pygame.draw.rect(
        shadow_layer,
        shadow_color,
        pygame.Rect(0, 0, shadow_rect.w, shadow_rect.h),
        border_radius=outer_radius,
    )
    pygame.draw.rect(
        shadow_layer,
        rim_color,
        inner_rect,
        width=2,
        border_radius=inner_radius,
    )
    target_surface.blit(shadow_layer, shadow_rect.topleft)


def draw_card_hover_overlay(
    target_surface: pygame.Surface,
    frame_rect: pygame.Rect,
    pedal_highlight: bool = False,
):
    _shadow_color, rim_color, accent_color, sheen_color = _hover_palette(
        bool(pedal_highlight)
    )
    overlay = pygame.Surface((frame_rect.w, frame_rect.h), pygame.SRCALPHA)
    rect = overlay.get_rect()
    inner_rect = rect.inflate(-8, -8)
    inner_radius = max(18, int(min(inner_rect.w, inner_rect.h) * 0.12))

    pygame.draw.rect(
        overlay,
        rim_color,
        inner_rect,
        width=2,
        border_radius=inner_radius,
    )

    top_bar_width = max(28, int(inner_rect.w * 0.28))
    top_bar_rect = pygame.Rect(
        inner_rect.x + 12,
        inner_rect.y + 8,
        min(top_bar_width, max(1, inner_rect.w - 24)),
        4,
    )
    pygame.draw.rect(
        overlay,
        accent_color,
        top_bar_rect,
        border_radius=4,
    )

    sheen_polygon = [
        (inner_rect.x, inner_rect.y),
        (inner_rect.x + int(inner_rect.w * 0.56), inner_rect.y),
        (inner_rect.x + int(inner_rect.w * 0.28), inner_rect.y + int(inner_rect.h * 0.34)),
        (inner_rect.x, inner_rect.y + int(inner_rect.h * 0.34)),
    ]
    pygame.draw.polygon(overlay, sheen_color, sheen_polygon)

    line_width = 3
    corner_length = max(18, int(min(inner_rect.w, inner_rect.h) * 0.12))
    top_left = (inner_rect.left + 8, inner_rect.top + 10)
    bottom_right = (inner_rect.right - 8, inner_rect.bottom - 10)

    pygame.draw.line(
        overlay,
        accent_color,
        top_left,
        (top_left[0] + corner_length, top_left[1]),
        width=line_width,
    )
    pygame.draw.line(
        overlay,
        accent_color,
        top_left,
        (top_left[0], top_left[1] + corner_length),
        width=line_width,
    )
    pygame.draw.line(
        overlay,
        accent_color,
        bottom_right,
        (bottom_right[0] - corner_length, bottom_right[1]),
        width=line_width,
    )
    pygame.draw.line(
        overlay,
        accent_color,
        bottom_right,
        (bottom_right[0], bottom_right[1] - corner_length),
        width=line_width,
    )

    target_surface.blit(overlay, frame_rect.topleft)
