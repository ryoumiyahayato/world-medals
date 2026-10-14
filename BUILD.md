# 本地重建

`background_rules.json` 的 `crop-only` 类型只启用逐件审核的矩形裁剪。输入尺寸和字节数必须匹配，裁剪区域内的原像素保留；摄影背景不被称为已经去除。该类型与背景处理分别计数，正文说明“裁去冗余画布／原背景保留”。未来有获准精细遮罩时再替换，不能把裁剪当成完整抠图。

此仓库不保存原始图片或构建展示图片。源码不能恢复原图。已发布的完整成品从私有 Releases 获取。

## 工具链

本版使用 Python 3.14.6、Pillow 12.3.0、BeautifulSoup 4.15.0。APK 需要 JDK 17+、Android SDK platform 36、build-tools 36.1.0（或36.0.0）。Node.js 用于现有目录检查。保留原持久签名，不创建替代签名来冒充可覆盖安装。

## 完整顺序（PowerShell）

在仓库根目录运行。外部素材目录必须保留索引所指的相对结构，包括 `assets/images/`、`assets/raw/`、`assets/processed/`、`originals/`、`我搜索到的东西/`。不要把素材复制进 Git 索引。

```powershell
py -3.14 -m venv .venv
.venv/Scripts/python.exe -m pip install -r mobile/requirements.txt
# 没有 pip 的现有虚拟环境可用：uv pip install --python .venv/Scripts/python.exe -r mobile/requirements.txt
$env:WORLD_MEDALS_MATERIAL_ROOT = Read-Host '外部原始素材根目录'
$env:JAVA_HOME = Read-Host 'JDK 根目录'
$env:ANDROID_HOME = Read-Host 'Android SDK 根目录'
$env:WORLD_MEDALS_RELEASE_INPUT = '1'
$env:WORLD_MEDALS_PRIVATE_RELEASE = '1'
$env:WORLD_MEDALS_IMAGE_WORKERS = '8'
$env:WORLD_MEDALS_DEFER_APK_CLEANUP = '1'
.venv/Scripts/python.exe mobile/scripts/inventory_materials.py
.venv/Scripts/python.exe mobile/scripts/export_catalog.py
.venv/Scripts/python.exe mobile/scripts/reconcile_local_metadata.py
.venv/Scripts/python.exe mobile/scripts/verify_background_batch.py
node mobile/scripts/validate_mobile.cjs
$env:SKIP_EXPORT = '1'
.venv/Scripts/python.exe mobile/scripts/build_apk.py
.venv/Scripts/python.exe mobile/scripts/package_release.py
```

在 `mobile/.local/` 恢复现有 `atlas.keystore` 和 `signing.json`，或通过 `SIGNING_KEYSTORE`、`SIGNING_ALIAS`、`SIGNING_PASSWORD` 提供同一签名。凭证不提交、不发布。

目录清点会识别引用、无图行、中文素材元数据 ID、未匹配素材、解码失败和按字节相等的重复文件，不用重命名合并章种。待核验素材不会自动加入正文。巨大原图触发 Pillow 安全限制时保留原文件，不关闭全局限制。

透明图只裁去所有非零 alpha 像素包围盒以外的画布。保留每个非零 alpha 像素、3.5% 长边安全边距和原色。不透明图只删除完全纯白的外围矩形行列；复杂背景、散点及方向校正需要人工审查，本版不猜测背景。苏联用户修复参考图保留画布和像素内容，仅加展示安全边距、缩小和压缩，不作为新摄影证据。列表 WebP 长边≤384、质量86；详情≤1200、质量90；不放大。衍生物不能无损恢复原图。

`data/release-input.json` 保存既有行、ID、版型及来源映射；`mobile/web/desktop-template.html` 保存原桌面布局模板。手机和桌面由同一索引导出，使用同一套展示图片。`index.html` 是本地生成的桌面成品，不进 Git。`mobile/build/site/index.html` 是手机界面；`desktop.html` 是桌面三列表格。

APK脚本在打包前从当前索引刷新桌面HTML，包含使用 `SKIP_EXPORT=1` 的构建，避免携带旧版桌面文件。桌面HTML可以直接以文件打开；手机页的笔顺和3D纸纹使用本地fetch，完整行为需要本地HTTP服务或APK的appassets协议。用 `py -m http.server 8000 --directory mobile/build/site --bind 127.0.0.1` 可在本机浏览器检查手机页；运行图片不依赖互联网。

既有目录内容完成审核并更新时，在优化前运行 `release_input.py` 更新可移植索引。本批索引已生成，不应在根目录轻量化后再次直接拍快照。内容录入、身份鉴定不是图片处理算法的能力。

无素材的源码检出只能验证依赖安装、脚本语法、索引结构和构建逻辑。导出遇到缺失素材会报错，不能声称完整重建成功。完整重建必须提供外部素材和签名。

输出位于 `mobile/build/`。原始图片和研究记录保留原地。构建器默认不永久删除旧 APK、旁文件或中间件；清理必须另获用户对具体文件清单的专项确认，按 RELEASE.md 执行。重建旧标签的旧脚本时仍设置 `WORLD_MEDALS_DEFER_APK_CLEANUP=1`，避免旧脚本的自动清理。发布前实际打开 HTML、检查详情图，并在可用设备上检查 APK 离线行为。没有设备时只报告签名、包内资源和浏览器断网验证，不能称实机安装通过。

v0.039起，APK构建结束后生成 `mobile/build/apk-build-info.json`。该文件记录构建时的Git提交及受跟踪构建源码是否有未提交修改，发布器写入对应 `release-info.json`。源码归档没有Git元数据时提交字段为null，不推测提交。此文件与签名密码分开，不记录密钥路径或凭证。

## 已核验浅色背景规则

`reviewed-runs` 保存经原尺寸审核的透明度坐标。每行记录不重叠的 `[起点,终点,透明度]` 区间；二项区间表示全不透明。此规则只改变alpha，保留源RGB，并按源尺寸和字节数校验输入。`protectedPolygons` 记录珐琅及来源标记的检查区域。

复杂背景可使用本地非生成式分割提出alpha建议。建议不直接启用。先对照原图补回被误判的内部珐琅、保护来源水印、检查轮廓与压缩边缘，再冻结审核后的坐标。正常重建只需规则和原图，不运行模型；模型权重及遮罩中间图片不进Git。

逐件批准的 `edge-connected-dark` 规则只删除与画布外沿连通、RGB最大通道≤24且通道差≤24的近黑像素。阈值保存在逐件规则中。内部暗色区域保留。仅逐件审核通过的图片启用，不用于自动批准其余黑底图。

重建7375背面时，在导出前从外部素材中的既有图录生成已审核裁片：

```powershell
.venv/Scripts/python.exe mobile/scripts/recover_catalog_crop.py --material-root "$env:WORLD_MEDALS_MATERIAL_ROOT"
```

此命令使用固定依赖 `pypdf==6.10.0`，提取PDF第230页（印刷页228）的 `Im7.jpg` 图像对象，原尺寸286×278。尺寸或对象名不符时停止。原PDF、旧错配文件和早期渲染裁片不修改；已有原尺寸提取文件直接复用。低清图片不放大，展示保留“低清参考”。

`data/display_images/background_rules.json` 仅保存逐件对照批准的规则，不保存原图。处理器只移除与画布外沿连通、RGB最小通道≥242且通道差≤12的浅色区域。孤立的内部浅色区域保留；不重建纹理或铭文，不旋转、改色或消除来源水印。源尺寸或文件字节数变化时停止该项，重新核验。苏联修复参考不使用此规则。输出仍是有损展示衍生物。

导出优先使用仓库中的可移植索引，避免把上一次生成的展示图再次当作原图输入。

中文素材目录的 `metadata.json` 用于补充关联核对，不是引用图片重建的必要条件。外部素材只有索引所需原图时，该核对步骤会说明跳过；HTML/APK 仍按已保存的正式索引重建。

已完成完整导出后，只更新已批准背景规则时，可运行 `.venv/Scripts/python.exe mobile/scripts/refresh_reviewed_backgrounds.py`，然后重建 APK 和 Release。该命令不改变章种、等级或历史版型 ID；正式全量重建仍使用上面的完整顺序。

## 背景接续与素材补救

`data/display_images/material_resolutions.json` 保存38条候选的来源核验与处置。明确等级的4条已写入正式索引；名称关联不证明实物材质、亚型或年代。普通构建直接使用已批准规则，不需要分割模型。总览审查与全分辨率遮罩批准分开记录；未批准的遮罩不会进入成品。

需要继续生成局部遮罩建议时，先按上文清点，再执行：

```powershell
uv pip install --python .venv/Scripts/python.exe -r mobile/requirements-segmentation.txt
New-Item -ItemType Directory -Force mobile/.local/models | Out-Null
$env:WORLD_MEDALS_MODEL_DIR = (Resolve-Path mobile/.local/models).Path
curl.exe -L --fail --retry 2 --max-time 300 -o "$env:WORLD_MEDALS_MODEL_DIR/u2netp.onnx" https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx
.venv/Scripts/python.exe mobile/scripts/review_backgrounds.py --model --workers 8 --start 0 --count 100
```

U2NETP只生成alpha建议，不生成RGB、文字或结构。输出在 `mobile/build/background-continuation/items/`，不提交。该模型会漏掉水印、悬挂结构或浅色部件；需要逐张原图对照和必要的人工遮罩。脚本不自动批准。更换输入或模型后用 `--output mobile/build/新批次目录`，不能把旧建议当作新审核。

已批准规则可用 `keepPolygons` 记录源像素坐标，保护与背景相连的白色勋带。处理器保留这些坐标内的原始alpha和RGB；允许留下少量原背景边缘。坐标仅适用于已核验的源尺寸和字节数。v0.030的一张低清勋带采用此保护，未使用模型遮罩。

超大法国历史合图的单文件预览使用 Node.js 22.23.1、Sharp 0.35.5。安装目录和预览均留本地：

```powershell
npm install --no-save --prefix mobile/.local/preview sharp@0.35.5
$env:NODE_PATH = (Resolve-Path mobile/.local/preview/node_modules).Path
New-Item -ItemType Directory -Force mobile/build/recovery | Out-Null
node mobile/scripts/bounded_preview.cjs "$env:WORLD_MEDALS_MATERIAL_ROOT/originals/france_legion_honour_open_batch2/commons-design-through-years.png" mobile/build/recovery/legion-design-bounded.png 520000000
```

该命令只将一个507,076,515像素PNG降采样为最长边1200的预览，单线程、128MB缓存、显式像素上限；不替换原图，不自动加入图鉴。失败原文件保留，补下载副本另存于本地原始素材区。源图本身裁断的结构不重建。


v0.041：4张背景处理（1张近黑背景、3张浅棕背景），累计737条；另2张仅裁去冗余画布，累计3张裁剪，原背景保留。浅棕背景采用逐张原尺寸审核后冻结的reviewed-runs；水印和周围矩形原背景保留，内部封闭背景及少量轮廓边缘保留，不重绘、不改RGB。6张原图保留，未新增章种或版型行。其余复杂边界继续待核，不以水印弱化的候选替代原图。

## Android模拟器离线检查

本轮使用SDK Command-Line Tools22.0、现有Emulator、API35 default x86_64 revision2和Pixel5配置。按[官方工具下载页](https://developer.android.com/studio)取得命令行工具，解压到SDK的 `cmdline-tools/22.0/`，该目录内应有 `bin/avdmanager.bat`。工具放在项目目录时，avdmanager不能按相对位置找到SDK镜像。

```powershell
$tools = Join-Path $env:ANDROID_HOME 'cmdline-tools/22.0/bin'
& (Join-Path $tools 'sdkmanager.bat') "--sdk_root=$env:ANDROID_HOME" 'system-images;android-35;default;x86_64'
New-Item -ItemType Directory -Force mobile/.local/avd | Out-Null
$env:ANDROID_AVD_HOME = (Resolve-Path mobile/.local/avd).Path
$avdPath = Join-Path $env:ANDROID_AVD_HOME 'world_medals_offline_api35.avd'
& (Join-Path $tools 'avdmanager.bat') create avd -n world_medals_offline_api35 -k 'system-images;android-35;default;x86_64' -d pixel_5 -p $avdPath
$emulator = Join-Path $env:ANDROID_HOME 'emulator/emulator.exe'
Start-Process -FilePath $emulator -WindowStyle Hidden -ArgumentList '-avd world_medals_offline_api35 -no-window -no-audio -no-snapshot -no-boot-anim -gpu swiftshader -memory 2048 -cores 2 -port 5560'
$adb = Join-Path $env:ANDROID_HOME 'platform-tools/adb.exe'
& $adb -s emulator-5560 wait-for-device
& $adb -s emulator-5560 shell getprop sys.boot_completed
```

上一命令返回1后执行：

```powershell
$edition = (Get-Content mobile/version.json | ConvertFrom-Json).name
& $adb -s emulator-5560 install -r "mobile/build/world-medals-$edition.apk"
& $adb -s emulator-5560 shell cmd connectivity airplane-mode enable
& $adb -s emulator-5560 shell svc wifi disable
& $adb -s emulator-5560 shell svc data disable
& $adb -s emulator-5560 shell settings get global airplane_mode_on
& $adb -s emulator-5560 shell dumpsys connectivity | Select-String 'Active default network'
& $adb -s emulator-5560 shell am start -W -n org.worldmedals.atlas/.MainActivity
```

实际检查搜索、缩略图和详情图，不能仅凭启动返回ok判定图片已显示。v0.041实际查看Military Brotherhood Medal；原背景保留、低清提示及悬挂结构可见。当前塔吉克正背面在断外网浏览器检查，包内文件与浏览器版本一致；未逐项模拟器检查全部图片。完成后用 `& $adb -s emulator-5560 emu kill` 关闭该模拟器。AVD、系统镜像、截图和工具缓存不提交或发布。实体手机仍未验证。


v0.042：14张既有本地照片完成背景处理，累计751条背景规则，裁剪累计3张另计。保留水印与其矩形原背景；两张用逐件审核的外轮廓几何约束缩小阴影，并冻结为reviewed-runs，正常构建不运行几何拟合。一张只删除章体左侧3个孤立背景像素。金属、悬环、勋带、背针及原RGB保留；其他贴近织物或边缘的单像素不作自动批量删除。未新增章种或等级行。原图、旧APK及旁文件保留。


v0.042代表性运行检查使用同一API35模拟器：安装0.042后，在飞行模式、Wi-Fi和移动数据关闭、无默认网络时冷启动；按亚洲→中亚→塔吉克斯坦→塔吉克斯坦共和国打开目录，选择功绩服务奖章，查看五角形绶带版正面并切换背面。未检查实体手机，也未逐张在模拟器遍历全部图片。

## 同源浅棕背景候选

可选工具只为600×600的WAWARDS浅棕底原图生成候选，不参与成品重建，也不批准图片。水印位置使用既有本地图片中的右侧字样像素模板定位；尺寸、背景不符或相关分数不足0.90时保留待人工检查。源RGB不变，水印与周围画布保留，闭合内部背景默认保留。

```powershell
uv pip install --python .venv/Scripts/python.exe -r mobile/requirements-colour-proposals.txt
.venv/Scripts/python.exe mobile/scripts/colour_background_proposals.py --start 1373 --count 27
```

材料目录沿用 `WORLD_MEDALS_MATERIAL_ROOT`。工具优先读取本地背景队列；没有该队列时读取可移植索引的图片顺序，接续序号因此可能不同。`--prefix` 限定来源目录，`--output` 可指定项目build内的新候选目录。缓存输入的文件大小或修改时间变化时停止复用，不能拿旧遮罩对应新图片。

输出为原尺寸原图／候选对照PNG和逐项JSON，均留在本地build。逐张检查章体、勋带、悬挂结构及完整水印后，才把审核后的alpha冻结为 `reviewed-runs`，再生成并检查WebP。模板定位不证明章种身份、等级、材质或图像性质。正常HTML/APK重建只读已批准坐标，不需要OpenCV或水印模板。


v0.043：本地新增37张背景处理，累计788条；裁剪累计3张另计。25张采用限定来源底色的连通区域候选，经原尺寸和压缩图逐张检查后冻结规则。水印及其周围原背景保留。1行改为“章体正面；勋带仅示局部”。另2张因图像性质或水印定位待核而保留原展示。新增章种和版型行均为0。剩余6542项背景队列待处理。原图、旧APK与旁文件保留。
