"""Geographic discovery queue; each historical award has one canonical record."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def system(name, periods=None, **other):
    return {'name':name,'periods':periods or [],**other}
def region(name,systems): return {'name':name,'systems':systems}
def continent(name,regions): return {'name':name,'regions':regions}

asian=[
 region('东亚',[
  system('中国',[system('清朝（1644–1912）'),system('中华民国（1912–1949，大陆时期）'),system('中华人民共和国（1949–）'),system('其他历史政权')]),
  system('日本',[system('德川幕府／近世时期'),system('明治时期（1868–1912）'),system('大正时期（1912–1926）'),system('昭和时期（1926–1989）'),system('平成时期（1989–2019）'),system('令和时期（2019–）')]),
  system('朝鲜半岛',[system('朝鲜王朝（1392–1897）'),system('大韩帝国（1897–1910）'),system('韩国'),system('朝鲜')])]),
 region('东南亚',[system(x) for x in ['暹罗／泰国','越南','柬埔寨','老挝','缅甸','马来诸国','印度尼西亚诸历史政权','菲律宾']]),
 region('南亚',[system('印度次大陆',[system(x) for x in ['莫卧儿帝国','英属印度','各土邦','印度','巴基斯坦','孟加拉国']])]+[system(x) for x in ['尼泊尔','不丹','斯里兰卡']]),
 region('中亚',[system(x) for x in ['布哈拉','希瓦','浩罕','俄罗斯帝国／苏联时期地方体系','哈萨克斯坦','乌兹别克斯坦','土库曼斯坦','吉尔吉斯斯坦','塔吉克斯坦']]),
 region('西亚',[system('奥斯曼帝国（约1299–1922）',[],status='active',target='ottoman')]+[system(x) for x in ['波斯／伊朗','阿富汗','阿拉伯半岛各政权','海湾各酋长国','伊拉克','黎凡特诸政权']]),
 region('北亚／跨区域政权',[system('俄罗斯帝国与苏联（交叉入口）',target='queue-russian')])]

german=[system('神圣罗马帝国时期',[system(x) for x in ['勃兰登堡／普鲁士','萨克森选侯国','巴伐利亚','各公国','各侯国','自由城市']]),
 system('德意志邦联（1815–1866）',[system('各成员邦')]),system('北德意志邦联（1867–1871）'),
 system('德意志帝国（1871–1918）',[system(x) for x in ['普鲁士王国','巴伐利亚王国','萨克森王国','符腾堡王国','巴登大公国','黑森大公国','梅克伦堡诸邦','萨克森诸公国','罗伊斯诸侯国','施瓦茨堡诸侯国','利珀','绍姆堡-利珀','瓦尔德克','安哈尔特','不伦瑞克','奥尔登堡','汉堡','不来梅','吕贝克']]),
 system('魏玛共和国（1918–1933）'),system('德国（1933–1945）'),system('德意志民主共和国（1949–1990）'),system('德意志联邦共和国（1949–）')]
europe=[region('北欧',[system(x) for x in ['丹麦','瑞典','挪威','芬兰','冰岛']]),
 region('西欧',[system(x) for x in ['英国／大英帝国','法国','比利时','荷兰','卢森堡','爱尔兰']]),
 region('中欧',[system('德国／德意志地区',german),system('哈布斯堡君主国／奥地利／奥匈帝国'),system('瑞士'),system('列支敦士登')]),
 region('南欧',[system(x) for x in ['意大利诸政权','西班牙','葡萄牙','梵蒂冈','圣马力诺','摩纳哥','马耳他']]),
 region('东欧',[system(x) for x in ['波兰','俄罗斯帝国／苏联／俄罗斯联邦','乌克兰','白俄罗斯','捷克与斯洛伐克','波罗的海三国']]),
 region('巴尔干／东南欧',[system(x) for x in ['希腊','罗马尼亚','保加利亚','塞尔维亚','南斯拉夫及后继国家','阿尔巴尼亚','黑山']])]
world={'as_of':'2026-09-25','continents':[
 continent('亚洲',asian),continent('欧洲',europe),
 continent('非洲',[region('北非',[system(x) for x in ['埃及','摩洛哥','突尼斯','阿尔及利亚','利比亚']]),region('撒哈拉以南非洲',[system(x) for x in ['埃塞俄比亚','南非诸政权','西非历史与现代政权','中非历史与现代政权','东非历史与现代政权']])]),
 continent('美洲',[region('北美',[system(x) for x in ['美国','加拿大','墨西哥']]),region('中美洲与加勒比',[system(x) for x in ['中美洲各国','加勒比历史与现代政权']]),region('南美',[system(x) for x in ['巴西帝国与共和国','阿根廷','智利','秘鲁','哥伦比亚','委内瑞拉','玻利维亚','厄瓜多尔','巴拉圭','乌拉圭']])]),
 continent('大洋洲',[region('澳大利亚与新西兰',[system('澳大利亚'),system('新西兰')]),region('太平洋诸岛',[system('历史王国、殖民地与独立国')])])],
 'historical_crosslinks':[{'name':x,'target':'ottoman' if x.startswith('奥斯曼') else 'queued'} for x in ['奥斯曼帝国（约1299–1922）','神圣罗马帝国','奥匈帝国','俄罗斯帝国','苏联','大英帝国','南斯拉夫']],
 'international':[system('联合国体系'),system('红十字与红新月体系'),system('其他国际授予机构')]}
(ROOT/'data/global_queue.json').write_text(json.dumps(world,ensure_ascii=False,indent=2),encoding='utf-8')
