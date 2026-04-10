#!/bin/zsh
set -e

# ========== 配置 ==========
APP_NAME="E5CM-CG"
ENTRY="main.py"
ICON_ICO="UI-img/app.ico"
ICON_ICNS="UI-img/app.icns"
DIST_DIR="dist_mac"
BUILD_DIR="build_mac"
DMG_NAME="${APP_NAME}-Mac-arm64.dmg"
VOL_NAME="${APP_NAME} 安装"
# ==========================

echo "【1/6】检查虚拟环境 .venv..."
if [ ! -f ".venv/bin/python" ]; then
    echo "错误：.venv 不存在，请先创建虚拟环境。"
    exit 1
fi
source .venv/bin/activate

echo "【2/6】安装/确认 PyInstaller..."
pip install --quiet pyinstaller pillow

echo "【3/6】生成 macOS .icns 图标..."
if [ -f "$ICON_ICO" ]; then
    python3 << 'PYEOF'
import os
from PIL import Image

ico_path = "UI-img/app.ico"
icns_path = "UI-img/app.icns"

img = Image.open(ico_path)
if img.mode != 'RGBA':
    img = img.convert('RGBA')

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

echo "【4/6】开始用 PyInstaller 打包（Apple Silicon arm64）..."

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

HIDDEN_IMPORTS=()
for d in core scenes ui; do
    if [ -d "$d" ]; then
        for f in $(find "$d" -name '*.py' | sed 's|/|.|g' | sed 's|\.py$||' | sed 's|^\.__init__$||'); do
            HIDDEN_IMPORTS+=("--hidden-import" "$f")
        done
    fi
done

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

echo "【5/6】签名与权限处理..."
if command -v codesign &>/dev/null; then
    codesign --force --deep --sign - "$DIST_DIR/$APP_NAME.app"
    echo "已进行 ad-hoc 签名。"
fi

# 移除隔离属性（防止"已损坏"提示）
xattr -cr "$DIST_DIR/$APP_NAME.app" 2>/dev/null || true

echo "【6/6】打包 DMG..."
TMP_DMG="${BUILD_DIR}/tmp.dmg"
MOUNT_POINT="/Volumes/${VOL_NAME}"
STAGING="${BUILD_DIR}/dmg_staging"

# 清理旧文件
rm -f "$TMP_DMG" "$DMG_NAME"
rm -rf "$STAGING"
mkdir -p "$STAGING"

# 复制 .app
cp -a "$DIST_DIR/$APP_NAME.app" "$STAGING/"

# 创建 Applications 软链接
ln -s /Applications "$STAGING/Applications"

# 创建临时可读写 DMG（预留一些空间）
echo "  创建临时 DMG..."
hdiutil create \
    -srcfolder "$STAGING" \
    -volname "$VOL_NAME" \
    -fs HFS+ \
    -format UDRW \
    -size 800m \
    "$TMP_DMG"

# 挂载
MOUNT_DEV=$(hdiutil attach "$TMP_DMG" -nobrowse -noverify | grep -o '/dev/disk[0-9]*s[0-9]*' | head -1)
echo "  挂载点: $MOUNT_POINT (设备: $MOUNT_DEV)"

# 等待挂载完成
sleep 1

# 设置图标布局和背景（通过 AppleScript 设置 Finder 窗口）
echo "  设置 DMG 窗口布局..."
osascript <<OSAEOF
    tell application "Finder"
        tell disk "$VOL_NAME"
            open
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            -- 窗口位置和大小
            set the bounds of container window to {400, 100, 1000, 500}
            -- 图标大小和间距
            set icon size of the icon view options of container window to 128
            set arrangement of the icon view options of container window to not arranged
            -- 设置 App 图标位置
            set position of item "$APP_NAME.app" of container window to {140, 200}
            -- 设置 Applications 图标位置
            set position of item "Applications" of container window to {380, 200}
            close
        end tell
    end tell
OSAEOF

# 刷新并确保布局生效
sleep 1
hdiutil detach "$MOUNT_DEV" || hdiutil detach "$MOUNT_DEV" -force

# 转换 DMG 为只读压缩格式（udzo）
echo "  压缩 DMG..."
hdiutil convert "$TMP_DMG" -format UDZO -o "$DMG_NAME"

# 清理临时文件
rm -f "$TMP_DMG"
rm -rf "$STAGING"

echo "======================================"
echo "DMG 打包完成！"
echo "输出文件: $(pwd)/$DMG_NAME"
echo "======================================"
echo "提示："
echo "  1. 该 DMG 仅适用于 Apple Silicon Mac (M1/M2/M3/M4)。"
echo "  2. 由于未使用 Apple Developer ID 签名，首次运行请："
echo "     右键点击 App -> 打开，或在 系统设置 -> 隐私与安全性 中允许。"
echo "  3. 如果发送后对方看到'已损坏'，可在终端执行："
echo "     xattr -cr /Applications/$APP_NAME.app"
