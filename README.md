# World Medals

全球、跨历史时期的勋章与奖章离线图鉴。当前交付物是可直接打开的三列式离线 HTML：

| 名称＋日期 | 等级／版别 | 完整图样 |
| --- | --- | --- |

## 当前版本

截至 2026-09-29，当前离线 HTML 包含 178 个分卷、3328 个正文版型行、4740 个引用本地图像文件。以上是当前文件统计，不代表全球范围已穷尽。缺图附录另列。

Android 个人研究版为 **v0.004（dev）**；源码、构建和更新说明见 [mobile/README.md](mobile/README.md)。图片替换接口见 [data/display_images/README.md](data/display_images/README.md)。

## 使用

直接打开仓库根目录的 `index.html`。图片均为仓库内本地资源，不依赖远端图床。

重新构建和验证：

```powershell
python site_build.py
python validate_site.py
python scripts/audit_regressions.py
node validate_interactions.mjs
```

主要目录：

- `data/volumes/`：各国家、时期与批次的结构化正文数据
- `data/checkpoints/`：增量接续位置与来源覆盖记录
- `assets/images/`：正文使用的本地图像
- `scripts/`：来源扫描、归并、构建与审查脚本

## 同步到 GitHub

`git push` 只上传已提交的内容。图片与缓存目录默认被忽略，每次更新图鉴后需把正文实际引用的图片一并纳入提交：

```powershell
python scripts/stage_catalogue_assets.py --stage
git add -A
git diff --cached --stat
git commit -m "Update offline catalogue and referenced images"
git push origin main
```

第一步会检查 `index.html` 引用的本地图片、样式和脚本，并将这些资源加入暂存区；资源缺失时停止。图片继续由 Git LFS 管理。仅运行该脚本、不加 `--stage` 可检查尚未跟踪的资源数量。克隆仓库后执行 `git lfs pull` 下载图片原文件。

## 数据与图片说明

本仓库采用“授予主体／历史时期 → 独立章种 → 等级／版型 → 具体图像”的结构。同一章种的等级、时期式样、制造商、材质、加剑与微型章不会重复计算为新的独立章种。

图片来源与许可并不统一；部分商业目录图片仅用于私有研究。仓库保持为私有并不等于获得公开出版、再分发或改作许可。不得删除原有出处与权利记录后公开发布整库。

