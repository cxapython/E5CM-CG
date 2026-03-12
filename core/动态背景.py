from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type

import pygame

try:
    from pygame._sdl2 import video as _sdl2_video
except Exception:
    _sdl2_video = None


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def clamp_int(value: float, minimum: int, maximum: int) -> int:
    return int(round(clamp(float(value), float(minimum), float(maximum))))


def lerp(start: float, end: float, amount: float) -> float:
    return float(start) + (float(end) - float(start)) * float(amount)


def smooth_towards(current: float, target: float, speed: float, delta_time: float) -> float:
    if delta_time <= 0.0:
        return float(current)
    mix = 1.0 - math.exp(-max(0.0, float(speed)) * float(delta_time))
    return lerp(float(current), float(target), mix)


def ease_out_cubic(value: float) -> float:
    value = clamp(float(value), 0.0, 1.0)
    return 1.0 - (1.0 - value) ** 3


@dataclass
class DynamicBackgroundContext:
    renderer: Any
    screen_size: Tuple[int, int]
    combo: int
    now: float
    delta_time: float = 0.0
    resource_root: str = ""
    runtime_root: str = ""
    project_root: str = ""
    preview: bool = False
    paused: bool = False


class DynamicBackgroundBase:
    mode_name = "关闭"

    def __init__(self, resource_root: str = "", runtime_root: str = "", project_root: str = ""):
        self.resource_root = str(resource_root or "")
        self.runtime_root = str(runtime_root or "")
        self.project_root = str(project_root or "")
        self._renderer_id: int = 0
        self._surface_cache: Dict[str, Optional[pygame.Surface]] = {}
        self._texture_cache: Dict[str, Any] = {}

    def configure_paths(self, resource_root: str = "", runtime_root: str = "", project_root: str = ""):
        self.resource_root = str(resource_root or self.resource_root or "")
        self.runtime_root = str(runtime_root or self.runtime_root or "")
        self.project_root = str(project_root or self.project_root or "")

    def reset(self):
        return None

    def dispose(self):
        self._texture_cache.clear()
        self._surface_cache.clear()
        self._renderer_id = 0

    def update(self, context: DynamicBackgroundContext):
        return None

    def render(self, context: DynamicBackgroundContext):
        raise NotImplementedError

    def render_preview_surface(
        self,
        target_surface: pygame.Surface,
        target_rect: Optional[pygame.Rect] = None,
        *,
        now: float = 0.0,
    ) -> bool:
        return False

    def _sync_renderer_cache(self, renderer):
        renderer_id = int(id(renderer))
        if renderer_id == int(self._renderer_id):
            return
        self._renderer_id = renderer_id
        self._texture_cache.clear()

    def _resolve_asset_path(self, *relative_parts: str) -> str:
        normalized = [str(part or "").replace("/", os.sep).replace("\\", os.sep) for part in relative_parts]
        candidates = []
        for base in (self.resource_root, self.project_root, self.runtime_root):
            if not base:
                continue
            candidate = os.path.abspath(os.path.join(base, *normalized))
            if candidate not in candidates:
                candidates.append(candidate)
        for candidate in candidates:
            try:
                if os.path.isfile(candidate):
                    return candidate
            except Exception:
                continue
        return str(candidates[0] if candidates else "")

    def _load_image(self, cache_key: str, *relative_parts: str) -> Optional[pygame.Surface]:
        cache_key = str(cache_key or "")
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
        path = self._resolve_asset_path(*relative_parts)
        if not path or (not os.path.isfile(path)):
            self._surface_cache[cache_key] = None
            return None
        try:
            surface = pygame.image.load(path).convert_alpha()
        except Exception:
            surface = None
        self._surface_cache[cache_key] = surface
        return surface

    def _get_texture(self, renderer, cache_key: str, surface: Optional[pygame.Surface]):
        if _sdl2_video is None or renderer is None or not isinstance(surface, pygame.Surface):
            return None
        self._sync_renderer_cache(renderer)
        cache_key = str(cache_key or "")
        texture = self._texture_cache.get(cache_key, None)
        if texture is not None:
            return texture
        try:
            texture = _sdl2_video.Texture.from_surface(renderer, surface)
            texture.blend_mode = 1
        except Exception:
            return None
        self._texture_cache[cache_key] = texture
        return texture

    @staticmethod
    def _set_draw_color(renderer, color: Tuple[int, int, int], alpha: int = 255):
        if renderer is None:
            return
        try:
            renderer.draw_blend_mode = 1
        except Exception:
            pass
        try:
            renderer.draw_color = (
                clamp_int(color[0], 0, 255),
                clamp_int(color[1], 0, 255),
                clamp_int(color[2], 0, 255),
                clamp_int(alpha, 0, 255),
            )
        except Exception:
            pass

    def _draw_texture(
        self,
        texture,
        dstrect,
        *,
        alpha: int = 255,
        color: Tuple[int, int, int] = (255, 255, 255),
        angle: float = 0.0,
        origin=None,
        flip_x: bool = False,
        flip_y: bool = False,
    ):
        if texture is None:
            return
        try:
            texture.alpha = clamp_int(alpha, 0, 255)
        except Exception:
            pass
        try:
            texture.color = (
                clamp_int(color[0], 0, 255),
                clamp_int(color[1], 0, 255),
                clamp_int(color[2], 0, 255),
            )
        except Exception:
            pass
        try:
            texture.blend_mode = 1
        except Exception:
            pass
        try:
            texture.draw(
                dstrect=dstrect,
                angle=float(angle),
                origin=origin,
                flip_x=bool(flip_x),
                flip_y=bool(flip_y),
            )
        except Exception:
            return


class DynamicBackgroundManager:
    _REGISTRY: Dict[str, Type[DynamicBackgroundBase]] = {}
    _ALIASES: Dict[str, str] = {
        "关闭": "关闭",
        "off": "关闭",
        "none": "关闭",
    }
    _BUILTINS_READY: bool = False

    def __init__(self, resource_root: str = "", runtime_root: str = "", project_root: str = ""):
        self.resource_root = str(resource_root or "")
        self.runtime_root = str(runtime_root or "")
        self.project_root = str(project_root or "")
        self._instances: Dict[str, DynamicBackgroundBase] = {}

    @classmethod
    def register_class(cls, background_cls: Type[DynamicBackgroundBase], *aliases: str):
        name = str(getattr(background_cls, "mode_name", "") or "").strip()
        if not name or name == "关闭":
            return
        cls._REGISTRY[name] = background_cls
        cls._ALIASES[str(name).lower()] = name
        for alias in aliases:
            text = str(alias or "").strip()
            if text:
                cls._ALIASES[text.lower()] = name

    @classmethod
    def _ensure_builtin_backgrounds(cls):
        if bool(cls._BUILTINS_READY):
            return
        cls._BUILTINS_READY = True
        try:
            import ui.dynamic_background  # noqa: F401
        except Exception:
            return

    @classmethod
    def normalize_mode(cls, value) -> str:
        cls._ensure_builtin_backgrounds()
        text = str(value or "").strip()
        if not text:
            return "关闭"
        if text in cls._REGISTRY:
            return text
        return str(cls._ALIASES.get(text.lower(), "关闭"))

    @classmethod
    def get_candidate_modes(cls) -> List[str]:
        cls._ensure_builtin_backgrounds()
        return ["关闭", *cls._REGISTRY.keys()]

    def configure_paths(self, resource_root: str = "", runtime_root: str = "", project_root: str = ""):
        if resource_root:
            self.resource_root = str(resource_root)
        if runtime_root:
            self.runtime_root = str(runtime_root)
        if project_root:
            self.project_root = str(project_root)
        for instance in self._instances.values():
            instance.configure_paths(
                resource_root=self.resource_root,
                runtime_root=self.runtime_root,
                project_root=self.project_root,
            )

    def reset(self):
        for instance in self._instances.values():
            instance.reset()

    def dispose(self):
        for instance in self._instances.values():
            try:
                instance.dispose()
            except Exception:
                continue
        self._instances.clear()

    def _get_instance(self, mode: str) -> Optional[DynamicBackgroundBase]:
        self._ensure_builtin_backgrounds()
        canonical = self.normalize_mode(mode)
        if canonical == "关闭":
            return None
        instance = self._instances.get(canonical, None)
        if instance is not None:
            return instance
        cls = self._REGISTRY.get(canonical, None)
        if cls is None:
            return None
        instance = cls(
            resource_root=self.resource_root,
            runtime_root=self.runtime_root,
            project_root=self.project_root,
        )
        self._instances[canonical] = instance
        return instance

    def update(self, mode: str, context: DynamicBackgroundContext):
        instance = self._get_instance(mode)
        if instance is None:
            return
        instance.update(context)

    def render(self, mode: str, context: DynamicBackgroundContext):
        instance = self._get_instance(mode)
        if instance is None:
            return
        instance.render(context)

    def render_preview_surface(
        self,
        mode: str,
        target_surface: pygame.Surface,
        target_rect: Optional[pygame.Rect] = None,
        *,
        now: float = 0.0,
    ) -> bool:
        instance = self._get_instance(mode)
        if instance is None or not isinstance(target_surface, pygame.Surface):
            return False
        try:
            return bool(
                instance.render_preview_surface(
                    target_surface,
                    target_rect,
                    now=float(now),
                )
            )
        except Exception:
            return False
