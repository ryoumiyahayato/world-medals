# 东南亚既有内容整理报告

日期：2026-10-25（Asia/Taipei）。本轮是既有目录、来源记录和接续任务的整理，不新增章种，不改变手机界面或三列图鉴。

## 当前基线与本批结果

已实际读取 mobile-current 的 build-info.json：0.075 / code 75，源码 bf01d9908df7692a651f846183c4fdb100ae5928，当前包记录7803行、8155个照片路径，updated_images=0，applied_batches=[]。这表示云端接入批次为空，不能推断此前本地处理图都未集成，也不能把历史处理总数视作本次集成。main的文档和审查记录可以晚于APK。

本批整理 599 条既有目录行、731 项原队列照片记录，并逐项核对 rowId、family 和当前展示 src 的绑定；发现绑定不一致 0 项。该检查只证明目录对应关系，未证明图像主体、真伪或正背面正确。恢复并读取10份地区历史checkpoint、10份来源矩阵及相关扫描记录；仅从云端ZIP按成员提取，没有恢复整个本地资料库。

本批新增章种0、版型行0；图片处理0、替换0、完成逐图来源鉴定0；目录事实修正0。本范围731项中10项为既有integrated_user_ai_display、721项仍待逐图审查。原队列status与全局已审/待审计数保持原值。完成的是目录记录整理和报告，以下是当前存量及待核事项。

## 当前收录范围

按现有分卷归属统计，含对应有记载未配图附录；family标识只作原目录分组数，未经本轮实体去重证明，不能等同独立章种总数。照片按队列路径项统计，不把正背面合并成一图，也不按相同路径删除内容。

| 范围 | 目录行 | family标识 | 有图行 | 无图行 | 照片队列项 | 尚待逐图审查 |
|---|---:|---:|---:|---:|---:|---:|
| 柬埔寨 | 97 | 49 | 97 | 0 | 155 | 145 |
| 老挝 | 19 | 8 | 19 | 0 | 34 | 34 |
| 文莱 | 93 | 40 | 93 | 0 | 122 | 122 |
| 新加坡 | 20 | 18 | 20 | 0 | 22 | 22 |
| 马来西亚及州属 | 62 | 37 | 62 | 0 | 73 | 73 |
| 菲律宾 | 21 | 14 | 21 | 0 | 38 | 38 |
| 缅甸 | 2 | 2 | 2 | 0 | 4 | 4 |
| 印度尼西亚 | 21 | 12 | 21 | 0 | 33 | 33 |
| 泰国 | 63 | 26 | 63 | 0 | 105 | 105 |
| 越南及既有历史分卷 | 201 | 161 | 104 | 97 | 145 | 145 |

东帝汶未发现独立国家奖励分卷；现有interfet卷是国际部队授予体系，不能算作东帝汶国家目录。英国缅甸星章、美国菲律宾战役章、联合国柬埔寨任务章、澳新越南服役奖励等仍归原授予主体，本表不以地名将它们迁入东南亚国家卷。法属印度支那地方奖励的无图附录另有12行，保留原归属，本轮未作实体鉴定。

## 6000多项与后续队列的关系

README历史段和BUILD.md的v0.043明确记载：累计背景处理788条、裁剪3条另计、剩余6542项背景队列。788+6542=7330只是当时该背景统计口径的算术关系；不是当前章种、版型行或照片数。无法仅凭这段文字确定用户早期“6000多张”唯一所指。迁移成员索引只找到background_rules.json，未找到当时6542项完整待办成员表；因此仍不能建立6542与8155项的逐项迁移映射，也不能将二者相加。

当前原照片审查队列共8155项，integrated=10、source_reviewed=359、individual_review_pending=7786、replacement_pending=8145。这些来自当前main队列字段。已完成来源审查不等于完成背景处理；replacement_pending沿用历史处理图未集成口径，并非已证实错误数或必须替换数。本轮不变更这些计数。

## 历史已完成与仍未完成的来源

以下是2026-09-27至28日来源矩阵状态，非本轮重新扫站结果。合计42个来源任务：完成15、部分3、未开始24。不能用单站扫描完成证明该国内容完整。

| 地区矩阵 | 已完成 | 部分 | 未开始 |
|---|---:|---:|---:|
| brunei | 2 | 0 | 3 |
| cambodia_historical_states | 2 | 0 | 3 |
| indonesia_republic_and_historical | 1 | 1 | 1 |
| laos_historical_states | 2 | 0 | 3 |
| malaysia_federal_and_states | 2 | 1 | 2 |
| myanmar_burma_historical | 1 | 1 | 1 |
| philippines_historical_and_republic | 1 | 0 | 2 |
| singapore | 2 | 0 | 2 |
| thailand | 1 | 0 | 4 |
| vietnam_historical_polities | 1 | 0 | 3 |

历史checkpoint的关键边界：

- 泰国：当年153个MedalBook对象页已扫完，87项无图候选；曾排除2条跨等级图像错配。不能把这2条历史排除再记成本轮修复。官方佩戴顺序与Commons仍待差异复核。
- 柬埔寨：当年World Awards、MedalBook两套目录已扫，128项MedalBook无图候选，1项取图失败；保护国、王国与人民共和国原分卷保留。
- 老挝：当年两套目录已扫，53项MedalBook无图候选；王国与人民民主共和国分开。
- 文莱：当年两套目录已扫，44项MedalBook无图候选；官方与Commons尚未完成。
- 马来西亚：当年MedalBook与联邦官方目录已扫；州属官方目录仍部分完成。576个MedalBook无图对象页不是576个独立缺失章种，联邦官方图可能已补足其中一部分。
- 新加坡：MedalBook、PMO目录当年已扫；65个MedalBook无图对象页和1个官方对象页缺图，彼此覆盖不能直接相加为缺章种数。
- 菲律宾：MedalBook134个对象页已扫，历史保留111项无图候选；Official Gazette/Honors Code与Commons差异核查仍待做。
- 缅甸、印尼：MedalBook已扫，Commons部分完成，分别仍有3、2项当时未解决图像；缅甸未识别原型、军衔与纯绶带图，印尼非官方重构均未据此加入正式奖励。
- 越南：早批MedalBook176页已扫、100项无图候选，后来另有v026南越批次；历史53个family不能直接与后批相加。

## 可据以修改的具体入口

以下只列当前文字和结构可确认的待核候选。涉及实物身份、等级、复制、残损和正背面的结论须回看对象页及原图；本轮不据文件名或颜色下结论。

当前有图行中检出 23 行含未落实版型、待核视图或缺source字段。它们保留原文，未写成错图：

| 原条目ID | 名称 | 当前等级／版型 | 待核事项 | 现有来源入口 |
|---|---|---|---|---|
| KHM-AWARD-ROYAL-ORDER-OF-SOWATHARA-USER-OTHER-20261003-09 | 索瓦塔拉王家勋章 | 军官级绶带花结图式；金色放射章体参考；参考 | 展示视图未填source  现有记录未填对象页；先查用户输入/原来源记录，不猜测 |
| KHM-AWARD-ROYAL-ORDER-OF-SOWATHARA-USER-OTHER-20261003-10 | 索瓦塔拉王家勋章 | 军官级绶带花结图式；银色放射章体参考，色差不作为实际材质鉴定；参考 | 展示视图未填source  现有记录未填对象页；先查用户输入/原来源记录，不猜测 |
| IDN-STAR-MAHAPUTERA-COMMONS | 马哈普特拉星章 | 等级待考；博物馆藏实物正面 | 等级／版型描述仍待落实  https://commons.wikimedia.org/wiki/File:Bintang_Mahaputera.jpg |
| ANNAM-ORDER-DRAGON-USER-OTHER-20261003-15 | 大南龙星 | 龙饰星章；红边蓝色汉字中心与银色放射臂；大十字／大军官细分等级待考；参考 | 等级／版型描述仍待落实；展示视图未填source  现有记录未填对象页；先查用户输入/原来源记录，不猜测 |
| ANNAM-ORDER-AGRICULTURAL-MERIT-USER-OTHER-20261003-17 | 安南农业功绩勋章 | 指挥官式领绶挂章参考；蓝色回纹方形边框、稻穗与红色日轮；具体等级及制造亚型待考；参考 | 等级／版型描述仍待落实  https://www.emering.com/medals/french/annam.html |
| TAI-ORDER-CIVIL-MERIT-USER-OTHER-20261003-13 | 民事功绩勋章 | 黑色十字佩挂章体；正面徽记／背面FEDERATION TAI；细分等级待考，正背未经证实为同一实物；参考 | 等级／版型描述仍待落实  https://www.indochinamedals.com/tai_and_nung/tn01_order_of_civil_merit.html |
| TAI-ORDER-CIVIL-MERIT-USER-OTHER-20261003-14 | 民事功绩勋章 | 大十字级星章图式；八组金色格状放射臂，实际材质待考；参考 | 等级／版型描述仍待落实  https://www.indochinamedals.com/tai_and_nung/tn01_order_of_civil_merit.html |
| V026-RVN-GALLANTRY_CROSS-2 | 英勇十字勋章 | 战场英勇十字勋章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam004.htm |
| V026-RVN-MILITARY_MERIT_MEDAL-2 | 军功奖章 | 最高军事功绩奖章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam006.htm |
| V026-RVN-NATIONAL_ORDER-2 | 国家勋章 | 最高国家功绩勋章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam005.htm |
| V026-RVN-NATIONAL_ORDER-3 | 国家勋章 | 最高国家功绩勋章；等级或版式 3 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam005.htm |
| V026-RVN-NATIONAL_ORDER-4 | 国家勋章 | 最高国家功绩勋章；等级或版式 4 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam005.htm |
| V026-RVN-NATIONAL_ORDER-5 | 国家勋章 | 最高国家功绩勋章；等级或版式 5 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam005.htm |
| V026-RVN-SPECIAL_SERVICE_MEDAL-2 | 特别服役奖章 | 特别勤务奖章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam013.htm |
| V026-RVN-ARMED_FORCES_HONOUR_MEDAL-2 | 武装部队荣誉奖章 | 军队荣誉奖章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam020.htm |
| V026-RVN-ARMED_FORCES_HONOUR_MEDAL-3 | 武装部队荣誉奖章 | 军队荣誉奖章；等级或版式 3 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam020.htm |
| V026-RVN-ARMED_FORCES_HONOUR_MEDAL-4 | 武装部队荣誉奖章 | 军队荣誉奖章；等级或版式 4 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam020.htm |
| V026-RVN-WOUND_MEDAL-2 | 负伤奖章 | 战伤荣誉奖章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam019.htm |
| V026-RVN-LOYALTY_MEDAL-2 | 忠诚奖章 | 军事忠诚奖章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam018.htm |
| V026-RVN-VIETNAMESE_CAMPAIGN_MEDAL-2 | 越南战役奖章 | 战役服役奖章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam001.htm |
| V026-RVN-VIETNAMESE_CAMPAIGN_MEDAL-3 | 越南战役奖章 | 战役服役奖章；等级或版式 3 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam001.htm |
| V026-RVN-VIETNAMESE_CAMPAIGN_MEDAL-4 | 越南战役奖章 | 战役服役奖章；等级或版式 4 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam001.htm |
| V026-RVN-AIR_FORCE_DISTINGUISHED_SERVICE_ORDER-2 | 空军卓越服务勋章 | 空军杰出功绩勋章；等级或版式 2 | 等级／版型描述仍待落实  https://www.medals.org.uk/south-vietnam/south-vietnam002.htm |

南越现有state-south-vietnam、south-vietnam、vietnam-south-v026三个卷名存在时期交叠，属于优先身份比对入口，不能仅凭名称相似合并。逐行对照family、等级、生产时期、图像来源和具体实物，证明重复后才提出合并。马来西亚官方多等级合图属于有标注的整版图示，不自动判作等级错配；商业实物照与官方图式、历史插图分别保留图像性质。

## 下一批接续与保存

先接续本范围原队列第一项：`KHM-AWARD-ROYAL-ORDER-OF-CAMBODIA-MEDALBOOK-010`，柬埔寨王家勋章，指挥官级，完整正面。来源：https://www.medalbook.com/asia/cambodia/cambodia-french-protectorate-1863-1948/orders/royal-order-of-cambodia/royal-order-of-cambodia-commander-5。按当前目录分卷ID过滤同一个image_replacement_current_20261021.json，保留原序，不创建东南亚重复队列。先完成这枚及同系列未完成视图的来源/正背/完整性核查，再继续后面的老挝、文莱等实际队列项。地区顺序以原队列为准。

本轮将报告入口、统计边界、未完成项和下一项写回既有material_reuse_20261021.json，并在原图片审查队列加本轮记录摘要；不把目录整理冒充逐图审查通过。南美洲、北美洲与奥斯曼既有接续记录保留。提交前合并了并行写入main的北美洲记录，保留其队列审查结果及计数。

仅报告与接续记录发生变化，权威release-input.json、当前cloud portable/catalog和图片均未改，不更新APK；固定最新版保持0.075。实体手机未验证。未跑全量测试、全仓库回归或全库图片鉴定，未主动计算文件哈希。

读取出处：mobile-current/build-info.json与cloud-state内catalog.js、cloud/state.json、cloud/portable.json；当前main原checkpoint及图片审查队列；local-backup-20261024/migration.json定位的project-part-07中的地区checkpoint、project-part-08中的来源矩阵与扫描记录。另检查project-final-delta.zip成员目录，未发现覆盖本轮地区checkpoint、来源矩阵和扫描记录的同名项。备份记录为历史线索，当前收录表仅取现行cloud-state。
