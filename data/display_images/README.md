# 展示图替换接口

原图留在原路径，处理图放在 `assets/processed/`。目前映射为空，不改变任何历史图片。Android 导出会读取 `overrides.json`。离线主图鉴 index.html 暂不替换。

每个键是原图项目相对路径，值示例（示例不自动生效）：
```json
{
  "file": "assets/processed/example.png",
  "original_sha256": "原始文件完整 SHA256",
  "processing": "background-removed",
  "model": "实际使用的工具与版本",
  "approved": false,
  "reviewed_by": "复核者",
  "reviewed_at": "YYYY-MM-DD"
}
```

processing：background-removed（背景处理）、ai-enhanced（AI处理）、ai-generated（AI生成示意，非实物照片）。模型名称不硬编码，待实际工具可用时填写，不预先声称使用某模型。

只有 approved=true 且来源校验、透明通道、非全透明、路径和审核记录通过时启用；源文件变化会报错，避免误替换。所有处理图需人工检查完整章体、铭文、颜色、背面对应关系和权利限制。不得以生成图补出的细节作为鉴定依据；分辨率增大不表示新增真实细节。

导出保留 originalSrc、processing 和处理文件校验值。详情可切换“来源原图／处理图”，生成示意有明确标识。移除映射或将 approved=false 后重新导出，即恢复原图。

下一阶段先补真实来源图片；收录完成到适当规模后再统一处理和复核。
