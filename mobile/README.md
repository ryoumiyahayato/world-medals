# Android 图鉴

现有 WebView 工程，v0.028。构建链保持 aapt2 → javac → D8 → zipalign → apksigner，使用持久签名。

完整命令见 [BUILD.md](../BUILD.md)，发布命令见 [RELEASE.md](../RELEASE.md)。手机与桌面共用可移植目录和衍生展示资源。列表缩略图，详情按需加载；原图不打包、不提交。

无 Android 设备时只验证签名、包内资源和浏览器断网行为，实机安装及厂商 WebView 表现不作通过声明。私有仓库更新沿用现有授权机制，不在网页或 APK 中嵌入 GitHub 凭证。
