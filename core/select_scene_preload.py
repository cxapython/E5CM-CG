from __future__ import annotations

import os
from typing import Callable, Iterable, Optional

import pygame

from core.select_scene_layout import (
    UIImageGetter,
    compute_thumbnail_card_layout,
)


CardListGetter = Callable[[int], Iterable[object]]
CardCoverPathGetter = Callable[[object], str]
CardRectGetter = Callable[[object], pygame.Rect]


def build_preload_page_order(base_page: int, total_pages: int) -> list[int]:
    try:
        total_pages = int(total_pages)
    except Exception:
        total_pages = 1
    if total_pages <= 0:
        total_pages = 1

    pages: list[int] = []
    seen = set()
    for page in (int(base_page), int(base_page) + 1, int(base_page) - 1, int(base_page) + 2):
        if 0 <= page < total_pages and page not in seen:
            pages.append(page)
            seen.add(page)
    return pages


def collect_preload_cover_keys(
    base_page: int,
    total_pages: int,
    get_cards_for_page: CardListGetter,
    get_card_cover_path: CardCoverPathGetter,
    get_card_rect: CardRectGetter,
    frame_path: str,
    get_ui_image: UIImageGetter,
    frame_scale_x: float,
    frame_scale_y: float,
    frame_x_offset: int,
    frame_y_offset_ratio: float,
    target_ratio: Optional[float] = None,
) -> list[tuple[str, int, int, int, str]]:
    keys: list[tuple[str, int, int, int, str]] = []
    seen = set()

    for page in build_preload_page_order(base_page, total_pages):
        for card in list(get_cards_for_page(int(page)) or []):
            try:
                cover_path = str(get_card_cover_path(card) or "")
            except Exception:
                cover_path = ""

            if (not cover_path) or (not os.path.isfile(cover_path)):
                continue

            try:
                card_rect = get_card_rect(card)
            except Exception:
                card_rect = pygame.Rect(0, 0, 0, 0)

            layout = compute_thumbnail_card_layout(
                base_rect=card_rect,
                frame_path=frame_path,
                get_ui_image=get_ui_image,
                frame_scale_x=frame_scale_x,
                frame_scale_y=frame_scale_y,
                frame_x_offset=frame_x_offset,
                frame_y_offset_ratio=frame_y_offset_ratio,
                target_ratio=target_ratio,
            )
            cover_rect = layout["封面矩形"]
            key = (
                cover_path,
                max(1, int(cover_rect.w)),
                max(1, int(cover_rect.h)),
                0,
                "cover",
            )
            if key not in seen:
                seen.add(key)
                keys.append(key)

    return keys
