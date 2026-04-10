#!/bin/zsh
set -e

# ========== 配置 ==========
APP_NAME="E5CM-CG"
ENTRY="main.py"
ICON_ICO="UI-img/app.ico"
ICON_ICNS="UI-img/app.icns"
DIST_DIR="dist_mac"
BUILD_DIR="build_mac"
# ==========================

echo "【1/5】检查虚拟环境 .venv..."
if [ ! -f ".venv/bin/python" ]; then
    echo "错误：.venv 不存在，请先创建虚拟环境。"
    exit 1
fi
source .venv/bin/activate

echo "【2/5】安装/确认 PyInstaller..."
pip install --quiet pyinstaller pillow

echo "【3/5】生成 macOS .icns 图标..."
if [ -f "$ICON_ICO" ]; then
    python3 << 'PYEOF'
import os, sys
from PIL import Image

ico_path = "UI-img/app.ico"
icns_path = "UI-img/app.icns"

img = Image.open(ico_path)
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# 生成 iconset
iconset_dir = "UI-img/app.iconset"
os.makedirs(iconset_dir, exist_ok=True)

sizes = [16, 32, 64, 128, 256, 512]
for size in sizes:
    img_resized = img.resize((size, size), Image.LANCZOS)
    img_resized.save(os.path.join(iconset_dir, f"icon_{size}x{size}.png"))
    if size <= 256:
        img_resized2 = img.resize((size*2, size*2), Image.LANCZOS)
        img_resized2.save(os.path.join(iconset_dir, f"icon_{size}x{size}@2x.png"))

os.system(f"iconutil -c icns {iconset_dir} -o {icns_path}")
os.system(f"rm -rf {iconset_dir}")
print(f"已生成: {icns_path}")
PYEOF
else
    echo "警告：未找到 $ICON_ICO，将使用默认图标。"
    ICON_ICNS=""
fi

echo "【4/5】开始用 PyInstaller 打包（Apple Silicon arm64）..."

# 数据目录：需要被打进 .app/Contents/MacOS/ 下的同级目录中
ADD_DATA_ARGS=(
    --add-data "UI-img:UI-img"
    --add-data "backmovies:backmovies"
    --add-data "config:config"
    --add-data "core:core"
    --add-data "scenes:scenes"
    --add-data "ui:ui"
    --add-data "冷资源:冷资源"
    --add-data "userdata:userdata"
    --add-data "state:state"
)

# 自动扫描并收集 core/scenes/ui 下的所有 .py 作为 hidden-import
HIDDEN_IMPORTS=()
for d in core scenes ui; do
    if [ -d "$d" ]; then
        for f in $(find "$d" -name '*.py' | sed 's|/|.|g' | sed 's|\.py$||' | sed 's|^\.__init__$||'); do
            HIDDEN_IMPORTS+=("--hidden-import" "$f")
        done
    fi
done

echo "共发现 $((${#HIDDEN_IMPORTS[@]} / 2)) 个 hidden imports。"

# tkinter / customtkinter 资源
HIDDEN_IMPORTS+=(
    "--hidden-import" "tkinter"
    "--hidden-import" "tkinter.font"
    "--hidden-import" "tkinter.ttk"
    "--hidden-import" "customtkinter"
    "--hidden-import" "tkinterdnd2"
    "--hidden-import" "PIL"
    "--hidden-import" "PIL.Image"
    "--hidden-import" "PIL.ImageTk"
    "--hidden-import" "pygame"
    "--hidden-import" "av"
    "--hidden-import" "numpy"
)

ICON_ARG=()
if [ -f "$ICON_ICNS" ]; then
    ICON_ARG=("--icon" "$ICON_ICNS")
fi

pyinstaller \
    --name "$APP_NAME" \
    --windowed \
    --target-arch arm64 \
    --osx-bundle-identifier "com.e5cmcg.app" \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR" \
    --noconfirm \
    --clean \
    --collect-all customtkinter \
    --collect-all tkinterdnd2 \
    "${ICON_ARG[@]}" \
    "${ADD_DATA_ARGS[@]}" \
    "${HIDDEN_IMPORTS[@]}" \
    "$ENTRY"

echo "【5/5】收尾..."
# 对未签名的 App 用 ad-hoc 签名，避免 Gatekeeper 拦截和崩溃
if command -v codesign &>/dev/null; then
    codesign --force --deep --sign - "$DIST_DIR/$APP_NAME.app"
    echo "已进行 ad-hoc 签名。"
fi

echo "======================================"
echo "打包完成！"
echo "输出位置: $(pwd)/$DIST_DIR/$APP_NAME.app"
echo "======================================"
echo "提示："
echo "  第一次运行如果提示'无法验证开发者'，请去'系统设置 -> 隐私与安全性'中允许。"
echo "  也可以右键点击 App -> 打开。"
