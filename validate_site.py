"""Static offline acceptance checks; no browser network or file fetch required."""
import hashlib,json,re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
html=(ROOT/'index.html').read_text(encoding='utf-8')
css=(ROOT/'assets/site.css').read_text(encoding='utf-8')
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.images=[];self.links=[];self.scripts=[];self.styles=[];self.family_buttons=[];self.family_rows=[]
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='img':self.images.append(a.get('src',''))
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='script' and 'src' in a:self.scripts.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.styles.append(a.get('href',''))
        if tag=='button' and a.get('data-family-toggle'):self.family_buttons.append((a['data-family-toggle'],a.get('aria-expanded')))
        if tag=='tr' and a.get('data-family-key'):self.family_rows.append((a['data-family-key'],'hidden' in a))
p=Page();p.feed(html)
gallery_images=[url for url in p.images if url]
catalogue=json.loads((ROOT/'data/catalogue.json').read_text(encoding='utf-8'))['records']
related=json.loads((ROOT/'data/related.json').read_text(encoding='utf-8'))
volume_records=[]
all_view_paths={}
asset_countries=defaultdict(set)
volume_files={
 'ottoman_extra':(['ottoman_commons_batch1.json','mena_round7_2026-09-26.json','ottoman_medalbook_pack2.json','ottoman_kuenker299_batch2.json','ottoman_kuenker299_batch3.json','ottoman_kuenker299_batch4.json','ottoman_kuenker299_batch5.json','ottoman_kuenker299_batch6.json','ottoman_itu_tayyare.json','ottoman_itu_ferahi.json','ottoman_sinop_mdc.json','ottoman_tasvir_humayun.json','ottoman_nam_danube.json','ottoman_spink21001.json','ottoman_spink_variants.json','ottoman_spink_archive_variants.json','ottoman_cgb_current.json'],['ottoman_commons_batch1_manifest.json','mena_round7_manifest_2026-09-26.json','ottoman_medalbook_pack2_manifest.json','ottoman_kuenker299_batch2_manifest.json','ottoman_kuenker299_batch3_manifest.json','ottoman_kuenker299_batch4_manifest.json','ottoman_kuenker299_batch5_manifest.json','ottoman_kuenker299_batch6_manifest.json','ottoman_itu_tayyare_manifest.json','ottoman_itu_ferahi_manifest.json','ottoman_sinop_mdc_manifest.json','ottoman_tasvir_humayun_manifest.json','ottoman_nam_danube_manifest.json','ottoman_spink21001_manifest.json','ottoman_spink_variants_manifest.json','ottoman_spink_archive_variants_manifest.json','ottoman_cgb_current_manifest.json'],{'奥斯曼帝国'},{'ottoman_commons_batch1.json','ottoman_medalbook_pack2.json','ottoman_kuenker299_batch2.json','ottoman_kuenker299_batch3.json','ottoman_kuenker299_batch4.json','ottoman_kuenker299_batch5.json','ottoman_kuenker299_batch6.json','ottoman_itu_tayyare.json','ottoman_itu_ferahi.json','ottoman_sinop_mdc.json','ottoman_tasvir_humayun.json','ottoman_nam_danube.json','ottoman_spink21001.json','ottoman_spink_variants.json','ottoman_spink_archive_variants.json','ottoman_cgb_current.json'}),
 'egypt':(['egypt_republic_pack1.json','mena_round7_2026-09-26.json','mena_gap_round1_2026-09-26.json','egypt_commons_verified.json','egypt_wawards_pack1.json','egypt_wawards_major_variants.json','egypt_wawards_medal_variants.json','egypt_omsa_unpictured_pack1.json','egypt_medals_org_variants.json','egypt_medals_org_republic_variants.json','egypt_emedals_variants.json','egypt_khedive_star_reconciled.json','egypt_spink26001.json','egypt_medalbook_variants.json'],['egypt_republic_pack1_manifest.json','mena_round7_manifest_2026-09-26.json','mena_gap_round1_manifest_2026-09-26.json','egypt_commons_verified_manifest.json','egypt_wawards_pack1_manifest.json','egypt_wawards_major_variants_manifest.json','egypt_wawards_medal_variants_manifest.json','egypt_omsa_unpictured_pack1_manifest.json','egypt_medals_org_variants_manifest.json','egypt_medals_org_republic_variants_manifest.json','egypt_emedals_variants_manifest.json','egypt_khedive_star_reconciled_manifest.json','egypt_spink26001_manifest.json','egypt_medalbook_variants_manifest.json'],{'埃及'},{'egypt_republic_pack1.json','egypt_commons_verified.json','egypt_wawards_pack1.json','egypt_wawards_major_variants.json','egypt_wawards_medal_variants.json','egypt_omsa_unpictured_pack1.json','egypt_medals_org_variants.json','egypt_medals_org_republic_variants.json','egypt_emedals_variants.json','egypt_khedive_star_reconciled.json','egypt_spink26001.json','egypt_medalbook_variants.json'}),
 'sudan':(['mena_round7_2026-09-26.json','sudan_wawards_pack1.json','sudan_medalbook_unpictured_pack1.json','sudan_commons_variants.json','sudan_presidency_official_variants.json','sudan_presidency_alt_official_variants.json','sudan_spink21001.json','sudan_noonans_variants.json','sudan_emedals_variants.json','sudan_noble_variants.json','sudan_spink_archive_variants.json'],['mena_round7_manifest_2026-09-26.json','sudan_wawards_pack1_manifest.json','sudan_medalbook_unpictured_pack1_manifest.json','sudan_commons_variants_manifest.json','sudan_presidency_official_variants_manifest.json','sudan_presidency_alt_official_variants_manifest.json','sudan_spink21001_manifest.json','sudan_noonans_variants_manifest.json','sudan_emedals_variants_manifest.json','sudan_noble_variants_manifest.json','sudan_spink_archive_variants_manifest.json'],{'苏丹'},{'sudan_wawards_pack1.json','sudan_medalbook_unpictured_pack1.json','sudan_commons_variants.json','sudan_presidency_official_variants.json','sudan_presidency_alt_official_variants.json','sudan_spink21001.json','sudan_noonans_variants.json','sudan_emedals_variants.json','sudan_noble_variants.json','sudan_spink_archive_variants.json'}),
 'iran':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'伊朗／波斯'},set()),
 'turkey':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'土耳其共和国'},set()),
 'syria':(['mena_round7_2026-09-26.json','syria_wawards_families.json'],['mena_round7_manifest_2026-09-26.json','syria_wawards_families_manifest.json'],{'叙利亚','叙利亚共和国'},{'syria_wawards_families.json'}),
 'oman':(['mena_round7_2026-09-26.json','oman_wawards_families.json'],['mena_round7_manifest_2026-09-26.json','oman_wawards_families_manifest.json'],{'阿曼','阿曼苏丹国'},{'oman_wawards_families.json'}),
 'jordan':(['jordan_wawards_families.json'],['jordan_wawards_families_manifest.json'],{'约旦哈希姆王国'},{'jordan_wawards_families.json'}),
 'saudi-arabia':(['saudi_arabia_wawards_families.json'],['saudi_arabia_wawards_families_manifest.json'],{'沙特阿拉伯王国'},{'saudi_arabia_wawards_families.json'}),
 'qatar':(['qatar_wawards_families.json'],['qatar_wawards_families_manifest.json'],{'卡塔尔国'},{'qatar_wawards_families.json'}),
 'kuwait':(['kuwait_wawards_families.json'],['kuwait_wawards_families_manifest.json'],{'科威特国'},{'kuwait_wawards_families.json'}),
 'bahrain':(['bahrain_wawards_families.json'],['bahrain_wawards_families_manifest.json'],{'巴林王国'},{'bahrain_wawards_families.json'}),
 'united-arab-emirates':(['united_arab_emirates_wawards_families.json'],['united_arab_emirates_wawards_families_manifest.json'],{'阿拉伯联合酋长国'},{'united_arab_emirates_wawards_families.json'}),
 'lebanon':(['lebanon_wawards_families.json'],['lebanon_wawards_families_manifest.json'],{'黎巴嫩共和国'},{'lebanon_wawards_families.json'}),
 'israel':(['israel_wawards_families.json'],['israel_wawards_families_manifest.json'],{'以色列国'},{'israel_wawards_families.json'}),
 'afghanistan':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'阿富汗'},set()),
 'pakistan':(['mena_round7_2026-09-26.json','pakistan_medalbook_variants.json','pakistan_medals_org_variants.json'],['mena_round7_manifest_2026-09-26.json','pakistan_medalbook_variants_manifest.json','pakistan_medals_org_variants_manifest.json'],{'巴基斯坦'},{'pakistan_medalbook_variants.json','pakistan_medals_org_variants.json'}),
 'nepal':(['nepal_medalbook_variants.json','nepal_medals_org_variants.json'],['nepal_medalbook_variants_manifest.json','nepal_medals_org_variants_manifest.json'],{'尼泊尔王国／尼泊尔'},{'nepal_medalbook_variants.json','nepal_medals_org_variants.json'}),
 'bhutan':(['bhutan_medalbook_variants.json','bhutan_medals_org_variants.json'],['bhutan_medalbook_variants_manifest.json','bhutan_medals_org_variants_manifest.json'],{'不丹王国'},{'bhutan_medalbook_variants.json','bhutan_medals_org_variants.json'}),
 'bangladesh':(['bangladesh_medalbook_variants.json','bangladesh_medals_org_variants.json'],['bangladesh_medalbook_variants_manifest.json','bangladesh_medals_org_variants_manifest.json'],{'孟加拉国'},{'bangladesh_medalbook_variants.json','bangladesh_medals_org_variants.json'}),
 'sri-lanka':(['sri_lanka_medalbook_variants.json','sri_lanka_medals_org_variants.json'],['sri_lanka_medalbook_variants_manifest.json','sri_lanka_medals_org_variants_manifest.json'],{'锡兰','斯里兰卡民主社会主义共和国'},{'sri_lanka_medalbook_variants.json','sri_lanka_medals_org_variants.json'}),
 'kazakhstan':(['mena_round7_2026-09-26.json','kazakhstan_medalbook_variants.json','kazakhstan_medals_org_variants.json'],['mena_round7_manifest_2026-09-26.json','kazakhstan_medalbook_variants_manifest.json','kazakhstan_medals_org_variants_manifest.json'],{'哈萨克斯坦','哈萨克斯坦共和国'},{'kazakhstan_medalbook_variants.json','kazakhstan_medals_org_variants.json'}),
 'kyrgyzstan':(['kyrgyzstan_medals_org_variants.json','kyrgyzstan_official_variants.json'],['kyrgyzstan_medals_org_variants_manifest.json','kyrgyzstan_official_variants_manifest.json'],{'吉尔吉斯共和国'},{'kyrgyzstan_medals_org_variants.json','kyrgyzstan_official_variants.json'}),
 'tajikistan':(['tajikistan_wawards_variants.json'],['tajikistan_wawards_variants_manifest.json'],{'塔吉克斯坦共和国'},{'tajikistan_wawards_variants.json'}),
 'turkmenistan':(['turkmenistan_wawards_variants.json','turkmenistan_medalbook_differential.json'],['turkmenistan_wawards_variants_manifest.json','turkmenistan_medalbook_differential_manifest.json'],{'土库曼斯坦'},{'turkmenistan_wawards_variants.json','turkmenistan_medalbook_differential.json'}),
 'cambodia_protectorate':(['cambodia_protectorate_medalbook_variants.json'],['cambodia_protectorate_medalbook_variants_manifest.json'],{'柬埔寨保护国（1863–1948）'},{'cambodia_protectorate_medalbook_variants.json'}),
 'cambodia_kingdom':(['cambodia_kingdom_wawards_variants.json','cambodia_kingdom_medalbook_differential.json'],['cambodia_kingdom_wawards_variants_manifest.json','cambodia_kingdom_medalbook_differential_manifest.json'],{'柬埔寨王国（1948–1970；1993–）','柬埔寨王国（1948–1970）'},{'cambodia_kingdom_wawards_variants.json','cambodia_kingdom_medalbook_differential.json'}),
 'kampuchea_peoples_republic':(['kampuchea_peoples_republic_wawards_variants.json'],['kampuchea_peoples_republic_wawards_variants_manifest.json'],{'柬埔寨人民共和国（1979–1989）'},{'kampuchea_peoples_republic_wawards_variants.json'}),
 'laos_kingdom':(['laos_kingdom_medalbook_variants.json','laos_kingdom_wawards_differential.json'],['laos_kingdom_medalbook_variants_manifest.json','laos_kingdom_wawards_differential_manifest.json'],{'老挝王国（1947–1975）'},{'laos_kingdom_medalbook_variants.json','laos_kingdom_wawards_differential.json'}),
 'laos_pdr':(['laos_pdr_wawards_variants.json'],['laos_pdr_wawards_variants_manifest.json'],{'老挝人民民主共和国（1975–）'},{'laos_pdr_wawards_variants.json'}),
 'brunei':(['brunei_wawards_variants.json','brunei_medalbook_differential.json'],['brunei_wawards_variants_manifest.json','brunei_medalbook_differential_manifest.json'],{'文莱达鲁萨兰国'},{'brunei_wawards_variants.json','brunei_medalbook_differential.json'}),
 'singapore':(['singapore_medalbook_variants.json','singapore_pmo_official_variants.json'],['singapore_medalbook_variants_manifest.json','singapore_pmo_official_variants_manifest.json'],{'新加坡共和国'},{'singapore_medalbook_variants.json','singapore_pmo_official_variants.json'}),
 'malaysia_federal':(['malaysia_federal_medalbook_variants.json','malaysia_federal_istiadat_variants.json'],['malaysia_federal_medalbook_variants_manifest.json','malaysia_federal_istiadat_variants_manifest.json'],{'马来西亚联邦'},{'malaysia_federal_medalbook_variants.json','malaysia_federal_istiadat_variants.json'}),
 'sabah':(['sabah_medalbook_variants.json'],['sabah_medalbook_variants_manifest.json'],{'沙巴州'},{'sabah_medalbook_variants.json'}),
 'sarawak':(['sarawak_medalbook_variants.json'],['sarawak_medalbook_variants_manifest.json'],{'砂拉越州'},{'sarawak_medalbook_variants.json'}),
 'johor':(['johor_medalbook_variants.json'],['johor_medalbook_variants_manifest.json'],{'柔佛苏丹国'},{'johor_medalbook_variants.json'}),
 'kedah':(['kedah_medalbook_variants.json'],['kedah_medalbook_variants_manifest.json'],{'吉打苏丹国'},{'kedah_medalbook_variants.json'}),
 'kelantan':(['kelantan_medalbook_variants.json'],['kelantan_medalbook_variants_manifest.json'],{'吉兰丹苏丹国'},{'kelantan_medalbook_variants.json'}),
 'pahang':(['pahang_medalbook_variants.json'],['pahang_medalbook_variants_manifest.json'],{'彭亨苏丹国'},{'pahang_medalbook_variants.json'}),
 'perak':(['perak_medalbook_variants.json'],['perak_medalbook_variants_manifest.json'],{'霹雳苏丹国'},{'perak_medalbook_variants.json'}),
 'philippines_republic':(['philippines_medalbook_variants.json'],['philippines_medalbook_variants_manifest.json'],{'菲律宾共和国'},set()),
 'philippines_insular':(['philippines_medalbook_variants.json'],['philippines_medalbook_variants_manifest.json'],{'菲律宾群岛政府（1901–1935）'},set()),
 'myanmar_modern':(['myanmar_medalbook_variants.json'],['myanmar_medalbook_variants_manifest.json'],{'缅甸联邦与社会主义共和国（1948–1988）'},set()),
 'konbaung':(['myanmar_medalbook_variants.json'],['myanmar_medalbook_variants_manifest.json'],{'贡榜王朝（1752–1885）'},set()),
 'indonesia':(['indonesia_medalbook_variants.json','indonesia_commons_variants.json'],['indonesia_medalbook_variants_manifest.json','indonesia_commons_variants_manifest.json'],{'印度尼西亚共和国'},{'indonesia_medalbook_variants.json','indonesia_commons_variants.json'}),
 'thailand':(['thailand_medalbook_variants.json'],['thailand_medalbook_variants_manifest.json'],{'泰国'},{'thailand_medalbook_variants.json'}),
 'british_india':(['british_india_medalbook_core.json'],['british_india_medalbook_core_manifest.json'],{'东印度公司／英属印度（1837–1947）'},set()),
 'india_republic':(['india_medalbook_variants.json','india_medals_org_differential.json'],['india_medalbook_variants_manifest.json','india_medals_org_differential_manifest.json'],{'印度共和国（1950–）'},set()),
 'dominion_india':(['india_medals_org_differential.json'],['india_medals_org_differential_manifest.json'],{'印度自治领（1947–1950）'},set()),
 'azad_hind':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'自由印度临时政府（1943–1945）'},set()),
 'bahawalpur':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'巴哈瓦尔布尔土邦（1802–1955）'},set()),
 'baroda':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'巴罗达土邦'},set()),
 'bikaner':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'比卡内尔土邦'},set()),
 'gwalior':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'瓜廖尔土邦'},set()),
 'jammu_kashmir':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'查谟—克什米尔土邦'},set()),
 'patiala':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'帕蒂亚拉土邦'},set()),
 'sikh_empire':(['india_medalbook_variants.json'],['india_medalbook_variants_manifest.json'],{'锡克帝国（1799–1849）'},set()),
 'annam_protectorate':(['vietnam_medalbook_variants.json'],['vietnam_medalbook_variants_manifest.json'],{'阮朝／安南保护国（1884–1945）'},set()),
 'tai_federation':(['vietnam_medalbook_variants.json'],['vietnam_medalbook_variants_manifest.json'],{'法属印度支那 · 傣联邦'},set()),
 'democratic_vietnam':(['vietnam_medalbook_variants.json'],['vietnam_medalbook_variants_manifest.json'],{'越南民主共和国（1945–1976）'},set()),
 'state_south_vietnam':(['vietnam_medalbook_variants.json'],['vietnam_medalbook_variants_manifest.json'],{'越南国／越南共和国（1950–1975）'},set()),
 'south_vietnam':(['vietnam_medalbook_variants.json'],['vietnam_medalbook_variants_manifest.json'],{'越南共和国（1955–1975）'},set()),
 'socialist_vietnam':(['vietnam_medalbook_variants.json'],['vietnam_medalbook_variants_manifest.json'],{'越南社会主义共和国（1976–）'},set()),
 'morocco':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'摩洛哥'},set()),
 'algeria':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'阿尔及利亚'},set()),
 'azerbaijan':(['mena_round7_2026-09-26.json','azerbaijan_wawards_families.json'],['mena_round7_manifest_2026-09-26.json','azerbaijan_wawards_families_manifest.json'],{'阿塞拜疆','阿塞拜疆共和国'},{'azerbaijan_wawards_families.json'},{'MENA7-AZRBAYCAN-POLISININ-100-ILLIYI-1918-2018-YUBILEY-MEDAL-C8723327D5F7','MENA7-AZRBAYCAN-POLISININ-100-ILLIYI-19182018-YUBILEY-MEDAL-80C6066C2D09','MENA7-AZRBAYCAN-XALQ-CUMHURIYYTININ-100-ILLIYI-1918-2018-YUBILEY-MEDAL-04657779A0DD','MENA7-BAK-DOVLT-UNIVERSITETININ-100-ILLIYI-YUBILEY-MEDAL-0614B173B6F2','MENA7-CSUR-DOYUSCU-MEDAL-0189B846E786','MENA7-DOYUSD-FRQLNMY-GOR-MEDAL-6DDC9ADC47D1','MENA7-FUZULININ-AZAD-OLUNMASNA-GOR-MEDAL-F65C4F3EC31E','MENA7-HEYDR-LIYEVIN-100-ILLIYI-1923-2023-YUBILEY-MEDAL-8236E094D1CD','MENA7-HRBI-MKDASLQ-SAHSIND-XIDMTLR-GOR-MEDAL-3479D950521A','MENA7-KLBCRIN-AZAD-OLUNMASNA-GOR-MEDAL-0F7DB13AB328','MENA7-PARTICIPANT-OF-THE-PATRIOTIC-WAR-MEDAL-BCC5BFCF350B','MENA7-QARABAG-ORDENI-9A30E4525E12','MENA7-SUQOVUSANN-AZAD-OLUNMASNA-GOR-MEDAL-D7F40F85DC08','MENA7-SUSANN-AZAD-OLUNMASNA-GOR-MEDAL-031DF37CC09D','MENA7-TARAGGI-E01AF1B77D09','MENA7-VTN-MUHARIBSI-ISTIRAKCS-MEDAL-C7BF10183A23','MENA7-VTN-MUHARIBSI-QHRMAN-MEDAL-0C63129DA77C','MENA7-XOCAVNDIN-AZAD-OLUNMASNA-GOR-MEDAL-1F0B0C5920B6','MENA7-ZFR-ORDENI-CF5CB9A2BC83'}),
 'armenia':(['armenia_pack1.json','armenia_wawards_differential.json'],['armenia_pack1_manifest.json','armenia_wawards_differential_manifest.json'],{'亚美尼亚','亚美尼亚共和国'},{'armenia_pack1.json','armenia_wawards_differential.json'}),
 'georgia':(['georgia_wawards_families.json'],['georgia_wawards_families_manifest.json'],{'格鲁吉亚'},{'georgia_wawards_families.json'}),
 'ukraine':(['ukraine_wawards_families.json'],['ukraine_wawards_families_manifest.json'],{'乌克兰'},{'ukraine_wawards_families.json'}),
 'moldova':(['moldova_wawards_families.json'],['moldova_wawards_families_manifest.json'],{'摩尔多瓦共和国'},{'moldova_wawards_families.json'}),
 'estonia':(['estonia_wawards_families.json'],['estonia_wawards_families_manifest.json'],{'爱沙尼亚'},{'estonia_wawards_families.json'}),
 'belarus':(['belarus_wawards_families.json'],['belarus_wawards_families_manifest.json'],{'白俄罗斯共和国'},{'belarus_wawards_families.json'}),
 'lithuania':(['lithuania_wawards_families.json'],['lithuania_wawards_families_manifest.json'],{'立陶宛共和国'},{'lithuania_wawards_families.json'}),
 'latvia':(['latvia_wawards_families.json'],['latvia_wawards_families_manifest.json'],{'拉脱维亚共和国'},{'latvia_wawards_families.json'}),
 'czechoslovakia':(['czech_slovak_fast_2026-09-28.json'],['czech_slovak_fast_2026-09-28_manifest.json'],{'捷克斯洛伐克','捷克斯洛伐克社会主义共和国'},set()),
 'czech-republic':(['czech_slovak_fast_2026-09-28.json'],['czech_slovak_fast_2026-09-28_manifest.json'],{'捷克共和国'},set()),
 'slovakia':(['czech_slovak_fast_2026-09-28.json'],['czech_slovak_fast_2026-09-28_manifest.json'],{'斯洛伐克共和国','斯洛伐克国（历史政体）'},set()),
 'romania-kingdom':(['romania_medals_org_batch1.json'],['romania_medals_org_batch1_manifest.json'],{'罗马尼亚王国'},{'romania_medals_org_batch1.json'}),
 'bulgaria-principality':(['bulgaria_wmi_batch1_2026-09-29.json'],['bulgaria_wmi_batch1_2026-09-29_manifest.json'],{'保加利亚公国'},set()),
 'bulgaria-kingdom':(['bulgaria_wmi_batch1_2026-09-29.json'],['bulgaria_wmi_batch1_2026-09-29_manifest.json'],{'保加利亚王国'},set()),
 'bulgaria-republic':(['bulgaria_wmi_batch1_2026-09-29.json'],['bulgaria_wmi_batch1_2026-09-29_manifest.json'],{'保加利亚共和国'},set()),
 'uzbekistan':(['mena_round7_2026-09-26.json','uzbekistan_medalbook_variants.json','uzbekistan_medals_org_variants.json','uzbekistan_presidency_variants.json'],['mena_round7_manifest_2026-09-26.json','uzbekistan_medalbook_variants_manifest.json','uzbekistan_medals_org_variants_manifest.json','uzbekistan_presidency_variants_manifest.json'],{'乌兹别克斯坦'},{'uzbekistan_medalbook_variants.json','uzbekistan_medals_org_variants.json','uzbekistan_presidency_variants.json'}),
 'yemen':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'也门'},set()),
 'spain_republic':(['mena_round7_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json'],{'西班牙第二共和国'},set()),
 'spain_kingdom':(['spain_military_batch1_2026-09-26.json','spain_boe2025_campaigns_pack1.json','spain_boe2025_discontinued_pack1.json','spain_boe2025_commemorative_pack1.json','spain_boe2025_institutional_pack1.json'],['spain_military_batch1_2026-09-26_manifest.json','spain_boe2025_campaigns_pack1_manifest.json','spain_boe2025_discontinued_pack1_manifest.json','spain_boe2025_commemorative_pack1_manifest.json','spain_boe2025_institutional_pack1_manifest.json']),
 'portugal':(['portugal_medals_org_fast_2026-09-28.json'],['portugal_medals_org_fast_2026-09-28_manifest.json'],None,{'portugal_medals_org_fast_2026-09-28.json'}),
 'netherlands':(['netherlands_wmi_batch1_2026-09-29.json'],['netherlands_wmi_batch1_2026-09-29_manifest.json'],None,{'netherlands_wmi_batch1_2026-09-29.json'}),
 'belgium':(['belgium_wmi_master_fast_2026-09-29.json'],['belgium_wmi_master_fast_2026-09-29_manifest.json'],None,{'belgium_wmi_master_fast_2026-09-29.json'}),
 'luxembourg':(['luxembourg_official_book_2007.json'],['luxembourg_official_book_2007_manifest.json'],None,{'luxembourg_official_book_2007.json'}),
 'ireland':(['ireland_garda_scott_medal_2023.json','ireland_defence_forces_medals_2010.json'],['ireland_garda_scott_medal_2023_manifest.json','ireland_defence_forces_medals_2010_manifest.json'],None,{'ireland_garda_scott_medal_2023.json'}),
 'united-nations':(['ireland_defence_forces_medals_2010.json'],['ireland_defence_forces_medals_2010_manifest.json']),
 'european-communities-union':(['ireland_defence_forces_medals_2010.json'],['ireland_defence_forces_medals_2010_manifest.json']),
 'icfy':(['ireland_defence_forces_medals_2010.json'],['ireland_defence_forces_medals_2010_manifest.json']),
 'nato':(['ireland_defence_forces_medals_2010.json'],['ireland_defence_forces_medals_2010_manifest.json']),
 'interfet':(['ireland_defence_forces_medals_2010.json'],['ireland_defence_forces_medals_2010_manifest.json']),
 'savoy_italy':(['mena_round7_2026-09-26.json','italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'],['mena_round7_manifest_2026-09-26.json','italy_crown_pack1_manifest.json','italy_medalbook_pack2_2026-09-26_manifest.json','italy_medalbook_pack3_2026-09-26_manifest.json','italy_medalbook_pack4_2026-09-26_manifest.json','italy_medalbook_pack5_2026-09-26_manifest.json'],{'意大利／萨佛依王朝'},{'italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'}),
 'habsburg-monarchy':(['austria_habsburg_medalsorg_fast_2026-09-28.json'],['austria_habsburg_medalsorg_fast_2026-09-28_manifest.json'],None,{'austria_habsburg_medalsorg_fast_2026-09-28.json'}),
 'austrian-empire':(['austria_empire_medalsorg_fast_2026-09-28.json'],['austria_empire_medalsorg_fast_2026-09-28_manifest.json'],None,{'austria_empire_medalsorg_fast_2026-09-28.json'}),
 'austro-hungary':(['austro_hungary_medalsorg_fast_2026-09-28.json'],['austro_hungary_medalsorg_fast_2026-09-28_manifest.json'],None,{'austro_hungary_medalsorg_fast_2026-09-28.json'}),
 'austria-republic':(['austria_republic_medalsorg_fast_2026-09-28.json'],['austria_republic_medalsorg_fast_2026-09-28_manifest.json'],None,{'austria_republic_medalsorg_fast_2026-09-28.json'}),
 'hungary':(['hungary_wmi_master_fast_2026-09-29.json'],['hungary_wmi_master_fast_2026-09-29_manifest.json'],None,set()),
 'finland':(['finland_orders_pack1.json'],['finland_orders_pack1_manifest.json']),
 'sweden':(['sweden_orders_pack1.json'],['sweden_orders_pack1_manifest.json']),
 'denmark':(['denmark_master_fast_2026-09-29.json'],['denmark_master_fast_2026-09-29_manifest.json'],None,{'denmark_master_fast_2026-09-29.json'}),
 'iceland':(['iceland_official_honours_2026-09-29.json'],['iceland_official_honours_2026-09-29_manifest.json'],None,{'iceland_official_honours_2026-09-29.json'}),
 'norway':(['norway_orders_pack1.json'],['norway_orders_pack1_manifest.json']),
 'poland':(['poland_wikipedia_master_pictured_2026-09-28.json'],['poland_wikipedia_master_pictured_2026-09-28_manifest.json'],{'波兰'},{'poland_wikipedia_master_pictured_2026-09-28.json'}),
 'uk':(['uk_mod_pack1.json','uk_us_gap_round2_2026-09-26.json'],['uk_mod_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json'],{'英国／大英帝国'},{'uk_mod_pack1.json'}),
 'united_states':(['us_nhhc_pack1.json','uk_us_gap_round2_2026-09-26.json'],['us_nhhc_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json'],{'美国'},{'us_nhhc_pack1.json'}),
 'russian_empire':(['russian_empire_pack1.json','russian_empire_gap_2026-09-26.json'],['russian_empire_pack1_manifest.json','russian_empire_gap_2026-09-26_manifest.json']),
 'soviet_union':(['soviet_union_pack1.json','russia_bulk_pack2.json','russia_bulk_pack3.json','soviet_gap_round4_2026-09-26.json','soviet_wikipedia_master_differential_2026-09-28.json','soviet_wikipedia_master_followup_2026-09-28.json'],['soviet_union_pack1_manifest.json','russia_bulk_pack2_manifest.json','russia_bulk_pack3_manifest.json','soviet_gap_round4_2026-09-26_manifest.json','soviet_wikipedia_master_differential_2026-09-28_manifest.json','soviet_wikipedia_master_followup_2026-09-28_manifest.json'],None,set(),{'USSR-MED-08-V-II-WIKI','USSR-MED-10-V-II-WIKI','USSR-MED-54-V-II-WIKI'}),
 'russian_federation':(['russian_federation_pack1.json'],['russian_federation_pack1_manifest.json']),
 'qing_empire':(['qing_medalbook_variants.json'],['qing_medalbook_variants_manifest.json'],{'大清帝国（1644–1912）'},set()),
 'peoples_republic_china':(['peoples_republic_china_medals_org.json'],['peoples_republic_china_medals_org_manifest.json'],{'中华人民共和国'},set()),
 'republic_of_china':(['east_asia_gap_round1_2026-09-26.json','republic_of_china_medalbook_variants.json'],['east_asia_gap_round1_2026-09-26_manifest.json','republic_of_china_medalbook_variants_manifest.json'],{'中华民国'},{'republic_of_china_medalbook_variants.json'}),
 'hong_kong':(['hong_kong_wawards_families.json'],['hong_kong_wawards_families_manifest.json'],{'香港特别行政区'},{'hong_kong_wawards_families.json'}),
 'cyprus':(['cyprus_wawards_families.json'],['cyprus_wawards_families_manifest.json'],{'塞浦路斯共和国'},{'cyprus_wawards_families.json'}),
 'greece':(['greece_medals_org_fast_2026-09-28.json'],['greece_medals_org_fast_2026-09-28_manifest.json'],None,{'greece_medals_org_fast_2026-09-28.json'}),
 'maldives':(['maldives_wawards_families.json'],['maldives_wawards_families_manifest.json'],{'马尔代夫共和国'},{'maldives_wawards_families.json'}),
 'korean_empire':(['east_asia_gap_round1_2026-09-26.json','korean_empire_medalbook_variants.json'],['east_asia_gap_round1_2026-09-26_manifest.json','korean_empire_medalbook_variants_manifest.json'],{'大韩帝国'},{'korean_empire_medalbook_variants.json'}),
 'south_korea':(['east_asia_gap_round1_2026-09-26.json','south_korea_official_complete_2026-09-27.json','south_korea_medalbook_differential.json'],['east_asia_gap_round1_2026-09-26_manifest.json','south_korea_official_complete_2026-09-27_manifest.json','south_korea_medalbook_differential_manifest.json'],{'韩国'},{'south_korea_medalbook_differential.json'}),
 'north_korea':(['east_asia_gap_round1_2026-09-26.json','north_korea_medalbook_variants.json','north_korea_medals_org_variants.json','north_korea_commons_cached_variants.json'],['east_asia_gap_round1_2026-09-26_manifest.json','north_korea_medalbook_variants_manifest.json','north_korea_medals_org_variants_manifest.json','north_korea_commons_cached_variants_manifest.json'],{'朝鲜'},{'north_korea_medalbook_variants.json','north_korea_medals_org_variants.json','north_korea_commons_cached_variants.json'}),
 'manchukuo':(['manchukuo_medalbook_variants.json'],['manchukuo_medalbook_variants_manifest.json'],{'满洲国（1932–1945）'},set()),
 'mongolian_peoples_republic':(['mongolia_medals_org_variants.json'],['mongolia_medals_org_variants_manifest.json'],{'蒙古人民共和国'},set()),
 'mongolia':(['mongolia_medals_org_variants.json'],['mongolia_medals_org_variants_manifest.json'],{'蒙古国（1992–）'},set()),
 'japan_meiji':(['japan_meiji.json','japan_meiji_round2.json','japan_meiji_round3.json','japan_meiji_pack4_new.json','japan_medalbook_variants.json'],['japan_meiji_manifest.json','japan_meiji_round2_manifest.json','japan_meiji_round3_manifest.json','japan_meiji_pack4_new_manifest.json','japan_medalbook_variants_manifest.json'],{'日本 · 明治时期'},{'japan_meiji.json','japan_meiji_round2.json','japan_meiji_round3.json','japan_meiji_pack4_new.json'}),
 'japan_taisho':(['japan_taisho_pack1.json','japan_taisho_pack4_new.json','japan_medalbook_variants.json'],['japan_taisho_pack1_manifest.json','japan_taisho_pack4_new_manifest.json','japan_medalbook_variants_manifest.json'],{'日本 · 大正时期'},{'japan_taisho_pack1.json','japan_taisho_pack4_new.json'}),
 'japan_showa':(['japan_medalbook_variants.json'],['japan_medalbook_variants_manifest.json'],{'日本 · 昭和时期'},set()),
 'japan_modern':(['japan_medalbook_variants.json'],['japan_medalbook_variants_manifest.json'],{'日本 · 现代'},set()),
 'japan_official':(['japan_cabinet_official_bulk_2026-09-28.json'],['japan_cabinet_official_bulk_2026-09-28_manifest.json'],{'日本'},{'japan_cabinet_official_bulk_2026-09-28.json'}),
 'france_first_empire':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_bourbon':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_july':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_second_republic':(['france_legion_evolution_pack1.json'],['france_legion_evolution_pack1_manifest.json']),
 'france_fourth_fifth':(['france_legion_evolution_pack1.json','france_legion_official_batch2.json','france_official_core_2026-09-29.json'],['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json','france_official_core_2026-09-29_manifest.json']),
 'germany_1933_1945':(['germany_1933_1945_gap_round1_2026-09-26.json'],['germany_1933_1945_gap_round1_2026-09-26_manifest.json']),
 'prussia_kingdom':(['prussia_kingdom.json','prussia_batch1_2026-09-26.json','prussia_batch2_2026-09-26.json'],['prussia_kingdom_manifest.json','prussia_batch1_manifest_2026-09-26.json','prussia_batch2_manifest_2026-09-26.json']),
 'france_third_republic':(['france_third_republic.json','france_third_republic_pack1.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json','france_legion_official_batch2.json'],['france_third_republic_manifest.json','france_third_republic_pack1_manifest.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json']),
 'france_second_empire':(['france_second_empire_pack1_2026-09-26.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json'],['france_second_empire_pack1_manifest_2026-09-26.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json']),
 'bavaria_kingdom':(['bavaria_kingdom_pack1.json','bavaria_kingdom_pack2.json'],['bavaria_kingdom_pack1_manifest.json','bavaria_kingdom_pack2_manifest.json']),
}
include_ids={
 'hungary':{'HUN-WMI-001','HUN-WMI-002','HUN-WMI-011','HUN-WMI-012','HUN-WMI-014','HUN-WMI-020'},
 'france_first_empire':{'FRA-LEGION-EVOLUTION-FIRST-EMPIRE-MODEL-GROUP'},
 'france_bourbon':{'FRA-LEGION-EVOLUTION-BOURBON-RESTORATION-MODEL-GROUP','FRA-LEGION-RESTORATION-OFFICER-DUDEVANT','FRA-LEGION-RESTORATION-CHEVALIER-HUGO-REDUCTION'},
 'france_july':{'FRA-LEGION-EVOLUTION-JULY-MONARCHY-MODEL-GROUP','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-1837','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-REDUCTION'},
 'france_second_republic':{'FRA-LEGION-EVOLUTION-SECOND-REPUBLIC-MODEL-GROUP'},
 'france_fourth_fifth':{'FRA-LEGION-EVOLUTION-FOURTH-FIFTH-REPUBLICS-MODEL-GROUP','FRA-LEGION-1945-GRAND-OFFICER-LECLERC-PLAQUE','FRA-LEGION-POST-1951-COMMANDER-NOHAIN','FRA-LEGION-FIFTH-REPUBLIC-OFFICER-FOUQUER-1971','FRA-LEGION-HONOUR-CURRENT-CHEVALIER-OFFICIAL','FRA-MEDAILLE-MILITAIRE-CURRENT-OFFICIAL','FRA-ORDRE-NATIONAL-MERITE-CURRENT-CHEVALIER-OFFICIAL','FRA-MEDAILLE-VICTIMES-TERRORISME-CURRENT-OFFICIAL'},
 'france_second_empire':{'FRA-SE-ITALY-1859-PRESENTATION-01','FRA-SE-MEXICO-1863-01','FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01','FRA-LEGION-EVOLUTION-SECOND-EMPIRE-MODEL-GROUP'},
}
awarding_authorities={
 'ireland':{'爱尔兰','爱尔兰国防军','爱尔兰国防军及爱尔兰国家应急服务机构'},
 'united-nations':{'联合国'},
 'european-communities-union':{'欧洲共同体','欧洲联盟'},
 'icfy':{'前南斯拉夫问题国际会议'},
 'nato':{'北大西洋公约组织'},
 'interfet':{'东帝汶国际部队'},
}
for slug,spec in volume_files.items():
    record_names,manifest_names=spec[:2]
    countries=spec[2] if len(spec)>2 else None
    unfiltered=spec[3] if len(spec)>3 else set()
    excluded=spec[4] if len(spec)>4 else set()
    record_paths=[ROOT/'data/volumes'/name for name in record_names if (ROOT/'data/volumes'/name).is_file()]
    manifest_paths=[ROOT/'data/volumes'/name for name in manifest_names if (ROOT/'data/volumes'/name).is_file()]
    if not record_paths or not manifest_paths:continue
    records=[]
    for path in record_paths:
        loaded=json.loads(path.read_text(encoding='utf-8'))['records']
        if countries and path.name not in unfiltered:
            loaded=[r for r in loaded if r.get('country_zh') in countries]
        if slug in awarding_authorities and path.name not in unfiltered:
            loaded=[r for r in loaded if r.get('awarding_authority') in awarding_authorities[slug]]
        if slug=='france_third_republic' and path.name=='france_legion_evolution_pack1.json':
            loaded=[r for r in loaded if r['id']=='FRA-LEGION-EVOLUTION-THIRD-REPUBLIC-MODEL-GROUP']
        if slug=='france_third_republic' and path.name=='france_legion_official_batch2.json':
            loaded=[r for r in loaded if r['id']=='FRA-LEGION-THIRD-REPUBLIC-CHEVALIER-RENDU']
        records.extend(loaded)
    records=[r for r in records if r['id'] not in excluded]
    if slug in include_ids:
        records=[r for r in records if r['id'] in include_ids[slug]]
    if slug=='france_third_republic':
        records=[r for r in records if r['id']!='FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01']
    if slug=='savoy_italy':
        records=[r for r in records if r['id']!='IT-KOI-058-V51']
    if slug=='germany_1933_1945':
        records=[r for r in records if r['id']!='GER-1933-1945-GERMAN-OLYMPIC-CROSS-V1']
    if slug=='egypt':
        records=[r for r in records if r['id']!='MENA7-KHEDIVE-S-STAR-62A559F82C88']
    superseded={r['supersedes_id'] for r in records if r.get('supersedes_id')}
    records=[r for r in records if r['id'] not in superseded]
    manifests=[json.loads(path.read_text(encoding='utf-8')) for path in manifest_paths]
    mapping={item['view_key']:item['local_path'] for data in manifests for item in data.get('images',[])}
    for record in records:
        if not record.get('views'):continue
        for view in record['views']:
            key=view['key']
            assert key in mapping,(slug,key)
            assert key not in all_view_paths,key
            all_view_paths[key]=mapping[key]
            asset_countries[mapping[key]].add(next(iter(countries)) if countries else slug)
        volume_records.append(record)
base_manifest={x['key']:x for x in json.loads((ROOT/'image_manifest.json').read_text(encoding='utf-8'))}
for record in catalogue:
    for view in record['views']:
        path='assets/images/ottoman/'+Path(base_manifest[view['key']]['path']).name
        asset_countries[path].add('奥斯曼帝国')
related_volume_specs=[
    ('ottoman_kuenker299_related.json','ottoman_kuenker299_related_manifest.json'),
    ('ottoman_cng_triple_alliance_related.json','ottoman_cng_triple_alliance_related_manifest.json'),
    ('ottoman_cgb_related.json','ottoman_cgb_related_manifest.json'),
    ('ottoman_milli_saraylar_related.json','ottoman_milli_saraylar_related_manifest.json'),
]
for related_name,related_manifest_name in related_volume_specs:
    related_volume_path=ROOT/'data/volumes'/related_name
    related_manifest_path=ROOT/'data/volumes'/related_manifest_name
    if not related_volume_path.is_file() or not related_manifest_path.is_file():continue
    related_extra=json.loads(related_volume_path.read_text(encoding='utf-8'))['records']
    related_meta=json.loads(related_manifest_path.read_text(encoding='utf-8'))
    related_mapping={item['view_key']:item['local_path'] for item in related_meta.get('images',[])}
    for record in related_extra:
        for view in record.get('views',[]):
            key=view['key']
            assert key in related_mapping,(record['id'],key)
            assert key not in all_view_paths,key
            all_view_paths[key]=related_mapping[key]
            asset_countries[related_mapping[key]].add('奥斯曼帝国')
    related.extend(related_extra)
cross_country_paths={path:sorted(countries) for path,countries in asset_countries.items() if len(countries)>1}
assert not cross_country_paths,cross_country_paths
hash_countries=defaultdict(set)
for path,countries in asset_countries.items():
    digest=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    hash_countries[digest].update(countries)
cross_country_hashes={digest:sorted(countries) for digest,countries in hash_countries.items() if len(countries)>1}
assert not cross_country_hashes,cross_country_hashes
expected_images=sum(len(x['views']) for x in catalogue+related+volume_records)
assert len(gallery_images)==expected_images,(len(gallery_images),expected_images)
assert all(url.startswith('assets/images/') and '..' not in url for url in gallery_images)
assert all(path in gallery_images for path in all_view_paths.values())
assert not re.search(r'<img[^>]+src=["\']https?://',html,re.I)
assert 'fetch(' not in html and 'type="module"' not in html
assert 'object-fit:contain' in css and 'object-fit:cover' not in css
for url in gallery_images+p.scripts+p.styles:
    f=ROOT/url
    assert f.is_file(),url
    if url in gallery_images:
        with Image.open(f) as img:img.verify()
assert all(h[1:] in p.ids for h in p.links if h.startswith('#')),[h for h in p.links if h.startswith('#') and h[1:] not in p.ids]
migration=json.loads((ROOT/'data/migration_log.json').read_text(encoding='utf-8'))['items']
assert len(migration)==28 and len({x['legacy_key'] for x in migration})==28
assert len(catalogue)>=27 and len({x['family'] for x in catalogue})>=20
assert all(x['id'] in p.ids for x in catalogue+related)
assert all(x['id'] in p.ids for x in volume_records)
assert len({x['id'] for x in catalogue+related+volume_records})==len(catalogue+related+volume_records)
assert len({x['family'] for x in catalogue+volume_records})<=len(catalogue+volume_records)
assert all(x['disposition'] in ('main_gallery','related_gallery','merged','unpictured_appendix') for x in migration)
assert len([x for x in migration if x['disposition']=='unpictured_appendix'])==0
assert 'Prussia' in html and 'Bavaria' in html and '奥斯曼帝国' in html
assert all(label not in html for label in ('第一轮整理中','开放图源补充卷','中东与穆斯林国家'))
assert 'france-legion-history' not in html
assert all(bad_id not in html for bad_id in (
    'MENA7-KING-FOUAD-MILITARY-STAR',
    'MENA7-ARMED-FORCES-CAMPAIGN',
    'MENA7-ARMED-FORCES-ENDURANCE',
))
assert all(anchor in p.ids for anchor in ('ottoman','egypt','sudan','iran','turkey','azerbaijan','armenia'))
assert p.family_buttons and len({key for key,_ in p.family_buttons})==len(p.family_buttons)
family_row_counts=defaultdict(int)
for key,hidden in p.family_rows:
    family_row_counts[key]+=1
    assert hidden,key
assert all(expanded=='false' and family_row_counts[key]>=2 for key,expanded in p.family_buttons)
assert set(family_row_counts)=={key for key,_ in p.family_buttons}
all_records=catalogue+volume_records
print(f'PASS: {len(all_records)} official rows, {len({x["family"] for x in all_records})} families, {len(gallery_images)} decoded local images, 28 migration decisions; all links and local resources exist')
