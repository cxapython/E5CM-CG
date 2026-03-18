import time

import pygame


def bind_select_scene_host_adapter(select_game_cls, refresh_layout_constants):
    def bind_external_surface(self, external_screen: pygame.Surface):
        if external_screen is None:
            return
        try:
            old_size = (int(getattr(self, "宽", 0) or 0), int(getattr(self, "高", 0) or 0))
        except Exception:
            old_size = (0, 0)

        self.屏幕 = external_screen
        try:
            self.宽, self.高 = self.屏幕.get_size()
        except Exception:
            self.宽, self.高 = (0, 0)

        new_size = (int(self.宽), int(self.高))
        if new_size != old_size:
            try:
                self.重算布局()
                self.安排预加载(基准页=int(getattr(self, "当前页", 0) or 0))
            except Exception:
                pass

    def frame_update(self):
        self._确保公共交互()

        if bool(getattr(self, "_需要退出", False)):
            return str(getattr(self, "_返回状态", "NORMAL") or "NORMAL")

        try:
            current_second = float(time.perf_counter())
            previous_second = float(
                getattr(self, "_动态背景上次刷新秒", current_second) or current_second
            )
            self._动态背景上次刷新秒 = current_second
            self._更新动态背景模块(
                float(max(0.0, current_second - previous_second)),
                current_second,
            )
            self.更新动画状态()
            self.每帧执行预加载(每帧数量=3)
            self._更新连续翻页()
            self._更新过渡()
        except Exception:
            pass

        if bool(getattr(self, "_需要退出", False)):
            return str(getattr(self, "_返回状态", "NORMAL") or "NORMAL")
        return None

    def frame_draw(self):
        self._确保公共交互()

        try:
            use_gpu_ui = bool(getattr(self, "_应使用GPU界面", lambda: False)())
            try:
                refresh_layout_constants()
            except Exception:
                pass

            self.绘制背景()
            if not bool(use_gpu_ui):
                self.绘制顶部()

                if bool(getattr(self, "动画中", False)):
                    self.绘制列表页_动画()
                else:
                    self.绘制列表页()

                if not bool(getattr(self, "是否详情页", False)):
                    self._绘制列表翻页按钮()

                if bool(getattr(self, "是否详情页", False)):
                    self.绘制详情浮层()
                    try:
                        self.绘制详情角标_大图()
                    except Exception:
                        pass
                else:
                    try:
                        self.确保播放背景音乐()
                    except Exception:
                        pass

                self.绘制底部()
            else:
                try:
                    if not bool(getattr(self, "是否详情页", False)):
                        self.确保播放背景音乐()
                except Exception:
                    pass
                if bool(getattr(self, "是否详情页", False)):
                    self.绘制详情浮层()
                    try:
                        self.绘制详情角标_大图()
                    except Exception:
                        pass

            if bool(getattr(self, "是否星级筛选页", False)):
                self.绘制星级筛选页()

            if bool(getattr(self, "是否设置页", False)):
                try:
                    self.绘制设置页()
                except Exception:
                    pass

            self._绘制过渡()

            try:
                if getattr(self, "_全局点击特效", None) is not None:
                    self._全局点击特效.更新并绘制(self.屏幕)
            except Exception:
                pass

            try:
                self._绘制消息提示()
            except Exception:
                pass
        except Exception:
            pass

    def handle_external_event(self, event):
        self._确保公共交互()

        if event is None:
            return None

        if event.type == pygame.VIDEORESIZE:
            try:
                new_screen = pygame.display.get_surface()
                if new_screen is not None:
                    self.屏幕 = new_screen
                self.重算布局()
                self.安排预加载(基准页=int(getattr(self, "当前页", 0) or 0))
                if bool(getattr(self, "是否设置页", False)):
                    try:
                        self._重算设置页布局()
                    except Exception:
                        pass
            except Exception:
                pass
            return None

        if event.type == pygame.QUIT:
            self._返回状态 = "NORMAL"
            self._需要退出 = True
            return "NORMAL"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:
                if getattr(self, "_全局点击特效", None) is not None:
                    x, y = event.pos
                    self._全局点击特效.触发(int(x), int(y))
            except Exception:
                pass

        try:
            if (
                getattr(self, "_过渡_特效", None) is not None
                and self._过渡_特效.是否动画中()
            ):
                if event.type != pygame.MOUSEMOTION:
                    return None
        except Exception:
            pass

        if bool(getattr(self, "是否设置页", False)):
            try:
                self._设置页_处理事件(event)
            except Exception:
                pass
            return None

        if bool(getattr(self, "是否星级筛选页", False)):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.筛选页面板矩形.collidepoint(event.pos):
                    self._启动过渡(
                        self._特效_按钮,
                        pygame.Rect(event.pos[0] - 20, event.pos[1] - 20, 40, 40),
                        self.关闭星级筛选页,
                    )
                    return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._启动过渡(
                    self._特效_按钮,
                    pygame.Rect(
                        self.筛选页面板矩形.centerx - 60,
                        self.筛选页面板矩形.y + 20,
                        120,
                        50,
                    ),
                    self.关闭星级筛选页,
                )
                return None

            for _, button in self.星级按钮列表:
                try:
                    button.处理事件(event)
                except Exception:
                    pass
            return None

        try:
            if self.按钮_歌曲分类.处理事件(event):
                self._启动过渡(
                    self._特效_按钮,
                    self.按钮_歌曲分类.矩形,
                    self.打开星级筛选页,
                )
        except Exception:
            pass

        try:
            if self.按钮_收藏夹.处理事件(event):
                self._启动过渡(
                    self._特效_按钮,
                    self.按钮_收藏夹.矩形,
                    self._切换收藏夹模式,
                )
        except Exception:
            pass

        try:
            if self.按钮_ALL.处理事件(event):
                self._启动过渡(
                    self._特效_按钮,
                    self.按钮_ALL.矩形,
                    self._重置列表筛选,
                )
        except Exception:
            pass

        try:
            if self.按钮_2P加入.处理事件(event):
                self._启动过渡(
                    self._特效_按钮,
                    self.按钮_2P加入.矩形,
                    lambda: self.显示消息提示(
                        "别做梦了你根本没有舞搭子 (*^__^*) 嘻嘻……",
                        持续秒=2.0,
                    ),
                )
        except Exception:
            pass

        try:
            if self.按钮_设置.处理事件(event):
                self._启动过渡(
                    self._特效_按钮,
                    self.按钮_设置.矩形,
                    self.打开设置页,
                )
        except Exception:
            pass

        try:
            if self.按钮_重选模式.处理事件(event):
                self._启动过渡(
                    self._特效_按钮,
                    self.按钮_重选模式.矩形,
                    self.请求回主程序重新选歌,
                )
                return None
        except Exception:
            pass

        if bool(getattr(self, "动画中", False)):
            return None

        if bool(getattr(self, "是否详情页", False)):
            try:
                previous_triggered = self.按钮_详情上一首.处理事件(event)
                next_triggered = self.按钮_详情下一首.处理事件(event)
                favorite_triggered = self.按钮_详情收藏.处理事件(event)

                if previous_triggered:
                    self._启动过渡(
                        self._特效_按钮,
                        self.按钮_详情上一首.矩形,
                        self.上一首,
                        覆盖图片=self.按钮_详情上一首._获取缩放图(),
                    )
                    return None
                if next_triggered:
                    self._启动过渡(
                        self._特效_按钮,
                        self.按钮_详情下一首.矩形,
                        self.下一首,
                        覆盖图片=self.按钮_详情下一首._获取缩放图(),
                    )
                    return None
                if favorite_triggered:
                    self._启动过渡(
                        self._特效_按钮,
                        self.按钮_详情收藏.矩形,
                        self._切换当前歌曲收藏,
                        覆盖图片=self.按钮_详情收藏._获取缩放图(),
                    )
                    return None
            except Exception:
                pass

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                try:
                    hits_side_buttons = (
                        self.按钮_详情上一首.矩形.collidepoint(event.pos)
                        or self.按钮_详情下一首.矩形.collidepoint(event.pos)
                        or self.按钮_详情收藏.矩形.collidepoint(event.pos)
                    )
                except Exception:
                    hits_side_buttons = False

                if (not hits_side_buttons) and self.详情大框矩形.collidepoint(event.pos):
                    self._启动过渡(
                        self._特效_大图确认,
                        self.详情大框矩形,
                        self._记录并处理大图确认点击,
                    )
                    return None

                if (not hits_side_buttons) and (
                    not self.详情大框矩形.collidepoint(event.pos)
                ):
                    self._启动过渡(
                        self._特效_按钮,
                        pygame.Rect(event.pos[0] - 20, event.pos[1] - 20, 40, 40),
                        self.返回列表,
                    )
                    return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._启动过渡(
                        self._特效_按钮,
                        self.详情大框矩形,
                        self.返回列表,
                    )
                    return None
                if event.key == pygame.K_LEFT:
                    try:
                        self._播放按钮音效()
                    except Exception:
                        pass
                    self.上一首()
                    return None
                if event.key == pygame.K_RIGHT:
                    try:
                        self._播放按钮音效()
                    except Exception:
                        pass
                    self.下一首()
                    return None

            return None

        self._处理列表页输入(event)

        if bool(getattr(self, "_需要退出", False)):
            return str(getattr(self, "_返回状态", "NORMAL") or "NORMAL")
        return None

    select_game_cls.绑定外部屏幕 = bind_external_surface
    select_game_cls.帧更新 = frame_update
    select_game_cls.帧绘制 = frame_draw
    select_game_cls.处理事件_外部 = handle_external_event
