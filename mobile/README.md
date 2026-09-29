# 全球勋奖章图鉴 · Android

首个开发版：**v0.001（dev）**。手机端为现有离线图鉴的独立查阅入口，不改写原始史料、原图或根目录 `index.html`。

## 已实现

- 透明空间场景与可调双色雾气；静态模式、系统/浅色/深色主题。
- 无字、无饰的实体三维书：封板、书脊、纸页块和可转动的独立书页。点击翻开后才显示搜索。WebGL 不可用时降为 CSS 三维书。
- 搜索时放大为可交互书页，检索词写在页首，国家选择和三列表格在书页内淡入、滚动；搜索条固定在浮动导航上方。
- 彩蛋：点击书页空白处逐页翻动；2.2秒内6次点击合书、旋转3圈。APK 随后移除自身任务并结束自身进程；浏览器仅演示退场并提供重新打开按钮。实际控件与奖章图片不参与连击。
- 浮起的磨砂胶囊导航：图鉴 / 分类 / 设置。收藏位于分类下。
- 大洲 → 地区 → 国家 → 朝代/时期目录；没有数据的大洲明确显示暂无分卷。
- 初始无查询、无默认国家、无奖章列表；选择国家/时期后只显示相应内容。
- 法国荣誉军团的历代版型归为一个折叠组，按现有日期字段升序；不从拍卖时间推断年代。保留每行原历史时期标签。地理导航不改写历史授予主体。
- 搜索别名、空格、重音与大小写归一化；“荣军”“荣 军”“榮軍”对应荣誉军团；单字、多关键词、名称内有序短简称搜索。
- 本地收藏、图片查看、正背切换、放大。来源与许可在详情及内置 `image-provenance.json` 中保留。
- 自选图片作为虚化景深背景，虚化强度 0–32，可恢复默认背景。
- 封面、封底独立选图；设置中有可复制、可编辑的AI生成/裁切提示词，不调用收费API。闭合书本可拖动原地旋转。向右回翻或点书页“返回”正常合书退出。
- 搜索按回车或停顿500毫秒后翻页，随后新页面显示结果；选择国家后同样先翻页。纸面使用独立生成的细纤维纹理，正式奖章照片保持原来源。
- 64px 流汗黄豆加载动画：加速至98%后回退；皇冠、火炬、镰锤、和平鸽、铁十字可点击掉落。趣味动画不是实际下载百分比。

## 本地构建

要求 Python 3.12+、JDK 17+、Android SDK platform 36、build-tools 36.0.0 或 36.1.0。无 Gradle、账号、服务器或 API key 依赖。

```powershell
python -m pip install -r mobile/requirements.txt
python mobile/scripts/build_apk.py
node mobile/scripts/test_search.cjs
```

构建链为 aapt2 → javac → D8 → zipalign → apksigner。默认最低 Android 8.0，建议使用已更新的 Android System WebView。没有原生 CPU 库，适配 ARM / ARM64 / x86 / x86_64。实际手机安装与各厂商表现仍需实机验证。

首次本地构建生成持久签名，保存在被 Git 忽略的 `mobile/.local/atlas.keystore` 和 `signing.json`。必须安全备份；后续签名改变将无法直接覆盖安装，不能在聊天、仓库或公开附件中暴露私钥与密码。

每次交付更新先运行 `python mobile/scripts/bump_version.py`：0.001 → 0.002 → 0.003。同步递增 Android versionCode；同一更新重新构建不递增。`mobile/version.json` 是唯一版本源，导出时写入应用。

## GitHub 更新

工作流 `.github/workflows/mobile-apk.yml` 已编写，尚未推送或配置云端签名。

1. 私有仓库 GitHub Actions Secrets 配置 `ATLAS_KEYSTORE_BASE64`（上述同一 keystore 的 Base64）与 `ATLAS_KEYSTORE_PASSWORD`（同一密码）。这些不进入 APK。
2. 推送相关代码或图鉴更新即构建签名 APK，并保留私有 workflow artifact 14天。
3. 发布更新前递增版本并打标签，例如 `mobile-v0.002`。工作流构建并创建待审核的 draft Release；确认后在 GitHub 发布。
4. APK 回到前台及前台运行时每15分钟检查一次可访问的 Releases（手动检查不受间隔限制）；包含 dev 预发布，排除草稿及未附对应 APK 的版本，分页后按版本号选择最高版本。失败不会显示“已是最新”。发现更高版后提示打开 GitHub 下载，Android 确认覆盖安装，保留收藏和设置。
5. 当前研究库若保持私有，未登录的 GitHub API 无法读取版本。应用会引导到外部浏览器登录后查看发布页。这不是后台推送服务或静默安装；不在 APK 内嵌个人 GitHub token。需要私有仓库自动通知时，可使用 GitHub 自带 Watch → Releases 通知。

工作流仅对私有仓库运行，不擅自公开研究图片。既有图片权利限制继续适用。

## 设计资产

内置 Image Gen 生成了应用抽象图标、早期书本背景和两版视觉概念。正式历史图像均来自现有项目，无生成式替代。

- `web/icon.png`：金色抽象绶带与八芒章饰，深蓝底、无文字，不指向真实章种。提示词摘要：abstract medal, folded ribbons, eight-point rosette, gold on ink navy, no text。
- `design/concept-v2.png`：空间背景、悬浮书、磨砂胶囊导航参考。用户随后明确去掉封面文字和装饰，并新增雾气调色、景深背景、四级分类；最终以这些修改为准。
- `web/book3d.js`：真实几何渲染；Three.js 0.160.1 以 MIT 许可本地打包，许可与下载校验保留在 `web/vendor/`。

生成文件位于 `mobile/build/`，包含离线预览站、签名 APK、SHA-256 与构建报告。图像由原图等比缩小至最长边不超过1200像素，不裁切、不插值放大、不移除水印；原图留在研究库。

## v0.002 兼容性修订
- 全屏层显式四边定位、vh 回退，避免旧 WebView 不支持 inset/dvh 时缩在左上角。书本固定在可见区域，摄像机按比例计算。
- 无加载文案，巨大模糊纹章背景；点开书不自动唤起键盘。
- 本地 Noto Serif SC（OFL），Hanzi Writer 3.7.3（MIT）与笔顺数据 2.0.1（Arphic Public License）。中文逐笔、其他文字逐字符；缺少笔顺数据时按字出现；减少动态效果时直接显示。
- 私有授权入口：GitHub fine-grained token，仅 world-medals 的 Contents read；由用户在原生密码框输入，AndroidKeyStore AES-GCM 本机保存，禁止备份，不进入网页或 APK。可在设置清除。请求禁用重定向，令牌仅发送至 api.github.com。浏览器登录不能替代手机授权。
- 云端签名工作流及正式 Release 仍需部署，授权本身不会生成发布包。
