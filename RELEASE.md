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

APK 旧包清理在本版验证后进行，使用现有 `remove_obsolete_apks`，只删除本项目构建目录中的旧 APK 及其签名/校验旁文件。原图和来源档案不删。
