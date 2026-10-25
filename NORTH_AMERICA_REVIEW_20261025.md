# 北美洲既有收录整理报告
日期：2026-10-25（Asia/Taipei）。范围仅美国、加拿大、墨西哥，含加拿大联邦及三个省份旧卷。

## 当前基线与接续
实时读取 mobile-current/build-info.json 及 cloud/state.json：0.075/code75，sourceCommit bf01d9908df7692a651f846183c4fdb100ae5928；7803行、8155个照片路径。只从当前状态包读取目录、出处及本批展示文件，没有恢复整套原图库。源码已接续 main 最新记录。

6542是v0.043背景待处理数；原6542成员队列未在已知迁移索引中定位，无法逐项证明与8155队列的关系。788条背景规则、3条裁剪规则是历史记录；已有接续记录发现727个路径与后续队列交叠，不可相加。当前总队列10项已集成用户处理展示、338项来源已审、7807项待逐图审查；8145是历史处理/替换待办口径，不是错图数，也不要求全部抠图。

## 本批实际完成
核对73行、75个展示视图与原队列条目，读取现有来源索引；75个当前展示文件均可解码，完成总览目视初查。此项不等于原尺寸原图鉴定或来源审查完成。目录事实修正0、背景处理0、图片替换0、新增章种0。

|范围|版型行|照片视图|现有family ID数|展示长边小于384像素|
|---|---:|---:|---:|---:|
|美国|27|29|27|19|
|加拿大|40|40|23|39|
|墨西哥|6|6|2|6|

family ID仅为当前目录分组键；加拿大跨旧卷的同名章尚未归一，因此不能把ID数当作已确认独立章种数。长边统计仅指现有展示文件，不是原图或章体有效像素，也不是替换清单。

## 后续修改重点
1. 加拿大：官方图式与商业目录的加拿大勋章同伴级分行保留，核对同名family的跨卷关系后再考虑归并；不得合并不同等级、男女佩式。官方图式画面上缘截断绶带，章体和悬挂可见；不因这张图声称完整绶带或摄影实物。追思十字章四种君主纪号需对象页逐件确认；查理三世纪号图未展示绶带，不能生成补齐。
2. 加拿大特别服役奖章已有“未附任务横杠（非完整获授组合）”限定，应保留。魁北克三级、萨斯喀彻温和安大略保持各自授予主体，不因都在加拿大而合成国家等级。
3. 美国：27行29视图。Ah Foy马尼拉湾与U.S.S. New York西印度群岛各两视图，保留原配对；对象页不可读，本次不能重新确认是否同件。多张NHHC小图已注明低清，背景中的地图、比例尺与旧标签不删除。银星、紫心等设立日期与版型年代继续分开。特别优异服役奖章悬挂范围、旧图中的附件性质仍需原页确认，不凭色彩鉴定材质。墨西哥服役奖章属于美国授予体系。
4. 墨西哥：阿兹特克鹰三个等级及长期服役三个等级分别保留。旧制第二级/第四级与现制名称对应关系、长期服役35/30/25年的制度时期需原页及制度资料核对，不按照片颜色改成金银铜。
5. 复制、改装、残损：本次只有现有展示与旧来源说明，未取得足以新增这些鉴定的证据；不得把“本次未发现”写成“保证真品完整”。

## 来源边界与下一批入口
加拿大国防部、NHHC、medals.org.uk的代表来源请求均在代理隧道阶段返回403；未取得对象页正文，不是来源网站已证实删除。未绕过策略、未反复重试。全部本批队列项保留原状态，仅追加总览记录。下一批先按原队列顺序核对加拿大官方同伴级，再核对美国内战奖章与两组实物正背面；加拿大旧卷和墨西哥按下表接续。原奥斯曼未完成任务继续保存在原checkpoint，不被本次范围替换。

## 逐行定位表
下表为当前目录原文摘要。尺寸均为展示文件；“待核”表示本次未重开来源确认，不表示已发现错图。

|条目ID／名称|等级版型（现有）|视图及尺寸|来源与后续任务|
|---|---|---|---|
|CAN-ORDER-CANADA-COMPANION-OFFICIAL／加拿大勋章|同伴级（Companion，C.C.）；颈挂章；官方图式·低清参考|官方正面图式 300×558|https://www.canada.ca/en/department-national-defence/services/medals/medals-chart-index/companion-order-canada-cc.html；对象页、等级/版型与具体视图待核；保留现图|
|US-CWM-1908-USN-STANDARD／美国海军内战奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 150×237|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/usn-civil-war-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-NGCM-1869-V-TYPE-I／美国海军良好行为奖章|I型马耳他十字式；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 496×858|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/navy-good-conduct-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-MANILA-BAY-1898-V-AH-FOY／马尼拉湾战役奖章|USS Olympia水兵Ah Foy受授实物；正背面；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 1161×1200；完整实物图·反面 1128×1200|https://www.history.navy.mil/our-collections/artifacts/uniforms-and-personal-equipment/awards/medals/battle-of-manila-bay-medal--ah-foy.html；对象页、等级/版型与具体视图待核；保留现图|
|US-SCM-1898-USN-STANDARD／美国海军西班牙战役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 154×239|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/usn-spanish-campaign-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-PC-MEDAL-1908-USN-STANDARD／美国海军菲律宾战役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 153×219|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/usn-philippine-campaign-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-SAMPSON-1901-V-NEW-YORK／西印度群岛海军战役奖章|U.S.S. New York舰名扣饰型；Feinbloom藏品正背面；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 587×783；完整实物图·反面 500×784|https://www.history.navy.mil/our-collections/artifacts/uniforms-and-personal-equipment/awards/medals/west-indies-naval-campaign-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-SMM-1901-V-BRONZE／特别优异服役奖章|铜质悬挂十字式；正面；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 1200×1187|https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/80-G-K-13000/80-G-K-13528.html；对象页、等级/版型与具体视图待核；保留现图|
|US-CUPM-1909-STANDARD／美国海军古巴绥靖奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 151×224|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/usn-cuban-pacification-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-NCM-1912-STANDARD／尼加拉瓜战役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 151×225|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/nicaraguan-campaign-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-MSM-1914-STANDARD／墨西哥服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 153×212|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/mexican-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-DCM-1916-STANDARD／多米尼加战役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 152×226|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/dominican-campaign-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-WWIVM-1917-STANDARD／第一次世界大战胜利奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 151×217|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/world-war-i-victory-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-SSM-1932-V-STANDARD／银星勋章|1932年改制奖章式；正面；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 900×1200|https://www.history.navy.mil/browse-by-topic/heritage/awards/decorations/silver-star.html；对象页、等级/版型与具体视图待核；保留现图|
|US-DFC-1926-V-STANDARD／优异飞行十字勋章|标准悬挂式十字章；正面；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 935×1200|https://www.history.navy.mil/browse-by-topic/heritage/awards/decorations/distinguished-flying-cross.html；对象页、等级/版型与具体视图待核；保留现图|
|US-NCM2-1926-STANDARD／第二次尼加拉瓜战役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 152×215|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/second-nicaraguan-campaign-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-YSM-1926-1932-STANDARD／长江服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 144×205|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/yangtze-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-PH-1932-V-OBVERSE／紫心勋章|1932年后奖章式；正面；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 806×1200|https://www.history.navy.mil/browse-by-topic/heritage/awards/decorations/purple-heart-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-CSM-1937-1942-STANDARD／中国服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 152×214|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/china-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-DSM-1939-1941-STANDARD／美国国防服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 153×217|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/american-defense-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-BSM-1944-V-PLAIN／铜星勋章|标准悬挂式；正面；美国海军历史与遗产司令部／国家档案来源|完整实物图·正面 826×1200|https://www.history.navy.mil/browse-by-topic/heritage/awards/decorations/bronze-star.html；对象页、等级/版型与具体视图待核；保留现图|
|US-WWIIVM-1945-STANDARD／第二次世界大战胜利奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 153×223|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/world-war-ii-victory-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-MHA-1949-BERLIN-AIRLIFT／人道行动奖章（柏林空运）|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 150×219|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/medal-for-humane-action-berlin-airlift.html；对象页、等级/版型与具体视图待核；保留现图|
|US-NDSM-1953-STANDARD／国防服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 147×205|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/national-defense-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-ASM-1961-STANDARD／南极服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 148×213|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/antarctic-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-HSM-1977-STANDARD／人道主义服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 150×196|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/humanitarian-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-KCM-1999-STANDARD／科索沃战役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 144×220|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/kosovo-campaign-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|US-NOSM-1945-STANDARD／海军占领服役奖章|标准悬挂式；NHHC目录原图；完整奖章与绶带，低清参考|官方目录实物图·低清参考 152×217|https://www.history.navy.mil/browse-by-topic/heritage/awards/service-campaign/navy-occupation-service-medal.html；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA025-124ECFF5EB／追思十字章|乔治五世纪号版；低清参考|完整正面（低清参考） 208×250|https://www.medals.org.uk/canada/canada025.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA025-6E74257719／追思十字章|伊丽莎白二世纪号版；低清参考|完整正面（低清参考） 176×250|https://www.medals.org.uk/canada/canada025.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA025-79879A580F／追思十字章|乔治六世纪号版；低清参考|完整正面（低清参考） 192×250|https://www.medals.org.uk/canada/canada025.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA025-C0282A5473／追思十字章|查理三世纪号版；低清参考|完整正面（低清参考） 260×250|https://www.medals.org.uk/canada/canada025.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA004-B70AF4ACB0／加拿大志愿服役奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 133×250|https://www.medals.org.uk/canada/canada004.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA001-42F68931B7／加拿大勋章|同伴级；男式佩章；低清参考|完整正面（低清参考） 162×250|https://www.medals.org.uk/canada/canada001.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA001-4EEF2FD1E1／加拿大勋章|成员级；低清参考|完整正面（低清参考） 135×250|https://www.medals.org.uk/canada/canada001.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA001-A57CCCFB07／加拿大勋章|军官级；女式蝴蝶结佩章；低清参考|完整正面（低清参考） 210×250|https://www.medals.org.uk/canada/canada001.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA001-DDD5093DD9／加拿大勋章|军官级；男式佩章；低清参考|完整正面（低清参考） 186×250|https://www.medals.org.uk/canada/canada001.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA006-741F32E63C／加拿大联邦成立百周年奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 164×250|https://www.medals.org.uk/canada/canada006.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA002-B4D3D71282／军事功绩勋章|军官级；低清参考|完整正面（低清参考） 124×250|https://www.medals.org.uk/canada/canada002.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA002-E5A7706B0D／军事功绩勋章|指挥官级；低清参考|完整正面（低清参考） 206×250|https://www.medals.org.uk/canada/canada002.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA002-EE1BA1696D／军事功绩勋章|成员级；低清参考|完整正面（低清参考） 130×250|https://www.medals.org.uk/canada/canada002.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA007-A806994B8B／勇敢十字章|男式佩章；低清参考|完整正面（低清参考） 163×250|https://www.medals.org.uk/canada/canada007.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA007-DEA548A1FA／勇敢十字章|女式蝴蝶结佩章；低清参考|完整正面（低清参考） 220×250|https://www.medals.org.uk/canada/canada007.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA018-44C8EEBE40／勇气之星章|女式蝴蝶结佩章；低清参考|完整正面（低清参考） 226×250|https://www.medals.org.uk/canada/canada018.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA018-49AC4F9073／勇气之星章|男式佩章；低清参考|完整正面（低清参考） 122×250|https://www.medals.org.uk/canada/canada018.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA019-7DCC7AE6CB／勇敢奖章|男式佩章；低清参考|完整正面（低清参考） 110×250|https://www.medals.org.uk/canada/canada019.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA019-F0AFA6C052／勇敢奖章|女式蝴蝶结佩章；低清参考|完整正面（低清参考） 218×250|https://www.medals.org.uk/canada/canada019.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA014-C7D566B0F6／特别服役奖章|章饰图示；未附任务横杠（非完整获授组合）；低清参考|完整正面（低清参考） 99×250|https://www.medals.org.uk/canada/canada014.htm；保留缺任务横杠限定；核对适用组合|
|V020-CANADA-CANADA008-F837F75E2B／功绩服役十字章|佩章；具体版型按图；军事部；低清参考|完整正面（低清参考） 115×250|https://www.medals.org.uk/canada/canada008.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA020-D9B0784F7C／功绩服役十字章|佩章；具体版型按图；民事部；低清参考|完整正面（低清参考） 129×250|https://www.medals.org.uk/canada/canada020.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA016-449DBD3306／海湾与科威特奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 139×250|https://www.medals.org.uk/canada/canada016.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA015-B10A0F848A／加拿大朝鲜战争志愿服役奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 148×250|https://www.medals.org.uk/canada/canada015.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA017-013599327E／加拿大联邦成立一百二十五周年奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 159×250|https://www.medals.org.uk/canada/canada017.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA010-CB7E4FEEF0／军事英勇之星章|佩章；具体版型按图；低清参考|完整正面（低清参考） 106×250|https://www.medals.org.uk/canada/canada010.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA011-25CA33039F／军事英勇奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 204×250|https://www.medals.org.uk/canada/canada011.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA005-31348AA7A8／索马里奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 116×250|https://www.medals.org.uk/canada/canada005.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA024-7ED9B1D3D6／加拿大维和服役奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 128×250|https://www.medals.org.uk/canada/canada024.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA023-3F8EA5888D／警察部队功绩勋章|军官级；低清参考|完整正面（低清参考） 105×250|https://www.medals.org.uk/canada/canada023.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA023-4D3F86D464／警察部队功绩勋章|成员级；低清参考|完整正面（低清参考） 101×250|https://www.medals.org.uk/canada/canada023.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA023-5E807ADF0E／警察部队功绩勋章|指挥官级；低清参考|完整正面（低清参考） 134×250|https://www.medals.org.uk/canada/canada023.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA027-43F03EBC5D／西南亚服役奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 115×250|https://www.medals.org.uk/canada/canada027.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA029-9F926D7F7C／治安官模范服役奖章|佩章；具体版型按图；低清参考|完整正面（低清参考） 92×250|https://www.medals.org.uk/canada/canada029.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA028-68C09ABB8B／魁北克国家勋章|大军官级；低清参考|完整正面（低清参考） 248×250|https://www.medals.org.uk/canada/canada028.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA028-CBEDFCC4AC／魁北克国家勋章|骑士级；低清参考|完整正面（低清参考） 183×250|https://www.medals.org.uk/canada/canada028.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA028-DACC08E148／魁北克国家勋章|军官级；低清参考|完整正面（低清参考） 183×250|https://www.medals.org.uk/canada/canada028.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA030-8AF12536A4／萨斯喀彻温功绩勋章|佩章；具体版型按图；低清参考|完整正面（低清参考） 128×250|https://www.medals.org.uk/canada/canada030.htm；对象页、等级/版型与具体视图待核；保留现图|
|V020-CANADA-CANADA031-8ED82DEAA1／安大略勋章|佩章；具体版型按图；低清参考|完整正面（低清参考） 122×250|https://www.medals.org.uk/canada/canada031.htm；对象页、等级/版型与具体视图待核；保留现图|
|V021-MEXICO-MEXICO001-9D7E04FC／阿兹特克鹰勋章|大十字级星章；来源所标旧制等级；低清参考|完整正面（低清参考） 247×250|https://www.medals.org.uk/mexico/mexico001.htm；旧制等级、制度时期及对应图片待核|
|V021-MEXICO-MEXICO001-D706CECB／阿兹特克鹰勋章|第二级星章；来源所标旧制等级；低清参考|完整正面（低清参考） 236×250|https://www.medals.org.uk/mexico/mexico001.htm；旧制等级、制度时期及对应图片待核|
|V021-MEXICO-MEXICO001-DE80AF9E／阿兹特克鹰勋章|第四级挂章；来源所标旧制等级；低清参考|完整正面（低清参考） 114×250|https://www.medals.org.uk/mexico/mexico001.htm；旧制等级、制度时期及对应图片待核|
|V021-MEXICO-MEXICO019-03B52246／长期服役奖章|特级挂章（35年服役）；低清参考|完整正面（低清参考） 124×250|https://www.medals.org.uk/mexico/mexico019.htm；旧制等级、制度时期及对应图片待核|
|V021-MEXICO-MEXICO019-55014D3F／长期服役奖章|第一级挂章（30年服役）；低清参考|完整正面（低清参考） 127×250|https://www.medals.org.uk/mexico/mexico019.htm；旧制等级、制度时期及对应图片待核|
|V021-MEXICO-MEXICO019-EC25768B／长期服役奖章|第二级挂章（25年服役）；低清参考|完整正面（低清参考） 121×250|https://www.medals.org.uk/mexico/mexico019.htm；旧制等级、制度时期及对应图片待核|

## 保存与交付
报告及原队列、checkpoint写入GitHub；没有修改权威目录、云端构建输入或图片，因此不触发封装、不上传图片、不替换当前APK。未跑全量测试或全仓库回归；实体手机未验证。
