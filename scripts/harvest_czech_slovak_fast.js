const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const root = path.resolve(__dirname, '..');
const imageDir = path.join(root, 'assets', 'images', 'czech_slovak_fast');
const harvestDir = path.join(root, 'data', 'image_harvest');
const normDir = path.join(root, 'data', 'normalized');
const checkpointDir = path.join(root, 'data', 'checkpoints');
for (const d of [imageDir, harvestDir, normDir, checkpointDir]) fs.mkdirSync(d, { recursive: true });

const COMMONS = 'https://commons.wikimedia.org';
const accessed = '2026-09-28';
const commonSource = (file) => `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(file).replace(/%20/g, '_')}`;

// Exact object files selected from Commons category/file pages. Files that are ribbons,
// portraits, certificates, boxes or reverse-only images are deliberately not in this list.
const specs = [
  // Czechoslovak Republic 1918–1948
  {id:'CSK-WL-COLLAR', country:'捷克斯洛伐克', period:'1918–1948', family:'CSK-ORDER-WHITE-LION', name:'白狮勋章', original:'Řád bílého lva / Order of the White Lion', date:'1922', variant:'大十字领饰；含领链、挂章与胸星；博物馆实物', file:'Order of the White Lion grand cross collar (Czechoslovakia 1922-1948) - Tallinn Museum of Orders.jpg', source:'Czechoslovak Republic text list; Tallinn Museum of Orders file page'},
  {id:'CSK-WL-SWORDS', country:'捷克斯洛伐克', period:'1918–1948', family:'CSK-ORDER-WHITE-LION', name:'白狮勋章', original:'Řád bílého lva / Order of the White Lion', date:'1922', variant:'大十字军用带剑挂章；Tallinn Museum of Orders实物', file:'Order of the White Lion grand cross with swords badge (Czechoslovakia 1922-1948) - Tallinn Museum of Orders.jpg', source:'Czechoslovak Republic text list; Tallinn Museum of Orders file page'},
  {id:'CSK-FALCON', country:'捷克斯洛伐克', period:'1918–1938', family:'CSK-ORDER-FALCON', name:'鹰勋章', original:'Řád sokola / Order of the Falcon', date:'1919', variant:'单一型挂章；完整章体与悬挂结构', file:'Falconorder.jpg', source:'Czechoslovak Republic text list; Commons file page'},
  {id:'CSK-WAR-CROSS-1918', country:'捷克斯洛伐克', period:'1918–1948', family:'CSK-WAR-CROSS-1918', name:'捷克斯洛伐克战争十字章', original:'Československý válečný kříž 1914–1918 / Czechoslovak War Cross 1918', date:'1918', variant:'1918版；完整十字章与悬挂件', file:'Czechoslovak War Cross 1918.jpg', source:'Czechoslovak Republic text list; Commons file page'},
  {id:'CSK-WAR-CROSS-1939', country:'捷克斯洛伐克', period:'1939–1945流亡政府', family:'CSK-WAR-CROSS-1939', name:'捷克斯洛伐克战争十字章', original:'Československý válečný kříž 1939 / Czechoslovak War Cross 1939–1945', date:'1940', variant:'1939版；完整十字章', file:'Czechoslovak War Cross 1939-1945.PNG', source:'CSSR/war-award cross-reference; Commons file page'},
  {id:'CSK-BRAVERY-ENEMY', country:'捷克斯洛伐克', period:'1945–1948', family:'CSK-MEDAL-BRAVERY', name:'对敌英勇奖章', original:'Československá medaile Za chrabrost před nepřítelem / Czechoslovak Medal for Bravery before the Enemy', date:'1945', variant:'完整佩戴章；正面', file:'Czechoslovak Medal for Bravery before the Enemy.jpg', source:'Czechoslovak Republic text list; Slovak MoD historical article; Commons file page'},
  {id:'CSK-MIL-ORDER-LIBERTY', country:'捷克斯洛伐克', period:'1945–1948', family:'CSK-MIL-ORDER-LIBERTY', name:'军事自由勋章', original:'Československý vojenský řád Za svobodu / Czechoslovak Military Order for Liberty', date:'1945', variant:'完整挂章；正面', file:'Czechoslovak Military Order for Liberty.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSK-WL-VICTORY-STAR', country:'捷克斯洛伐克', period:'1945–1948', family:'CSK-MIL-WHITE-LION-VICTORY', name:'白狮军事勋章（胜利）', original:'Vojenský řád bílého lva Za vítězství / Military Order of the White Lion for Victory', date:'1945', variant:'胸星；完整星章', file:'Ster van de Militaire Orde van de Witte Leeuw voor de Overwinning 1945.jpg', source:'Czechoslovak award catalogue cross-reference; Commons file page'},
  // Czechoslovak Socialist Republic 1948–1989
  {id:'CSSR-GOLD-STAR-HERO', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-GOLD-STAR-HERO', name:'社会主义共和国英雄金星', original:'Zlatá hvězda hrdiny ČSSR / Gold Star of Hero of the CSSR', date:'1955', variant:'金星奖章；完整章体', file:'Gold Star Hero CSSR.png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-KLEMENT-GOTTWALD', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-KLEMENT-GOTTWALD', name:'克莱门特·哥特瓦尔德勋章', original:'Řád Klementa Gottwalda / Order of Klement Gottwald', date:'1953', variant:'挂章正面；Tallinn Museum of Orders实物', file:'Order of Klement Gottwald badge obverse (Czechoslovakia 1955-1960) - Tallinn Museum of Orders.jpg', source:'CSSR text list; Tallinn Museum of Orders file page'},
  {id:'CSSR-FRIENDSHIP', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-FRIENDSHIP', name:'友谊勋章', original:'Řád přátelství / Order of Friendship', date:'1976', variant:'完整挂章；正面', file:'Order of Friendship (CSSR) 1.png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-LABOUR-ORDER', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-LABOUR', name:'劳动勋章', original:'Řád práce / Order of Labour', date:'1951', variant:'完整挂章；正面', file:'Order of Labor (CSSR).png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-SLOVAK-UPRISING-II', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-SNP', name:'斯洛伐克民族起义勋章', original:'Řád Slovenského národního povstání / Order of the Slovak National Uprising', date:'1945', variant:'二等；完整挂章；正面', file:'Order of the Slovak National Uprising 2 kl.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-SLOVAK-UPRISING-II-BACK', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-SNP', name:'斯洛伐克民族起义勋章', original:'Řád Slovenského národního povstání / Order of the Slovak National Uprising', date:'1945', variant:'二等；同类实物背面参考', file:'Order of the Slovak National Uprising 2 kl rev.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-VICTORIOUS-FEBRUARY', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-VICTORIOUS-FEBRUARY', name:'胜利二月勋章', original:'Řád Vítězného února / Order of Victorious February', date:'1949', variant:'完整挂章；正面', file:'Order victory in February.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-SOCIALISM', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-SOCIALISM', name:'社会主义勋章', original:'Řád socialismu / Order of Socialism', date:'1951', variant:'正面；完整实物', file:'Rad socialismu avers.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-RED-BANNER', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-RED-BANNER', name:'红旗勋章', original:'Řád rudé zástavy / Order of the Red Banner', date:'1955', variant:'完整挂章；正面', file:'Red Banner CSSR.png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-RED-STAR', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-RED-STAR', name:'红星勋章', original:'Řád rudé hvězdy / Order of the Red Star', date:'1955', variant:'完整挂章；正面', file:'Red star CSSR.png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-RED-BANNER-LABOUR', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-RED-BANNER-LABOUR', name:'劳动红旗勋章', original:'Řád rudé zástavy práce / Order of the Red Banner of Labour', date:'1955', variant:'完整挂章；正面', file:'Order of the Red Banner of Labour.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-RED-STAR-LABOUR', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-RED-STAR-LABOUR', name:'劳动红星勋章', original:'Řád rudé hvězdy práce / Order of the Red Star of Labour', date:'1955', variant:'完整挂章；正面', file:'Order of the Red Star of Labour.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-DEVOTION-WORK', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-DECORATION-DEVOTION-WORK', name:'忠于社会主义劳动奖章', original:'Medaile Za obětavou práci pro socialismus / Medal for Devoted Work for Socialism', date:'1953', variant:'完整奖章；正面', file:'Decoration for Devotion to Work.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-LOYAL-WORK', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-DECORATION-LOYAL-WORK', name:'忠诚劳动奖章', original:'Vyznamenání Za pracovní věrnost / Decoration for Loyal Work', date:'1951', variant:'完整奖章；正面', file:'Decoration for Loyal Work.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-BUILD-SOCIALIST-HOMELAND', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-ORDER-BUILDING-SOCIALIST-HOMELAND', name:'建设社会主义祖国勋章', original:'Řád budování socialistické vlasti / Order of Building of the Socialist Homeland', date:'1953', variant:'完整挂章；正面', file:'Řád budování socialistické vlasti.jpg', source:'CSSR text list; Commons file page'},
  {id:'CSSR-COMENIUS', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-COMENIUS-MEDAL', name:'夸美纽斯奖章', original:'Medaile Jana Amose Komenského / Medal of J. A. Comenius', date:'1953', variant:'完整圆章；正面', file:'ComeniusMedal1953 1.png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-ARMY-MERIT-I', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-MEDAL-MERIT-CSLA', name:'捷克斯洛伐克人民军功绩奖章', original:'Medaile Za zásluhy o Československou lidovou armádu / Medal for Merit to the Czechoslovak People’s Army', date:'1955', variant:'一等；完整圆章', file:'CZ Medal Za zasluhy o CSLA 1kl.png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-ARMY-MERIT-II', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-MEDAL-MERIT-CSLA', name:'捷克斯洛伐克人民军功绩奖章', original:'Medaile Za zásluhy o Československou lidovou armádu / Medal for Merit to the Czechoslovak People’s Army', date:'1955', variant:'二等；完整圆章', file:'CZ Medal Za zasluhy o CSLA 2kl.png', source:'CSSR text list; Commons file page'},
  {id:'CSSR-ARMY-MERIT-III', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-MEDAL-MERIT-CSLA', name:'捷克斯洛伐克人民军功绩奖章', original:'Medaile Za zásluhy o Československou lidovou armádu / Medal for Merit to the Czechoslovak People’s Army', date:'1955', variant:'三等；完整圆章', file:'CZ Medal Za zasluhy o CSLA 3kl.png', source:'CSSR text list; Commons file page'},
  {id:'CSK-BACHMAC', country:'捷克斯洛伐克', period:'1918–1948', family:'CSK-BACHMAC-COMMEMORATIVE', name:'巴赫马奇纪念奖章', original:'Bachmačská pamětní medaile / Bachmac Commemorative Medal', date:'1928', variant:'完整奖章；正面', file:'Bachmac Commemorative Medal.jpg', source:'Czechoslovak military commemorative list; Commons file page'},
  {id:'CSK-SOKOLOV', country:'捷克斯洛伐克', period:'1918–1948', family:'CSK-SOKOLOV-COMMEMORATIVE', name:'索科洛夫纪念奖章', original:'Sokolovská medaile / Sokolov Commemorative Medal', date:'1948', variant:'完整奖章；正面', file:'Sokolov medal.JPG', source:'Czechoslovak military commemorative list; Commons file page'},
  {id:'CSK-SNP-COMMEMORATIVE', country:'捷克斯洛伐克社会主义共和国', period:'1948–1989', family:'CSSR-SNP-COMMEMORATIVE', name:'斯洛伐克民族起义勋章纪念章', original:'Pamätná medaila Radu Slovenského národného povstania / Commemorative Medal of the Order of the Slovak National Uprising', date:'1949', variant:'正面；完整奖章', file:'Pamatna medaila Radu Slovenskeho narodneho povstania averz.jpg', source:'CSSR text list; Commons file page'},
  // Czech Republic 1993–present
  {id:'CZE-WHITE-LION', country:'捷克共和国', period:'1993–今', family:'CZE-ORDER-WHITE-LION', name:'白狮勋章', original:'Řád Bílého lva / Order of the White Lion', date:'1994（现行法）', variant:'一等挂章；完整实物', file:'Bílý lev.jpg', source:'Prague Castle official state decorations; Commons file page'},
  {id:'CZE-MASARYK', country:'捷克共和国', period:'1993–今', family:'CZE-ORDER-MASARYK', name:'托马斯·加里格·马萨里克勋章', original:'Řád Tomáše Garrigua Masaryka / Order of Tomáš Garrigue Masaryk', date:'1994（现行法）', variant:'完整挂章；正面', file:'Řád masaryka.jpg', source:'Prague Castle official state decorations; Commons file page'},
  {id:'CZE-HEROISM', country:'捷克共和国', period:'1993–今', family:'CZE-MEDAL-HEROISM', name:'英勇奖章', original:'Medaile Za hrdinství / Medal for Heroism', date:'1994', variant:'完整奖章；正面', file:'Tapferkeitsmedaille der Tschechischen Republik.jpg', source:'Prague Castle official state decorations; Commons file page'},
  {id:'CZE-MERIT', country:'捷克共和国', period:'1993–今', family:'CZE-MEDAL-MERIT', name:'功绩奖章', original:'Medaile Za zásluhy / Medal of Merit', date:'1994', variant:'一等；完整奖章', file:'Medaile Za zásluhy 1. stupně.jpg', source:'Prague Castle official state decorations; Commons file page'},
  {id:'CZE-MOD-CROSS', country:'捷克共和国', period:'1997–今', family:'CZE-MOD-CROSS', name:'国防部长功绩十字章', original:'Záslužný kříž ministra obrany České republiky / Cross of Merit of the Minister of Defence', date:'1997', variant:'完整十字章；正面', file:'Záslužný kříž ministra obrany.jpg', source:'Czech MoD official military awards page; Commons file page'},
  {id:'CZE-MOD-GOLD-LINDEN', country:'捷克共和国', period:'2008–今', family:'CZE-MOD-GOLD-LINDEN', name:'金色菩提树奖章', original:'Zlatá lípa / Golden Linden Decoration of the Ministry of Defence', date:'2008', variant:'完整挂章；正面', file:'Golden Linden Decoration the Ministry of Defence of the Czech Republic.jpg', source:'Czech MoD official military awards page; Commons file page'},
  {id:'CZE-MOD-STATE-DEFENCE-CROSS', country:'捷克共和国', period:'2008–今', family:'CZE-MOD-STATE-DEFENCE-CROSS', name:'国家防御十字章', original:'Kříž obrany státu ministra obrany České republiky / State Defence Cross', date:'2008', variant:'完整十字章；正面', file:'Kříž obrany státu ministra obrany České republiky.jpg', source:'Czech MoD official military awards page; Commons file page'},
  {id:'CZE-MOD-INJURY', country:'捷克共和国', period:'1997–今', family:'CZE-MOD-INJURY', name:'负伤奖章', original:'Medaile za zranění / Medal for Injury', date:'1997', variant:'完整奖章；正面', file:'Medailezazraneni.jpg', source:'Czech MoD official military awards page; Commons file page'},
  {id:'CZE-MEYS', country:'捷克共和国', period:'1993–今', family:'CZE-MEYS-MEDAL', name:'教育、青年与体育部奖章', original:'Medaile Ministerstva školství, mládeže a tělovýchovy / Medal of the Ministry of Education, Youth and Sports', date:'待考', variant:'正面；完整圆章', file:'Medaile MŠMT avers.jpg', source:'Czech awards inventory; Commons file page'},
  {id:'CZE-MEYS-BACK', country:'捷克共和国', period:'1993–今', family:'CZE-MEYS-MEDAL', name:'教育、青年与体育部奖章', original:'Medaile Ministerstva školství, mládeže a tělovýchovy / Medal of the Ministry of Education, Youth and Sports', date:'待考', variant:'同一版型背面；完整圆章', file:'Medaile MŠMT revers.jpg', source:'Czech awards inventory; Commons file page'},
  {id:'CZE-ARTIS', country:'捷克共和国', period:'2000–今', family:'CZE-ARTIS-BOHEMIAE-AMICIS', name:'艺术之友奖章', original:'Artis Bohemiae Amicis', date:'2000', variant:'文化部正式奖章；完整实物', file:'Artis Bohemiae Amicis.JPG', source:'Czech Ministry of Culture awards inventory; Commons file page'},
  {id:'CZE-DIPLOMACY', country:'捷克共和国', period:'1998–今', family:'CZE-DIPLOMACY-MEDAL', name:'外交功绩奖章', original:'Medaile ministra zahraničních věcí Za zásluhy o diplomacii / Medal for Merits in Diplomacy', date:'待考', variant:'外交部正式奖章套件；完整章体', file:'Medaile ministra zahraničních věcí Za zásluhy o diplomacii set.jpg', source:'Czech awards inventory; Commons file page'},
  {id:'CZE-DIPLOMACY-EN', country:'捷克共和国', period:'1998–今', family:'CZE-DIPLOMACY-MEDAL', name:'外交功绩奖章', original:'Medal for Services to Diplomacy', date:'待考', variant:'完整章体照片；正面', file:'Distinguished Contribution to Diplomacy Medal.jpg', source:'Czech Ministry of Foreign Affairs award inventory; Commons file page'},
  // Slovakia 1993–present
  {id:'SVK-WHITE-DOUBLE-CROSS-I-MIL', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-ORDER-WHITE-DOUBLE-CROSS', name:'白色双十字勋章', original:'Rad Bieleho dvojkríža / Order of the White Double Cross', date:'1993', variant:'一等；军事类别；完整挂章', file:'Biely dvojkríž 1. triedy vojenského druhu.jpg', source:'President of Slovakia official state decorations; Commons file page'},
  {id:'SVK-HLINKA-I', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-ORDER-HLINKA', name:'安德烈·赫林卡勋章', original:'Rad Andreja Hlinku / Order of Andrej Hlinka', date:'1993', variant:'一等；完整挂章', file:'Rad Andreja Hlinku 1- triedy.jpg', source:'President of Slovakia official state decorations; Commons file page'},
  {id:'SVK-STUR-I-MIL', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-ORDER-STUR', name:'卢多维特·什图尔勋章', original:'Rad Ľudovíta Štúra / Order of Ľudovít Štúr', date:'1993', variant:'一等；军事类别；完整挂章', file:'Rad Ľudovíta Štúra 1. triedy vojenského druhu.jpg', source:'President of Slovakia official state decorations; Commons file page'},
  {id:'SVK-STEFANIK-I', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-CROSS-STEFANIK', name:'米兰·拉斯蒂斯拉夫·什捷法尼克十字章', original:'Kríž Milana Rastislava Štefánika / Milan Rastislav Štefánik Cross', date:'1993', variant:'完整十字章；等级待核', file:'Kríž Milana Rastislava Štefánika.jpg', source:'President of Slovakia official state decorations; Commons file page'},
  {id:'SVK-PRIBINA-I', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-CROSS-PRIBINA', name:'普里比纳十字章', original:'Pribinov kríž / Pribina Cross', date:'1993', variant:'一等；完整挂章', file:'Pribinov kríž 1. triedy.jpg', source:'President of Slovakia official state decorations; Commons file page'},
  {id:'SVK-PRIBINA-II', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-CROSS-PRIBINA', name:'普里比纳十字章', original:'Pribinov kríž / Pribina Cross', date:'1993', variant:'二等；完整挂章', file:'Pribinov kriz 2 triedy.jpg', source:'President of Slovakia official state decorations; Commons file page'},
  {id:'SVK-PRIBINA-III', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-CROSS-PRIBINA', name:'普里比纳十字章', original:'Pribinov kríž / Pribina Cross', date:'1993', variant:'三等；完整挂章', file:'Pribinov kriz 3 triedy.jpg', source:'President of Slovakia official state decorations; Commons file page'},
  {id:'SVK-SNP-I', country:'斯洛伐克共和国／捷克斯洛伐克历史沿革', period:'1945–今', family:'CSK-ORDER-SNP', name:'斯洛伐克民族起义勋章', original:'Rad Slovenského národného povstania / Order of the Slovak National Uprising', date:'1945', variant:'一等；完整挂章', file:'Rad Slovenského národného povstania 1. triedy.jpg', source:'Czechoslovak/CSSR text list; Commons file page'},
  {id:'SVK-DIPLOMACY', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-DIPLOMACY-MEDAL', name:'斯洛伐克外交功绩奖章', original:'Medaila za zásluhy o slovenskú diplomaciu / Medal for Services to Slovak Diplomacy', date:'待考', variant:'完整奖章；正面', file:'Medaila za zásluhy o slovenskú diplomaciu.jpg', source:'Slovak MFA/Wikipedia inventory; Commons file page'},
  {id:'SVK-DIPLOMACY-WOMEN', country:'斯洛伐克共和国', period:'1993–今', family:'SVK-DIPLOMACY-MEDAL', name:'斯洛伐克外交功绩奖章', original:'Medaila za zásluhy o slovenskú diplomaciu / Medal for Services to Slovak Diplomacy', date:'待考', variant:'女士版；完整奖章', file:'Medaila za zásluhy o slovenskú diplomaciu Dámska.jpg', source:'Slovak MFA/Wikipedia inventory; Commons file page'},
  // Historical Slovak award system, kept explicitly separate from 1993 Republic
  {id:'SVK1939-DEFENCE-MARCH', country:'斯洛伐克国（历史政体）', period:'1939', family:'SVK1939-DEFENCE-MARCH', name:'1939年斯洛伐克防卫纪念章', original:'Pamätná medaila Za obranu Slovenska v marci 1939', date:'1939', variant:'完整纪念章；正面', file:'Pamatna medaila Za obranu Slovenska v marci 1939.jpg', source:'Slovak military decorations category; Commons file page'},
  {id:'SVK1939-WW-CROSS-I', country:'斯洛伐克国（历史政体）', period:'1939–1944', family:'SVK1939-WORLD-WAR-CROSS', name:'世界大战十字章', original:'Pamätný kríž svetovej vojny / World War Cross', date:'1939–1944', variant:'一等；完整十字章', file:'Pamatny kriz svetovej vojny 1 stupna.jpg', source:'Slovak military decorations category; Commons file page'},
  {id:'SVK1939-WW-CROSS-II', country:'斯洛伐克国（历史政体）', period:'1939–1944', family:'SVK1939-WORLD-WAR-CROSS', name:'世界大战十字章', original:'Kríž svetovej vojny Slovenskej republiky / World War Cross', date:'1939–1944', variant:'二等；镀金青铜版；完整十字章', file:'Bronzovy pozlateny Kriz svetovej vojny 2 stupna Slovenskej republiky 1939 az 1944.jpg', source:'Slovak military decorations category; Commons file page'},
  {id:'SVK1939-RESISTANCE-I', country:'斯洛伐克国（历史政体）', period:'1939–1944', family:'SVK1939-RESISTANCE-CROSS', name:'抵抗十字章', original:'Kríž odboja / Resistance Cross', date:'1939–1944', variant:'一等；完整十字章', file:'Kriz odboja 1 stupna vojnovej Slovenskej republiky.jpg', source:'Slovak military decorations category; Commons file page'},
  {id:'SVK1939-MIL-MERIT', country:'斯洛伐克国（历史政体）', period:'1939–1944', family:'SVK1939-MILITARY-MERIT', name:'军事功绩奖章', original:'Vojenská medaila Za zásluhy', date:'1940', variant:'完整奖章；正面', file:'Vojenska medaila Za zasluhy rok 1940.jpg', source:'Slovak military decorations category; Commons file page'},
  {id:'SVK1939-BRAVERY-II', country:'斯洛伐克国（历史政体）', period:'1939–1944', family:'SVK1939-BRAVERY', name:'英勇奖章', original:'Vojenské vyznamenanie Za hrdinstvo / Military Decoration for Bravery', date:'1940', variant:'二等；完整奖章', file:'Vojenske vyznamenanie Za hrdinstvo 2 stupna (1940).jpg', source:'Slovak military decorations category; Commons file page'}
];

function slug(s) {
  return s.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^A-Za-z0-9]+/g, '_').replace(/^_|_$/g, '').toLowerCase();
}
function sha256(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function extFor(file, mime) {
  const ext = path.extname(file).toLowerCase();
  if (ext === '.jpeg' || ext === '.jpg' || ext === '.png' || ext === '.webp') return ext;
  return mime === 'image/png' ? '.png' : '.jpg';
}

async function commonsInfo(titles) {
  const u = `${COMMONS}/w/api.php?action=query&prop=imageinfo&iiprop=url|size|mime|extmetadata&titles=${encodeURIComponent(titles.join('|'))}&format=json`;
  const r = await fetch(u, {headers:{'user-agent':'world-medals-research/1.0 (offline catalogue)'}});
  if (!r.ok) throw new Error(`Commons API ${r.status}`);
  const j = await r.json();
  const out = new Map();
  for (const p of Object.values(j.query?.pages || {})) if (p.imageinfo?.[0]) out.set(p.title, p.imageinfo[0]);
  return out;
}

(async () => {
  const info = new Map();
  const preMetaPath = path.join(harvestDir, 'czech_slovak_fast_commons_metadata.json');
  if (fs.existsSync(preMetaPath)) {
    try {
      const pre = JSON.parse(fs.readFileSync(preMetaPath, 'utf8').replace(/^\uFEFF/, ''));
      for (const [k, v] of Object.entries(pre)) info.set(k, v);
    } catch (e) { console.error(`prefetched metadata read failed: ${e.message}`); }
  }
  if (!info.size) {
    for (let i=0; i<specs.length; i+=12) {
      const chunk = specs.slice(i, i+12).map(s => `File:${s.file}`);
      try { for (const [k,v] of await commonsInfo(chunk)) info.set(k,v); }
      catch (e) { console.error(`info batch ${i}: ${e.message}`); }
      if (i + 12 < specs.length) await new Promise(r => setTimeout(r, 1800));
    }
  }
  const localFiles = fs.readdirSync(imageDir).filter(f => fs.statSync(path.join(imageDir, f)).isFile());
  const normalizeStem = (x) => slug(x).replace(/_jpg$|_jpeg$|_png$|_webp$/g, '');
  const resolvePrefetchedFile = (s) => {
    const wanted = normalizeStem(s.file);
    return localFiles.find(f => normalizeStem(f).startsWith(wanted) || normalizeStem(f).includes(wanted));
  };
  const files = [];
  const records = [];
  const missing = [];
  for (let i=0; i<specs.length; i++) {
    const s = specs[i], title = `File:${s.file}`, ii = info.get(title);
    const prefetchedName = resolvePrefetchedFile(s);
    if (!ii && !prefetchedName) { missing.push({candidate_id:s.id, file:s.file, source_page_url:commonSource(s.file), status:'Commons API file not found and no local prefetch'}); continue; }
    const iiSafe = ii || {url:'', descriptionurl:commonSource(s.file), mime:'image/jpeg'};
    const ext = extFor(s.file, iiSafe.mime), outName = `${s.id.toLowerCase()}${ext}`, rel = `assets/images/czech_slovak_fast/${outName}`, outPath = path.join(imageDir, outName);
    let buf;
    try {
      const prefetchedPath = prefetchedName ? path.join(imageDir, prefetchedName) : null;
      if (prefetchedPath && fs.existsSync(prefetchedPath)) {
        buf = fs.readFileSync(prefetchedPath);
        if (prefetchedPath !== outPath && !fs.existsSync(outPath)) fs.writeFileSync(outPath, buf);
      } else {
        const r = await fetch(iiSafe.url, {headers:{'user-agent':'world-medals-research/1.0 (offline catalogue)'}});
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        buf = Buffer.from(await r.arrayBuffer());
        fs.writeFileSync(outPath, buf);
      }
      const md = await sharp(buf).metadata();
      // Decode and rasterize once here; interrupted downloads must not enter the
      // manifest even if a container header is readable.
      await sharp(buf).resize({width:280,height:280,fit:'inside'}).png().toBuffer();
      const fileRec = {
        file_id:`csk-${slug(s.id)}`, relative_path:rel, candidate_ids:[s.id], family_id:s.family,
        source_page_url:iiSafe.descriptionurl || commonSource(s.file), image_url:iiSafe.url || commonSource(s.file), institution_or_author:'Wikimedia Commons file page (original uploader/institution as credited there)',
        license_or_rights:'See exact Commons file page; preserve attribution and license metadata', accessed, source_image_kind:prefetchedName ? 'complete object image; Commons max-size derivative cached after original route HTTP 429' : 'complete object photograph or complete object image', bytes:buf.length,
        width:md.width, height:md.height, mime:iiSafe.mime, sha256:sha256(buf), decode_status:'verified with sharp', visual_integrity:'pending manual contact-sheet review; complete local file, not search preview', variant_match:s.variant,
        chapter_eligibility:'candidate for pictured row pending visual review', source_file_title:s.file, notes:s.source
      };
      files.push(fileRec);
      records.push({ candidate_id:s.id, family_id:s.family, variant_key:s.variant, match_status:'new_family_candidate', name:s.name, original:s.original, country:s.country, period_scope:s.period, date_candidates:[s.date], official_status:s.source, image_status:'complete local image downloaded; visual review pending', image_manifest_file_ids:[fileRec.file_id], public_row_readiness:'provisional_pictured_row', notes:`Commons source file: ${s.file}` });
    } catch (e) {
      missing.push({candidate_id:s.id, file:s.file, source_page_url:commonSource(s.file), status:e.message});
    }
    if (i + 1 < specs.length) await new Promise(r => setTimeout(r, 350));
  }
  const key = files.map((f,i) => ({n:i+1, file_id:f.file_id, candidate_id:f.candidate_ids[0], rel:f.relative_path}));
  fs.writeFileSync(path.join(harvestDir,'czech_slovak_fast_contact_sheet_key.json'), JSON.stringify(key,null,2)+'\n');
  // Build a labeled contact sheet for manual rejection of ribbons/portraits/boxes.
  const cellW=320, cellH=360, cols=5, rows=Math.ceil(files.length/cols);
  const composites=[];
  for (let i=0;i<files.length;i++) {
    const f=files[i], p=path.join(root,f.relative_path), meta=await sharp(p).metadata();
    const thumb=await sharp(p).resize({width:280,height:280,fit:'inside',background:{r:255,g:255,b:255,alpha:1}}).png().toBuffer();
    const label=`${i+1} ${f.candidate_ids[0]}`;
    const svg=Buffer.from(`<svg width="${cellW}" height="${cellH}"><rect width="100%" height="100%" fill="white"/><text x="8" y="310" font-family="Arial" font-size="13" fill="black">${label}</text><text x="8" y="330" font-family="Arial" font-size="11" fill="#555">${meta.width}×${meta.height}</text></svg>`);
    // Draw the label layer first; the image thumbnail must remain visible above it.
    composites.push({input:svg,left:(i%cols)*cellW,top:Math.floor(i/cols)*cellH});
    composites.push({input:thumb,left:(i%cols)*cellW+20,top:Math.floor(i/cols)*cellH+10});
  }
  await sharp({create:{width:cols*cellW,height:rows*cellH,channels:4,background:{r:245,g:245,b:245,alpha:1}}}).composite(composites).jpeg({quality:88}).toFile(path.join(harvestDir,'czech_slovak_fast_contact_sheet.jpg'));

  const harvest={schema:'image-harvest-v1',batch_id:'czech_slovak_fast_2026-09-28',generated_at:'2026-09-28T00:00:00+08:00',scope:'Czechoslovakia/Czech Republic/Slovakia master-list differential; exact Commons files only',source_access_policy:'One direct retrieval per exact Commons original route; no thumbnail or search-preview substitution.',files,blocked_or_unresolved_routes:missing,counts:{requested_specs:specs.length,downloaded_files:files.length,decoded_files:files.length,visually_checked_files:0,body_eligible_rows:0,manual_review_pending:files.length,missing_or_failed:missing.length},public_files_modified:[]};
  fs.writeFileSync(path.join(harvestDir,'czech_slovak_fast_2026-09-28.json'), JSON.stringify(harvest,null,2)+'\n');
  const normalized={schema:'normalized-award-candidate-v1',batch_id:'czech_slovak_fast_2026-09-28',generated_at:'2026-09-28T00:00:00+08:00',input:'data/raw_candidates/czech_slovak_awards_master_2026-09-28.jsonl',dedupe_boundary:'Selected exact Commons object files; same-family front/back retained as views, not new families.',records,conflicts:[],summary:{input_candidates:121,selected_image_specs:specs.length,downloaded_files:files.length,records_with_local_image:records.length,manual_visual_review_pending:files.length,public_files_modified:[]}};
  fs.writeFileSync(path.join(normDir,'czech_slovak_fast_2026-09-28.json'), JSON.stringify(normalized,null,2)+'\n');
  const cpPath=path.join(checkpointDir,'czech_slovak_fast_2026-09-28.json');
  const cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));
  cp.status='images_downloaded_manual_review_pending'; cp.images={requested_specs:specs.length,downloaded_files:files.length,decoded_files:files.length,body_eligible_rows:0,manual_review_pending:files.length,failed_or_missing:missing.length,contact_sheet:'data/image_harvest/czech_slovak_fast_contact_sheet.jpg'}; cp.normalized={families:new Set(records.map(r=>r.family_id)).size,variants:records.length,status:'provisional_until_visual_review'}; cp.next_action='Open contact sheet; reject any ribbon-only/portrait/box/reverse-only assets, then mark visually_checked and send isolated package to parent.'; fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
  console.log(JSON.stringify({requested:specs.length, downloaded:files.length, decoded:files.length, missing:missing.length, families:new Set(records.map(r=>r.family_id)).size, contact_sheet:'data/image_harvest/czech_slovak_fast_contact_sheet.jpg'},null,2));
})();
