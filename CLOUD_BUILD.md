# 云端图片更新
源码和更新描述进入Git；图片、当前构建状态和APK放在私有Release，不需要本地构建副本。
固定标签mobile-current只保留world-medals-current.apk、world-medals-cloud-state.zip、build-info.json三个当前附件。先上传并核对候选，通过后替换；失败回滚，成功后删除该最新版中的上一包。
图片直接上传到image-inbox Release，再新增cloud/updates/<唯一批次ID>.json：
{"id":"batch-001","images":[{"row_id":"既有条目ID","expected_src":"当前catalog.js中的src","asset_id":123,"kind":"user_processed_display"}]}
明确为AI处理时使用ai_processed_display。条目和当前src须共同指向唯一视图。新图分配独立路径，其他复用旧图的条目保持原图。名称、等级和章种不由图片自动猜测。
保留原出处，并标注处理图性质。已接入的处理图原文件进入当前云端状态；随后删除已接入的inbox附件。批次按ID去重；后续提交仍包含之前排队的批次描述。
版本号依据云端状态递增，mobile/version.json为最低种子版本。首次从local-backup-20261024提取必要输入，以后只下载当前云端状态。
复用已有ATLAS_KEYSTORE_BASE64和ATLAS_KEYSTORE_PASSWORD Secrets。密钥仅在云端runner临时目录使用。
当前接入针对已有条目图片。目录结构或事实源变更时须显式刷新云端目录，不能让缓存覆盖新事实。
