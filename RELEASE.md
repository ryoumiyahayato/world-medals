# 私有 Release 发布

原图、研究缓存、苏联参考原始输出、签名凭证及处理临时文件不上传。Git 只保存程序、可移植索引和构建方法。已有历史不改写；本版取消原图跟踪并保留本地文件，旧提交仍可能包含过去已经提交的素材。

按 BUILD.md 完成资源生成、检查及 APK 签名后，只提交必要源码。先核对实际暂存内容，不使用 `git add .`。本版工作流改为手动源码检查；没有外部原图的云端不会自动构建完整成品，也不上传本地签名。

```powershell
gh repo view ryoumiyahayato/world-medals --json nameWithOwner,isPrivate
# 必须确认预期仓库且 isPrivate=true，才执行上传。
git diff --cached --stat
git ls-files assets originals sources
git commit -m 'Generate trimmed thumbnail and detail assets for private releases'
git push origin HEAD:main
.venv/Scripts/python.exe mobile/scripts/package_release.py
$edition = (Get-Content mobile/version.json | ConvertFrom-Json).name
$tag = 'mobile-v' + $edition
gh release create $tag "mobile/build/world-medals-html-$edition.zip" "mobile/build/world-medals-$edition.apk" mobile/build/SHA256SUMS.txt mobile/build/release-info.json --repo ryoumiyahayato/world-medals --target (git rev-parse HEAD) --title "World Medals $edition" --notes-file mobile/build/release-notes.md
gh release view $tag --repo ryoumiyahayato/world-medals --json url,tagName,assets,isDraft
```

`package_release.py` 为 HTML ZIP 和 APK 生成 SHA-256、版本、提交号和环境信息。只计算发布成品校验，不生成原图库哈希清单。HTML ZIP 包含运行图片、来源和许可记录；不是原图库压缩包。

Release 备注必须区分已处理、已验证和待核验。受限图片保留来源权利说明；Private 不代表取得出版许可。此版只用于用户授权的私有研究分发。

2026-10-12 用户清理约束：构建和发布默认保留旧 APK、旁文件及构建中间件。新包验证完成后，先列出拟清理的绝对路径、大小和可恢复范围；只有取得用户对该批永久删除的专项确认，才可显式调用 `remove_obsolete_apks(output, confirm_permanent_delete=True)`。发布授权不等于删除授权。该函数使用 `Path.unlink()`，不进入回收站、不自动备份；仍只允许本项目 `mobile/build` 内的 APK 及旁文件，原图和来源档案不删。

v0.030：7,311项完成缩略总览和局部遮罩分析，30张新增背景处理获准，17张非完整勋章展示撤下；7,264张遮罩未获准，保留原展示。38条候选中22条确认参考关系、9条勋略排除、7条阻塞；其中4条明确等级参考进入正文。8个失败项中5项得到补下载／本地替代／受限预览处置，3项阻塞。不得把总览审核称为7,311张全分辨率精修完成。模型建议未发布。

本地逐项清单位于 `mobile/build/background-continuation/dispositions.json`、`mobile/build/recovery/failure-dispositions.json` 和 `data/display_images/material_resolutions.json`。只向Release上传HTML ZIP、APK、SHA256SUMS和release-info；处理预览、模型、原素材及含工作站路径的内部清单不上传。

v0.031保留上述处理结果，并将两条参考图的“另一件实物”改为“来源参考图正面”。不同照片来源不能证明实物不同；不移动已发布的v0.030标签。


v0.032：接续v0.031既定背景队列，34张逐件原尺寸对照后，6张启用既有242/12外沿连通浅色规则；28张因低清边界、图式背景、来源字样或阴影继续保留原展示。累计71张背景规则，7,258张遮罩仍未获准。未启用模型遮罩，未新增章种或版型。7条候选与3条失败项仅回看既有证据，仍阻塞；两条原图地址在2026-10-12再次返回404。原图和旧未提交修改保留。


v0.033：在v0.032之后完成两批既定队列图片审查，200张进行原图、确定性242/12蒙版与删除像素对照，其中93张完成原尺寸检查。46张经现有Künker 299图录与完整轮廓检查通过，154张保留原展示；累计117张启用，7,212张未批准。18张来源编号或实物对应冲突只记录为阻塞，不改写历史归属。未新增奖种、等级行或模型蒙版。所有旧APK继续保留；任何永久清理须另行确认具体路径。
