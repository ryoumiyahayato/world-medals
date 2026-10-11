# 本地重建

此仓库不保存原始图片或构建展示图片。源码不能恢复原图。已发布的完整成品从私有 Releases 获取。

## 工具链

本版使用 Python 3.14.6、Pillow 12.3.0、BeautifulSoup 4.15.0。APK 需要 JDK 17+、Android SDK platform 36、build-tools 36.1.0（或36.0.0）。Node.js 用于现有目录检查。保留原持久签名，不创建替代签名来冒充可覆盖安装。

## 完整顺序（PowerShell）

在仓库根目录运行。外部素材目录必须保留索引所指的相对结构，例如 `assets/images/`、`assets/processed/`、`originals/`。不要把素材复制进 Git 索引。

```powershell
py -3.14 -m venv .venv
.venv/Scripts/python.exe -m pip install -r mobile/requirements.txt
$env:WORLD_MEDALS_MATERIAL_ROOT = Read-Host '外部原始素材根目录'
$env:JAVA_HOME = Read-Host 'JDK 根目录'
$env:ANDROID_HOME = Read-Host 'Android SDK 根目录'
$env:WORLD_MEDALS_RELEASE_INPUT = '1'
$env:WORLD_MEDALS_PRIVATE_RELEASE = '1'
$env:WORLD_MEDALS_IMAGE_WORKERS = '8'
$env:WORLD_MEDALS_DEFER_APK_CLEANUP = '1'
.venv/Scripts/python.exe mobile/scripts/inventory_materials.py
.venv/Scripts/python.exe mobile/scripts/export_catalog.py
node mobile/scripts/validate_mobile.cjs
$env:SKIP_EXPORT = '1'
.venv/Scripts/python.exe mobile/scripts/build_apk.py
.venv/Scripts/python.exe mobile/scripts/package_release.py
```

在 `mobile/.local/` 恢复现有 `atlas.keystore` 和 `signing.json`，或通过 `SIGNING_KEYSTORE`、`SIGNING_ALIAS`、`SIGNING_PASSWORD` 提供同一签名。凭证不提交、不发布。

目录清点会识别引用、无图行、中文素材元数据 ID、未匹配素材、解码失败和按字节相等的重复文件，不用重命名合并章种。待核验素材不会自动加入正文。巨大原图触发 Pillow 安全限制时保留为失败记录，不关闭限制。

透明图只裁去所有非零 alpha 像素包围盒以外的画布。保留每个非零 alpha 像素、3.5% 长边安全边距和原色。不透明图只删除完全纯白的外围矩形行列；复杂背景、散点及方向校正需要人工审查，本版不猜测背景。苏联用户修复参考图保留画布和像素内容，仅加展示安全边距、缩小和压缩，不作为新摄影证据。列表 WebP 长边≤384、质量86；详情≤1200、质量90；不放大。衍生物不能无损恢复原图。

`data/release-input.json` 保存既有行、ID、版型及来源映射；`mobile/web/desktop-template.html` 保存原桌面布局模板。手机和桌面由同一索引导出，使用同一套展示图片。`index.html` 是本地生成的桌面成品，不进 Git。`mobile/build/site/index.html` 是手机界面；`desktop.html` 是桌面三列表格。

既有目录内容完成审核并更新时，在优化前运行 `release_input.py` 更新可移植索引。本批索引已生成，不应在根目录轻量化后再次直接拍快照。内容录入、身份鉴定不是图片处理算法的能力。

无素材的源码检出只能验证依赖安装、脚本语法、索引结构和构建逻辑。导出遇到缺失素材会报错，不能声称完整重建成功。完整重建必须提供外部素材和签名。

输出位于 `mobile/build/`。原始图片和研究记录保留原地。发布前实际打开 HTML、检查详情图，并在可用设备上检查 APK 离线行为。没有设备时只报告签名、包内资源和浏览器断网验证，不能称实机安装通过。
