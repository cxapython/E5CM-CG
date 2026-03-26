from __future__ import annotations

from typing import Callable, Optional

import pygame


UIImageGetter = Callable[[str, bool], Optional[pygame.Surface]]

_THUMBNAIL_FRAME_DESIGN_HEIGHT = 256.0
_THUMBNAIL_VISIBLE_BOTTOM_PX = 231.0
_DEFAULT_SLOT_PARAMS = {
    "small": {
        "封面左占比": 0.10,
        "封面上占比": 0.045,
        "封面宽占比": 0.845,
        "封面高占比": 0.940,
        "信息条高占比": 0.315,
        "信息条左右内边距占比": 0.035,
        "星区上内边距占比": 0.0,
        "星区高占比": 0.34,
        "文本区左右内边距占比": 0.040,
        "底栏高占比": 0.22,
        "底栏底部留白占比": 0.18,
    },
    "large": {
        "封面左占比": 0.05,
        "封面上占比": 0.02,
        "封面宽占比": 0.95,
        "封面高占比": 1.0,
        "信息条高占比": 0.35,
        "信息条左右内边距占比": 0.040,
        "星区上内边距占比": 0.050,
        "星区高占比": 0.3,
        "文本区左右内边距占比": 0.050,
        "底栏高占比": 0.245,
        "底栏底部留白占比": 0.06,
    },
}


def _safe_float(value: object, fallback: float) -> float:
    try:
        return float(value)
    except Exception:
        return float(fallback)


def _resolve_slot_params(is_large: bool, slot_params: Optional[dict]) -> dict:
    profile_key = "large" if bool(is_large) else "small"
    resolved = dict(_DEFAULT_SLOT_PARAMS[profile_key])
    if not isinstance(slot_params, dict):
        return resolved
    for key in resolved.keys():
        if key in slot_params:
            resolved[key] = _safe_float(slot_params.get(key), resolved[key])
    return resolved


def _is_visible_anchor_mode(anchor_mode: object) -> bool:
    text = str(anchor_mode or "").strip().lower()
    return text in ("visible", "cover_visible", "封面可视", "封面可视底", "可视")


def compute_frame_slot_layout(
    frame_rect: pygame.Rect,
    is_large: bool,
    slot_params: Optional[dict] = None,
    small_visible_bottom_px: Optional[float] = None,
    small_frame_design_height: Optional[float] = None,
    small_info_anchor: Optional[str] = "visible",
) -> dict:
    frame_width = max(1, int(frame_rect.w))
    frame_height = max(1, int(frame_rect.h))

    params = _resolve_slot_params(bool(is_large), slot_params)

    def clamp_rect(rect: pygame.Rect, outer_rect: pygame.Rect) -> pygame.Rect:
        x = max(outer_rect.left, min(rect.x, outer_rect.right - 1))
        y = max(outer_rect.top, min(rect.y, outer_rect.bottom - 1))
        w = max(1, min(rect.w, outer_rect.right - x))
        h = max(1, min(rect.h, outer_rect.bottom - y))
        return pygame.Rect(x, y, w, h)

    cover_rect = pygame.Rect(
        int(round(frame_rect.x + frame_width * params["封面左占比"])),
        int(round(frame_rect.y + frame_height * params["封面上占比"])),
        max(1, int(round(frame_width * params["封面宽占比"]))),
        max(1, int(round(frame_height * params["封面高占比"]))),
    )
    cover_rect = clamp_rect(cover_rect, frame_rect)

    cover_visible_rect = cover_rect.copy()
    if not is_large:
        design_height = max(
            1.0,
            _safe_float(small_frame_design_height, _THUMBNAIL_FRAME_DESIGN_HEIGHT),
        )
        visible_bottom_px = _safe_float(
            small_visible_bottom_px, _THUMBNAIL_VISIBLE_BOTTOM_PX
        )
        # Small-card frame art has a visible lower border above the texture tail.
        # Cover should be clipped here so overflow is hidden.
        visible_bottom = int(
            round(
                frame_rect.y
                + frame_height
                * (visible_bottom_px / design_height)
            )
        )
        visible_bottom = max(cover_visible_rect.top + 1, min(cover_rect.bottom, visible_bottom))
        visible_height = max(1, min(cover_visible_rect.h, visible_bottom - cover_visible_rect.y))
        cover_visible_rect.h = visible_height
        cover_visible_rect = clamp_rect(cover_visible_rect, cover_rect)

    # Single-anchor model:
    # small cards default to visible-bottom anchor to avoid mixed-bottom gaps.
    if (not is_large) and _is_visible_anchor_mode(small_info_anchor):
        info_anchor_rect = cover_visible_rect
    else:
        info_anchor_rect = cover_rect
    info_bar_height = max(
        14, int(round(info_anchor_rect.h * params["信息条高占比"]))
    )
    info_bar_rect = pygame.Rect(
        info_anchor_rect.x,
        info_anchor_rect.bottom - info_bar_height,
        info_anchor_rect.w,
        info_bar_height,
    )
    info_bar_rect = clamp_rect(info_bar_rect, info_anchor_rect)

    info_bar_padding_x = max(
        4, int(round(info_bar_rect.w * params["信息条左右内边距占比"]))
    )
    text_padding_x = max(4, int(round(info_bar_rect.w * params["文本区左右内边距占比"])))

    star_rect = pygame.Rect(
        info_bar_rect.x + info_bar_padding_x,
        info_bar_rect.y
        + max(1, int(round(info_bar_rect.h * params["星区上内边距占比"]))),
        max(10, info_bar_rect.w - info_bar_padding_x * 2),
        max(6, int(round(info_bar_rect.h * params["星区高占比"]))),
    )
    star_rect = clamp_rect(star_rect, info_bar_rect)

    bottom_bar_height = max(10, int(round(info_bar_rect.h * params["底栏高占比"])))
    bottom_bar_bottom_padding = max(
        1, int(round(info_bar_rect.h * params["底栏底部留白占比"]))
    )
    bottom_bar_rect = pygame.Rect(
        info_bar_rect.x + text_padding_x,
        info_bar_rect.bottom - bottom_bar_height - bottom_bar_bottom_padding,
        max(10, info_bar_rect.w - text_padding_x * 2),
        bottom_bar_height,
    )
    bottom_bar_rect = clamp_rect(bottom_bar_rect, info_bar_rect)

    center_gap = max(8, int(round(bottom_bar_rect.w * 0.05)))
    left_width = max(10, int(round(bottom_bar_rect.w * 0.52)))
    left_width = min(left_width, max(10, bottom_bar_rect.w - center_gap - 10))
    right_width = max(10, bottom_bar_rect.w - left_width - center_gap)

    play_count_rect = pygame.Rect(
        bottom_bar_rect.x,
        bottom_bar_rect.y,
        left_width,
        bottom_bar_rect.h,
    )
    bpm_rect = pygame.Rect(
        bottom_bar_rect.right - right_width,
        bottom_bar_rect.y,
        right_width,
        bottom_bar_rect.h,
    )

    play_count_rect = clamp_rect(play_count_rect, bottom_bar_rect)
    bpm_rect = clamp_rect(bpm_rect, bottom_bar_rect)

    return {
        "封面矩形": cover_rect,
        "封面可视矩形": cover_visible_rect,
        "信息条矩形": info_bar_rect,
        "星星区域": star_rect,
        "游玩区域": play_count_rect,
        "bpm区域": bpm_rect,
    }


def compute_thumbnail_frame_rect(
    base_rect: pygame.Rect,
    frame_path: str,
    get_ui_image: UIImageGetter,
    frame_scale_x: float,
    frame_scale_y: float,
    frame_x_offset: int,
    frame_y_offset_ratio: float,
    target_ratio: Optional[float] = None,
) -> pygame.Rect:
    try:
        frame_scale_x = float(frame_scale_x)
    except Exception:
        frame_scale_x = 1.0
    try:
        frame_scale_y = float(frame_scale_y)
    except Exception:
        frame_scale_y = 1.0
    try:
        frame_x_offset = int(frame_x_offset)
    except Exception:
        frame_x_offset = 0
    try:
        frame_y_offset = int(round(float(frame_y_offset_ratio) * float(base_rect.h)))
    except Exception:
        frame_y_offset = 0

    frame_scale_x = max(0.05, min(5.0, frame_scale_x))
    frame_scale_y = max(0.05, min(5.0, frame_scale_y))
    candidate_width = max(1, int(round(float(base_rect.w) * frame_scale_x)))
    candidate_height = max(1, int(round(float(base_rect.h) * frame_scale_y)))

    if candidate_width <= 0 or candidate_height <= 0:
        return pygame.Rect(
            int(base_rect.x + frame_x_offset),
            int(base_rect.y + frame_y_offset),
            max(1, int(base_rect.w)),
            max(1, int(base_rect.h)),
        )

    if target_ratio is not None:
        try:
            layout_ratio = float(target_ratio)
        except Exception:
            layout_ratio = 4.0 / 3.0
    else:
        original_frame = get_ui_image(frame_path, True)
        if original_frame is not None:
            try:
                original_width, original_height = original_frame.get_size()
            except Exception:
                original_width, original_height = (0, 0)
        else:
            original_width, original_height = (0, 0)

        if original_width <= 0 or original_height <= 0:
            original_width = max(1, int(base_rect.w))
            original_height = max(1, int(base_rect.h))

        layout_ratio = float(original_width) / float(max(1, original_height))

    layout_ratio = max(0.2, min(5.0, layout_ratio))

    if (float(candidate_width) / float(max(1, candidate_height))) > layout_ratio:
        frame_height = candidate_height
        frame_width = max(1, int(round(float(frame_height) * layout_ratio)))
    else:
        frame_width = candidate_width
        frame_height = max(1, int(round(float(frame_width) / max(0.001, layout_ratio))))

    frame_rect = pygame.Rect(0, 0, frame_width, frame_height)
    frame_rect.center = base_rect.center
    frame_rect.x += int(frame_x_offset)
    frame_rect.y += int(frame_y_offset)
    return frame_rect


def compute_thumbnail_card_layout(
    base_rect: pygame.Rect,
    frame_path: str,
    get_ui_image: UIImageGetter,
    frame_scale_x: float,
    frame_scale_y: float,
    frame_x_offset: int,
    frame_y_offset_ratio: float,
    target_ratio: Optional[float] = None,
    slot_params: Optional[dict] = None,
    small_visible_bottom_px: Optional[float] = None,
    small_frame_design_height: Optional[float] = None,
    small_info_anchor: Optional[str] = "visible",
) -> dict:
    frame_rect = compute_thumbnail_frame_rect(
        base_rect=base_rect,
        frame_path=frame_path,
        get_ui_image=get_ui_image,
        frame_scale_x=frame_scale_x,
        frame_scale_y=frame_scale_y,
        frame_x_offset=frame_x_offset,
        frame_y_offset_ratio=frame_y_offset_ratio,
        target_ratio=target_ratio,
    )
    local_frame_rect = pygame.Rect(0, 0, frame_rect.w, frame_rect.h)
    layout = dict(
        compute_frame_slot_layout(
            local_frame_rect,
            is_large=False,
            slot_params=slot_params,
            small_visible_bottom_px=small_visible_bottom_px,
            small_frame_design_height=small_frame_design_height,
            small_info_anchor=small_info_anchor,
        )
    )
    layout["框矩形"] = frame_rect
    layout["局部框矩形"] = local_frame_rect
    return layout
