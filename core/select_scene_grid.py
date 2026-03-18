from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class CardGridConfig:
    columns: int
    rows: int
    outer_padding: int
    vertical_padding: int
    gap_x: int
    gap_y: int
    min_region_w: int
    min_region_h: int
    fallback_padding: int
    min_raw_card_w: int
    min_raw_card_h: int
    card_scale_x: float
    card_scale_y: float
    min_card_w: int
    min_card_h: int
    vertical_shift_ratio: float


def build_card_grid_rects(
    container_rect: pygame.Rect,
    page_index: int,
    page_size: int,
    total_items: int,
    config: CardGridConfig,
) -> list[pygame.Rect]:
    area = container_rect.inflate(
        -int(config.outer_padding) * 2,
        -int(config.vertical_padding) * 2,
    )
    if area.w < int(config.min_region_w) or area.h < int(config.min_region_h):
        area = container_rect.inflate(
            -int(config.fallback_padding),
            -int(config.fallback_padding),
        )

    raw_card_width = max(
        int(config.min_raw_card_w),
        (area.w - (int(config.columns) - 1) * int(config.gap_x)) // max(1, int(config.columns)),
    )
    raw_card_height = max(
        int(config.min_raw_card_h),
        (area.h - (int(config.rows) - 1) * int(config.gap_y)) // max(1, int(config.rows)),
    )

    card_width = max(int(config.min_card_w), int(raw_card_width * float(config.card_scale_x)))
    card_height = max(int(config.min_card_h), int(raw_card_height * float(config.card_scale_y)))

    block_width = int(config.columns) * card_width + (int(config.columns) - 1) * int(config.gap_x)
    block_height = int(config.rows) * card_height + (int(config.rows) - 1) * int(config.gap_y)
    start_x = area.centerx - block_width // 2
    start_y = area.centery - block_height // 2
    start_y -= int(area.h * float(config.vertical_shift_ratio))

    start_index = int(page_index) * int(page_size)
    rects: list[pygame.Rect] = []
    for row in range(int(config.rows)):
        for column in range(int(config.columns)):
            relative_index = row * int(config.columns) + column
            item_index = start_index + relative_index
            if item_index >= int(total_items):
                continue

            x = start_x + column * (card_width + int(config.gap_x))
            y = start_y + row * (card_height + int(config.gap_y))
            rects.append(pygame.Rect(x, y, card_width, card_height))

    return rects
