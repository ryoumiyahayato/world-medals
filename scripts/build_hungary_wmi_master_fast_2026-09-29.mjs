import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const stem = 'hungary_wmi_master_fast_2026-09-29';
const imageDir = `assets/images/${stem}`;
const wmi = 'https://www.medals.org.uk/hungary/';
const sourceId = 'wmi_hungary_directory';
const baseNote = '本地文件为完整正面低清参考（原图长边250px）；对应WMI对象页的图注/实物关联需按本条说明核查。WMI未声明摄影者或再分发许可；公开发布权利未核实。';

// Statuses distinguish well-matched object pages from visual candidates retained for later reconciliation.
const data = [
  ['Return of Southern Hungary Medal 1941','南匈牙利回归纪念奖章','Southern Hungary Medal 1941','1941年','匈牙利摄政时期（1918–1944）','HUN-RETURN-SOUTHERN-HUNGARY-MEDAL','正面完整；低清参考',`${wmi}hungary-regency/hungary-regency001.htm`,'Obverse；WMI称设立于1941年。','matched'],
  ['Order of the Holy Crown','圣冠勋章','Magyar Szent Korona rend','1943年3月17日','匈牙利王国（摄政时期；1918–1944）','HUN-ORDER-OF-THE-HOLY-CROWN','大十字级星章；正面完整；低清参考',`${wmi}hungary-regency/hungary-regency004.htm`,'WMI列设立日17 March 1943，图注含Grand Cross: Star, Obverse；本地照片与该星章的对应为视觉匹配。','matched'],
  ['Hungarian Order of Merit','匈牙利功绩勋章','Magyar Érdemrend','1922年6月14日','匈牙利王国（摄政时期；1918–1944）','HUN-HUNGARIAN-ORDER-OF-MERIT-1922','等级／民武版待核；正面完整；低清参考',`${wmi}hungary-regency/hungary-regency002.htm`,'WMI列设立日14 June 1922及Class 1–5、徽章和星章；具体图对应等级待考。','candidate'],
  ['Hungarian Order of Merit','匈牙利功绩勋章','Magyar Érdemrend','1922年6月14日','匈牙利王国（摄政时期；1918–1944）','HUN-HUNGARIAN-ORDER-OF-MERIT-1922','战争饰／授带版待核；正面完整；低清参考',`${wmi}hungary-regency/hungary-regency002.htm`,'同系列不同实物/版型候选；WMI列红色战争饰变体选项，具体图注与等级待考。','candidate'],
  ['Hungarian Order of Merit','匈牙利功绩勋章','Magyar Érdemrend','1922年6月14日','匈牙利王国（摄政时期；1918–1944）','HUN-HUNGARIAN-ORDER-OF-MERIT-1922','星章／挂章版待核；正面完整；低清参考',`${wmi}hungary-regency/hungary-regency002.htm`,'同系列版型候选；WMI列星章及五级挂章，具体图注与等级待考。','candidate'],
  ['Order of Merit of the Hungarian Republic','匈牙利共和国功绩勋章','Magyar Köztársasági Érdemrend','1946年1月1日','匈牙利共和国（1944–1949）','HUN-ORDER-OF-MERIT-HUNGARIAN-REPUBLIC','等级／版型待核；正面完整；低清参考',`${wmi}hungary-1944/hungary1944-001.htm`,'WMI列设立日1 January 1946、五级及三种奖章；本地照片所属级别待核。','candidate'],
  ['Hungarian award candidate 007','匈牙利正式奖章（待考）','Hungarian award; object title unresolved','待考','匈牙利人民共和国时期（1949–1989；暂定）','HUN-WMI-CANDIDATE-007','具体章种、等级待考；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr-text.htm`,'仅据本地图像保留候选；须回到对应单项对象页确认名称、日期和具体等级。','unresolved'],
  ['Hungarian award candidate 008','匈牙利正式奖章（待考）','Hungarian award; object title unresolved','待考','匈牙利人民共和国时期（1949–1989；暂定）','HUN-WMI-CANDIDATE-008','具体章种、等级待考；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr-text.htm`,'仅据本地图像保留候选；须回到对应单项对象页确认名称、日期和具体等级。','unresolved'],
  ['Hungarian award candidate 009','匈牙利正式奖章（待考）','Hungarian award; object title unresolved','待考','匈牙利人民共和国时期（1949–1989；暂定）','HUN-WMI-CANDIDATE-009','具体章种、等级待考；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr-text.htm`,'仅据本地图像保留候选；须回到对应单项对象页确认名称、日期和具体等级。','unresolved'],
  ['Sports Merit Medal of the Hungarian Republic','匈牙利共和国体育功绩奖章','Magyar Köztársasági Sportérdemérem','1947年','匈牙利共和国（1944–1949）','HUN-SPORTS-MERIT-MEDAL-1947','级别待核；正面完整；低清参考',`${wmi}hungary-1944/hungary1944-007.htm`,'WMI称设立于1947年、分三级；图片对应等级待核。','candidate'],
  ['1848 Commemorative Medal','1848纪念奖章','48-as Díszérem','1948年','匈牙利共和国（1944–1949）','HUN-1848-COMMEMORATIVE-MEDAL','正面完整；低清参考',`${wmi}hungary-1944/hungary1944-009.htm`,'WMI称1948年设立以纪念1848年起义百年；图中“100”及肖像与题名相符。','matched'],
  ['Kossuth Bridge Commemorative Medal','科苏特桥纪念奖章','Kossuth Bridge Commemorative Medal','1946年','匈牙利共和国（1944–1949）','HUN-KOSSUTH-BRIDGE-COMMEMORATIVE-MEDAL','银质／铜质组别待核；无授带；正面完整；低清参考',`${wmi}hungary-1944/hungary1944-008.htm`,'WMI称1946年设立，授予桥梁建设参与者，分银、铜两种；本地无授带桥梁图样吻合。','matched'],
  ['Gold Star of Hero of Socialist Labour','社会主义劳动英雄金星','Szocialista Munka Höse cím Arany Csillaga','1953年','匈牙利人民共和国（1949–1989）','HUN-GOLD-STAR-HERO-OF-SOCIALIST-LABOUR','型别待核；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr004.htm`,'WMI称1953年设立并列四种型别；本地金星佩挂照对应关系待核。','candidate'],
  ['Gold Star of Hero of the Hungarian People’s Republic','匈牙利人民共和国英雄金星','Magyar Népköztársaság Höse cím Arany Csillaga','1979年','匈牙利人民共和国（1949–1989）','HUN-GOLD-STAR-HERO-OF-HPR','正面完整；低清参考',`${wmi}hungary-pr/hungary-pr003.htm`,'WMI称1979年设立；红色佩带与边饰三角见对象页说明，图像对应为视觉匹配。','matched'],
  ['Order of the Red Banner of Labour','劳动红旗勋章','Munka Vörös Zásló Érdemrendje','1957–1989年型','匈牙利人民共和国（1949–1989）','HUN-ORDER-OF-RED-BANNER-OF-LABOUR','型别待核；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr005.htm`,'WMI列第二型使用期1957–1989；本地照片与具体型别对应待考。','candidate'],
  ['Hungarian award candidate 016','匈牙利正式勋奖章（待考）','Hungarian award; object title unresolved','待考','匈牙利（时期待考）','HUN-WMI-CANDIDATE-016','具体章种、等级待考；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr-text.htm`,'本地照片已解码；奖名及对象页映射待考，不据外观猜定授予性质。','unresolved'],
  ['Brotherhood in Arms Medal','兄弟武装友谊奖章','Fegyverbarátságért Érdemérem','1979年4月27日','匈牙利人民共和国（1949–1989）','HUN-BROTHERHOOD-IN-ARMS-MEDAL','等级待核；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr007.htm`,'WMI列设立日27 April 1979及三等级；此图对应等级待核。','candidate'],
  ['1956 Commemorative Medal','1956纪念奖章','1956-os Emlékérem','1991年','匈牙利共和国（1989年至今）','HUN-1956-COMMEMORATIVE-MEDAL','图像／对象对应待核；低清参考',`${wmi}hungary/hungary007.htm`,'WMI称1991年设立，但该对象页未列照片；本地图片尚不能证明对应本奖，待考并暂不发布。','unresolved'],
  ['Hungarian award candidate 019','匈牙利人民共和国正式奖章（待考）','Hungarian award; object title unresolved','待考','匈牙利人民共和国时期（暂定）','HUN-WMI-CANDIDATE-019','具体章种、等级待考；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr-text.htm`,'本地照片已解码；对应对象页尚未确认。','unresolved'],
  ['Mining Service Medal','矿业服务奖章','Bányász Szolgálati Érdemérem','1956–1991年','匈牙利人民共和国（1949–1989）','HUN-MINING-SERVICE-MEDAL','第4级铜质；正面完整；低清参考',`${wmi}hungary-pr/hungary-pr014.htm`,'WMI称1956年设立、1991年停授；第4级铜质对象有正反图。本地工具徽记与对象图注吻合。','matched'],
  ['Order of the Red Star','红星勋章','Vörös Csillag Érdemrend','日期待考','匈牙利人民共和国（1949–1989）','HUN-ORDER-OF-THE-RED-STAR','星章正面；低清参考',`${wmi}hungary-pr/hungary-pr-text.htm`,'WMI文本清单列有该正式勋章；单项对象页及设立日期尚未核实，暂存待核。','candidate'],
  ['Hungarian Order of Saint Stephen','匈牙利圣斯蒂芬勋章','Magyar Szent István Rend','2011年','匈牙利共和国（1989年至今）','HUN-ORDER-OF-SAINT-STEPHEN','大十字级勋章；正面完整；低清参考',`${wmi}hungary/hungary034.htm`,'WMI称2011年设立，单一大十字级；对象页列徽章正面及星章，本地照片对应徽章暂定。','candidate'],
  ['Cross of Merit (Civilian)','民事功绩十字章','Magyar Köztársasági Érdemkereszt (polgari)','1991年','匈牙利共和国（1989年至今）','HUN-CROSS-OF-MERIT-CIVILIAN','铜级候选；正面完整；低清参考',`${wmi}hungary/hungary003.htm`,'WMI称1991年设立，民事级分金、银、铜；具体等级及本地图对应待核。','candidate'],
  ['Border Guards Service Decoration','边防警卫服役奖章','Határorségi Szolgálati Jel','1992年','匈牙利共和国（1989年至今）','HUN-BORDER-GUARDS-SERVICE-DECORATION','具体级别与图像映射待考；低清参考',`${wmi}hungary/hungary023.htm`,'WMI称1992年设立、按10/20/30年服役授予，但页面无实物图且所述授带与本地照片不符；暂不发布。','unresolved'],
];

const dims = [[154,250],[247,250],[173,250],[179,250],[265,250],[155,250],[162,250],[169,250],[192,250],[149,250],[152,250],[257,250],[139,250],[143,250],[150,250],[138,250],[164,250],[161,250],[142,250],[146,250],[260,250],[187,250],[155,250],[139,250]];
const records = [];
const images = [];
const candidates = [];
for (let i=0;i<data.length;i++) {
  const [pageTitle,name,original,date,period,family,variant,url,detail,status] = data[i];
  const n = String(i+1).padStart(3,'0');
  const id = `HUN-WMI-${n}`;
  const viewKey = `${id}-FRONT`;
  const localPath = `${imageDir}/HUN-${n}-V01-front.jpg`;
  const file = path.join(root,localPath);
  const bytes = fs.readFileSync(file);
  const [width,height] = dims[i];
  const pageMapConfirmed = !['unresolved'].includes(status);
  records.push({
    id, family, country_zh: period.startsWith('匈牙利王国') ? '匈牙利王国' : period.startsWith('匈牙利共和国') ? '匈牙利' : period.startsWith('匈牙利人民共和国') ? '匈牙利人民共和国' : '匈牙利',
    period_scope: period, name, original, date, variant,
    views:[{key:viewKey,label:'正面'}], source_ids:[sourceId], image_kind:'specimen_photo_reference',
    html_eligible: pageMapConfirmed && !['candidate'].includes(status),
    notes:`${baseNote} ${detail} 该来源照片与本地文件的原始URL映射未保存在现有缓存中；访问日期2026-09-29。`
  });
  images.push({
    view_key:viewKey, local_path:localPath, source_id:sourceId, download_status:'reused_local_existing_decoded_file',
    source_page_url:url, source_original_url:null, retrieval_url:null,
    license:'WMI页面说明图像由贡献者及获许可目录/拍卖方提供；本对象的摄影者、许可条款和本地文件原图地址未在现存缓存中，公开发布权利未核实。',
    width,height,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
    image_kind:'catalogue_object_view_candidate', decoded:true, visually_checked:true,
    notes:`${detail} ${status==='matched'?'页面与图片作了视觉匹配。':status==='candidate'?'系列页/奖名候选匹配，等级或图文映射仍待复核。':'只作待核候选，不进入已核正文。'}`
  });
  candidates.push({
    source_id:sourceId, source_system:'World Medals Index (medals.org.uk)', page_title:pageTitle,
    name_original:original, aliases:[], date_candidates:date==='待考'||date==='日期待考'?[]:[date], category:'formal_order_or_medal',
    grade_material_clues:variant, object_url:url, image_page_url:null, original_image_url:null,
    local_image_path:localPath, status:status==='unresolved'?'unresolved_object_mapping':status==='candidate'?'needs_grade_or_page_image_match':'normalized_with_provisional_visual_match',
    notes:`${detail} ${bytes.length?`本地JPEG ${width}×${height}，SHA-256 ${crypto.createHash('sha256').update(bytes).digest('hex')}`:'本地文件为空'}. ${status==='unresolved'?'不得仅凭搜索摘要或外观确认章种。':''}`,
    access_date:'2026-09-29'
  });
}

// Preserve the empty 25th file as a failed candidate, never as a volume image.
const badRel = `${imageDir}/HUN-025-V01-front.jpg`;
candidates.push({source_id:sourceId,source_system:'World Medals Index (medals.org.uk)',page_title:'Hungarian award candidate 025',name_original:'待考',aliases:[],date_candidates:[],category:'formal_order_or_medal',grade_material_clues:'对象、等级待考',object_url:`${wmi}hungary.htm`,image_page_url:null,original_image_url:null,local_image_path:badRel,status:'excluded_empty_file',notes:'现存文件为0字节，不能解码或进入正文；对象页对应关系待考。',access_date:'2026-09-29'});

const volume = {
  as_of:'2026-09-29', volume_id:stem,
  scope:'匈牙利各历史授予主体的WMI图像收口批次；覆盖摄政王国、1944–1949共和国、人民共和国和1989年至今共和国的已取样候选，不代表穷尽该来源。',
  source_boundary:'使用现有HUN-001–025本地文件并查阅World Medals Index分时期索引及选定对象页。24张JPG可解码；第25张为0字节。正文级对象页映射只确认其中部分，其余保留待核，不宣称完成WMI目录全扫。',
  records
};
const manifest={as_of:'2026-09-29',volume_id:stem,harvest_date:'2026-09-29',images,unpictured_candidates:[],counts:{files:24,decoded:24,visually_checked_complete_fronts:24,long_edge_at_least_1200:0,publication_rights_unverified:24,object_page_image_url_mappings_missing:24}};
const matrixPath=path.join(root,'data/source_atlas/hungary_source_matrix.json');
const matrix=JSON.parse(fs.readFileSync(matrixPath,'utf8'));
matrix.as_of='2026-09-29';
matrix.sources=matrix.sources.filter(s=>s.source_id!=='wmi_hungary_directory');
matrix.sources.push({source_id:sourceId,source_name:'World Medals Index — Hungary period lists and selected object pages',base_url:'https://www.medals.org.uk/hungary/hungary.htm',source_type:'specialist_orders_medals_index',languages:['en'],scope:'Austro-Hungarian/Hungarian historical periods; the current pictured batch samples Regency 1918–1944, Republic 1944–1949, People’s Republic 1949–1989, and Hungary 1989–present.',date_coverage:'1867–present in the index; this batch has pictured candidates mainly 1941–present',has_images:true,has_pagination:false,download_method:'period_text_lists_to_selected_object_pages; existing image files reused',priority:1,status:'partial',last_checked:'2026-09-29',coverage_result:'Period index and four Text Lists inspected; selected object pages opened. 24 local complete-front files decode, 17 have candidate object-page links and 7 remain unresolved/weakly mapped; exact original image URLs are absent from current cache. One additional empty image file excluded. Not a recursive page sweep.',planned_object_pages:'not enumerated in this fast closeout',completed_object_pages:17,partial_object_pages:7,coverage_boundary:'List not exhausted; image-to-object page mapping and original image URL remain unverified for many local files.',candidate_file:`data/raw_candidates/${stem}.jsonl`,volume_file:`data/volumes/${stem}.json`,manifest_file:`data/volumes/${stem}_manifest.json`});
matrix.coverage={planned:3,completed:1,partial:1,blocked:0,not_started:1};
matrix.next_action='继续WMI匈牙利多时期文本清单，逐项完成图像—对象页映射并记录原图地址；随后扩展官方/匈牙利语来源。';

const checkpoint={as_of:'2026-09-29',batch:'Hungary WMI master fast pictured closeout',status:'partial_artifacts_created_mapping_incomplete',plan:['Read existing Hungary source matrix and local WMI image batch.','Reuse only decoded local images; match selected WMI pages and keep uncertain candidates explicit.','Write standard volume, manifest, raw candidate file, source matrix and checkpoint; do not rebuild site.'],completed:['Inspected root AGENTS.md, Hungary matrix and existing legacy Wawards evidence.','Opened WMI Hungary index and Regency, 1944–1949, People’s Republic and current Republic text lists; selected object pages include pages for the Southern Hungary medal, Holy Crown, Hungarian Order of Merit, 1944 Republic order, 1848 and Kossuth Bridge medals, Hero Stars, Red Banner of Labour, Brotherhood in Arms, Mining Service, Saint Stephen and current service awards.','Decoded and visually inspected HUN-001–024; all are complete front-reference files with 250 px long edge.'],partially_completed:['24 standard pictured rows assembled; 9 have comparatively strong page/image matches, other image/page associations remain provisional or unresolved.','Original WMI image URLs and item-specific rights are absent from the existing local cache; publication rights remain unverified.'],not_started:['Exhaust every WMI Hungary Text List object page and pagination/category branch.','Verify exact object/page/image URL for all 24 local images and resolve the 7 weak/unresolved matches.','Check official Hungarian and Hungarian-language sources; merge into index in a later unified build.'],blocked:[],counts:{wmi_period_text_lists_inspected:4,selected_object_pages_opened:17,raw_candidate_records:candidates.length,normalized_family_groups:new Set(records.map(r=>r.family)).size,volume_records:records.length,complete_local_images:images.length,unresolved_candidates:candidates.filter(x=>x.status.includes('unresolved')||x.status==='excluded_empty_file').length,empty_or_unusable_images:1},source_coverage:matrix.coverage,outputs:[`data/raw_candidates/${stem}.jsonl`,`data/source_atlas/hungary_source_matrix.json`,`data/volumes/${stem}.json`,`data/volumes/${stem}_manifest.json`,`data/checkpoints/${stem}.json`,imageDir],next_action:'完成余下图片的对象页与原图URL映射，排除或确认不匹配候选，再进入统一HTML合并队列。'};

fs.writeFileSync(path.join(root,`data/volumes/${stem}.json`),JSON.stringify(volume,null,2)+'\n','utf8');
fs.writeFileSync(path.join(root,`data/volumes/${stem}_manifest.json`),JSON.stringify(manifest,null,2)+'\n','utf8');
fs.writeFileSync(path.join(root,`data/raw_candidates/${stem}.jsonl`),candidates.map(x=>JSON.stringify(x)).join('\n')+'\n','utf8');
fs.writeFileSync(matrixPath,JSON.stringify(matrix,null,2)+'\n','utf8');
fs.writeFileSync(path.join(root,`data/checkpoints/${stem}.json`),JSON.stringify(checkpoint,null,2)+'\n','utf8');
console.log(JSON.stringify({volume_rows:records.length,image_files:images.length,raw_candidates:candidates.length,confirmed_families:new Set(records.map(r=>r.family)).size,html_eligible:records.filter(r=>r.html_eligible).length,unresolved:candidates.filter(x=>x.status.includes('unresolved')||x.status==='excluded_empty_file').length}));
