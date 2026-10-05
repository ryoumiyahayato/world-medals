"""Regenerate the existing offline index.html from local records and images."""
import json,re
from collections import defaultdict
from html import escape
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
read=lambda name:json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
catalogue=read('catalogue.json')['records']
related=read('related.json')
unpictured=read('unpictured.json')
queue=read('global_queue.json')
manifest={x['key']:x for x in json.loads((ROOT/'image_manifest.json').read_text(encoding='utf-8'))}
volume_specs=[
 {'slug':'iraq_kingdom','title':'伊拉克王国','anchor':'iraq-kingdom','aliases':'伊拉克 Iraq Kingdom Police نوط الشرطة','country_group':'iraq',
  'record_files':['minimum_coverage_iraq_20260929.json'],'manifest_files':['minimum_coverage_iraq_20260929_manifest.json']},
 {'slug':'canada','title':'加拿大','anchor':'canada','aliases':'加拿大 Canada Order of Canada',
  'record_files':['minimum_coverage_root_20260929.json'],'manifest_files':['minimum_coverage_root_20260929_manifest.json'],'countries':['加拿大']},
 {'slug':'new_zealand','title':'新西兰','anchor':'new-zealand','aliases':'新西兰 New Zealand Aotearoa Order of Merit',
  'record_files':['minimum_coverage_root_20260929.json'],'manifest_files':['minimum_coverage_root_20260929_manifest.json'],'countries':['新西兰']},
 {'slug':'ottoman_extra','title':'奥斯曼帝国','anchor':'ottoman-extra-internal','aliases':'奥斯曼 Ottoman Empire Osmanlı',
  'record_files':['ottoman_commons_batch1.json','mena_round7_2026-09-26.json','ottoman_medalbook_pack2.json','ottoman_kuenker299_batch2.json','ottoman_kuenker299_batch3.json','ottoman_kuenker299_batch4.json','ottoman_kuenker299_batch5.json','ottoman_kuenker299_batch6.json','ottoman_itu_tayyare.json','ottoman_itu_ferahi.json','ottoman_sinop_mdc.json','ottoman_tasvir_humayun.json','ottoman_nam_danube.json','ottoman_spink21001.json','ottoman_spink_variants.json','ottoman_spink_archive_variants.json','ottoman_cgb_current.json'],
  'manifest_files':['ottoman_commons_batch1_manifest.json','mena_round7_manifest_2026-09-26.json','ottoman_medalbook_pack2_manifest.json','ottoman_kuenker299_batch2_manifest.json','ottoman_kuenker299_batch3_manifest.json','ottoman_kuenker299_batch4_manifest.json','ottoman_kuenker299_batch5_manifest.json','ottoman_kuenker299_batch6_manifest.json','ottoman_itu_tayyare_manifest.json','ottoman_itu_ferahi_manifest.json','ottoman_sinop_mdc_manifest.json','ottoman_tasvir_humayun_manifest.json','ottoman_nam_danube_manifest.json','ottoman_spink21001_manifest.json','ottoman_spink_variants_manifest.json','ottoman_spink_archive_variants_manifest.json','ottoman_cgb_current_manifest.json'],
  'countries':['奥斯曼帝国'],'unfiltered_record_files':['ottoman_commons_batch1.json','ottoman_medalbook_pack2.json','ottoman_kuenker299_batch2.json','ottoman_kuenker299_batch3.json','ottoman_kuenker299_batch4.json','ottoman_kuenker299_batch5.json','ottoman_kuenker299_batch6.json','ottoman_itu_tayyare.json','ottoman_itu_ferahi.json','ottoman_sinop_mdc.json','ottoman_tasvir_humayun.json','ottoman_nam_danube.json','ottoman_spink21001.json','ottoman_spink_variants.json','ottoman_spink_archive_variants.json','ottoman_cgb_current.json']},
 {'slug':'egypt','title':'埃及','anchor':'egypt','aliases':'埃及 Egypt مصر Khedivate Republic',
  'record_files':['egypt_republic_pack1.json','mena_round7_2026-09-26.json','mena_gap_round1_2026-09-26.json','egypt_commons_verified.json','egypt_wawards_pack1.json','egypt_wawards_major_variants.json','egypt_wawards_medal_variants.json','egypt_omsa_unpictured_pack1.json','egypt_medals_org_variants.json','egypt_medals_org_republic_variants.json','egypt_emedals_variants.json','egypt_khedive_star_reconciled.json','egypt_spink26001.json','egypt_medalbook_variants.json'],
  'manifest_files':['egypt_republic_pack1_manifest.json','mena_round7_manifest_2026-09-26.json','mena_gap_round1_manifest_2026-09-26.json','egypt_commons_verified_manifest.json','egypt_wawards_pack1_manifest.json','egypt_wawards_major_variants_manifest.json','egypt_wawards_medal_variants_manifest.json','egypt_omsa_unpictured_pack1_manifest.json','egypt_medals_org_variants_manifest.json','egypt_medals_org_republic_variants_manifest.json','egypt_emedals_variants_manifest.json','egypt_khedive_star_reconciled_manifest.json','egypt_spink26001_manifest.json','egypt_medalbook_variants_manifest.json'],
  'countries':['埃及'],'unfiltered_record_files':['egypt_republic_pack1.json','egypt_commons_verified.json','egypt_wawards_pack1.json','egypt_wawards_major_variants.json','egypt_wawards_medal_variants.json','egypt_omsa_unpictured_pack1.json','egypt_medals_org_variants.json','egypt_medals_org_republic_variants.json','egypt_emedals_variants.json','egypt_khedive_star_reconciled.json','egypt_spink26001.json','egypt_medalbook_variants.json'],
  'exclude_ids':['MENA7-KHEDIVE-S-STAR-62A559F82C88']},
 {'slug':'sudan','title':'苏丹','anchor':'sudan','aliases':'苏丹 Sudan Anglo-Egyptian Sudan',
  'record_files':['mena_round7_2026-09-26.json','sudan_wawards_pack1.json','sudan_medalbook_unpictured_pack1.json','sudan_commons_variants.json','sudan_presidency_official_variants.json','sudan_presidency_alt_official_variants.json','sudan_spink21001.json','sudan_noonans_variants.json','sudan_emedals_variants.json','sudan_noble_variants.json','sudan_spink_archive_variants.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json','sudan_wawards_pack1_manifest.json','sudan_medalbook_unpictured_pack1_manifest.json','sudan_commons_variants_manifest.json','sudan_presidency_official_variants_manifest.json','sudan_presidency_alt_official_variants_manifest.json','sudan_spink21001_manifest.json','sudan_noonans_variants_manifest.json','sudan_emedals_variants_manifest.json','sudan_noble_variants_manifest.json','sudan_spink_archive_variants_manifest.json'],'countries':['苏丹'],'unfiltered_record_files':['sudan_wawards_pack1.json','sudan_medalbook_unpictured_pack1.json','sudan_commons_variants.json','sudan_presidency_official_variants.json','sudan_presidency_alt_official_variants.json','sudan_spink21001.json','sudan_noonans_variants.json','sudan_emedals_variants.json','sudan_noble_variants.json','sudan_spink_archive_variants.json']},
 {'slug':'iran','title':'波斯／伊朗','anchor':'iran','aliases':'波斯 伊朗 Persia Iran Qajar Pahlavi',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['伊朗／波斯']},
 {'slug':'turkey','title':'土耳其共和国','anchor':'turkey','aliases':'土耳其 Turkey Türkiye Republic',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['土耳其共和国']},
 {'slug':'syria','title':'叙利亚','anchor':'syria','aliases':'叙利亚 Syria',
  'record_files':['mena_round7_2026-09-26.json','syria_wawards_families.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json','syria_wawards_families_manifest.json'],'countries':['叙利亚','叙利亚共和国'],'unfiltered_record_files':['syria_wawards_families.json']},
 {'slug':'oman','title':'阿曼','anchor':'oman','aliases':'阿曼 Oman',
  'record_files':['mena_round7_2026-09-26.json','oman_wawards_families.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json','oman_wawards_families_manifest.json'],'countries':['阿曼','阿曼苏丹国'],'unfiltered_record_files':['oman_wawards_families.json']},
 {'slug':'jordan','title':'约旦哈希姆王国','anchor':'jordan','aliases':'约旦 Jordan Hashemite Kingdom الأردنية',
  'record_files':['jordan_wawards_families.json'],'manifest_files':['jordan_wawards_families_manifest.json'],'countries':['约旦哈希姆王国'],'unfiltered_record_files':['jordan_wawards_families.json']},
 {'slug':'saudi-arabia','title':'沙特阿拉伯','anchor':'saudi-arabia','aliases':'沙特 沙特阿拉伯 Saudi Arabia المملكة العربية السعودية',
  'record_files':['saudi_arabia_wawards_families.json'],'manifest_files':['saudi_arabia_wawards_families_manifest.json'],'countries':['沙特阿拉伯王国'],'unfiltered_record_files':['saudi_arabia_wawards_families.json']},
 {'slug':'qatar','title':'卡塔尔','anchor':'qatar','aliases':'卡塔尔 Qatar دولة قطر',
  'record_files':['qatar_wawards_families.json'],'manifest_files':['qatar_wawards_families_manifest.json'],'countries':['卡塔尔国'],'unfiltered_record_files':['qatar_wawards_families.json']},
 {'slug':'kuwait','title':'科威特','anchor':'kuwait','aliases':'科威特 Kuwait دولة الكويت',
  'record_files':['kuwait_wawards_families.json'],'manifest_files':['kuwait_wawards_families_manifest.json'],'countries':['科威特国'],'unfiltered_record_files':['kuwait_wawards_families.json']},
 {'slug':'bahrain','title':'巴林','anchor':'bahrain','aliases':'巴林 Bahrain مملكة البحرين',
  'record_files':['bahrain_wawards_families.json'],'manifest_files':['bahrain_wawards_families_manifest.json'],'countries':['巴林王国'],'unfiltered_record_files':['bahrain_wawards_families.json']},
 {'slug':'united-arab-emirates','title':'阿拉伯联合酋长国','anchor':'united-arab-emirates','aliases':'阿联酋 阿拉伯联合酋长国 United Arab Emirates UAE الإمارات',
  'record_files':['united_arab_emirates_wawards_families.json'],'manifest_files':['united_arab_emirates_wawards_families_manifest.json'],'countries':['阿拉伯联合酋长国'],'unfiltered_record_files':['united_arab_emirates_wawards_families.json']},
 {'slug':'lebanon','title':'黎巴嫩','anchor':'lebanon','aliases':'黎巴嫩 Lebanon الجمهورية اللبنانية',
  'record_files':['lebanon_wawards_families.json'],'manifest_files':['lebanon_wawards_families_manifest.json'],'countries':['黎巴嫩共和国'],'unfiltered_record_files':['lebanon_wawards_families.json']},
 {'slug':'israel','title':'以色列','anchor':'israel','aliases':'以色列 Israel ישראל',
  'record_files':['israel_wawards_families.json'],'manifest_files':['israel_wawards_families_manifest.json'],'countries':['以色列国'],'unfiltered_record_files':['israel_wawards_families.json']},
 {'slug':'afghanistan','title':'阿富汗','anchor':'afghanistan','aliases':'阿富汗 Afghanistan',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['阿富汗']},
 {'slug':'pakistan','title':'巴基斯坦','anchor':'pakistan','aliases':'巴基斯坦 Pakistan',
  'record_files':['mena_round7_2026-09-26.json','pakistan_medalbook_variants.json','pakistan_medals_org_variants.json'],
  'manifest_files':['mena_round7_manifest_2026-09-26.json','pakistan_medalbook_variants_manifest.json','pakistan_medals_org_variants_manifest.json'],
  'countries':['巴基斯坦'],'unfiltered_record_files':['pakistan_medalbook_variants.json','pakistan_medals_org_variants.json']},
 {'slug':'nepal','title':'尼泊尔王国／尼泊尔','anchor':'nepal','aliases':'尼泊尔 Nepal Kingdom of Nepal Gorkha Gurkha',
  'record_files':['nepal_medalbook_variants.json','nepal_medals_org_variants.json'],
  'manifest_files':['nepal_medalbook_variants_manifest.json','nepal_medals_org_variants_manifest.json'],
  'countries':['尼泊尔王国／尼泊尔'],'unfiltered_record_files':['nepal_medalbook_variants.json','nepal_medals_org_variants.json']},
 {'slug':'bhutan','title':'不丹王国','anchor':'bhutan','aliases':'不丹 Bhutan Kingdom of Bhutan Druk',
  'record_files':['bhutan_medalbook_variants.json','bhutan_medals_org_variants.json'],
  'manifest_files':['bhutan_medalbook_variants_manifest.json','bhutan_medals_org_variants_manifest.json'],
  'countries':['不丹王国'],'unfiltered_record_files':['bhutan_medalbook_variants.json','bhutan_medals_org_variants.json']},
 {'slug':'bangladesh','title':'孟加拉国','anchor':'bangladesh','aliases':'孟加拉国 Bangladesh People Republic of Bangladesh',
  'record_files':['bangladesh_medalbook_variants.json','bangladesh_medals_org_variants.json'],
  'manifest_files':['bangladesh_medalbook_variants_manifest.json','bangladesh_medals_org_variants_manifest.json'],
  'countries':['孟加拉国'],'unfiltered_record_files':['bangladesh_medalbook_variants.json','bangladesh_medals_org_variants.json']},
 {'slug':'sri-lanka','title':'锡兰／斯里兰卡','anchor':'sri-lanka','aliases':'锡兰 斯里兰卡 Ceylon Sri Lanka',
  'record_files':['sri_lanka_medalbook_variants.json','sri_lanka_medals_org_variants.json'],
  'manifest_files':['sri_lanka_medalbook_variants_manifest.json','sri_lanka_medals_org_variants_manifest.json'],
  'countries':['锡兰','斯里兰卡民主社会主义共和国'],'unfiltered_record_files':['sri_lanka_medalbook_variants.json','sri_lanka_medals_org_variants.json']},
 {'slug':'kazakhstan','title':'哈萨克斯坦共和国','anchor':'kazakhstan','aliases':'哈萨克斯坦 Kazakhstan Qazaqstan Republic of Kazakhstan',
  'record_files':['mena_round7_2026-09-26.json','kazakhstan_medalbook_variants.json','kazakhstan_medals_org_variants.json'],
  'manifest_files':['mena_round7_manifest_2026-09-26.json','kazakhstan_medalbook_variants_manifest.json','kazakhstan_medals_org_variants_manifest.json'],
  'countries':['哈萨克斯坦','哈萨克斯坦共和国'],'unfiltered_record_files':['kazakhstan_medalbook_variants.json','kazakhstan_medals_org_variants.json']},
 {'slug':'kyrgyzstan','title':'吉尔吉斯共和国','anchor':'kyrgyzstan','aliases':'吉尔吉斯斯坦 吉尔吉斯共和国 Kyrgyzstan Kyrgyz Republic',
  'record_files':['kyrgyzstan_medals_org_variants.json','kyrgyzstan_official_variants.json'],
  'manifest_files':['kyrgyzstan_medals_org_variants_manifest.json','kyrgyzstan_official_variants_manifest.json'],
  'countries':['吉尔吉斯共和国'],'unfiltered_record_files':['kyrgyzstan_medals_org_variants.json','kyrgyzstan_official_variants.json']},
 {'slug':'tajikistan','title':'塔吉克斯坦共和国','anchor':'tajikistan','aliases':'塔吉克斯坦 塔吉克斯坦共和国 Tajikistan Republic of Tajikistan Тоҷикистон',
  'record_files':['tajikistan_wawards_variants.json'],
  'manifest_files':['tajikistan_wawards_variants_manifest.json'],
  'countries':['塔吉克斯坦共和国'],'unfiltered_record_files':['tajikistan_wawards_variants.json']},
 {'slug':'turkmenistan','title':'土库曼斯坦','anchor':'turkmenistan','aliases':'土库曼斯坦 Turkmenistan Türkmenistan',
  'record_files':['turkmenistan_wawards_variants.json','turkmenistan_medalbook_differential.json'],
  'manifest_files':['turkmenistan_wawards_variants_manifest.json','turkmenistan_medalbook_differential_manifest.json'],
  'countries':['土库曼斯坦'],'unfiltered_record_files':['turkmenistan_wawards_variants.json','turkmenistan_medalbook_differential.json']},
 {'slug':'cambodia_protectorate','title':'柬埔寨保护国（1863–1948）','anchor':'cambodia-protectorate','aliases':'柬埔寨保护国 French Protectorate Cambodia Protectorat français du Cambodge',
  'record_files':['cambodia_protectorate_medalbook_variants.json'],
  'manifest_files':['cambodia_protectorate_medalbook_variants_manifest.json'],
  'countries':['柬埔寨保护国（1863–1948）'],'unfiltered_record_files':['cambodia_protectorate_medalbook_variants.json'],'country_group':'cambodia'},
 {'slug':'cambodia_kingdom','title':'柬埔寨王国（1948–1970；1993–）','anchor':'cambodia-kingdom','aliases':'柬埔寨 柬埔寨王国 Cambodia Kingdom of Cambodia Kampuchea Khmer',
  'record_files':['cambodia_kingdom_wawards_variants.json','cambodia_kingdom_medalbook_differential.json'],
  'manifest_files':['cambodia_kingdom_wawards_variants_manifest.json','cambodia_kingdom_medalbook_differential_manifest.json'],
  'countries':['柬埔寨王国（1948–1970；1993–）','柬埔寨王国（1948–1970）'],'unfiltered_record_files':['cambodia_kingdom_wawards_variants.json','cambodia_kingdom_medalbook_differential.json'],'country_group':'cambodia'},
 {'slug':'kampuchea_peoples_republic','title':'柬埔寨人民共和国（1979–1989）','anchor':'kampuchea-peoples-republic','aliases':'柬埔寨人民共和国 People’s Republic of Kampuchea Peoples Republic Kampuchea PRK',
  'record_files':['kampuchea_peoples_republic_wawards_variants.json'],
  'manifest_files':['kampuchea_peoples_republic_wawards_variants_manifest.json'],
  'countries':['柬埔寨人民共和国（1979–1989）'],'unfiltered_record_files':['kampuchea_peoples_republic_wawards_variants.json'],'country_group':'cambodia'},
 {'slug':'laos_kingdom','title':'老挝王国（1947–1975）','anchor':'laos-kingdom','aliases':'老挝 老挝王国 Laos Kingdom of Laos Royaume du Laos',
  'record_files':['laos_kingdom_medalbook_variants.json','laos_kingdom_wawards_differential.json'],
  'manifest_files':['laos_kingdom_medalbook_variants_manifest.json','laos_kingdom_wawards_differential_manifest.json'],
  'countries':['老挝王国（1947–1975）'],'unfiltered_record_files':['laos_kingdom_medalbook_variants.json','laos_kingdom_wawards_differential.json'],'country_group':'laos'},
 {'slug':'laos_pdr','title':'老挝人民民主共和国（1975–）','anchor':'laos-pdr','aliases':'老挝 老挝人民民主共和国 Laos Lao PDR Peoples Democratic Republic',
  'record_files':['laos_pdr_wawards_variants.json'],
  'manifest_files':['laos_pdr_wawards_variants_manifest.json'],
  'countries':['老挝人民民主共和国（1975–）'],'unfiltered_record_files':['laos_pdr_wawards_variants.json'],'country_group':'laos'},
 {'slug':'brunei','title':'文莱达鲁萨兰国','anchor':'brunei','aliases':'文莱 Brunei Brunei Darussalam Negara Brunei Darussalam',
  'record_files':['brunei_wawards_variants.json','brunei_medalbook_differential.json'],
  'manifest_files':['brunei_wawards_variants_manifest.json','brunei_medalbook_differential_manifest.json'],
  'countries':['文莱达鲁萨兰国'],'unfiltered_record_files':['brunei_wawards_variants.json','brunei_medalbook_differential.json']},
 {'slug':'singapore','title':'新加坡共和国','anchor':'singapore','aliases':'新加坡 Singapore Republic of Singapore',
  'record_files':['singapore_medalbook_variants.json','singapore_pmo_official_variants.json'],
  'manifest_files':['singapore_medalbook_variants_manifest.json','singapore_pmo_official_variants_manifest.json'],
  'countries':['新加坡共和国'],'unfiltered_record_files':['singapore_medalbook_variants.json','singapore_pmo_official_variants.json']},
 {'slug':'malaysia_federal','title':'马来西亚联邦','anchor':'malaysia-federal','aliases':'马来西亚 Malaysia Federation federal awards','record_files':['malaysia_federal_medalbook_variants.json','malaysia_federal_istiadat_variants.json'],'manifest_files':['malaysia_federal_medalbook_variants_manifest.json','malaysia_federal_istiadat_variants_manifest.json'],'countries':['马来西亚联邦'],'unfiltered_record_files':['malaysia_federal_medalbook_variants.json','malaysia_federal_istiadat_variants.json'],'country_group':'malaysia'},
 {'slug':'sabah','title':'沙巴州','anchor':'sabah','aliases':'沙巴 Sabah Malaysia','record_files':['sabah_medalbook_variants.json'],'manifest_files':['sabah_medalbook_variants_manifest.json'],'countries':['沙巴州'],'unfiltered_record_files':['sabah_medalbook_variants.json'],'country_group':'malaysia'},
 {'slug':'sarawak','title':'砂拉越州','anchor':'sarawak','aliases':'砂拉越 Sarawak Malaysia','record_files':['sarawak_medalbook_variants.json'],'manifest_files':['sarawak_medalbook_variants_manifest.json'],'countries':['砂拉越州'],'unfiltered_record_files':['sarawak_medalbook_variants.json'],'country_group':'malaysia'},
 {'slug':'johor','title':'柔佛苏丹国','anchor':'johor','aliases':'柔佛 Johor Sultanate Malaysia','record_files':['johor_medalbook_variants.json'],'manifest_files':['johor_medalbook_variants_manifest.json'],'countries':['柔佛苏丹国'],'unfiltered_record_files':['johor_medalbook_variants.json'],'country_group':'malaysia'},
 {'slug':'kedah','title':'吉打苏丹国','anchor':'kedah','aliases':'吉打 Kedah Sultanate Malaysia','record_files':['kedah_medalbook_variants.json'],'manifest_files':['kedah_medalbook_variants_manifest.json'],'countries':['吉打苏丹国'],'unfiltered_record_files':['kedah_medalbook_variants.json'],'country_group':'malaysia'},
 {'slug':'kelantan','title':'吉兰丹苏丹国','anchor':'kelantan','aliases':'吉兰丹 Kelantan Sultanate Malaysia','record_files':['kelantan_medalbook_variants.json'],'manifest_files':['kelantan_medalbook_variants_manifest.json'],'countries':['吉兰丹苏丹国'],'unfiltered_record_files':['kelantan_medalbook_variants.json'],'country_group':'malaysia'},
 {'slug':'pahang','title':'彭亨苏丹国','anchor':'pahang','aliases':'彭亨 Pahang Sultanate Malaysia','record_files':['pahang_medalbook_variants.json'],'manifest_files':['pahang_medalbook_variants_manifest.json'],'countries':['彭亨苏丹国'],'unfiltered_record_files':['pahang_medalbook_variants.json'],'country_group':'malaysia'},
 {'slug':'perak','title':'霹雳苏丹国','anchor':'perak','aliases':'霹雳 Perak Sultanate Malaysia','record_files':['perak_medalbook_variants.json'],'manifest_files':['perak_medalbook_variants_manifest.json'],'countries':['霹雳苏丹国'],'unfiltered_record_files':['perak_medalbook_variants.json'],'country_group':'malaysia'},
 {'slug':'philippines_republic','title':'菲律宾共和国','anchor':'philippines-republic','aliases':'菲律宾 Philippines Republic Pilipinas','record_files':['philippines_medalbook_variants.json'],'manifest_files':['philippines_medalbook_variants_manifest.json'],'countries':['菲律宾共和国'],'country_group':'philippines'},
 {'slug':'philippines_insular','title':'菲律宾群岛政府（1901–1935）','anchor':'philippines-insular','aliases':'菲律宾群岛政府 Insular Government Philippine Islands','record_files':['philippines_medalbook_variants.json'],'manifest_files':['philippines_medalbook_variants_manifest.json'],'countries':['菲律宾群岛政府（1901–1935）'],'country_group':'philippines'},
 {'slug':'myanmar_modern','title':'缅甸联邦与社会主义共和国（1948–1988）','anchor':'myanmar-modern','aliases':'缅甸 Myanmar Burma Union Socialist Republic','record_files':['myanmar_medalbook_variants.json'],'manifest_files':['myanmar_medalbook_variants_manifest.json'],'countries':['缅甸联邦与社会主义共和国（1948–1988）'],'country_group':'myanmar'},
 {'slug':'konbaung','title':'贡榜王朝（1752–1885）','anchor':'konbaung','aliases':'贡榜王朝 Konbaung Burma Tsalwe','record_files':['myanmar_medalbook_variants.json'],'manifest_files':['myanmar_medalbook_variants_manifest.json'],'countries':['贡榜王朝（1752–1885）'],'country_group':'myanmar'},
 {'slug':'indonesia','title':'印度尼西亚共和国','anchor':'indonesia','aliases':'印度尼西亚 印尼 Indonesia Republik Indonesia','record_files':['indonesia_medalbook_variants.json','indonesia_commons_variants.json'],'manifest_files':['indonesia_medalbook_variants_manifest.json','indonesia_commons_variants_manifest.json'],'countries':['印度尼西亚共和国'],'unfiltered_record_files':['indonesia_medalbook_variants.json','indonesia_commons_variants.json']},
 {'slug':'thailand','title':'泰国','anchor':'thailand','aliases':'泰国 Thailand Siam 暹罗',
  'record_files':['thailand_medalbook_variants.json'],'manifest_files':['thailand_medalbook_variants_manifest.json'],'countries':['泰国'],'unfiltered_record_files':['thailand_medalbook_variants.json']},
 {'slug':'british_india','title':'东印度公司／英属印度（1837–1947）','anchor':'british-india','aliases':'东印度公司 英属印度 British India East India Company Indian Empire Star Crown Kaisar-i-Hind',
  'record_files':['british_india_medalbook_core.json'],'manifest_files':['british_india_medalbook_core_manifest.json'],'countries':['东印度公司／英属印度（1837–1947）'],'country_group':'india'},
 {'slug':'india_republic','title':'印度共和国（1950–）','anchor':'india-republic','aliases':'印度 India Republic Bharat 印度共和国',
  'record_files':['india_medalbook_variants.json','india_medals_org_differential.json'],'manifest_files':['india_medalbook_variants_manifest.json','india_medals_org_differential_manifest.json'],'countries':['印度共和国（1950–）'],'country_group':'india'},
 {'slug':'dominion_india','title':'印度自治领（1947–1950）','anchor':'dominion-india','aliases':'印度自治领 Dominion of India 1947 1950',
  'record_files':['india_medals_org_differential.json'],'manifest_files':['india_medals_org_differential_manifest.json'],'countries':['印度自治领（1947–1950）'],'country_group':'india'},
 {'slug':'azad_hind','title':'自由印度临时政府（1943–1945）','anchor':'azad-hind','aliases':'自由印度 Azad Hind Provisional Government INA',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['自由印度临时政府（1943–1945）'],'country_group':'india'},
 {'slug':'bahawalpur','title':'巴哈瓦尔布尔土邦（1802–1955）','anchor':'bahawalpur','aliases':'巴哈瓦尔布尔 Bahawalpur Abbasi 巴基斯坦土邦',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['巴哈瓦尔布尔土邦（1802–1955）'],'country_group':'india'},
 {'slug':'baroda','title':'巴罗达土邦','anchor':'baroda','aliases':'巴罗达 Baroda Gaekwad',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['巴罗达土邦'],'country_group':'india'},
 {'slug':'bikaner','title':'比卡内尔土邦','anchor':'bikaner','aliases':'比卡内尔 Bikaner',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['比卡内尔土邦'],'country_group':'india'},
 {'slug':'gwalior','title':'瓜廖尔土邦','anchor':'gwalior','aliases':'瓜廖尔 Gwalior Scindia',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['瓜廖尔土邦'],'country_group':'india'},
 {'slug':'jammu_kashmir','title':'查谟—克什米尔土邦','anchor':'jammu-kashmir','aliases':'查谟 克什米尔 Jammu Kashmir',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['查谟—克什米尔土邦'],'country_group':'india'},
 {'slug':'patiala','title':'帕蒂亚拉土邦','anchor':'patiala','aliases':'帕蒂亚拉 Patiala Phulkian',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['帕蒂亚拉土邦'],'country_group':'india'},
 {'slug':'sikh_empire','title':'锡克帝国（1799–1849）','anchor':'sikh-empire','aliases':'锡克帝国 Sikh Empire Punjab 旁遮普',
  'record_files':['india_medalbook_variants.json'],'manifest_files':['india_medalbook_variants_manifest.json'],'countries':['锡克帝国（1799–1849）'],'country_group':'india'},
 {'slug':'annam_protectorate','title':'阮朝／安南保护国（1884–1945）','anchor':'annam-protectorate','aliases':'阮朝 安南 Annam Nguyen Dynasty 大南龙星 金磬章','record_files':['vietnam_medalbook_variants.json'],'manifest_files':['vietnam_medalbook_variants_manifest.json'],'countries':['阮朝／安南保护国（1884–1945）'],'country_group':'vietnam'},
 {'slug':'tai_federation','title':'法属印度支那 · 傣联邦','anchor':'tai-federation','aliases':'傣联邦 泰族 Sip Song Chau Tai Tonkin','record_files':['vietnam_medalbook_variants.json'],'manifest_files':['vietnam_medalbook_variants_manifest.json'],'countries':['法属印度支那 · 傣联邦'],'country_group':'vietnam'},
 {'slug':'democratic_vietnam','title':'越南民主共和国（1945–1976）','anchor':'democratic-vietnam','aliases':'北越 越南民主共和国 North Vietnam Democratic Republic Vietnam','record_files':['vietnam_medalbook_variants.json'],'manifest_files':['vietnam_medalbook_variants_manifest.json'],'countries':['越南民主共和国（1945–1976）'],'country_group':'vietnam'},
 {'slug':'state_south_vietnam','title':'越南国／越南共和国（1950–1975）','anchor':'state-south-vietnam','aliases':'越南国 南越 State of Vietnam Republic South Vietnam 国家勋章','record_files':['vietnam_medalbook_variants.json'],'manifest_files':['vietnam_medalbook_variants_manifest.json'],'countries':['越南国／越南共和国（1950–1975）'],'country_group':'vietnam'},
 {'slug':'south_vietnam','title':'越南共和国（1955–1975）','anchor':'south-vietnam','aliases':'南越 Republic of Vietnam South Vietnam','record_files':['vietnam_medalbook_variants.json'],'manifest_files':['vietnam_medalbook_variants_manifest.json'],'countries':['越南共和国（1955–1975）'],'country_group':'vietnam'},
 {'slug':'socialist_vietnam','title':'越南社会主义共和国（1976–）','anchor':'socialist-vietnam','aliases':'越南 Vietnam Socialist Republic Việt Nam','record_files':['vietnam_medalbook_variants.json'],'manifest_files':['vietnam_medalbook_variants_manifest.json'],'countries':['越南社会主义共和国（1976–）'],'country_group':'vietnam'},
 {'slug':'morocco','title':'摩洛哥','anchor':'morocco','aliases':'摩洛哥 Morocco',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['摩洛哥']},
 {'slug':'algeria','title':'阿尔及利亚','anchor':'algeria','aliases':'阿尔及利亚 Algeria',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['阿尔及利亚']},
 {'slug':'azerbaijan','title':'阿塞拜疆','anchor':'azerbaijan','aliases':'阿塞拜疆 Azerbaijan',
  'record_files':['mena_round7_2026-09-26.json','azerbaijan_wawards_families.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json','azerbaijan_wawards_families_manifest.json'],'countries':['阿塞拜疆','阿塞拜疆共和国'],'unfiltered_record_files':['azerbaijan_wawards_families.json'],
  'exclude_ids':['MENA7-AZRBAYCAN-POLISININ-100-ILLIYI-1918-2018-YUBILEY-MEDAL-C8723327D5F7','MENA7-AZRBAYCAN-POLISININ-100-ILLIYI-19182018-YUBILEY-MEDAL-80C6066C2D09','MENA7-AZRBAYCAN-XALQ-CUMHURIYYTININ-100-ILLIYI-1918-2018-YUBILEY-MEDAL-04657779A0DD','MENA7-BAK-DOVLT-UNIVERSITETININ-100-ILLIYI-YUBILEY-MEDAL-0614B173B6F2','MENA7-CSUR-DOYUSCU-MEDAL-0189B846E786','MENA7-DOYUSD-FRQLNMY-GOR-MEDAL-6DDC9ADC47D1','MENA7-FUZULININ-AZAD-OLUNMASNA-GOR-MEDAL-F65C4F3EC31E','MENA7-HEYDR-LIYEVIN-100-ILLIYI-1923-2023-YUBILEY-MEDAL-8236E094D1CD','MENA7-HRBI-MKDASLQ-SAHSIND-XIDMTLR-GOR-MEDAL-3479D950521A','MENA7-KLBCRIN-AZAD-OLUNMASNA-GOR-MEDAL-0F7DB13AB328','MENA7-PARTICIPANT-OF-THE-PATRIOTIC-WAR-MEDAL-BCC5BFCF350B','MENA7-QARABAG-ORDENI-9A30E4525E12','MENA7-SUQOVUSANN-AZAD-OLUNMASNA-GOR-MEDAL-D7F40F85DC08','MENA7-SUSANN-AZAD-OLUNMASNA-GOR-MEDAL-031DF37CC09D','MENA7-TARAGGI-E01AF1B77D09','MENA7-VTN-MUHARIBSI-ISTIRAKCS-MEDAL-C7BF10183A23','MENA7-VTN-MUHARIBSI-QHRMAN-MEDAL-0C63129DA77C','MENA7-XOCAVNDIN-AZAD-OLUNMASNA-GOR-MEDAL-1F0B0C5920B6','MENA7-ZFR-ORDENI-CF5CB9A2BC83']},
 {'slug':'armenia','title':'亚美尼亚','anchor':'armenia','aliases':'亚美尼亚 Armenia Հայաստան',
  'record_files':['armenia_pack1.json','armenia_wawards_differential.json'],'manifest_files':['armenia_pack1_manifest.json','armenia_wawards_differential_manifest.json'],'countries':['亚美尼亚','亚美尼亚共和国'],'unfiltered_record_files':['armenia_pack1.json','armenia_wawards_differential.json']},
 {'slug':'georgia','title':'格鲁吉亚','anchor':'georgia','aliases':'格鲁吉亚 Georgia საქართველო',
  'record_files':['georgia_wawards_families.json'],'manifest_files':['georgia_wawards_families_manifest.json'],'countries':['格鲁吉亚'],'unfiltered_record_files':['georgia_wawards_families.json']},
 {'slug':'ukraine','title':'乌克兰','anchor':'ukraine','aliases':'乌克兰 Ukraine Україна',
  'record_files':['ukraine_wawards_families.json'],'manifest_files':['ukraine_wawards_families_manifest.json'],'countries':['乌克兰'],'unfiltered_record_files':['ukraine_wawards_families.json']},
 {'slug':'moldova','title':'摩尔多瓦','anchor':'moldova','aliases':'摩尔多瓦 Moldova Republica Moldova',
  'record_files':['moldova_wawards_families.json'],'manifest_files':['moldova_wawards_families_manifest.json'],'countries':['摩尔多瓦共和国'],'unfiltered_record_files':['moldova_wawards_families.json']},
 {'slug':'estonia','title':'爱沙尼亚','anchor':'estonia','aliases':'爱沙尼亚 Estonia Eesti',
  'record_files':['estonia_wawards_families.json'],'manifest_files':['estonia_wawards_families_manifest.json'],'countries':['爱沙尼亚'],'unfiltered_record_files':['estonia_wawards_families.json']},
 {'slug':'belarus','title':'白俄罗斯','anchor':'belarus','aliases':'白俄罗斯 Belarus Беларусь',
  'record_files':['belarus_wawards_families.json'],'manifest_files':['belarus_wawards_families_manifest.json'],'countries':['白俄罗斯共和国'],'unfiltered_record_files':['belarus_wawards_families.json']},
 {'slug':'lithuania','title':'立陶宛','anchor':'lithuania','aliases':'立陶宛 Lithuania Lietuva',
  'record_files':['lithuania_wawards_families.json'],'manifest_files':['lithuania_wawards_families_manifest.json'],'countries':['立陶宛共和国'],'unfiltered_record_files':['lithuania_wawards_families.json']},
 {'slug':'latvia','title':'拉脱维亚','anchor':'latvia','aliases':'拉脱维亚 Latvia Latvija',
  'record_files':['latvia_wawards_families.json'],'manifest_files':['latvia_wawards_families_manifest.json'],'countries':['拉脱维亚共和国'],'unfiltered_record_files':['latvia_wawards_families.json']},
 {'slug':'czechoslovakia','title':'捷克斯洛伐克','anchor':'czechoslovakia','aliases':'捷克斯洛伐克 Czechoslovakia Československo ČSSR',
  'record_files':['czech_slovak_fast_2026-09-28.json'],'manifest_files':['czech_slovak_fast_2026-09-28_manifest.json'],'countries':['捷克斯洛伐克','捷克斯洛伐克社会主义共和国']},
 {'slug':'czech-republic','title':'捷克共和国','anchor':'czech-republic','aliases':'捷克 捷克共和国 Czech Republic Czechia Česko',
  'record_files':['czech_slovak_fast_2026-09-28.json'],'manifest_files':['czech_slovak_fast_2026-09-28_manifest.json'],'countries':['捷克共和国']},
 {'slug':'slovakia','title':'斯洛伐克','anchor':'slovakia','aliases':'斯洛伐克 Slovakia Slovak Republic Slovensko',
  'record_files':['czech_slovak_fast_2026-09-28.json'],'manifest_files':['czech_slovak_fast_2026-09-28_manifest.json'],'countries':['斯洛伐克共和国','斯洛伐克国（历史政体）']},
 {'slug':'romania-kingdom','title':'罗马尼亚王国','anchor':'romania-kingdom','aliases':'罗马尼亚 Romania Kingdom of Romania România',
  'record_files':['romania_medals_org_batch1.json'],'manifest_files':['romania_medals_org_batch1_manifest.json'],'countries':['罗马尼亚王国'],'unfiltered_record_files':['romania_medals_org_batch1.json']},
 {'slug':'bulgaria-principality','title':'保加利亚公国','anchor':'bulgaria-principality','aliases':'保加利亚公国 Principality of Bulgaria Княжество България',
  'record_files':['bulgaria_wmi_batch1_2026-09-29.json'],'manifest_files':['bulgaria_wmi_batch1_2026-09-29_manifest.json'],'countries':['保加利亚公国'],'country_group':'bulgaria'},
 {'slug':'bulgaria-kingdom','title':'保加利亚王国','anchor':'bulgaria-kingdom','aliases':'保加利亚王国 Kingdom of Bulgaria Царство България',
  'record_files':['bulgaria_wmi_batch1_2026-09-29.json'],'manifest_files':['bulgaria_wmi_batch1_2026-09-29_manifest.json'],'countries':['保加利亚王国'],'country_group':'bulgaria'},
 {'slug':'bulgaria-republic','title':'保加利亚共和国','anchor':'bulgaria-republic','aliases':'保加利亚共和国 Republic of Bulgaria Република България',
  'record_files':['bulgaria_wmi_batch1_2026-09-29.json'],'manifest_files':['bulgaria_wmi_batch1_2026-09-29_manifest.json'],'countries':['保加利亚共和国'],'country_group':'bulgaria'},
 {'slug':'uzbekistan','title':'乌兹别克斯坦','anchor':'uzbekistan','aliases':'乌兹别克斯坦 Uzbekistan',
  'record_files':['mena_round7_2026-09-26.json','uzbekistan_medalbook_variants.json','uzbekistan_medals_org_variants.json','uzbekistan_presidency_variants.json'],
  'manifest_files':['mena_round7_manifest_2026-09-26.json','uzbekistan_medalbook_variants_manifest.json','uzbekistan_medals_org_variants_manifest.json','uzbekistan_presidency_variants_manifest.json'],
  'countries':['乌兹别克斯坦'],'unfiltered_record_files':['uzbekistan_medalbook_variants.json','uzbekistan_medals_org_variants.json','uzbekistan_presidency_variants.json']},
 {'slug':'yemen','title':'也门','anchor':'yemen','aliases':'也门 Yemen',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['也门']},
 {'slug':'spain_republic','title':'西班牙第二共和国','anchor':'spain-republic','aliases':'西班牙 第二共和国 Spain Second Republic Isabella',
  'record_files':['mena_round7_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json'],'countries':['西班牙第二共和国'],'country_group':'spain'},
 {'slug':'spain_kingdom','title':'西班牙王国','anchor':'spain-kingdom','aliases':'西班牙王国 Spain Reino de España BOE',
  'record_files':['spain_military_batch1_2026-09-26.json','spain_boe2025_campaigns_pack1.json','spain_boe2025_discontinued_pack1.json','spain_boe2025_commemorative_pack1.json','spain_boe2025_institutional_pack1.json'],'manifest_files':['spain_military_batch1_2026-09-26_manifest.json','spain_boe2025_campaigns_pack1_manifest.json','spain_boe2025_discontinued_pack1_manifest.json','spain_boe2025_commemorative_pack1_manifest.json','spain_boe2025_institutional_pack1_manifest.json'],'country_group':'spain'},
 {'slug':'portugal','title':'葡萄牙','anchor':'portugal','aliases':'葡萄牙 Portugal Portuguese Kingdom Republic',
  'record_files':['portugal_medals_org_fast_2026-09-28.json'],'manifest_files':['portugal_medals_org_fast_2026-09-28_manifest.json'],'unfiltered_record_files':['portugal_medals_org_fast_2026-09-28.json']},
 {'slug':'netherlands','title':'荷兰王国','anchor':'netherlands','aliases':'荷兰 荷兰王国 Netherlands Kingdom of the Netherlands Nederland',
  'record_files':['netherlands_wmi_batch1_2026-09-29.json'],'manifest_files':['netherlands_wmi_batch1_2026-09-29_manifest.json'],'unfiltered_record_files':['netherlands_wmi_batch1_2026-09-29.json']},
 {'slug':'belgium','title':'比利时王国','anchor':'belgium','aliases':'比利时 比利时王国 Belgium Kingdom of Belgium Belgique België',
  'record_files':['belgium_wmi_master_fast_2026-09-29.json'],'manifest_files':['belgium_wmi_master_fast_2026-09-29_manifest.json'],'unfiltered_record_files':['belgium_wmi_master_fast_2026-09-29.json']},
 {'slug':'luxembourg','title':'卢森堡大公国','anchor':'luxembourg','aliases':'卢森堡 卢森堡大公国 Luxembourg Grand Duchy Lëtzebuerg Gold Lion Adolph Nassau Oak Crown',
  'record_files':['luxembourg_official_book_2007.json'],'manifest_files':['luxembourg_official_book_2007_manifest.json'],'unfiltered_record_files':['luxembourg_official_book_2007.json']},
 {'slug':'ireland','title':'爱尔兰／爱尔兰国防军','anchor':'ireland','aliases':'爱尔兰 Ireland Éire Irish Defence Forces An Fórsa Cosanta Garda Scott Medal An Bonn Scott',
  'record_files':['ireland_garda_scott_medal_2023.json','ireland_defence_forces_medals_2010.json'],'manifest_files':['ireland_garda_scott_medal_2023_manifest.json','ireland_defence_forces_medals_2010_manifest.json'],'unfiltered_record_files':['ireland_garda_scott_medal_2023.json'],'awarding_authorities':['爱尔兰','爱尔兰国防军','爱尔兰国防军及爱尔兰国家应急服务机构']},
 {'slug':'united-nations','title':'联合国','anchor':'united-nations','aliases':'联合国 United Nations UN ONU ONUC UNIFIL UNTSO peacekeeping',
  'record_files':['ireland_defence_forces_medals_2010.json'],'manifest_files':['ireland_defence_forces_medals_2010_manifest.json'],'awarding_authorities':['联合国']},
 {'slug':'european-communities-union','title':'欧洲共同体／欧洲联盟','anchor':'european-communities-union','aliases':'欧洲共同体 欧洲联盟 European Community European Union EC EU ESDP',
  'record_files':['ireland_defence_forces_medals_2010.json'],'manifest_files':['ireland_defence_forces_medals_2010_manifest.json'],'awarding_authorities':['欧洲共同体','欧洲联盟']},
 {'slug':'icfy','title':'前南斯拉夫问题国际会议','anchor':'icfy','aliases':'前南斯拉夫问题国际会议 International Conference on the Former Yugoslavia ICFY',
  'record_files':['ireland_defence_forces_medals_2010.json'],'manifest_files':['ireland_defence_forces_medals_2010_manifest.json'],'awarding_authorities':['前南斯拉夫问题国际会议']},
 {'slug':'nato','title':'北大西洋公约组织','anchor':'nato','aliases':'北约 北大西洋公约组织 NATO North Atlantic Treaty Organization',
  'record_files':['ireland_defence_forces_medals_2010.json'],'manifest_files':['ireland_defence_forces_medals_2010_manifest.json'],'awarding_authorities':['北大西洋公约组织']},
 {'slug':'interfet','title':'东帝汶国际部队','anchor':'interfet','aliases':'东帝汶国际部队 International Force East Timor INTERFET',
  'record_files':['ireland_defence_forces_medals_2010.json'],'manifest_files':['ireland_defence_forces_medals_2010_manifest.json'],'awarding_authorities':['东帝汶国际部队']},
 {'slug':'savoy_italy','title':'萨佛依王朝／意大利王国','anchor':'savoy-italy','aliases':'萨佛依 意大利 Savoy Italy Annunciation',
  'record_files':['mena_round7_2026-09-26.json','italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'],'manifest_files':['mena_round7_manifest_2026-09-26.json','italy_crown_pack1_manifest.json','italy_medalbook_pack2_2026-09-26_manifest.json','italy_medalbook_pack3_2026-09-26_manifest.json','italy_medalbook_pack4_2026-09-26_manifest.json','italy_medalbook_pack5_2026-09-26_manifest.json'],'countries':['意大利／萨佛依王朝'],'unfiltered_record_files':['italy_crown_pack1.json','italy_medalbook_pack2_2026-09-26.json','italy_medalbook_pack3_2026-09-26.json','italy_medalbook_pack4_2026-09-26.json','italy_medalbook_pack5_2026-09-26.json'],'exclude_ids':['IT-KOI-058-V51']},
 {'slug':'habsburg-monarchy','title':'哈布斯堡君主国','anchor':'habsburg-monarchy','aliases':'哈布斯堡 Habsburg Monarchy Austria Österreich',
  'record_files':['austria_habsburg_medalsorg_fast_2026-09-28.json'],'manifest_files':['austria_habsburg_medalsorg_fast_2026-09-28_manifest.json'],'unfiltered_record_files':['austria_habsburg_medalsorg_fast_2026-09-28.json'],'country_group':'austria'},
 {'slug':'austrian-empire','title':'奥地利帝国','anchor':'austrian-empire','aliases':'奥地利帝国 Austrian Empire Kaisertum Österreich',
  'record_files':['austria_empire_medalsorg_fast_2026-09-28.json'],'manifest_files':['austria_empire_medalsorg_fast_2026-09-28_manifest.json'],'unfiltered_record_files':['austria_empire_medalsorg_fast_2026-09-28.json'],'country_group':'austria'},
 {'slug':'austro-hungary','title':'奥匈帝国','anchor':'austro-hungary','aliases':'奥匈帝国 Austria-Hungary Österreich-Ungarn',
  'record_files':['austro_hungary_medalsorg_fast_2026-09-28.json'],'manifest_files':['austro_hungary_medalsorg_fast_2026-09-28_manifest.json'],'unfiltered_record_files':['austro_hungary_medalsorg_fast_2026-09-28.json'],'country_group':'austria'},
 {'slug':'austria-republic','title':'奥地利共和国','anchor':'austria-republic','aliases':'奥地利 Austria Republic Österreich',
  'record_files':['austria_republic_medalsorg_fast_2026-09-28.json'],'manifest_files':['austria_republic_medalsorg_fast_2026-09-28_manifest.json'],'unfiltered_record_files':['austria_republic_medalsorg_fast_2026-09-28.json'],'country_group':'austria'},
 {'slug':'hungary','title':'匈牙利','anchor':'hungary','aliases':'匈牙利 Hungary Magyarország Hungarian awards',
  'record_files':['hungary_wmi_master_fast_2026-09-29.json'],'manifest_files':['hungary_wmi_master_fast_2026-09-29_manifest.json'],
  'include_ids':['HUN-WMI-001','HUN-WMI-002','HUN-WMI-011','HUN-WMI-012','HUN-WMI-014','HUN-WMI-020']},
 {'slug':'finland','title':'芬兰共和国','anchor':'finland','aliases':'芬兰 Finland Suomi White Rose Lion Cross of Liberty',
  'record_files':['finland_orders_pack1.json'],'manifest_files':['finland_orders_pack1_manifest.json']},
 {'slug':'sweden','title':'瑞典王国','anchor':'sweden','aliases':'瑞典 Sweden Sverige Serafimerorden Seraphim',
  'record_files':['sweden_orders_pack1.json'],'manifest_files':['sweden_orders_pack1_manifest.json']},
 {'slug':'denmark','title':'丹麦王国','anchor':'denmark','aliases':'丹麦 丹麦王国 Denmark Kingdom of Denmark Danmark Elephant Dannebrog',
  'record_files':['denmark_master_fast_2026-09-29.json'],'manifest_files':['denmark_master_fast_2026-09-29_manifest.json'],'unfiltered_record_files':['denmark_master_fast_2026-09-29.json']},
 {'slug':'iceland','title':'冰岛','anchor':'iceland','aliases':'冰岛 Iceland Ísland Falcon Fálkaorðan Heiðursmerki',
  'record_files':['iceland_official_honours_2026-09-29.json'],'manifest_files':['iceland_official_honours_2026-09-29_manifest.json'],'unfiltered_record_files':['iceland_official_honours_2026-09-29.json']},
 {'slug':'norway','title':'挪威王国','anchor':'norway','aliases':'挪威 Norway Norge St Olav Sankt Olavs Orden',
  'record_files':['norway_orders_pack1.json'],'manifest_files':['norway_orders_pack1_manifest.json']},
 {'slug':'poland','title':'波兰','anchor':'poland','aliases':'波兰 Poland Polska Polish',
  'record_files':['poland_wikipedia_master_pictured_2026-09-28.json'],
  'manifest_files':['poland_wikipedia_master_pictured_2026-09-28_manifest.json'],
  'countries':['波兰'],'unfiltered_record_files':['poland_wikipedia_master_pictured_2026-09-28.json']},
 {'slug':'uk','title':'英国','anchor':'uk','aliases':'英国 大英帝国 United Kingdom Great Britain British Empire England Scotland Wales Northern Ireland',
  'record_files':['uk_mod_pack1.json','uk_us_gap_round2_2026-09-26.json','uk_mod_completion_20260930.json'],'manifest_files':['uk_mod_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json','uk_mod_completion_20260930_manifest.json'],'countries':['英国／大英帝国'],'unfiltered_record_files':['uk_mod_pack1.json']},
 {'slug':'united_states','title':'美国','anchor':'united-states','aliases':'美国 United States USA U.S. NHHC NARA',
  'record_files':['us_nhhc_pack1.json','uk_us_gap_round2_2026-09-26.json'],'manifest_files':['us_nhhc_pack1_manifest.json','uk_us_gap_round2_2026-09-26_manifest.json'],'countries':['美国'],'unfiltered_record_files':['us_nhhc_pack1.json']},
 {'slug':'russian_empire','title':'俄罗斯帝国','anchor':'russian-empire','aliases':'俄罗斯帝国 Imperial Russia Российская империя',
  'record_files':['russian_empire_pack1.json','russian_empire_gap_2026-09-26.json'],'manifest_files':['russian_empire_pack1_manifest.json','russian_empire_gap_2026-09-26_manifest.json'],'country_group':'russia'},
 {'slug':'soviet_union','title':'苏联','anchor':'soviet-union','aliases':'苏联 USSR Soviet Union СССР',
  'record_files':['soviet_union_pack1.json','russia_bulk_pack2.json','russia_bulk_pack3.json','soviet_gap_round4_2026-09-26.json','soviet_wikipedia_master_differential_2026-09-28.json','soviet_wikipedia_master_followup_2026-09-28.json','soviet_completion_20260929.json'],'manifest_files':['soviet_union_pack1_manifest.json','russia_bulk_pack2_manifest.json','russia_bulk_pack3_manifest.json','soviet_gap_round4_2026-09-26_manifest.json','soviet_wikipedia_master_differential_2026-09-28_manifest.json','soviet_wikipedia_master_followup_2026-09-28_manifest.json','soviet_completion_20260929_manifest.json'],'exclude_ids':['USSR-MED-08-V-II-WIKI','USSR-MED-10-V-II-WIKI','USSR-MED-54-V-II-WIKI'],'country_group':'russia'},
 {'slug':'russian_federation','title':'俄罗斯联邦','anchor':'russian-federation','aliases':'俄罗斯联邦 Russia Russian Federation Российская Федерация',
  'record_files':['russian_federation_pack1.json'],'manifest_files':['russian_federation_pack1_manifest.json'],'country_group':'russia'},
 {'slug':'qing_empire','title':'大清帝国（1644–1912）','anchor':'qing-empire','aliases':'大清 清朝 清帝国 Qing Imperial China 双龙宝星 宝星功牌',
  'record_files':['qing_medalbook_variants.json'],'manifest_files':['qing_medalbook_variants_manifest.json'],'countries':['大清帝国（1644–1912）'],'country_group':'china'},
 {'slug':'peoples_republic_china','title':'中华人民共和国（1949–）','anchor':'peoples-republic-china','aliases':'中华人民共和国 中国 PRC People Republic China 中苏友谊',
  'record_files':['peoples_republic_china_medals_org.json'],'manifest_files':['peoples_republic_china_medals_org_manifest.json'],'countries':['中华人民共和国'],'country_group':'china'},
 {'slug':'republic_of_china','title':'中华民国（1912–）','anchor':'republic-of-china','aliases':'中华民国 Republic of China ROC 勋章',
  'record_files':['east_asia_gap_round1_2026-09-26.json','republic_of_china_medalbook_variants.json'],'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json','republic_of_china_medalbook_variants_manifest.json'],'countries':['中华民国'],'unfiltered_record_files':['republic_of_china_medalbook_variants.json'],'country_group':'china'},
 {'slug':'hong_kong','title':'香港','anchor':'hong-kong','aliases':'香港 Hong Kong 香港特别行政区',
  'record_files':['hong_kong_wawards_families.json'],'manifest_files':['hong_kong_wawards_families_manifest.json'],'countries':['香港特别行政区'],'unfiltered_record_files':['hong_kong_wawards_families.json'],'country_group':'china'},
 {'slug':'cyprus','title':'塞浦路斯','anchor':'cyprus','aliases':'塞浦路斯 Cyprus Κύπρος',
  'record_files':['cyprus_wawards_families.json'],'manifest_files':['cyprus_wawards_families_manifest.json'],'countries':['塞浦路斯共和国'],'unfiltered_record_files':['cyprus_wawards_families.json']},
 {'slug':'greece','title':'希腊','anchor':'greece','aliases':'希腊 Greece Hellenic Kingdom Republic Ελλάδα',
  'record_files':['greece_medals_org_fast_2026-09-28.json'],'manifest_files':['greece_medals_org_fast_2026-09-28_manifest.json'],'unfiltered_record_files':['greece_medals_org_fast_2026-09-28.json']},
 {'slug':'maldives','title':'马尔代夫','anchor':'maldives','aliases':'马尔代夫 Maldives ދިވެހި',
  'record_files':['maldives_wawards_families.json'],'manifest_files':['maldives_wawards_families_manifest.json'],'countries':['马尔代夫共和国'],'unfiltered_record_files':['maldives_wawards_families.json']},
 {'slug':'korean_empire','title':'大韩帝国（1897–1910）','anchor':'korean-empire','aliases':'大韩帝国 Korean Empire 대한제국',
  'record_files':['east_asia_gap_round1_2026-09-26.json','korean_empire_medalbook_variants.json'],'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json','korean_empire_medalbook_variants_manifest.json'],'countries':['大韩帝国'],'unfiltered_record_files':['korean_empire_medalbook_variants.json'],'country_group':'korea'},
 {'slug':'south_korea','title':'韩国','anchor':'south-korea','aliases':'韩国 大韩民国 South Korea Republic of Korea 대한민국',
  'record_files':['east_asia_gap_round1_2026-09-26.json','south_korea_official_complete_2026-09-27.json','south_korea_medalbook_differential.json'],
  'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json','south_korea_official_complete_2026-09-27_manifest.json','south_korea_medalbook_differential_manifest.json'],
  'countries':['韩国'],'unfiltered_record_files':['south_korea_medalbook_differential.json'],'country_group':'korea'},
 {'slug':'north_korea','title':'朝鲜','anchor':'north-korea','aliases':'朝鲜 朝鲜民主主义人民共和国 North Korea DPRK 조선',
  'record_files':['east_asia_gap_round1_2026-09-26.json','north_korea_medalbook_variants.json','north_korea_medals_org_variants.json','north_korea_commons_cached_variants.json'],'manifest_files':['east_asia_gap_round1_2026-09-26_manifest.json','north_korea_medalbook_variants_manifest.json','north_korea_medals_org_variants_manifest.json','north_korea_commons_cached_variants_manifest.json'],'countries':['朝鲜'],'unfiltered_record_files':['north_korea_medalbook_variants.json','north_korea_medals_org_variants.json','north_korea_commons_cached_variants.json'],'country_group':'korea'},
 {'slug':'manchukuo','title':'满洲国（1932–1945）','anchor':'manchukuo','aliases':'满洲国 Manchukuo Manzhouguo 大勋位兰花章 景云章 龙光章 柱国章',
  'record_files':['manchukuo_medalbook_variants.json'],'manifest_files':['manchukuo_medalbook_variants_manifest.json'],'countries':['满洲国（1932–1945）'],'country_group':'manchukuo'},
 {'slug':'mongolian_peoples_republic','title':'蒙古人民共和国（1924–1992）','anchor':'mongolian-peoples-republic','aliases':'蒙古人民共和国 Mongolia Mongolian People’s Republic MPR',
  'record_files':['mongolia_medals_org_variants.json'],'manifest_files':['mongolia_medals_org_variants_manifest.json'],'countries':['蒙古人民共和国'],'country_group':'mongolia'},
 {'slug':'mongolia','title':'蒙古国（1992–）','anchor':'mongolia','aliases':'蒙古国 Mongolia',
  'record_files':['mongolia_medals_org_variants.json'],'manifest_files':['mongolia_medals_org_variants_manifest.json'],'countries':['蒙古国（1992–）'],'country_group':'mongolia'},
 {'slug':'japan','title':'日本','anchor':'japan','aliases':'日本 日本国 日本帝国 Japan Meiji Taisho Showa Heisei Reiwa 明治 大正 昭和 平成 令和',
  'record_files':['japan_meiji.json','japan_meiji_round2.json','japan_meiji_round3.json','japan_meiji_pack4_new.json','japan_taisho_pack1.json','japan_taisho_pack4_new.json','japan_medalbook_variants.json','japan_cabinet_official_bulk_2026-09-28.json'],
  'manifest_files':['japan_meiji_manifest.json','japan_meiji_round2_manifest.json','japan_meiji_round3_manifest.json','japan_meiji_pack4_new_manifest.json','japan_taisho_pack1_manifest.json','japan_taisho_pack4_new_manifest.json','japan_medalbook_variants_manifest.json','japan_cabinet_official_bulk_2026-09-28_manifest.json'],
  'unfiltered_record_files':['japan_meiji.json','japan_meiji_round2.json','japan_meiji_round3.json','japan_meiji_pack4_new.json','japan_taisho_pack1.json','japan_taisho_pack4_new.json','japan_medalbook_variants.json','japan_cabinet_official_bulk_2026-09-28.json'],'country_group':'japan'},
 {'slug':'france_first_empire','title':'法国第一帝国（1804–1814）','anchor':'france-first-empire','aliases':'法国 第一帝国 Napoleon I 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-FIRST-EMPIRE-MODEL-GROUP'],'country_group':'france'},
 {'slug':'france_bourbon','title':'法国波旁复辟（1814–1830）','anchor':'france-bourbon','aliases':'法国 波旁复辟 Bourbon Restoration 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-BOURBON-RESTORATION-MODEL-GROUP','FRA-LEGION-RESTORATION-OFFICER-DUDEVANT','FRA-LEGION-RESTORATION-CHEVALIER-HUGO-REDUCTION'],'country_group':'france'},
 {'slug':'france_july','title':'法国七月王朝（1830–1848）','anchor':'france-july','aliases':'法国 七月王朝 July Monarchy 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-JULY-MONARCHY-MODEL-GROUP','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-1837','FRA-LEGION-JULY-OFFICER-VICTOR-HUGO-REDUCTION'],'country_group':'france'},
 {'slug':'france_second_republic','title':'法国第二共和国（1848–1852）','anchor':'france-second-republic','aliases':'法国 第二共和国 Second Republic 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-SECOND-REPUBLIC-MODEL-GROUP'],'country_group':'france'},
 {'slug':'france_fourth_fifth','title':'法国第四／第五共和国（1946–）','anchor':'france-fourth-fifth','aliases':'法国 第四共和国 第五共和国 Fourth Fifth Republic 荣誉军团 Légion d’honneur',
  'record_files':['france_legion_evolution_pack1.json','france_legion_official_batch2.json','france_official_core_2026-09-29.json'],
  'manifest_files':['france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json','france_official_core_2026-09-29_manifest.json'],
  'include_ids':['FRA-LEGION-EVOLUTION-FOURTH-FIFTH-REPUBLICS-MODEL-GROUP','FRA-LEGION-1945-GRAND-OFFICER-LECLERC-PLAQUE','FRA-LEGION-POST-1951-COMMANDER-NOHAIN','FRA-LEGION-FIFTH-REPUBLIC-OFFICER-FOUQUER-1971','FRA-LEGION-HONOUR-CURRENT-CHEVALIER-OFFICIAL','FRA-MEDAILLE-MILITAIRE-CURRENT-OFFICIAL','FRA-ORDRE-NATIONAL-MERITE-CURRENT-CHEVALIER-OFFICIAL','FRA-MEDAILLE-VICTIMES-TERRORISME-CURRENT-OFFICIAL'],'country_group':'france'},
 {'slug':'germany_1933_1945','title':'德国（1933–1945）','anchor':'germany-1933-1945','aliases':'德国 德意志国 Germany Deutsches Reich 1933 1945',
  'record_files':['germany_1933_1945_gap_round1_2026-09-26.json'],'manifest_files':['germany_1933_1945_gap_round1_2026-09-26_manifest.json'],
  'exclude_ids':['GER-1933-1945-GERMAN-OLYMPIC-CROSS-V1']},
 {'slug':'prussia_kingdom','title':'普鲁士王国（1701–1918）','anchor':'prussia-kingdom','aliases':'普鲁士 Prussia Kingdom of Prussia',
  'record_files':['prussia_kingdom.json','prussia_batch1_2026-09-26.json','prussia_batch2_2026-09-26.json'],
  'manifest_files':['prussia_kingdom_manifest.json','prussia_batch1_manifest_2026-09-26.json','prussia_batch2_manifest_2026-09-26.json']},
 {'slug':'france_third_republic','title':'法国第三共和国（1870–1940）','anchor':'france-third-republic','aliases':'法国 France Third Republic',
  'record_files':['france_third_republic.json','france_third_republic_pack1.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json','france_legion_official_batch2.json'],
  'manifest_files':['france_third_republic_manifest.json','france_third_republic_pack1_manifest.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json','france_legion_official_batch2_manifest.json'],
  'exclude_ids':['FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01'],
  'file_include_ids':{'france_legion_evolution_pack1.json':['FRA-LEGION-EVOLUTION-THIRD-REPUBLIC-MODEL-GROUP'],'france_legion_official_batch2.json':['FRA-LEGION-THIRD-REPUBLIC-CHEVALIER-RENDU']},'country_group':'france'},
 {'slug':'france_second_empire','title':'法国第二帝国（1852–1870）','anchor':'france-second-empire','aliases':'法国 France Second Empire Napoleon III',
  'record_files':['france_second_empire_pack1_2026-09-26.json','france_commons_pack2_2026-09-26.json','france_legion_evolution_pack1.json'],
  'manifest_files':['france_second_empire_pack1_manifest_2026-09-26.json','france_commons_pack2_2026-09-26_manifest.json','france_legion_evolution_pack1_manifest.json'],
  'include_ids':['FRA-SE-ITALY-1859-PRESENTATION-01','FRA-SE-MEXICO-1863-01','FRA-LEGION-HONOUR-SECOND-EMPIRE-CHEVALIER-1852-1870-01','FRA-LEGION-EVOLUTION-SECOND-EMPIRE-MODEL-GROUP'],'country_group':'france'},
 {'slug':'bavaria_kingdom','title':'巴伐利亚王国（1806–1918）','anchor':'bavaria-kingdom','aliases':'巴伐利亚 Bavaria Kingdom of Bavaria',
  'record_files':['bavaria_kingdom_pack1.json','bavaria_kingdom_pack2.json'],
  'manifest_files':['bavaria_kingdom_pack1_manifest.json','bavaria_kingdom_pack2_manifest.json']},
]
minimum_specs=read('volumes/minimum_east_south_africa_20260929_specs.json')
volume_specs.extend(minimum_specs)
france_completion_specs=ROOT/'data/volumes/france_completion_20260929_specs.json'
if france_completion_specs.exists():
    volume_specs.extend(json.loads(france_completion_specs.read_text(encoding='utf-8')))
german_completion_specs=ROOT/'data/volumes/german_completion_20260929_specs.json'
if german_completion_specs.exists():
    volume_specs.extend(json.loads(german_completion_specs.read_text(encoding='utf-8')))
user_soviet_file=ROOT/'data/volumes/user_soviet_20261003.json'
if user_soviet_file.exists():
    user_rows=json.loads(user_soviet_file.read_text('utf-8'))['records']
    for spec in volume_specs:
        if spec['anchor']=='soviet-union':
            spec['record_files'].append('user_soviet_20261003.json')
            spec['manifest_files'].append('user_soviet_20261003_manifest.json')
            spec.setdefault('file_include_ids',{})['user_soviet_20261003.json']=[r['id'] for r in user_rows if r['family'].startswith('USSR-')]
            spec.setdefault('unfiltered_record_files',[]).append('user_soviet_20261003.json')
    volume_specs.append(dict(slug='rsfsr_user_references',title='俄罗斯苏维埃联邦社会主义共和国·红旗勋章前身',anchor='rsfsr-awards',aliases='苏俄 RSFSR РСФСР 红旗勋章',country_group='russia',record_files=['user_soviet_20261003.json'],manifest_files=['user_soviet_20261003_manifest.json'],unfiltered_record_files=['user_soviet_20261003.json'],file_include_ids={'user_soviet_20261003.json':[r['id'] for r in user_rows if r['family'].startswith('RSFSR-')]}))
france_identify_integration=ROOT/'data/volumes/france_identify_20260930_integration.json'
if france_identify_integration.exists():
    integration=json.loads(france_identify_integration.read_text(encoding='utf-8'))
    volume_specs.extend(integration['new_specs'])
    for spec in volume_specs:
        ids=integration['volume_rows'].get(spec['anchor'])
        if ids:
            spec['record_files'].append('france_identify_20260930.json')
            spec['manifest_files'].append('france_identify_20260930_manifest.json')
            spec.setdefault('unfiltered_record_files',[]).append('france_identify_20260930.json')
            spec.setdefault('file_include_ids',{})['france_identify_20260930.json']=ids
user_other_integration=ROOT/'data/volumes/user_other_20261003_integration.json'
if user_other_integration.exists():
    integration=json.loads(user_other_integration.read_text('utf-8'))
    for spec in volume_specs:
        ids=integration['volume_rows'].get(spec['anchor'])
        if ids:
            spec['record_files'].append('user_other_20261003.json')
            spec['manifest_files'].append('user_other_20261003_manifest.json')
            spec.setdefault('unfiltered_record_files',[]).append('user_other_20261003.json')
            spec.setdefault('file_include_ids',{})['user_other_20261003.json']=ids
            if spec.get('include_ids'):spec['include_ids'].extend(ids)
for batch_name in ('source_batch_20261005','austria_pending_20261005','austria_republic_20261005','source_stage_v017_20261005','darabanth_20261005'):
    batch_integration=ROOT/f'data/volumes/{batch_name}_integration.json'
    if not batch_integration.exists():continue
    integration=json.loads(batch_integration.read_text('utf-8'))
    if integration['volume_rows'].get('cuba') and not any(s['anchor']=='cuba' for s in volume_specs):
        volume_specs.append(dict(slug='cuba',title='古巴',anchor='cuba',aliases='古巴 Cuba Solidaridad',country_group='cuba',record_files=[],manifest_files=[]))
    if integration['volume_rows'].get('france-kingdom'):
        volume_specs.append(dict(slug='france-kingdom',title='法国王国·旧制度时期',anchor='france-kingdom',aliases='法国王国 France Kingdom Ancien Régime 圣灵 圣路易',country_group='france',record_files=[],manifest_files=[]))
    if integration['volume_rows'].get('austria-carinthia'):
        volume_specs.append(dict(slug='austria-carinthia',title='奥地利·克恩顿州',anchor='austria-carinthia',aliases='克恩顿 Kärnten Carinthia',country_group='austria',record_files=[],manifest_files=[]))
    for spec in volume_specs:
        ids=integration['volume_rows'].get(spec['anchor'])
        if ids:
            spec['record_files'].append(batch_name+'.json')
            spec['manifest_files'].append(batch_name+'_manifest.json')
            spec.setdefault('unfiltered_record_files',[]).append(batch_name+'.json')
            spec.setdefault('file_include_ids',{})[batch_name+'.json']=ids
            if spec.get('include_ids'):spec['include_ids'].extend(ids)
volumes=[]
view_paths={}
for spec in volume_specs:
    slug,title,anchor,aliases=(spec[k] for k in ('slug','title','anchor','aliases'))
    data_paths=[ROOT/'data/volumes'/name for name in spec['record_files'] if (ROOT/'data/volumes'/name).is_file()]
    manifest_paths=[ROOT/'data/volumes'/name for name in spec['manifest_files'] if (ROOT/'data/volumes'/name).is_file()]
    if not data_paths or not manifest_paths:continue
    records=[]
    for data_path in data_paths:
        loaded=json.loads(data_path.read_text(encoding='utf-8'))['records']
        if spec.get('countries') and data_path.name not in spec.get('unfiltered_record_files',[]):
            loaded=[r for r in loaded if r.get('country_zh') in spec['countries']]
        if spec.get('awarding_authorities') and data_path.name not in spec.get('unfiltered_record_files',[]):
            loaded=[r for r in loaded if r.get('awarding_authority') in spec['awarding_authorities']]
        if data_path.name in spec.get('file_include_ids',{}):
            allowed=set(spec['file_include_ids'][data_path.name])
            loaded=[r for r in loaded if r['id'] in allowed]
        records.extend(loaded)
    if spec.get('include_ids'):
        records=[r for r in records if r['id'] in spec['include_ids']]
    if spec.get('exclude_ids'):
        records=[r for r in records if r['id'] not in spec['exclude_ids']]
    superseded={r['supersedes_id'] for r in records if r.get('supersedes_id')}
    records=[r for r in records if r['id'] not in superseded]
    metadata=[json.loads(path.read_text(encoding='utf-8')) for path in manifest_paths]
    mapping={x['view_key']:x['local_path'] for meta in metadata for x in meta.get('images',[])}
    pictured=[];pending=[]
    for r in records:
        if not r.get('views'):pending.append(r);continue
        for view in r['views']:
            key=view['key']
            if key not in mapping:raise ValueError(f'Missing image mapping: {slug} {r["id"]} {key}')
            if key in view_paths:raise ValueError(f'Duplicate view key: {key}')
            path=ROOT/mapping[key]
            if not path.is_file():raise FileNotFoundError(path)
            with Image.open(path) as im:im.verify()
            view_paths[key]=mapping[key]
        pictured.append(r)
    if not pictured and not pending:
        continue
    country_group=spec.get('country_group') or ('japan' if slug.startswith('japan_') else slug)
    volumes.append({'slug':slug,'title':title,'anchor':anchor,'aliases':aliases,'country':country_group,'records':pictured,'pending':pending,
                    'candidates':[x for meta in metadata for x in meta.get('unpictured_candidates',[])]})
globally_superseded={r['supersedes_id'] for v in volumes for r in v['records'] if r.get('supersedes_id')}
for v in volumes:
    v['records']=[r for r in v['records'] if r['id'] not in globally_superseded]
    v['pending']=[r for r in v['pending'] if r['id'] not in globally_superseded]
if len({r['id'] for vol in volumes for r in vol['records']+vol['pending']})!=sum(len(v['records']+v['pending']) for v in volumes):
    raise ValueError('Duplicate volume record ID')
image_keys={v['key'] for r in catalogue+related for v in r['views']}
assert len({r['id'] for r in catalogue+related})==len(catalogue+related)
for key in image_keys:
    img=manifest[key]
    path=ROOT/'assets/images/ottoman'/Path(img['path']).name
    assert path.is_file(),path
    with Image.open(path) as im: im.verify()
for key,img in manifest.items():
    if key in image_keys:view_paths[key]='assets/images/ottoman/'+Path(img['path']).name

# Adjacent school, association, qualification and unofficial pieces are useful
# references, but are deliberately kept out of the official family count.
related_volume_specs=[
    ('darabanth_related_20261005.json','darabanth_related_20261005_manifest.json'),
    ('austria_republic_related_20261005.json','austria_republic_related_20261005_manifest.json'),
    ('austria_pending_related_20261005.json','austria_pending_related_20261005_manifest.json'),
    ('german_completion_related_20260929.json','german_completion_related_20260929_manifest.json'),
    ('ottoman_kuenker299_related.json','ottoman_kuenker299_related_manifest.json'),
    ('ottoman_cng_triple_alliance_related.json','ottoman_cng_triple_alliance_related_manifest.json'),
    ('ottoman_cgb_related.json','ottoman_cgb_related_manifest.json'),
    ('ottoman_milli_saraylar_related.json','ottoman_milli_saraylar_related_manifest.json'),
]
for related_name,related_manifest_name in related_volume_specs:
    related_volume_path=ROOT/'data/volumes'/related_name
    related_manifest_path=ROOT/'data/volumes'/related_manifest_name
    if not related_volume_path.is_file() or not related_manifest_path.is_file():continue
    related_volume=json.loads(related_volume_path.read_text(encoding='utf-8'))['records']
    related_metadata=json.loads(related_manifest_path.read_text(encoding='utf-8'))
    related_mapping={x['view_key']:x['local_path'] for x in related_metadata.get('images',[])}
    for record in related_volume:
        for view in record.get('views',[]):
            key=view['key']
            if key not in related_mapping:raise ValueError(f'Missing related image mapping: {record["id"]} {key}')
            if key in view_paths:raise ValueError(f'Duplicate related view key: {key}')
            path=ROOT/related_mapping[key]
            if not path.is_file():raise FileNotFoundError(path)
            with Image.open(path) as im:im.verify()
            view_paths[key]=related_mapping[key]
    related.extend(related_volume)

# Ottoman records harvested in later source batches belong to the same historical
# state and therefore join the main Ottoman section instead of becoming a
# user-visible "supplement volume".
ottoman_extra=next((v for v in volumes if v['slug']=='ottoman_extra'),None)
if ottoman_extra:
    catalogue.extend(ottoman_extra['records'])
    volumes=[v for v in volumes if v['slug']!='ottoman_extra']
families={r['family'] for r in catalogue}
all_record_ids=[r['id'] for r in catalogue+related]+[r['id'] for v in volumes for r in v['records']]
if len(set(all_record_ids))!=len(all_record_ids):
    raise ValueError('Duplicate record ID across country sections')

style=(ROOT/'assets/site.css').read_text(encoding='utf-8-sig')
if '/* WORLD_MEDALS_V2 */' not in style:
 style+='''
/* WORLD_MEDALS_V2 */
html{scroll-behavior:smooth}body{--accent:#214a45}
.layout{grid-template-columns:300px minmax(0,1fr)}nav{max-height:calc(100vh - 10px);font-size:13px}
nav a{display:block;color:#244d49;text-decoration:none;padding:3px 8px;border-radius:3px}
nav a:hover,nav a:focus{background:#eaf0ed;text-decoration:underline}
#showAll{width:100%;margin:0 0 8px;padding:7px 9px;border:1px solid var(--line);border-radius:4px;background:#fff;color:#244d49;text-align:left;cursor:pointer}#showAll:hover,#showAll:focus{background:#eaf0ed}
nav details{padding-left:9px}nav summary{padding:3px 0}nav .count{font-size:11px;color:#687a75;display:block;padding-left:8px}
nav .queued{color:#687a75}nav .rulers{margin-left:11px;border-left:1px solid #dce5e1}
.period-section{scroll-margin-top:18px;margin-bottom:38px}.period-section h2{font-size:20px;margin:22px 20px 4px}
.period-section .years{margin:0 20px 12px;color:#61736e}.section-note{margin:12px 20px}
tr{scroll-margin-top:15px}tr:target{outline:3px solid #bc9162;outline-offset:-3px}
#searchResults{margin:4px 0 0;max-height:220px;overflow:auto;border:1px solid var(--line);max-width:670px;background:white}
#searchResults[hidden]{display:none}#searchResults a{display:block;padding:6px 10px;color:#214a45;text-decoration:none;border-bottom:1px solid var(--line)}
#searchResults a:hover,#searchResults a:focus{background:#edf4f0}
#queue-status{padding:18px 20px;margin:20px;border:1px solid var(--line);background:var(--soft);scroll-margin-top:10px}
#queue-status[hidden]{display:none}.noimage{padding:4px 0;list-style:none}.noimage li{margin:5px 0}
.gallery-meta{font-size:12px;color:#60716e;margin:0 20px 10px}
.family-heading td{padding:0;background:#edf3f0;border-top:2px solid #c9d8d2}.family-toggle{width:100%;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 12px;border:0;background:transparent;color:#183f3a;text-align:left;font:inherit;cursor:pointer}.family-toggle:hover,.family-toggle:focus{background:#e2ece7}.family-toggle .family-name{font-weight:700}.family-toggle .family-original{font-weight:400;color:#60716e;margin-left:8px}.family-toggle .family-count{font-size:12px;color:#60716e;white-space:nowrap}.family-toggle .family-arrow{display:inline-block;width:1.1em}.family-member[hidden]{display:none}.family-member td:first-child{padding-left:22px}
@media(max-width:850px){.layout{display:block}nav{max-height:300px}.period-section h2{margin-left:9px}}
'''
(ROOT/'assets/site.css').write_text(style,encoding='utf-8')

def year(r):
    m=re.search(r'\d{4}',r['date'])
    return int(m.group()) if m else 9999
search_index=[]
def add_search(label,target,extra='',context=''):
    search_index.append({'label':label,'target':target,'text':label+' '+extra,'context':context})
def queued_link(name):
    add_search(name,'queue-status','queued '+('Prussia' if '普鲁士' in name else '')+' '+('Bavaria' if '巴伐利亚' in name else ''))
    return '<a class="queued" href="#queue-status" data-queued="'+escape(name,quote=True)+'">'+escape(name)+' · 待收录</a>'

node_anchor_map={
 '日本':'japan',
 '清朝（1644–1912）':'qing-empire','中华人民共和国（1949–）':'peoples-republic-china',
 '暹罗／泰国':'thailand','越南':'socialist-vietnam','印度尼西亚':'indonesia',
 '埃及':'egypt','苏丹':'sudan','波斯／伊朗':'iran','土耳其共和国':'turkey',
 '叙利亚':'syria','阿曼':'oman','阿富汗':'afghanistan','巴基斯坦':'pakistan',
 '约旦':'jordan',
 '沙特阿拉伯':'saudi-arabia',
 '卡塔尔':'qatar',
 '科威特':'kuwait',
 '巴林':'bahrain',
 '阿拉伯联合酋长国':'united-arab-emirates',
 '黎巴嫩':'lebanon',
 '以色列':'israel',
 '印度':'india-republic','英属印度':'british-india','各土邦':'bahawalpur','孟加拉国':'bangladesh',
 '尼泊尔':'nepal','不丹':'bhutan','斯里兰卡':'sri-lanka',
 '摩洛哥':'morocco','阿尔及利亚':'algeria','阿塞拜疆':'azerbaijan','亚美尼亚':'armenia',
 '格鲁吉亚':'georgia',
 '香港':'hong-kong','塞浦路斯':'cyprus','马尔代夫':'maldives',
 '哈萨克斯坦':'kazakhstan','吉尔吉斯斯坦':'kyrgyzstan','塔吉克斯坦':'tajikistan','塔吉克斯坦共和国':'tajikistan','土库曼斯坦':'turkmenistan','柬埔寨':'cambodia-kingdom','老挝':'laos-kingdom','文莱':'brunei','新加坡':'singapore','马来西亚联邦':'malaysia-federal','沙巴州':'sabah','砂拉越州':'sarawak','柔佛苏丹国':'johor','吉打苏丹国':'kedah','吉兰丹苏丹国':'kelantan','彭亨苏丹国':'pahang','霹雳苏丹国':'perak','乌兹别克斯坦':'uzbekistan','也门':'yemen',
 '英国':'uk','英国／大英帝国':'uk','大英帝国':'uk',
 '美国':'united-states','加拿大':'canada','新西兰':'new-zealand','伊拉克':'iraq-kingdom',
 '俄罗斯帝国':'russian-empire','苏联':'soviet-union','俄罗斯联邦':'russian-federation','瑞典':'sweden','丹麦':'denmark','冰岛':'iceland','挪威':'norway','荷兰':'netherlands','比利时':'belgium','卢森堡':'luxembourg','爱尔兰':'ireland',
 '意大利诸政权':'savoy-italy','匈牙利':'hungary',
 '芬兰':'finland',
 '西班牙王国':'spain-kingdom','西班牙第二共和国':'spain-republic',
 '普鲁士王国':'prussia-kingdom','普鲁士王国（1701–1918）':'prussia-kingdom',
 '普鲁士王国（1871–1918）':'prussia-kingdom','第一帝国（1804–1814）':'france-first-empire',
 '波旁复辟（1814–1830）':'france-bourbon','七月王朝（1830–1848）':'france-july',
 '第二共和国（1848–1852）':'france-second-republic','第二帝国（1852–1870）':'france-second-empire',
 '第三共和国（1870–1940）':'france-third-republic','第四／第五共和国（1946–）':'france-fourth-fifth',
 '巴伐利亚王国':'bavaria-kingdom',
 '德国（1933–1945）':'germany-1933-1945',
 '中华民国（1912–）':'republic-of-china','大韩帝国（1897–1910）':'korean-empire',
 '满洲国（1932–1945）':'manchukuo',
 '韩国':'south-korea','朝鲜':'north-korea',
}
for spec in minimum_specs:
    for country in spec.get('countries',[]):
        node_anchor_map[country]=spec['anchor']

def render_node(node,level=0):
    name=node['name']; children=node.get('periods',[])
    if name=='菲律宾' and any(v['anchor']=='philippines-republic' for v in volumes):
        group=[v for v in volumes if v['country']=='philippines']
        count=f'{len({r["family"] for v in group for r in v["records"]})}独立章种 · {sum(len(v["records"]) for v in group)}等级／版型 · {sum(len(r["views"]) for v in group for r in v["records"])}图'
        add_search(name,'philippines-republic','Philippines Pilipinas 菲律宾共和国 菲律宾群岛政府')
        return '<a href="#philippines-republic" data-country-filter="philippines">菲律宾</a><span class="count">'+count+'</span>'
    if name=='缅甸' and any(v['anchor']=='myanmar-modern' for v in volumes):
        group=[v for v in volumes if v['country']=='myanmar']
        count=f'{len({r["family"] for v in group for r in v["records"]})}独立章种 · {sum(len(v["records"]) for v in group)}等级／版型 · {sum(len(r["views"]) for v in group for r in v["records"])}图'
        add_search(name,'myanmar-modern','Myanmar Burma 缅甸 贡榜王朝')
        return '<a href="#myanmar-modern" data-country-filter="myanmar">缅甸</a><span class="count">'+count+'</span>'
    if name in node_anchor_map:
        anchor=node_anchor_map[name]
        volume=next((v for v in volumes if v['anchor']==anchor),None)
        if volume:
            count=f'{len({r["family"] for r in volume["records"]})}独立章种 · {len(volume["records"])}等级／版型 · {sum(len(r["views"]) for r in volume["records"])}图'
            add_search(name,anchor,volume['aliases'])
            return '<a href="#'+anchor+'" data-section-filter="'+anchor+'">'+escape(name)+'</a><span class="count">'+count+'</span>'
    if node.get('target')=='ottoman':
        count=f'{len(families)}章种 · {len(catalogue)}版型 · {len({v["key"] for r in catalogue for v in r["views"]})}图'
        add_search(name,'ottoman','Ottoman Empire Osmanlı')
        return '<a href="#ottoman" data-country-filter="ottoman">'+escape(name)+'</a><span class="count">'+count+'</span>'
    if children:
        nested=''.join(render_node(x,level+1) for x in children)
        if name=='中国' and any(v['anchor']=='republic-of-china' for v in volumes):
            add_search(name,'republic-of-china','中国 中华民国 China Republic of China')
            return '<details><summary>'+escape(name)+'</summary><a href="#republic-of-china" data-country-filter="china">中国</a>'+nested+'</details>'
        if name=='朝鲜半岛' and any(v['anchor']=='korean-empire' for v in volumes):
            add_search(name,'korean-empire','朝鲜半岛 Korea 韩国 朝鲜 大韩帝国')
            return '<details open><summary>'+escape(name)+'</summary><a href="#korean-empire" data-country-filter="korea">朝鲜半岛</a>'+nested+'</details>'
        if name=='印度次大陆' and any(v['anchor']=='india-republic' for v in volumes):
            add_search(name,'india-republic','印度次大陆 India Indian princely states Azad Hind Bahawalpur Patiala')
            return '<details open><summary>'+escape(name)+'</summary><a href="#india-republic" data-country-filter="india">印度次大陆</a>'+nested+'</details>'
        if name=='法国' and any(v['anchor']=='france-third-republic' for v in volumes):
            add_search(name,'france-third-republic','France 法国')
            return '<details open><summary>'+escape(name)+'</summary><a href="#france-first-empire" data-country-filter="france">法国</a>'+nested+'</details>'
        if name=='德国／德意志地区' and any(v['anchor']=='prussia-kingdom' for v in volumes):
            add_search(name,'prussia-kingdom','Germany Prussia')
            return '<details><summary>'+escape(name)+'</summary><a href="#prussia-kingdom" data-country-filter="prussia_kingdom">普鲁士王国</a>'+nested+'</details>'
        if name=='俄罗斯帝国／苏联／俄罗斯联邦' and any(v['anchor']=='russian-empire' for v in volumes):
            add_search(name,'russian-empire','Russia USSR Soviet Imperial Russian Federation')
            return '<details open><summary>'+escape(name)+'</summary><a href="#russian-empire" data-country-filter="russia">俄罗斯诸时期</a>'+nested+'</details>'
        if name=='西班牙' and any(v['anchor']=='spain-kingdom' for v in volumes):
            add_search(name,'spain-kingdom','Spain España 西班牙')
            return '<details open><summary>'+escape(name)+'</summary><a href="#spain-kingdom" data-country-filter="spain">西班牙</a>'+nested+'</details>'
        return '<details><summary>'+escape(name)+'</summary>'+queued_link(name)+nested+'</details>'
    return queued_link(name)

nav=['<button type="button" id="showAll">显示全部国家</button><details open><summary>世界</summary>']
for c in queue['continents']:
    nav.append('<details'+(' open' if c['name']=='亚洲' else '')+'><summary>'+escape(c['name'])+'</summary>')
    for region in c['regions']:
        nav.append('<details'+(' open' if region['name']=='西亚' else '')+'><summary>'+escape(region['name'])+'</summary>')
        for node in region['systems']:nav.append(render_node(node))
        nav.append('</details>')
    nav.append('</details>')
nav.append('<details><summary>国际授予机构</summary>')
for item in queue['international']:nav.append(queued_link(item['name']))
nav.append('</details></details>')

def row_html(r,family_key=None,collapsed=False):
    pics=[]
    for v in r['views']:
        url=view_paths[v['key']]
        alt=r['name']+' '+r['variant']+' '+v['label']
        eligibility=' data-publication-eligible="false"' if v.get('publication_eligible') is False else ''
        pics.append('<figure class="imagebox"><img loading="lazy"'+eligibility+' src="'+escape(url,quote=True)+'" alt="'+escape(alt,quote=True)+'"><figcaption>'+escape(v['label'])+'</figcaption></figure>')
    name=' '.join([r['name'],r['original'],r['date'],r['variant']])
    volume=next((volume for volume in volumes if r in volume['records']),None)
    alias=(r.get('country_zh') or volume['aliases']) if volume else (r.get('country_zh') or 'Ottoman Empire Osmanlı')
    context=volume['title'] if volume else (r.get('country_zh') or '奥斯曼帝国')
    add_search(name,r['id'],alias,context)
    family_attrs=(' class="family-member" data-family-key="'+escape(family_key,quote=True)+'"'+(' hidden' if collapsed else '')) if family_key else ''
    family_attrs+=' data-award-family="'+escape(r['family'],quote=True)+'"'
    if r.get('publication_eligible') is False:
        family_attrs+=' data-publication-eligible="false"'
    return '<tr id="'+escape(r['id'],quote=True)+'"'+family_attrs+' data-source-ids="'+escape(','.join(r['source_ids']),quote=True)+'"><td class="name"><strong>'+escape(r['name'])+'</strong><span class="original">'+escape(r['original'])+'</span><span class="date">'+escape(r['date'])+'</span></td><td class="meta">'+escape(r['variant'])+'</td><td class="pictures"><div class="imagegrid'+(' pair' if len(pics)>1 else '')+'">'+''.join(pics)+'</div></td></tr>'
def table(records):
    grouped={}
    for record in records:grouped.setdefault(record['family'],[]).append(record)
    rows=[]
    for family_records in grouped.values():
        if len(family_records)==1:
            rows.append(row_html(family_records[0]))
            continue
        key='family-'+family_records[0]['id']
        first=family_records[0]
        original=first.get('original','')
        count=str(len(family_records))+'版型 · '+str(sum(len(r['views']) for r in family_records))+'图'
        rows.append('<tr class="family-heading"><td colspan="3"><button type="button" class="family-toggle" data-family-toggle="'+escape(key,quote=True)+'" aria-expanded="false"><span><span class="family-arrow">▶</span><span class="family-name">'+escape(first['name'])+'</span><span class="family-original">'+escape(original)+'</span></span><span class="family-count">'+count+'</span></button></td></tr>')
        rows.extend(row_html(r,key,True) for r in family_records)
    return '<div class="scroller"><table><colgroup><col class="namecol"><col class="kindcol"><col class="imagecol"></colgroup><thead><tr><th>名称＋日期</th><th>等级／版别</th><th>完整图样</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

sections=['<section class="period-section" data-country="ottoman" id="ottoman"><h2>奥斯曼帝国（约1299–1922）</h2><p class="section-note">'+str(len(families))+'独立章种 · '+str(len(catalogue))+'等级／版型 · '+str(len({v['key'] for r in catalogue for v in r['views']}))+'张本地图</p>'+table(sorted(catalogue,key=lambda r:(year(r),r['family'],r['id'])))+'</section>']
for volume in volumes:
    records=sorted(volume['records'],key=lambda r:(year(r),r['family'],r['id']))
    add_search(volume['title'],volume['anchor'],volume['aliases'])
    count=f'{len({r["family"] for r in records})}独立章种 · {len(records)}等级／版型 · {sum(len(r["views"]) for r in records)}张本地图'
    sections.append('<section class="period-section" data-country="'+escape(volume['country'],quote=True)+'" id="'+volume['anchor']+'"><h2>'+escape(volume['title'])+'</h2><p class="section-note">'+count+'</p>'+table(records)+'</section>')
    if volume['pending'] or volume['candidates']:
        pending_id=volume['anchor']+'-unpictured'
        items=[r['name']+' · '+r['date'] for r in volume['pending']+volume['candidates']]
        for item in items:add_search(item,pending_id,volume['aliases'])
        pending_lines=''.join('<li data-id="'+escape(r.get('id',r.get('family','')),quote=True)+'" data-family="'+escape(r.get('family',''),quote=True)+'" data-name="'+escape(r['name'],quote=True)+'" data-original="'+escape(r.get('original',''),quote=True)+'" data-date="'+escape(r['date'],quote=True)+'" data-variant="'+escape(r.get('variant','有记载未配图'),quote=True)+'" data-source-ids="'+escape(','.join(r.get('source_ids',[])),quote=True)+'">'+escape(label)+'</li>' for r,label in zip(volume['pending']+volume['candidates'],items))
        sections.append('<section class="period-section" data-country="'+escape(volume['country'],quote=True)+'" id="'+pending_id+'"><h2>'+escape(volume['title']+' · 有记载，暂缺完整图片')+'</h2><ul class="noimage">'+pending_lines+'</ul></section>')
german_related=[r for r in related if r.get('country_group')=='germany']
other_related=[r for r in related if r.get('country_group')!='germany']
if german_related:
    sections.append('<section class="period-section" data-country="germany" id="germany-related"><h2>德国 · 团体荣誉与资格徽章（附编）</h2><p class="gallery-meta">有记载，暂缺完整图片；不计入正式勋奖章章种数。</p>'+table(sorted(german_related,key=year))+'</section>')
if other_related:
    sections.append('<section class="period-section" id="related"><h2>相关奖励与纪念佩饰</h2><p class="gallery-meta">此附编不计入正式勋奖章章种数；复制品已明示。</p>'+table(sorted(other_related,key=year))+'</section>')
if unpictured:
    lines=[]
    for item in unpictured:
        label=item['name']+' · '+item['date']+' · '+item['known_grade']
        add_search(label,'unpictured',item['original'])
        lines.append('<li>'+escape(label)+'</li>')
    sections.append('<section class="period-section" id="unpictured"><h2>有记载，暂缺完整图片</h2><ul class="noimage">'+''.join(lines)+'</ul></section>')
for system in ('奥斯曼帝国 Ottoman Empire','亚洲 西亚'):
    add_search(system,'ottoman')

script='''const index=window.WORLD_MEDALS_SEARCH;
const input=document.getElementById('search'), results=document.getElementById('searchResults');
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
const gallerySections=[...document.querySelectorAll('main > section.period-section')];
function showAllSections(){for(const section of gallerySections)section.hidden=false;document.getElementById('queue-status').hidden=true;}
function showCountry(country){for(const section of gallerySections)section.hidden=section.dataset.country!==country;document.getElementById('queue-status').hidden=true;}
function setFamily(key,open){const button=document.querySelector('[data-family-toggle="'+CSS.escape(key)+'"]');if(!button)return;button.setAttribute('aria-expanded',String(open));const arrow=button.querySelector('.family-arrow');if(arrow)arrow.textContent=open?'▼':'▶';for(const row of document.querySelectorAll('[data-family-key="'+CSS.escape(key)+'"]'))row.hidden=!open;}
function revealFamily(node){const row=node&&node.closest('tr.family-member');if(row)setFamily(row.dataset.familyKey,true);}
function showTarget(target){const node=document.getElementById(target);const section=node&&node.closest('section.period-section');if(!section)return;revealFamily(node);for(const item of gallerySections)item.hidden=item!==section;document.getElementById('queue-status').hidden=true;}
function showResults(){const q=norm(input.value.trim());results.innerHTML='';results.hidden=!q;if(!q)return;
 let found=index.filter(x=>norm(x.text).includes(q)).sort((a,b)=>(a.target==='queue-status')-(b.target==='queue-status'));
 const count=document.createElement('p');count.className='search-count';count.textContent='共 '+found.length+' 项';results.append(count);
 for(const x of found){const a=document.createElement('a');a.href='#'+x.target;a.textContent=(x.context?'【'+x.context+'】':'')+x.label;a.addEventListener('click',()=>{results.hidden=true;input.value='';if(x.target==='queue-status'){for(const section of gallerySections)section.hidden=true;document.getElementById('queueName').textContent=x.label;document.getElementById('queue-status').hidden=false}else showTarget(x.target)});results.append(a)}
 if(!found.length){const p=document.createElement('p');p.textContent='未找到已登记项目';results.append(p)} }
for(const eventName of ['input','search','change','compositionend','keyup'])input.addEventListener(eventName,showResults);
document.getElementById('showAll').addEventListener('click',showAllSections);
for(const button of document.querySelectorAll('[data-family-toggle]'))button.addEventListener('click',()=>setFamily(button.dataset.familyToggle,button.getAttribute('aria-expanded')!=='true'));
for(const a of document.querySelectorAll('a[data-country-filter]'))a.addEventListener('click',()=>showCountry(a.dataset.countryFilter));
for(const a of document.querySelectorAll('a[data-section-filter]'))a.addEventListener('click',()=>showTarget(a.dataset.sectionFilter));
for(const a of document.querySelectorAll('a[data-queued]'))a.addEventListener('click',()=>{for(const section of gallerySections)section.hidden=true;document.getElementById('queueName').textContent=a.dataset.queued;document.getElementById('queue-status').hidden=false});
const viewer=document.getElementById('viewer');document.getElementById('closeViewer').onclick=()=>viewer.close();
for(const im of document.querySelectorAll('td.pictures img'))im.addEventListener('click',()=>{document.getElementById('viewerTitle').textContent=im.alt;document.getElementById('viewerImage').src=im.src;viewer.showModal()});
viewer.addEventListener('click',e=>{if(e.target===viewer)viewer.close()});
if(globalThis.location&&location.hash){const node=document.getElementById(location.hash.slice(1));revealFamily(node)}
if(globalThis.addEventListener)addEventListener('hashchange',()=>{const node=document.getElementById(location.hash.slice(1));revealFamily(node)});
'''
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Cache-Control" content="no-store"><title>全球勋章、奖章与官方奖励图鉴</title><link rel="stylesheet" href="assets/site.css"></head><body>'''
all_records=catalogue+[r for v in volumes for r in v['records']]
all_family_count=len({r['family'] for r in all_records})
html+='<header><h1>全球勋章、奖章与官方奖励图鉴</h1><p>'+str(all_family_count)+'独立章种 · '+str(len(all_records))+'等级／版型</p><label for="search">检索</label> <input id="search" type="search" placeholder="名称、原名、年代、国家；支持单字" autocomplete="off"><div id="searchResults" hidden></div><p class="small">点击国家或时期后仅显示该栏目；同章种多版型可折叠展开；点击图片查看完整原图。</p></header>'
html+='<div class="layout"><nav aria-label="全球目录">'+''.join(nav)+'</nav><main>'+''.join(sections)+'<section id="queue-status" hidden><h2 id="queueName">待收录</h2><p>该范围尚未开始实物收录。此节点保留在全球工作目录中。</p></section></main></div>'
html+='<dialog id="viewer"><div class="dialogtop"><span id="viewerTitle"></span><button type="button" id="closeViewer">关闭</button></div><img id="viewerImage" alt="完整原图"></dialog>'
html+='<script>window.WORLD_MEDALS_SEARCH='+json.dumps(search_index,ensure_ascii=False).replace('</','<\\/')+';</script><script>'+script+'</script></body></html>'
(ROOT/'index.html').write_text(html,encoding='utf-8')
print('index',len(all_records),'main rows',all_family_count,'main families',len(related),'related rows',len(view_paths),'local files')
