import os
import shutil
import sys


def _规范目录路径(路径: object) -> str:
    try:
        文本 = str(路径 or "").strip()
    except Exception:
        文本 = ""
    if not 文本:
        return ""
    try:
        return os.path.abspath(文本)
    except Exception:
        return ""


def _取根目录(根目录: object = "") -> str:
    规范后 = _规范目录路径(根目录)
    if 规范后:
        return 规范后
    return 取运行根目录()


def _确保父目录存在(路径: str) -> None:
    父目录 = os.path.dirname(os.path.abspath(str(路径 or "").strip()))
    if 父目录:
        os.makedirs(父目录, exist_ok=True)


def _回退到现有路径(目标路径: str, 旧路径列表: list[str]) -> str:
    if 目标路径 and os.path.exists(目标路径):
        return os.path.abspath(目标路径)
    for 旧路径 in 旧路径列表:
        if 旧路径 and os.path.exists(旧路径):
            return os.path.abspath(旧路径)
    return os.path.abspath(目标路径) if str(目标路径 or "").strip() else ""


def _尝试迁移文件(目标路径: str, *旧路径列表: str) -> str:
    目标绝对路径 = os.path.abspath(str(目标路径 or "").strip()) if str(目标路径 or "").strip() else ""
    if not 目标绝对路径:
        return ""

    if os.path.isfile(目标绝对路径):
        return 目标绝对路径

    有效旧路径列表 = [
        os.path.abspath(str(旧路径 or "").strip())
        for 旧路径 in 旧路径列表
        if str(旧路径 or "").strip()
    ]

    for 旧路径 in 有效旧路径列表:
        if (not os.path.isfile(旧路径)) or (旧路径 == 目标绝对路径):
            continue

        try:
            _确保父目录存在(目标绝对路径)
            os.replace(旧路径, 目标绝对路径)
            return 目标绝对路径
        except Exception:
            pass

        try:
            _确保父目录存在(目标绝对路径)
            shutil.copy2(旧路径, 目标绝对路径)
            try:
                os.remove(旧路径)
            except Exception:
                pass
            return 目标绝对路径
        except Exception:
            continue

    return _回退到现有路径(目标绝对路径, 有效旧路径列表)


def _尝试迁移目录(目标目录: str, *旧目录列表: str) -> str:
    目标绝对目录 = os.path.abspath(str(目标目录 or "").strip()) if str(目标目录 or "").strip() else ""
    if not 目标绝对目录:
        return ""

    if os.path.isdir(目标绝对目录):
        return 目标绝对目录

    有效旧目录列表 = [
        os.path.abspath(str(旧目录 or "").strip())
        for 旧目录 in 旧目录列表
        if str(旧目录 or "").strip()
    ]

    for 旧目录 in 有效旧目录列表:
        if (not os.path.isdir(旧目录)) or (旧目录 == 目标绝对目录):
            continue

        try:
            os.makedirs(os.path.dirname(目标绝对目录), exist_ok=True)
        except Exception:
            pass

        try:
            os.replace(旧目录, 目标绝对目录)
            return 目标绝对目录
        except Exception:
            pass

        try:
            for 当前根, 目录列表, 文件列表 in os.walk(旧目录):
                相对路径 = os.path.relpath(当前根, 旧目录)
                if 相对路径 in (".", ""):
                    目标当前根 = 目标绝对目录
                else:
                    目标当前根 = os.path.join(目标绝对目录, 相对路径)
                os.makedirs(目标当前根, exist_ok=True)

                for 目录名 in 目录列表:
                    os.makedirs(os.path.join(目标当前根, 目录名), exist_ok=True)

                for 文件名 in 文件列表:
                    源路径 = os.path.join(当前根, 文件名)
                    目标路径 = os.path.join(目标当前根, 文件名)
                    if os.path.exists(目标路径):
                        continue
                    try:
                        os.replace(源路径, 目标路径)
                    except Exception:
                        shutil.copy2(源路径, 目标路径)
                        try:
                            os.remove(源路径)
                        except Exception:
                            pass

            for 当前根, 目录列表, 文件列表 in os.walk(旧目录, topdown=False):
                if 目录列表 or 文件列表:
                    continue
                try:
                    os.rmdir(当前根)
                except Exception:
                    pass
            try:
                os.rmdir(旧目录)
            except Exception:
                pass
            return 目标绝对目录
        except Exception:
            continue

    return _回退到现有路径(目标绝对目录, 有效旧目录列表)


def 取运行根目录() -> str:
    try:
        if getattr(sys, "frozen", False):
            return os.path.dirname(os.path.abspath(sys.executable))
    except Exception:
        pass

    try:
        启动脚本路径 = str(sys.argv[0] or "").strip()
        if 启动脚本路径:
            return os.path.dirname(os.path.abspath(启动脚本路径))
    except Exception:
        pass

    try:
        return os.path.abspath(os.getcwd())
    except Exception:
        return "."


def 获取项目根目录() -> str:
    return 取运行根目录()


def 拼运行路径(*片段: str) -> str:
    return os.path.abspath(os.path.join(取运行根目录(), *片段))


def 拼路径(*片段: str) -> str:
    return 拼运行路径(*片段)


def 取项目根目录(资源: dict | None = None) -> str:
    资源字典 = 资源 if isinstance(资源, dict) else {}
    根目录 = str(资源字典.get("根", "") or "").strip()
    if 根目录:
        return os.path.abspath(根目录)
    return 取运行根目录()


def 取资源根目录(资源: dict | None = None) -> str:
    return 取项目根目录(资源)


def 取配置根目录(根目录: str | None = None) -> str:
    return os.path.join(_取根目录(根目录), "config")


def 取布局配置路径(文件名: str, 根目录: str | None = None) -> str:
    根 = _取根目录(根目录)
    return _尝试迁移文件(
        os.path.join(根, "config", "layout", str(文件名 or "").strip()),
        os.path.join(根, "json", str(文件名 or "").strip()),
    )


def 取动画配置路径(文件名: str, 根目录: str | None = None) -> str:
    根 = _取根目录(根目录)
    return _尝试迁移文件(
        os.path.join(根, "config", "animation", str(文件名 or "").strip()),
        os.path.join(根, "json", str(文件名 or "").strip()),
    )


def 取调试配置路径(文件名: str, 根目录: str | None = None) -> str:
    根 = _取根目录(根目录)
    return _尝试迁移文件(
        os.path.join(根, "config", "debug", str(文件名 or "").strip()),
        os.path.join(根, "json", str(文件名 or "").strip()),
    )


def 取应用配置路径(文件名: str, 根目录: str | None = None) -> str:
    根 = _取根目录(根目录)
    return _尝试迁移文件(
        os.path.join(根, "config", "app", str(文件名 or "").strip()),
        os.path.join(根, "json", str(文件名 or "").strip()),
    )


def 取状态根目录(根目录: str | None = None) -> str:
    return os.path.join(_取根目录(根目录), "state")


def 取状态数据库路径(
    文件名: str = "runtime_state.sqlite3",
    根目录: str | None = None,
) -> str:
    根 = _取根目录(根目录)
    return _尝试迁移文件(
        os.path.join(根, "state", str(文件名 or "").strip()),
        os.path.join(根, "json", str(文件名 or "").strip()),
    )


def 取用户数据根目录(根目录: str | None = None) -> str:
    return os.path.join(_取根目录(根目录), "userdata")


def 取个人资料目录(根目录: str | None = None) -> str:
    根 = _取根目录(根目录)
    return os.path.join(根, "userdata", "profile")


def 取个人资料路径(根目录: str | None = None) -> str:
    根 = _取根目录(根目录)
    return _尝试迁移文件(
        os.path.join(根, "userdata", "profile", "个人资料.json"),
        os.path.join(根, "json", "个人资料.json"),
    )


def 取个人资料头像目录(根目录: str | None = None) -> str:
    根 = _取根目录(根目录)
    return _尝试迁移目录(
        os.path.join(根, "userdata", "profile", "avatars"),
        os.path.join(根, "json", "个人资料"),
    )


def 拼资源路径(*片段: str, 资源: dict | None = None) -> str:
    项目根目录 = 取项目根目录(资源)

    if len(片段) == 1:
        路径 = str(片段[0] or "").strip()
        if not 路径:
            return ""
        if os.path.isabs(路径):
            return os.path.abspath(路径)
        return os.path.abspath(os.path.join(项目根目录, 路径))

    return os.path.abspath(os.path.join(项目根目录, *片段))


def 取songs根目录(
    资源: dict | None = None,
    状态: dict | None = None,
) -> str:
    候选路径列表: list[str] = []

    if isinstance(状态, dict):
        候选路径列表.extend(
            [
                _规范目录路径(状态.get("外置songs根目录", "")),
                _规范目录路径(状态.get("songs根目录", "")),
            ]
        )

    if isinstance(资源, dict):
        候选路径列表.extend(
            [
                _规范目录路径(资源.get("外置songs根目录", "")),
                _规范目录路径(资源.get("songs根目录", "")),
            ]
        )

    for 候选路径 in 候选路径列表:
        if 候选路径 and os.path.isdir(候选路径):
            return 候选路径

    return 拼资源路径("songs", 资源=资源)



def 默认资源路径() -> dict:
    根 = 取运行根目录()
    return {
        "背景_玩家": 拼路径("冷资源", "backimages", "b_scene_screen.png"),
        "背景_模式": 拼路径("冷资源", "backimages", "scene2.jpg"),
        "背景_子模式": 拼路径("冷资源", "backimages", "scene3.jpg"),
        "图_花式": 拼路径("UI-img", "大模式选择界面", "按钮", "花式模式按钮.png"),
        "图_竞速": 拼路径("UI-img", "大模式选择界面", "按钮", "竞速模式按钮.png"),
        "图_疯狂": 拼路径("UI-img", "玩法选择界面", "按钮", "疯狂模式按钮.png"),
        "图_混音": 拼路径("UI-img", "玩法选择界面", "按钮", "混音模式按钮.png"),
        "图_表演候选": [
            拼路径("UI-img", "玩法选择界面", "按钮", "表演模式按钮.png"),
            拼路径("UI-img", "玩法选择界面", "按钮", "花式表演按钮.png"),
            拼路径("UI-img", "玩法选择界面", "按钮", "竞速表演按钮.png"),
        ],
        "图_club候选": [
            拼路径("UI-img", "玩法选择界面", "按钮", "club模式按钮.png"),
            拼路径("UI-img", "玩法选择界面", "按钮", "花式club按钮.png"),
            拼路径("UI-img", "玩法选择界面", "按钮", "竞速club按钮.png"),
        ],
        "音乐_开始": 拼路径("冷资源", "backsound", "back_music_logo.mp3"),
        "音乐_UI": 拼路径("冷资源", "backsound", "back_music_ui.mp3"),
        "音乐_show": 拼路径("冷资源", "backsound", "show.mp3"),
        "音乐_devil": 拼路径("冷资源", "backsound", "devil.mp3"),
        "音乐_remix": 拼路径("冷资源", "backsound", "remix.mp3"),
        "音乐_club": 拼路径("冷资源", "backsound", "club.mp3"),
        "backmovies目录": 拼路径("backmovies"),
        "投币_背景视频": "",
        "投币_BGM": 拼路径("冷资源", "backsound", "back_music_logo.mp3"),
        "投币_logo": 拼路径("UI-img", "拼贴banner", "大logo.png"),
        "投币_联网图标": 拼路径("UI-img", "联网状态", "已联网.png"),
        "投币_按钮": 拼路径("UI-img", "投币界面", "投币按钮.png"),
        "1P按钮": 拼路径("UI-img", "玩家选择界面", "1P.png"),
        "2P按钮": 拼路径("UI-img", "玩家选择界面", "2P.png"),
        "登陆_top背景": 拼路径("UI-img", "top栏", "top栏背景.png"),
        "登陆_个人中心": 拼路径("UI-img", "top栏", "个人中心.png"),
        "登陆_场景1_游客": 拼路径("UI-img", "个人中心-登陆", "场景1-游客.png"),
        "登陆_场景1_vip半透明": 拼路径("UI-img", "个人中心-登陆", "场景1-vip磁卡-半透明.png"),
        "登陆_场景2_游客": 拼路径("UI-img", "个人中心-登陆", "场景2-游客.png"),
        "登陆_请刷卡背景": 拼路径("UI-img", "个人中心-登陆", "请刷卡背景.png"),
        "登陆_请刷卡内容": 拼路径("UI-img", "个人中心-登陆", "请刷卡内容.png"),
        "登陆_请刷卡内容白": 拼路径("UI-img", "个人中心-登陆", "请刷卡内容白色.png"),
        "登陆_磁卡": 拼路径("UI-img", "个人中心-登陆", "磁卡.png"),
        "按钮音效": 拼路径("冷资源", "Buttonsound", "点击-增益5.mp3"),
        "投币音效": 拼路径("冷资源", "Buttonsound", "投币.mp3"),
        "刷卡音效": 拼路径("冷资源", "Buttonsound", "刷卡+5.mp3"),
        "根": 根,
    }
