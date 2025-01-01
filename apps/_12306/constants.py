# 城市与编码映射关系
SITE_MAP = {'北京北': 'VAP', '北京东': 'BOP', '北京': 'BJP', '北京南': 'VNP', '北京西': 'BXP', '广州南': 'IZQ', '重庆北': 'CUW',
            '重庆': 'CQW', '重庆南': 'CRW', '广州东': 'GGQ', '上海': 'SHH', '上海南': 'SNH', '上海虹桥': 'AOH', '上海西': 'SXH',
            '天津北': 'TBP', '天津': 'TJP', '天津南': 'TIP', '天津西': 'TXP', '长春': 'CCT', '长春南': 'CET', '长春西': 'CRT',
            '成都东': 'ICW', '成都南': 'CNW', '成都': 'CDW', '长沙': 'CSQ', '长沙南': 'CWQ', '福州': 'FZS', '福州南': 'FYS',
            '贵阳': 'GIW', '广州': 'GZQ', '广州西': 'GXQ', '哈尔滨': 'HBB', '哈尔滨东': 'VBB', '哈尔滨西': 'VAB', '合肥': 'HFH',
            '呼和浩特东': 'NDC', '呼和浩特': 'HHC', '海口东': 'HMQ', '海口': 'VUQ', '杭州东': 'HGH', '杭州': 'HZH', '杭州南': 'XHH',
            '济南': 'JNK', '济南东': 'JAK', '济南西': 'JGK', '昆明': 'KMM', '昆明西': 'KXM', '拉萨': 'LSO', '兰州东': 'LVJ',
            '兰州': 'LZJ', '兰州西': 'LAJ', '南昌': 'NCG', '南京': 'NJH', '南京南': 'NKH', '南宁': 'NNZ', '石家庄北': 'VVP',
            '石家庄': 'SJP', '沈阳': 'SYT', '沈阳北': 'SBT', '沈阳东': 'SDT', '太原北': 'TBV', '太原东': 'TDV', '太原': 'TYV',
            '武汉': 'WHN', '王家营西': 'KNM', '乌鲁木齐南': 'WMR', '西安北': 'EAY', '西安': 'XAY', '西安南': 'CAY', '西宁西': 'XXO',
            '银川': 'YIJ', '郑州': 'ZZF', '阿尔山': 'ART', '安康': 'AKY', '阿克苏': 'ASR', '阿里河': 'AHX', '阿拉山口': 'AKR',
            '安平': 'APT', '安庆': 'AQH', '安顺': 'ASW', '鞍山': 'AST', '安阳': 'AYF', '北安': 'BAB', '蚌埠': 'BBH', '白城': 'BCT',
            '北海': 'BHZ', '白河': 'BEL', '白涧': 'BAP', '宝鸡': 'BJY', '滨江': 'BJB', '博克图': 'BKX', '百色': 'BIZ', '白山市': 'HJL',
            '北台': 'BTT', '包头东': 'BDC', '包头': 'BTC', '北屯市': 'BXR', '本溪': 'BXT', '白云鄂博': 'BEC', '白银西': 'BXJ',
            '亳州': 'BZH', '赤壁': 'CBN', '常德': 'VGQ', '承德': 'CDP', '长甸': 'CDT', '赤峰': 'CFD', '茶陵': 'CDG', '苍南': 'CEH',
            '昌平': 'CPP', '崇仁': 'CRG', '昌图': 'CTT', '长汀镇': 'CDB', '曹县': 'CXK', '楚雄': 'COM', '陈相屯': 'CXT', '长治北': 'CBF',
            '长征': 'CZJ', '池州': 'IYH', '常州': 'CZH', '郴州': 'CZQ', '长治': 'CZF', '沧州': 'COP', '崇左': 'CZZ', '大安北': 'RNT',
            '大成': 'DCT', '丹东': 'DUT', '东方红': 'DFB', '东莞东': 'DMQ', '大虎山': 'DHD', '敦煌': 'DHJ', '敦化': 'DHL', '德惠': 'DHT',
            '东京城': 'DJB', '大涧': 'DFP', '都江堰': 'DDW', '大连北': 'DFT', '大理': 'DKM', '大连': 'DLT', '定南': 'DNG', '大庆': 'DZX',
            '东胜': 'DOC', '大石桥': 'DQT', '大同': 'DTV', '东营': 'DPK', '大杨树': 'DUX', '都匀': 'RYW', '邓州': 'DOF', '达州': 'RXW',
            '德州': 'DZP', '额济纳': 'EJC', '二连': 'RLC', '恩施': 'ESN', '福鼎': 'FES', '风陵渡': 'FLV', '涪陵': 'FLW',
            '富拉尔基': 'FRX', '抚顺北': 'FET', '佛山': 'FSQ', '阜新': 'FXD', '阜阳': 'FYH', '格尔木': 'GRO', '广汉': 'GHW',
            '古交': 'GJV', '桂林北': 'GBZ', '古莲': 'GRX', '桂林': 'GLZ', '固始': 'GXN', '广水': 'GSN', '干塘': 'GNJ', '广元': 'GYW',
            '广州北': 'GBQ', '赣州': 'GZG', '公主岭': 'GLT', '公主岭南': 'GBT', '淮安': 'AUH', '鹤北': 'HMB', '淮北': 'HRH',
            '淮滨': 'HVN', '河边': 'HBV', '潢川': 'KCN', '韩城': 'HCY', '邯郸': 'HDP', '横道河子': 'HDB', '鹤岗': 'HGB', '皇姑屯': 'HTT',
            '红果': 'HEM', '黑河': 'HJB', '怀化': 'HHQ', '汉口': 'HKN', '葫芦岛': 'HLD', '海拉尔': 'HRX', '霍林郭勒': 'HWD',
            '海伦': 'HLB', '侯马': 'HMV', '哈密': 'HMR', '淮南': 'HAH', '桦南': 'HNB', '海宁西': 'EUH', '鹤庆': 'HQM', '怀柔北': 'HBP',
            '怀柔': 'HRP', '黄石东': 'OSN', '华山': 'HSY', '黄石': 'HSN', '黄山': 'HKH', '衡水': 'HSP', '衡阳': 'HYQ', '菏泽': 'HIK',
            '贺州': 'HXZ', '汉中': 'HOY', '惠州': 'HCQ', '吉安': 'VAG', '集安': 'JAL', '江边村': 'JBG', '晋城': 'JCF', '金城江': 'JJZ',
            '景德镇': 'JCG', '嘉峰': 'JFF', '加格达奇': 'JGX', '井冈山': 'JGG', '蛟河': 'JHL', '金华南': 'RNH', '金华西': 'JBH',
            '九江': 'JJG', '吉林': 'JLL', '荆门': 'JMN', '佳木斯': 'JMB', '济宁': 'JIK', '集宁南': 'JAC', '酒泉': 'JQJ', '江山': 'JUH',
            '吉首': 'JIQ', '九台': 'JTL', '镜铁山': 'JVJ', '鸡西': 'JXB', '蓟县': 'JKP', '绩溪县': 'JRH', '嘉峪关': 'JGJ', '江油': 'JFW',
            '锦州': 'JZD', '金州': 'JZT', '库尔勒': 'KLR', '开封': 'KFF', '岢岚': 'KLV', '凯里': 'KLW', '喀什': 'KSR', '昆山南': 'KNH',
            '奎屯': 'KTR', '开原': 'KYT', '六安': 'UAH', '灵宝': 'LBF', '芦潮港': 'UCH', '隆昌': 'LCW', '陆川': 'LKZ', '利川': 'LCN',
            '临川': 'LCG', '潞城': 'UTP', '鹿道': 'LDL', '娄底': 'LDQ', '临汾': 'LFV', '良各庄': 'LGP', '临河': 'LHC', '漯河': 'LON',
            '绿化': 'LWJ', '隆化': 'UHP', '丽江': 'LHM', '临江': 'LQL', '龙井': 'LJL', '吕梁': 'LHV', '醴陵': 'LLG', '柳林南': 'LKV',
            '滦平': 'UPP', '六盘水': 'UMW', '灵丘': 'LVV', '旅顺': 'LST', '陇西': 'LXJ', '澧县': 'LEQ', '兰溪': 'LWH', '临西': 'UEP',
            '龙岩': 'LYS', '耒阳': 'LYQ', '洛阳': 'LYF', '洛阳东': 'LDF', '连云港东': 'UKH', '临沂': 'LVK', '洛阳龙门': 'LLF',
            '柳园': 'DHR', '凌源': 'LYD', '辽源': 'LYL', '立志': 'LZX', '柳州': 'LZZ', '辽中': 'LZD', '麻城': 'MCN', '免渡河': 'MDX',
            '牡丹江': 'MDB', '莫尔道嘎': 'MRX', '满归': 'MHX', '明光': 'MGH', '漠河': 'MVX', '茂名东': 'MDQ', '茂名': 'MMZ',
            '密山': 'MSB', '马三家': 'MJT', '麻尾': 'VAW', '绵阳': 'MYW', '梅州': 'MOQ', '满洲里': 'MLX', '宁波东': 'NVH', '宁波': 'NGH',
            '南岔': 'NCB', '南充': 'NCW', '南丹': 'NDZ', '南大庙': 'NMP', '南芬': 'NFT', '讷河': 'NHX', '嫩江': 'NGX', '内江': 'NJW',
            '南平': 'NPS', '南通': 'NUH', '南阳': 'NFF', '碾子山': 'NZX', '平顶山': 'PEN', '盘锦': 'PVD', '平凉': 'PIJ', '平凉南': 'POJ',
            '平泉': 'PQP', '坪石': 'PSQ', '萍乡': 'PXG', '凭祥': 'PXZ', '郫县西': 'PCW', '攀枝花': 'PRW', '蕲春': 'QRN', '青城山': 'QSW',
            '青岛': 'QDK', '清河城': 'QYP', '黔江': 'QNW', '曲靖': 'QJM', '前进镇': 'QEB', '齐齐哈尔': 'QHX', '七台河': 'QTB',
            '沁县': 'QVV', '泉州东': 'QRS', '泉州': 'QYS', '衢州': 'QEH', '融安': 'RAZ', '汝箕沟': 'RQJ', '瑞金': 'RJG', '日照': 'RZK',
            '双城堡': 'SCB', '绥芬河': 'SFB', '韶关东': 'SGQ', '山海关': 'SHD', '绥化': 'SHB', '三间房': 'SFX', '苏家屯': 'SXT',
            '舒兰': 'SLL', '三明': 'SMS', '神木': 'OMY', '三门峡': 'SMF', '商南': 'ONY', '遂宁': 'NIW', '四平': 'SPT', '商丘': 'SQF',
            '上饶': 'SRG', '韶山': 'SSQ', '宿松': 'OAH', '汕头': 'OTQ', '邵武': 'SWS', '涉县': 'OEP', '三亚': 'SEQ', '邵阳': 'SYQ',
            '十堰': 'SNN', '双鸭山': 'SSB', '松原': 'VYT', '深圳': 'SZQ', '苏州': 'SZH', '随州': 'SZN', '宿州': 'OXH', '朔州': 'SUV',
            '深圳西': 'OSQ', '塘豹': 'TBQ', '塔尔气': 'TVX', '潼关': 'TGY', '塘沽': 'TGP', '塔河': 'TXX', '通化': 'THL', '泰来': 'TLX',
            '吐鲁番': 'TFR', '通辽': 'TLD', '铁岭': 'TLT', '陶赖昭': 'TPT', '图们': 'TML', '铜仁': 'RDQ', '唐山北': 'FUP',
            '田师府': 'TFT', '泰山': 'TAK', '唐山': 'TSP', '天水': 'TSJ', '通远堡': 'TYT', '太阳升': 'TQT', '泰州': 'UTH', '桐梓': 'TZW',
            '通州西': 'TAP', '五常': 'WCB', '武昌': 'WCN', '瓦房店': 'WDT', '威海': 'WKK', '芜湖': 'WHH', '乌海西': 'WXC',
            '吴家屯': 'WJT', '武隆': 'WLW', '乌兰浩特': 'WWT', '渭南': 'WNY', '威舍': 'WSM', '歪头山': 'WIT', '武威': 'WUJ',
            '武威南': 'WWJ', '无锡': 'WXH', '乌西': 'WXR', '乌伊岭': 'WPB', '武夷山': 'WAS', '万源': 'WYY', '万州': 'WYW', '梧州': 'WZZ',
            '温州': 'RZH', '温州南': 'VRH', '西昌': 'ECW', '许昌': 'XCF', '西昌南': 'ENW', '香坊': 'XFB', '轩岗': 'XGV', '兴国': 'EUG',
            '宣汉': 'XHY', '新会': 'EFQ', '新晃': 'XLQ', '锡林浩特': 'XTC', '兴隆县': 'EXP', '厦门北': 'XKS', '厦门': 'XMS',
            '厦门高崎': 'XBS', '秀山': 'ETW', '小市': 'XST', '向塘': 'XTG', '宣威': 'XWM', '新乡': 'XXF', '信阳': 'XUN', '咸阳': 'XYY',
            '襄阳': 'XFN', '熊岳城': 'XYT', '兴义': 'XRZ', '新沂': 'VIH', '新余': 'XUG', '徐州': 'XCH', '延安': 'YWY', '宜宾': 'YBW',
            '亚布力南': 'YWB', '叶柏寿': 'YBD', '宜昌东': 'HAN', '永川': 'YCW', '宜昌': 'YCN', '盐城': 'AFH', '运城': 'YNV',
            '伊春': 'YCB', '榆次': 'YCV', '杨村': 'YBP', '宜春西': 'YCG', '伊尔施': 'YET', '燕岗': 'YGW', '永济': 'YIV', '延吉': 'YJL',
            '营口': 'YKT', '牙克石': 'YKX', '阎良': 'YNY', '玉林': 'YLZ', '榆林': 'ALY', '一面坡': 'YPB', '伊宁': 'YMR', '阳平关': 'YAY',
            '玉屏': 'YZW', '原平': 'YPV', '延庆': 'YNP', '阳泉曲': 'YYV', '玉泉': 'YQB', '阳泉': 'AQP', '玉山': 'YNG', '营山': 'NUW',
            '燕山': 'AOP', '榆树': 'YRT', '鹰潭': 'YTG', '烟台': 'YAK', '伊图里河': 'YEX', '玉田县': 'ATP', '义乌': 'YWH', '阳新': 'YON',
            '义县': 'YXD', '益阳': 'AEQ', '岳阳': 'YYQ', '永州': 'AOQ', '扬州': 'YLH', '淄博': 'ZBK', '镇城底': 'ZDV', '自贡': 'ZGW',
            '珠海': 'ZHQ', '珠海北': 'ZIQ', '湛江': 'ZJZ', '镇江': 'ZJH', '张家界': 'DIQ', '张家口': 'ZKP', '张家口南': 'ZMP',
            '周口': 'ZKN', '哲里木': 'ZLC', '扎兰屯': 'ZTX', '驻马店': 'ZDN', '肇庆': 'ZVQ', '周水子': 'ZIT', '昭通': 'ZDW',
            '中卫': 'ZWJ', '资阳': 'ZYW', '遵义': 'ZIW', '枣庄': 'ZEK', '资中': 'ZZW', '株洲': 'ZZQ', '枣庄西': 'ZFK', '昂昂溪': 'AAX',
            '阿城': 'ACB', '安达': 'ADX', '安德': 'ARW', '安定': 'ADP', '安广': 'AGT', '艾河': 'AHP', '安化': 'PKQ', '艾家村': 'AJJ',
            '鳌江': 'ARH', '安家': 'AJB', '阿金': 'AJD', '阿克陶': 'AER', '安口窑': 'AYY', '敖力布告': 'ALD', '安龙': 'AUZ',
            '阿龙山': 'ASX', '安陆': 'ALN', '阿木尔': 'JTX', '阿南庄': 'AZM', '安庆西': 'APH', '鞍山西': 'AXT', '安塘': 'ATV',
            '安亭北': 'ASH', '阿图什': 'ATR', '安图': 'ATL', '安溪': 'AXS', '博鳌': 'BWQ', '北碚': 'BPW', '白壁关': 'BGV',
            '蚌埠南': 'BMH', '巴楚': 'BCR', '板城': 'BUP', '北戴河': 'BEP', '保定': 'BDP', '宝坻': 'BPP', '八达岭': 'ILP', '巴东': 'BNN',
            '柏果': 'BGM', '布海': 'BUT', '白河东': 'BIY', '贲红': 'BVC', '宝华山': 'BWH', '白河县': 'BEY', '白芨沟': 'BJJ',
            '碧鸡关': 'BJM', '北滘': 'IBQ', '碧江': 'BLQ', '白鸡坡': 'BBM', '笔架山': 'BSB', '八角台': 'BTD', '保康': 'BKD',
            '白奎堡': 'BKB', '白狼': 'BAT', '百浪': 'BRZ', '博乐': 'BOR', '宝拉格': 'BQC', '巴林': 'BLX', '宝林': 'BNB', '北流': 'BOZ',
            '勃利': 'BLB', '布列开': 'BLR', '宝龙山': 'BND', '八面城': 'BMD', '班猫箐': 'BNM', '八面通': 'BMB', '北马圈子': 'BRP',
            '北票南': 'RPD', '白旗': 'BQP', '宝泉岭': 'BQB', '白泉': 'BQL', '白沙': 'BSW', '巴山': 'BAY', '白水江': 'BSY',
            '白沙坡': 'BPM', '白石山': 'BAL', '白水镇': 'BUM', '坂田': 'BTQ', '泊头': 'BZP', '北屯': 'BYP', '本溪湖': 'BHT',
            '博兴': 'BXK', '八仙筒': 'VXD', '白音察干': 'BYC', '背荫河': 'BYB', '北营': 'BIV', '巴彦高勒': 'BAC', '白音他拉': 'BID',
            '鲅鱼圈': 'BYT', '白银市': 'BNJ', '白音胡硕': 'BCD', '巴中': 'IEW', '霸州': 'RMP', '北宅': 'BVP', '赤壁北': 'CIN',
            '查布嘎': 'CBC', '长城': 'CEJ', '长冲': 'CCM', '承德东': 'CCP', '赤峰西': 'CID', '嵯岗': 'CAX', '柴岗': 'CGT', '长葛': 'CEF',
            '柴沟堡': 'CGV', '城固': 'CGY', '陈官营': 'CAJ', '成高子': 'CZB', '草海': 'WBW', '柴河': 'CHB', '册亨': 'CHZ',
            '草河口': 'CKT', '崔黄口': 'CHP', '巢湖': 'CIH', '蔡家沟': 'CJT', '成吉思汗': 'CJX', '岔江': 'CAM', '蔡家坡': 'CJY',
            '昌乐': 'CLK', '超梁沟': 'CYP', '慈利': 'CUQ', '昌黎': 'CLP', '长岭子': 'CLT', '晨明': 'CMB', '长农': 'CNJ', '昌平北': 'VBP',
            '常平': 'DAQ', '长坡岭': 'CPM', '辰清': 'CQB', '楚山': 'CSB', '长寿': 'EFW', '磁山': 'CSP', '苍石': 'CST', '草市': 'CSL',
            '察素齐': 'CSC', '长山屯': 'CVT', '长汀': 'CES', '昌图西': 'CPT', '春湾': 'CQQ', '磁县': 'CIP', '岑溪': 'CNZ', '辰溪': 'CXQ',
            '磁西': 'CRP', '长兴南': 'CFH', '磁窑': 'CYK', '朝阳': 'CYD', '春阳': 'CAL', '城阳': 'CEK', '创业村': 'CEX', '朝阳川': 'CYL',
            '朝阳地': 'CDD', '长垣': 'CYF', '朝阳镇': 'CZL', '滁州北': 'CUH', '常州北': 'ESH', '滁州': 'CXH', '潮州': 'CKQ',
            '常庄': 'CVK', '曹子里': 'CFP', '车转湾': 'CWM', '郴州西': 'ICQ', '沧州西': 'CBP', '德安': 'DAG', '大安': 'RAT',
            '大坝': 'DBJ', '大板': 'DBC', '大巴': 'DBD', '到保': 'RBT', '定边': 'DYJ', '东边井': 'DBB', '德伯斯': 'RDT', '打柴沟': 'DGJ',
            '德昌': 'DVW', '滴道': 'DDB', '大磴沟': 'DKJ', '刀尔登': 'DRD', '得耳布尔': 'DRX', '东方': 'UFQ', '丹凤': 'DGY',
            '东丰': 'DIL', '都格': 'DMM', '大官屯': 'DTT', '大关': 'RGW', '东光': 'DGP', '东海': 'DHB', '大灰厂': 'DHP', '大红旗': 'DQD',
            '东海县': 'DQH', '德惠西': 'DXT', '达家沟': 'DJT', '东津': 'DKB', '杜家': 'DJL', '大口屯': 'DKP', '东来': 'RVD',
            '德令哈': 'DHO', '大陆号': 'DLC', '带岭': 'DLB', '大林': 'DLD', '达拉特旗': 'DIC', '独立屯': 'DTX', '豆罗': 'DLV',
            '达拉特西': 'DNC', '东明村': 'DMD', '洞庙河': 'DEP', '东明县': 'DNF', '大拟': 'DNZ', '大平房': 'DPD', '大盘石': 'RPP',
            '大埔': 'DPI', '大堡': 'DVT', '大其拉哈': 'DQX', '道清': 'DML', '对青山': 'DQB', '德清西': 'MOH', '大庆西': 'RHX',
            '东升': 'DRQ', '独山': 'RWW', '砀山': 'DKH', '登沙河': 'DWT', '读书铺': 'DPM', '大石头': 'DSL', '东胜西': 'DYC',
            '大石寨': 'RZT', '东台': 'DBH', '定陶': 'DQK', '灯塔': 'DGT', '大田边': 'DBM', '东通化': 'DTL', '丹徒': 'RUH', '大屯': 'DNT',
            '东湾': 'DRJ', '大武口': 'DFJ', '低窝铺': 'DWJ', '大王滩': 'DZZ', '大湾子': 'DFM', '大兴沟': 'DXL', '大兴': 'DXX',
            '定西': 'DSJ', '甸心': 'DXM', '东乡': 'DXG', '代县': 'DKV', '定襄': 'DXV', '东戌': 'RXP', '东辛庄': 'DXD', '丹阳': 'DYH',
            '大雁': 'DYX', '德阳': 'DYW', '当阳': 'DYN', '丹阳北': 'EXH', '大英东': 'IAW', '东淤地': 'DBV', '大营': 'DYV', '定远': 'EWH',
            '岱岳': 'RYV', '大元': 'DYZ', '大营镇': 'DJP', '大营子': 'DZD', '大战场': 'DTJ', '德州东': 'DIP', '低庄': 'DVQ',
            '东镇': 'DNV', '道州': 'DFZ', '东至': 'DCH', '东庄': 'DZV', '兑镇': 'DWV', '豆庄': 'ROP', '定州': 'DXP', '大竹园': 'DZY',
            '大杖子': 'DAP', '豆张庄': 'RZP', '峨边': 'EBW', '二道沟门': 'RDP', '二道湾': 'RDX', '二龙': 'RLD', '二龙山屯': 'ELA',
            '峨眉': 'EMW', '二密河': 'RML', '二营': 'RYJ', '鄂州': 'ECN', '福安': 'FAS', '丰城': 'FCG', '丰城南': 'FNG', '肥东': 'FIH',
            '发耳': 'FEM', '富海': 'FHX', '福海': 'FHR', '凤凰城': 'FHT', '奉化': 'FHH', '富锦': 'FIB', '范家屯': 'FTT', '福利屯': 'FTB',
            '丰乐镇': 'FZB', '阜南': 'FNH', '阜宁': 'AKH', '抚宁': 'FNP', '福清': 'FQS', '福泉': 'VMW', '丰水村': 'FSJ', '丰顺': 'FUQ',
            '繁峙': 'FSV', '抚顺': 'FST', '福山口': 'FKP', '扶绥': 'FSZ', '冯屯': 'FTX', '浮图峪': 'FYP', '富县东': 'FDY', '凤县': 'FXY',
            '富县': 'FEY', '费县': 'FXK', '凤阳': 'FUH', '汾阳': 'FAV', '扶余北': 'FBT', '分宜': 'FYG', '富源': 'FYM', '扶余': 'FYT',
            '富裕': 'FYX', '抚州北': 'FBG', '凤州': 'FZY', '丰镇': 'FZC', '范镇': 'VZK', '固安': 'GFP', '广安': 'VJW', '高碑店': 'GBP',
            '沟帮子': 'GBD', '甘草店': 'GDJ', '谷城': 'GCN', '藁城': 'GEP', '高村': 'GCV', '古城镇': 'GZB', '广德': 'GRH', '贵定': 'GTW',
            '贵定南': 'IDW', '古东': 'GDV', '贵港': 'GGZ', '官高': 'GVP', '葛根庙': 'GGT', '干沟': 'GGL', '甘谷': 'GGJ', '高各庄': 'GGP',
            '甘河': 'GAX', '根河': 'GEX', '郭家店': 'GDT', '孤家子': 'GKT', '古浪': 'GLJ', '皋兰': 'GEJ', '高楼房': 'GFM',
            '归流河': 'GHT', '关林': 'GLF', '甘洛': 'VOW', '郭磊庄': 'GLP', '高密': 'GMK', '公庙子': 'GMC', '工农湖': 'GRT',
            '广宁寺': 'GNT', '广南卫': 'GNM', '高平': 'GPF', '甘泉北': 'GEY', '共青城': 'GAG', '甘旗卡': 'GQD', '甘泉': 'GQY',
            '高桥镇': 'GZD', '赶水': 'GSW', '灌水': 'GST', '孤山口': 'GSP', '果松': 'GSL', '高山子': 'GSD', '嘎什甸子': 'GXD',
            '高台': 'GTJ', '高滩': 'GAY', '古田': 'GTS', '官厅': 'GTP', '官厅西': 'KEP', '贵溪': 'GXG', '涡阳': 'GYH', '巩义': 'GXF',
            '高邑': 'GIP', '巩义南': 'GYF', '固原': 'GUJ', '菇园': 'GYL', '公营子': 'GYD', '光泽': 'GZS', '古镇': 'GNQ', '瓜州': 'GZJ',
            '高州': 'GSQ', '固镇': 'GEH', '盖州': 'GXT', '官字井': 'GOT', '革镇堡': 'GZT', '冠豸山': 'GSS', '盖州西': 'GAT',
            '红安': 'HWN', '淮安南': 'AMH', '红安西': 'VXN', '海安县': 'HIH', '黄柏': 'HBL', '海北': 'HEB', '鹤壁': 'HAF', '华城': 'VCQ',
            '合川': 'WKW', '河唇': 'HCZ', '汉川': 'HCN', '海城': 'HCT', '黑冲滩': 'HCJ', '黄村': 'HCP', '海城西': 'HXT', '化德': 'HGC',
            '洪洞': 'HDV', '霍尔果斯': 'HFR', '横峰': 'HFG', '韩府湾': 'HXJ', '汉沽': 'HGP', '红光镇': 'IGW', '浑河': 'HHT',
            '红花沟': 'VHD', '黄花筒': 'HUD', '贺家店': 'HJJ', '和静': 'HJR', '红江': 'HFM', '黑井': 'HIM', '获嘉': 'HJF', '河津': 'HJV',
            '涵江': 'HJS', '华家': 'HJT', '河间西': 'HXP', '花家庄': 'HJM', '河口南': 'HKJ', '黄口': 'KOH', '湖口': 'HKG', '呼兰': 'HUB',
            '葫芦岛北': 'HPD', '浩良河': 'HHB', '哈拉海': 'HIT', '鹤立': 'HOB', '桦林': 'HIB', '黄陵': 'ULY', '海林': 'HRB',
            '虎林': 'VLB', '寒岭': 'HAT', '和龙': 'HLL', '海龙': 'HIL', '哈拉苏': 'HAX', '呼鲁斯太': 'VTJ', '火连寨': 'HLT',
            '黄梅': 'VEH', '蛤蟆塘': 'HMT', '韩麻营': 'HYP', '黄泥河': 'HHL', '海宁': 'HNH', '惠农': 'HMJ', '和平': 'VAQ',
            '花棚子': 'HZM', '花桥': 'VQH', '宏庆': 'HEY', '怀仁': 'HRV', '华容': 'HRN', '华山北': 'HDY', '黄松甸': 'HDL',
            '和什托洛盖': 'VSR', '红山': 'VSB', '汉寿': 'VSQ', '衡山': 'HSQ', '黑水': 'HOT', '惠山': 'VCH', '虎什哈': 'HHP',
            '红寺堡': 'HSJ', '虎石台': 'HUT', '海石湾': 'HSO', '衡山西': 'HEQ', '红砂岘': 'VSJ', '黑台': 'HQB', '桓台': 'VTK',
            '和田': 'VTR', '会同': 'VTQ', '海坨子': 'HZT', '黑旺': 'HWK', '海湾': 'RWH', '红星': 'VXB', '徽县': 'HYY', '红兴隆': 'VHB',
            '换新天': 'VTB', '红岘台': 'HTJ', '红彦': 'VIX', '合阳': 'HAY', '海阳': 'HYK', '衡阳东': 'HVQ', '华蓥': 'HUW', '汉阴': 'HQY',
            '黄羊滩': 'HGJ', '汉源': 'WHW', '湟源': 'HNO', '河源': 'VIQ', '花园': 'HUN', '黄羊镇': 'HYJ', '湖州': 'VZH', '化州': 'HZZ',
            '黄州': 'VON', '霍州': 'HZV', '惠州西': 'VXQ', '巨宝': 'JRT', '靖边': 'JIY', '金宝屯': 'JBD', '晋城北': 'JEF', '金昌': 'JCJ',
            '鄄城': 'JCK', '交城': 'JNV', '建昌': 'JFD', '峻德': 'JDB', '井店': 'JFP', '鸡东': 'JOB', '江都': 'UDH', '鸡冠山': 'JST',
            '金沟屯': 'VGP', '静海': 'JHP', '金河': 'JHX', '锦河': 'JHB', '精河': 'JHR', '精河南': 'JIR', '江华': 'JHZ', '建湖': 'AJH',
            '纪家沟': 'VJD', '晋江': 'JJS', '江津': 'JJW', '姜家': 'JJB', '金坑': 'JKT', '芨岭': 'JLJ', '金马村': 'JMM', '江门': 'JWQ',
            '角美': 'JES', '莒南': 'JOK', '井南': 'JNP', '建瓯': 'JVS', '经棚': 'JPC', '江桥': 'JQX', '九三': 'SSX', '金山北': 'EGH',
            '京山': 'JCN', '建始': 'JRN', '嘉善': 'JSH', '稷山': 'JVV', '吉舒': 'JSL', '建设': 'JET', '甲山': 'JOP', '建三江': 'JIB',
            '嘉善南': 'EAH', '金山屯': 'JTB', '江所田': 'JOM', '景泰': 'JTJ', '九台南': 'JNL', '吉文': 'JWX', '进贤': 'JUG',
            '莒县': 'JKK', '嘉祥': 'JUK', '介休': 'JXV', '井陉': 'JJP', '嘉兴': 'JXH', '嘉兴南': 'EPH', '夹心子': 'JXT', '简阳': 'JYW',
            '揭阳': 'JRQ', '建阳': 'JYS', '姜堰': 'UEH', '巨野': 'JYK', '江永': 'JYZ', '靖远': 'JYJ', '缙云': 'JYH', '江源': 'SZL',
            '济源': 'JYF', '靖远西': 'JXJ', '胶州北': 'JZK', '焦作东': 'WEF', '靖州': 'JEQ', '荆州': 'JBN', '金寨': 'JZH', '晋州': 'JXP',
            '胶州': 'JXK', '锦州南': 'JOD', '焦作': 'JOF', '旧庄窝': 'JVP', '金杖子': 'JYD', '开安': 'KAT', '库车': 'KCR', '康城': 'KCP',
            '库都尔': 'KDX', '宽甸': 'KDT', '克东': 'KOB', '开江': 'KAW', '康金井': 'KJB', '喀喇其': 'KQX', '开鲁': 'KLC',
            '克拉玛依': 'KHR', '口前': 'KQL', '奎山': 'KAB', '昆山': 'KSH', '克山': 'KSB', '开通': 'KTT', '康熙岭': 'KXZ', '昆阳': 'KAM',
            '克一河': 'KHX', '开原西': 'KXT', '康庄': 'KZP', '来宾': 'UBZ', '老边': 'LLT', '灵宝西': 'LPF', '龙川': 'LUQ', '乐昌': 'LCQ',
            '黎城': 'UCP', '聊城': 'UCK', '蓝村': 'LCK', '林东': 'LRC', '乐都': 'LDO', '梁底下': 'LDP', '六道河子': 'LVP', '鲁番': 'LVM',
            '廊坊': 'LJP', '落垡': 'LOP', '廊坊北': 'LFP', '老府': 'UFD', '兰岗': 'LNB', '龙骨甸': 'LGM', '芦沟': 'LOM', '龙沟': 'LGJ',
            '拉古': 'LGB', '临海': 'UFH', '林海': 'LXX', '拉哈': 'LHX', '凌海': 'JID', '柳河': 'LNL', '六合': 'KLH', '龙华': 'LHP',
            '滦河沿': 'UNP', '六合镇': 'LEX', '亮甲店': 'LRT', '刘家店': 'UDT', '刘家河': 'LVT', '连江': 'LKS', '李家': 'LJB',
            '罗江': 'LJW', '廉江': 'LJZ', '庐江': 'UJH', '两家': 'UJT', '龙江': 'LJX', '龙嘉': 'UJL', '莲江口': 'LHB', '蔺家楼': 'ULK',
            '李家坪': 'LIJ', '兰考': 'LKF', '林口': 'LKB', '路口铺': 'LKQ', '老莱': 'LAX', '拉林': 'LAB', '陆良': 'LRM', '龙里': 'LLW',
            '零陵': 'UWZ', '临澧': 'LWQ', '兰棱': 'LLB', '卢龙': 'UAP', '喇嘛甸': 'LMX', '里木店': 'LMB', '洛门': 'LMJ', '龙南': 'UNG',
            '梁平': 'UQW', '罗平': 'LPM', '落坡岭': 'LPP', '六盘山': 'UPJ', '乐平市': 'LPG', '临清': 'UQK', '龙泉寺': 'UQJ',
            '乐山北': 'UTW', '乐善村': 'LUM', '冷水江东': 'UDQ', '连山关': 'LGT', '流水沟': 'USP', '陵水': 'LIQ', '罗山': 'LRN',
            '鲁山': 'LAF', '丽水': 'USH', '梁山': 'LMK', '灵石': 'LSV', '露水河': 'LUL', '庐山': 'LSG', '林盛堡': 'LBT', '柳树屯': 'LSD',
            '龙山镇': 'LAS', '梨树镇': 'LSB', '李石寨': 'LET', '黎塘': 'LTZ', '轮台': 'LAR', '芦台': 'LTP', '龙塘坝': 'LBM',
            '濑湍': 'LVZ', '骆驼巷': 'LTJ', '李旺': 'VLJ', '莱芜东': 'LWK', '狼尾山': 'LRJ', '灵武': 'LNJ', '莱芜西': 'UXK',
            '朗乡': 'LXB', '陇县': 'LXY', '临湘': 'LXQ', '芦溪': 'LUG', '莱西': 'LXK', '林西': 'LXC', '滦县': 'UXP', '略阳': 'LYY',
            '辽阳': 'LYT', '临沂北': 'UYK', '凌源东': 'LDD', '连云港': 'UIH', '临颍': 'LNF', '老营': 'LXL', '龙游': 'LMH', '罗源': 'LVS',
            '林源': 'LYX', '涟源': 'LAQ', '涞源': 'LYP', '耒阳西': 'LPQ', '临泽': 'LEJ', '龙爪沟': 'LZT', '雷州': 'UAQ', '六枝': 'LIW',
            '鹿寨': 'LIZ', '来舟': 'LZS', '龙镇': 'LZA', '拉鲊': 'LEM', '马鞍山': 'MAH', '毛坝': 'MBY', '毛坝关': 'MGY', '麻城北': 'MBN',
            '渑池': 'MCF', '明城': 'MCL', '庙城': 'MAP', '渑池南': 'MNF', '茅草坪': 'KPM', '猛洞河': 'MUQ', '磨刀石': 'MOB',
            '弥渡': 'MDF', '帽儿山': 'MRB', '明港': 'MGN', '梅河口': 'MHL', '马皇': 'MHZ', '孟家岗': 'MGB', '美兰': 'MHQ',
            '汨罗东': 'MQQ', '马莲河': 'MHB', '茅岭': 'MLZ', '庙岭': 'MLL', '茂林': 'MLD', '穆棱': 'MLB', '马林': 'MID', '马龙': 'MGM',
            '汨罗': 'MLQ', '木里图': 'MUD', '玛纳斯湖': 'MNR', '冕宁': 'UGW', '沐滂': 'MPQ', '马桥河': 'MQB', '闽清': 'MQS',
            '民权': 'MQF', '明水河': 'MUT', '麻山': 'MAB', '眉山': 'MSW', '漫水湾': 'MKW', '茂舍祖': 'MOM', '米沙子': 'MST',
            '美溪': 'MEB', '勉县': 'MVY', '麻阳': 'MVQ', '密云北': 'MUP', '米易': 'MMW', '麦园': 'MYS', '墨玉': 'MUR', '庙庄': 'MZJ',
            '米脂': 'MEY', '明珠': 'MFQ', '宁安': 'NAB', '农安': 'NAT', '南博山': 'NBK', '南仇': 'NCK', '南城司': 'NSP', '宁村': 'NCZ',
            '宁德': 'NES', '南观村': 'NGP', '南宫东': 'NFP', '南关岭': 'NLT', '宁国': 'NNH', '宁海': 'NHH', '南河川': 'NHJ',
            '南华': 'NHS', '泥河子': 'NHD', '宁家': 'NVT', '南靖': 'NJS', '牛家': 'NJB', '能家': 'NJD', '南口': 'NKP', '南口前': 'NKT',
            '南朗': 'NNQ', '乃林': 'NLD', '尼勒克': 'NIR', '那罗': 'ULZ', '宁陵县': 'NLF', '奈曼': 'NMD', '宁明': 'NMZ', '南木': 'NMX',
            '南平南': 'NNS', '那铺': 'NPZ', '南桥': 'NQD', '那曲': 'NQO', '暖泉': 'NQJ', '南台': 'NTT', '南头': 'NOQ', '宁武': 'NWV',
            '南湾子': 'NWP', '南翔北': 'NEH', '宁乡': 'NXQ', '内乡': 'NXF', '牛心台': 'NXT', '南峪': 'NUP', '娘子关': 'NIP',
            '南召': 'NAF', '南杂木': 'NZT', '平安': 'PAL', '蓬安': 'PAW', '平安驿': 'PNO', '磐安镇': 'PAJ', '平安镇': 'PZT',
            '蒲城东': 'PEY', '蒲城': 'PCY', '裴德': 'PDB', '偏店': 'PRP', '平顶山西': 'BFF', '坡底下': 'PXJ', '瓢儿屯': 'PRT',
            '平房': 'PFB', '平岗': 'PGL', '平关': 'PGM', '盘关': 'PAM', '平果': 'PGZ', '徘徊北': 'PHP', '平河口': 'PHM', '盘锦北': 'PBD',
            '潘家店': 'PDP', '皮口': 'PKT', '普兰店': 'PLT', '偏岭': 'PNT', '平山': 'PSB', '彭山': 'PSW', '皮山': 'PSR', '彭水': 'PHW',
            '磐石': 'PSL', '平社': 'PSV', '平台': 'PVT', '平田': 'PTM', '莆田': 'PTS', '葡萄菁': 'PTW', '普湾': 'PWT', '平旺': 'PWV',
            '平型关': 'PGV', '普雄': 'POW', '郫县': 'PWW', '平洋': 'PYX', '彭阳': 'PYJ', '平遥': 'PYV', '平邑': 'PIK', '平原堡': 'PPJ',
            '平原': 'PYK', '平峪': 'PYP', '彭泽': 'PZG', '邳州': 'PJH', '平庄': 'PZD', '泡子': 'POD', '平庄南': 'PND', '乾安': 'QOT',
            '庆安': 'QAB', '迁安': 'QQP', '祁东北': 'QRQ', '七甸': 'QDM', '曲阜东': 'QAK', '庆丰': 'QFT', '奇峰塔': 'QVP', '曲阜': 'QFK',
            '琼海': 'QYQ', '秦皇岛': 'QTP', '千河': 'QUY', '清河': 'QIP', '清河门': 'QHD', '清华园': 'QHP', '渠旧': 'QJZ', '綦江': 'QJW',
            '潜江': 'QJN', '全椒': 'INH', '秦家': 'QJB', '祁家堡': 'QBT', '清涧县': 'QNY', '秦家庄': 'QZV', '七里河': 'QLD',
            '渠黎': 'QLZ', '秦岭': 'QLY', '青龙山': 'QGH', '祁门': 'QIH', '前磨头': 'QMP', '青山': 'QSB', '确山': 'QSN', '清水': 'QUJ',
            '前山': 'QXQ', '戚墅堰': 'QYH', '青田': 'QVH', '桥头': 'QAT', '青铜峡': 'QTJ', '前卫': 'QWD', '前苇塘': 'QWP', '渠县': 'QRW',
            '祁县': 'QXV', '青县': 'QXP', '桥西': 'QXJ', '清徐': 'QUV', '旗下营': 'QXC', '千阳': 'QOY', '沁阳': 'QYF', '泉阳': 'QYL',
            '祁阳北': 'QVQ', '七营': 'QYJ', '庆阳山': 'QSJ', '清远': 'QBQ', '清原': 'QYT', '钦州东': 'QDZ', '钦州': 'QRZ',
            '青州市': 'QZK', '瑞安': 'RAH', '荣昌': 'RCW', '瑞昌': 'RCG', '如皋': 'RBH', '容桂': 'RUQ', '任丘': 'RQP', '乳山': 'ROK',
            '融水': 'RSZ', '热水': 'RSD', '容县': 'RXZ', '饶阳': 'RVP', '汝阳': 'RYF', '绕阳河': 'RHD', '汝州': 'ROF', '石坝': 'OBJ',
            '上板城': 'SBP', '施秉': 'AQW', '上板城南': 'OBP', '世博园': 'ZWT', '双城北': 'SBB', '商城': 'SWN', '莎车': 'SCR',
            '顺昌': 'SCS', '舒城': 'OCH', '神池': 'SMV', '沙城': 'SCP', '石城': 'SCT', '山城镇': 'SCL', '山丹': 'SDJ', '顺德': 'ORQ',
            '绥德': 'ODY', '邵东': 'SOQ', '水洞': 'SIL', '商都': 'SXC', '十渡': 'SEP', '四道湾': 'OUD', '顺德学院': 'OJQ', '绅坊': 'OLH',
            '双丰': 'OFB', '四方台': 'STB', '水富': 'OTW', '三关口': 'OKJ', '桑根达来': 'OGC', '韶关': 'SNQ', '上高镇': 'SVK',
            '上杭': 'JBS', '沙海': 'SED', '松河': 'SBM', '沙河': 'SHP', '沙河口': 'SKT', '赛汗塔拉': 'SHC', '沙河市': 'VOP',
            '沙后所': 'SSD', '山河屯': 'SHL', '三河县': 'OXP', '四合永': 'OHD', '三汇镇': 'OZW', '双河镇': 'SEL', '石河子': 'SZR',
            '三合庄': 'SVP', '三家店': 'ODP', '水家湖': 'SQH', '沈家河': 'OJJ', '松江河': 'SJL', '尚家': 'SJB', '孙家': 'SUB',
            '沈家': 'OJB', '松江': 'SAH', '三江口': 'SKD', '司家岭': 'OLK', '松江南': 'IMH', '石景山南': 'SRP', '邵家堂': 'SJJ',
            '三江县': 'SOZ', '三家寨': 'SMM', '十家子': 'SJD', '松江镇': 'OZL', '施家嘴': 'SHM', '深井子': 'SWT', '什里店': 'OMP',
            '疏勒': 'SUR', '疏勒河': 'SHJ', '舍力虎': 'VLD', '石磷': 'SPB', '双辽': 'ZJD', '绥棱': 'SIB', '石岭': 'SOL', '石林': 'SLM',
            '石林南': 'LNM', '石龙': 'SLQ', '萨拉齐': 'SLC', '索伦': 'SNT', '商洛': 'OLY', '沙岭子': 'SLP', '石门县北': 'VFQ',
            '三门峡南': 'SCF', '三门县': 'OQH', '石门县': 'OMQ', '三门峡西': 'SXF', '肃宁': 'SYP', '宋': 'SOB', '双牌': 'SBZ',
            '四平东': 'PPT', '遂平': 'SON', '沙坡头': 'SFJ', '商丘南': 'SPF', '水泉': 'SID', '石泉县': 'SXY', '石桥子': 'SQT',
            '石人城': 'SRB', '石人': 'SRL', '山市': 'SQB', '神树': 'SWB', '鄯善': 'SSR', '三水': 'SJQ', '泗水': 'OSK', '石山': 'SAD',
            '松树': 'SFT', '首山': 'SAT', '三十家': 'SRD', '三十里堡': 'SST', '松树镇': 'SSL', '松桃': 'MZQ', '索图罕': 'SHX',
            '三堂集': 'SDH', '石头': 'OTB', '神头': 'SEV', '沙沱': 'SFM', '上万': 'SWP', '孙吴': 'SKB', '沙湾县': 'SXR', '遂溪': 'SXZ',
            '沙县': 'SAS', '绍兴': 'SOH', '歙县': 'OVH', '石岘': 'SXL', '上西铺': 'SXM', '石峡子': 'SXJ', '绥阳': 'SYB', '沭阳': 'FMH',
            '寿阳': 'SYV', '水洋': 'OYP', '三阳川': 'SYJ', '上腰墩': 'SPJ', '三营': 'OEJ', '顺义': 'SOP', '三义井': 'OYD',
            '三源浦': 'SYL', '三原': 'SAY', '上虞': 'BDH', '上园': 'SUD', '水源': 'OYJ', '桑园子': 'SAJ', '绥中北': 'SND',
            '苏州北': 'OHH', '宿州东': 'SRH', '深圳东': 'BJQ', '深州': 'OZP', '孙镇': 'OZY', '绥中': 'SZD', '尚志': 'SZB', '师庄': 'SNM',
            '松滋': 'SIN', '师宗': 'SEM', '苏州园区': 'KAH', '苏州新区': 'ITH', '泰安': 'TMK', '台安': 'TID', '通安驿': 'TAJ',
            '桐柏': 'TBF', '通北': 'TBB', '汤池': 'TCX', '桐城': 'TTH', '郯城': 'TZK', '铁厂': 'TCL', '桃村': 'TCK', '通道': 'TRQ',
            '田东': 'TDZ', '天岗': 'TGL', '土贵乌拉': 'TGC', '通沟': 'TOL', '太谷': 'TGV', '塔哈': 'THX', '棠海': 'THM', '唐河': 'THF',
            '泰和': 'THG', '太湖': 'TKH', '团结': 'TIX', '谭家井': 'TNJ', '陶家屯': 'TOT', '唐家湾': 'PDQ', '统军庄': 'TZP',
            '泰康': 'TKX', '吐列毛杜': 'TMD', '图里河': 'TEX', '亭亮': 'TIZ', '田林': 'TFZ', '铜陵': 'TJH', '铁力': 'TLB',
            '铁岭西': 'PXT', '天门': 'TMN', '天门南': 'TNN', '太姥山': 'TLS', '土牧尔台': 'TRC', '土门子': 'TCJ', '潼南': 'TVW',
            '洮南': 'TVT', '太平川': 'TIT', '太平镇': 'TEB', '图强': 'TQX', '台前': 'TTK', '天桥岭': 'TQL', '土桥子': 'TQJ',
            '汤山城': 'TCT', '桃山': 'TAB', '塔石嘴': 'TIM', '通途': 'TUT', '汤旺河': 'THB', '同心': 'TXJ', '土溪': 'TSW', '桐乡': 'TCH',
            '田阳': 'TRZ', '天义': 'TND', '汤阴': 'TYF', '驼腰岭': 'TIL', '太阳山': 'TYJ', '汤原': 'TYB', '塔崖驿': 'TYP',
            '滕州东': 'TEK', '台州': 'TZH', '天祝': 'TZJ', '滕州': 'TXK', '天镇': 'TZV', '桐子林': 'TEW', '天柱山': 'QWH', '文安': 'WBP',
            '武安': 'WAP', '王安镇': 'WVP', '旺苍': 'WEW', '五叉沟': 'WCT', '文昌': 'WEQ', '温春': 'WDB', '五大连池': 'WRB',
            '文登': 'WBK', '五道沟': 'WDL', '五道河': 'WHP', '文地': 'WNZ', '卫东': 'WVT', '武当山': 'WRN', '望都': 'WDP',
            '乌尔旗汗': 'WHX', '潍坊': 'WFK', '万发屯': 'WFB', '王府': 'WUT', '瓦房店西': 'WXT', '王岗': 'WGB', '武功': 'WGY',
            '湾沟': 'WGL', '吴官田': 'WGM', '乌海': 'WVC', '苇河': 'WHB', '卫辉': 'WHF', '吴家川': 'WCJ', '五家': 'WUB', '威箐': 'WAM',
            '午汲': 'WJP', '渭津': 'WJL', '王家湾': 'WJJ', '倭肯': 'WQB', '五棵树': 'WKT', '五龙背': 'WBT', '乌兰哈达': 'WLC',
            '万乐': 'WEB', '瓦拉干': 'WVX', '温岭': 'VHH', '五莲': 'WLK', '乌拉特前旗': 'WQC', '乌拉山': 'WSC', '卧里屯': 'WLX',
            '渭南北': 'WBY', '乌奴耳': 'WRX', '万宁': 'WNQ', '万年': 'WWG', '渭南南': 'WVY', '渭南镇': 'WNJ', '沃皮': 'WPT',
            '吴堡': 'WUY', '吴桥': 'WUP', '汪清': 'WQL', '武清': 'WWP', '武山': 'WSJ', '文水': 'WEV', '魏善庄': 'WSP', '王瞳': 'WTP',
            '五台山': 'WSV', '王团庄': 'WZJ', '五五': 'WVR', '无锡东': 'WGH', '卫星': 'WVB', '闻喜': 'WXV', '武乡': 'WVV',
            '无锡新区': 'IFH', '武穴': 'WXN', '吴圩': 'WYZ', '王杨': 'WYB', '五营': 'WWB', '武义': 'RYH', '瓦窑田': 'WIM', '五原': 'WYC',
            '苇子沟': 'WZL', '韦庄': 'WZY', '五寨': 'WZV', '王兆屯': 'WZB', '微子镇': 'WQP', '魏杖子': 'WKD', '新安': 'EAM',
            '兴安': 'XAZ', '新安县': 'XAF', '新保安': 'XAP', '下板城': 'EBP', '西八里': 'XLP', '宣城': 'ECH', '兴城': 'XCD',
            '小村': 'XEM', '新绰源': 'XRX', '下城子': 'XCB', '新城子': 'XCT', '喜德': 'EDW', '小得江': 'EJM', '西大庙': 'XMP',
            '小董': 'XEZ', '小东': 'XOD', '息烽': 'XFW', '信丰': 'EFG', '襄汾': 'XFV', '新干': 'EGG', '孝感': 'XGN', '西固城': 'XUJ',
            '夏官营': 'XGJ', '西岗子': 'NBB', '襄河': 'XXB', '新和': 'XIR', '宣和': 'XWJ', '斜河涧': 'EEP', '新华屯': 'XAX',
            '新华': 'XHB', '新化': 'EHQ', '宣化': 'XHP', '兴和西': 'XEC', '小河沿': 'XYD', '下花园': 'XYP', '小河镇': 'EKY',
            '徐家': 'XJB', '峡江': 'EJG', '新绛': 'XJV', '辛集': 'ENP', '新江': 'XJM', '西街口': 'EKM', '许家屯': 'XJT', '许家台': 'XTJ',
            '谢家镇': 'XMT', '兴凯': 'EKB', '小榄': 'EAQ', '香兰': 'XNB', '兴隆店': 'XDD', '新乐': 'ELP', '新林': 'XPX', '小岭': 'XLB',
            '新李': 'XLJ', '西林': 'XYB', '西柳': 'GCT', '仙林': 'XPH', '新立屯': 'XLD', '兴隆镇': 'XZB', '新立镇': 'XGT', '新民': 'XMD',
            '西麻山': 'XMB', '下马塘': 'XAT', '孝南': 'XNV', '咸宁北': 'XRN', '兴宁': 'ENQ', '咸宁': 'XNN', '犀浦东': 'XAW',
            '西平': 'XPN', '兴平': 'XPY', '新坪田': 'XPM', '霞浦': 'XOS', '溆浦': 'EPQ', '犀浦': 'XIW', '新青': 'XQB', '新邱': 'XQD',
            '兴泉堡': 'XQJ', '仙人桥': 'XRL', '小寺沟': 'ESP', '杏树': 'XSB', '夏石': 'XIZ', '浠水': 'XZN', '下社': 'XSV', '徐水': 'XSP',
            '小哨': 'XAM', '新松浦': 'XOB', '杏树屯': 'XDT', '许三湾': 'XSJ', '湘潭': 'XTQ', '邢台': 'XTP', '仙桃西': 'XAN',
            '下台子': 'EIP', '徐闻': 'XJQ', '新窝铺': 'EPD', '修武': 'XWF', '新县': 'XSN', '西乡': 'XQY', '湘乡': 'XXQ', '西峡': 'XIF',
            '孝西': 'XOV', '小新街': 'XXM', '新兴县': 'XGQ', '西小召': 'XZC', '小西庄': 'XXP', '向阳': 'XDB', '旬阳': 'XUY',
            '旬阳北': 'XBY', '襄阳东': 'XWN', '兴业': 'SNZ', '小雨谷': 'XHM', '信宜': 'EEQ', '小月旧': 'XFM', '小扬气': 'XYX',
            '祥云': 'EXM', '襄垣': 'EIF', '夏邑县': 'EJH', '新友谊': 'EYB', '新阳镇': 'XZJ', '徐州东': 'UUH', '新帐房': 'XZX',
            '悬钟': 'XRP', '新肇': 'XZT', '忻州': 'XXV', '汐子': 'XZD', '西哲里木': 'XRD', '新杖子': 'ERP', '姚安': 'YAC', '依安': 'YAX',
            '永安': 'YAS', '永安乡': 'YNB', '亚布力': 'YBB', '元宝山': 'YUD', '羊草': 'YAB', '秧草地': 'YKM', '阳澄湖': 'AIH',
            '迎春': 'YYB', '叶城': 'YER', '盐池': 'YKJ', '砚川': 'YYY', '阳春': 'YQQ', '宜城': 'YIN', '应城': 'YHN', '禹城': 'YCK',
            '羊场': 'YED', '阳城': 'YNF', '阳岔': 'YAL', '郓城': 'YPK', '雁翅': 'YAP', '云彩岭': 'ACP', '虞城县': 'IXH', '营城子': 'YCT',
            '永登': 'YDJ', '英德': 'YDQ', '尹地': 'YDM', '永定': 'YGS', '雁荡山': 'YGH', '于都': 'YDG', '园墩': 'YAJ', '英德西': 'IIQ',
            '永丰营': 'YYM', '杨岗': 'YRB', '阳高': 'YOV', '阳谷': 'YIK', '友好': 'YOB', '余杭': 'EVH', '沿河城': 'YHP', '岩会': 'AEP',
            '羊臼河': 'YHM', '永嘉': 'URH', '营街': 'YAM', '盐津': 'AEW', '余江': 'YHG', '叶集': 'YCH', '燕郊': 'AJP', '姚家': 'YAT',
            '岳家井': 'YGJ', '一间堡': 'YJT', '英吉沙': 'YIR', '云居寺': 'AFP', '燕家庄': 'AZK', '永康': 'RFH', '营口东': 'YGT',
            '银浪': 'YJX', '永郎': 'YLW', '宜良北': 'YSM', '永乐店': 'YDY', '伊拉哈': 'YLX', '伊林': 'YLB', '杨陵': 'YSY', '彝良': 'ALW',
            '杨林': 'YLM', '余粮堡': 'YLD', '杨柳青': 'YQP', '月亮田': 'YUM', '亚龙湾': 'TWQ', '义马': 'YMF', '玉门': 'YXJ',
            '云梦': 'YMN', '元谋': 'YMM', '阳明堡': 'YVV', '一面山': 'YST', '沂南': 'YNK', '宜耐': 'YVM', '伊宁东': 'YNR',
            '营盘水': 'YZJ', '羊堡': 'ABM', '阳泉北': 'YPP', '乐清': 'UPH', '焉耆': 'YSR', '源迁': 'AQK', '姚千户屯': 'YQT',
            '阳曲': 'YQV', '榆树沟': 'YGP', '月山': 'YBF', '玉石': 'YSJ', '偃师': 'YSF', '沂水': 'YUK', '榆社': 'YSV', '窑上': 'ASP',
            '元氏': 'YSP', '杨树岭': 'YAD', '野三坡': 'AIP', '榆树屯': 'YSX', '榆树台': 'YUT', '鹰手营子': 'YIP', '源潭': 'YTQ',
            '牙屯堡': 'YTZ', '烟筒山': 'YSL', '烟筒屯': 'YUX', '羊尾哨': 'YWM', '越西': 'YHW', '攸县': 'YOG', '玉溪': 'YXM',
            '永修': 'ACG', '弋阳': 'YIG', '酉阳': 'AFW', '余姚': 'YYH', '岳阳东': 'YIQ', '阳邑': 'ARP', '鸭园': 'YYL', '鸳鸯镇': 'YYJ',
            '燕子砭': 'YZY', '宜州': 'YSZ', '仪征': 'UZH', '兖州': 'YZK', '迤资': 'YQM', '羊者窝': 'AEM', '杨杖子': 'YZD', '镇安': 'ZEY',
            '治安': 'ZAD', '招柏': 'ZBP', '张百湾': 'ZUP', '枝城': 'ZCN', '子长': 'ZHY', '诸城': 'ZQK', '邹城': 'ZIK', '赵城': 'ZCV',
            '章党': 'ZHT', '肇东': 'ZDB', '照福铺': 'ZFM', '章古台': 'ZGD', '赵光': 'ZGB', '中和': 'ZHX', '中华门': 'VNH',
            '枝江北': 'ZIN', '钟家村': 'ZJY', '朱家沟': 'ZUB', '紫荆关': 'ZYP', '周家': 'ZOB', '诸暨': 'ZDH', '镇江南': 'ZEH',
            '周家屯': 'ZOD', '褚家湾': 'CWJ', '湛江西': 'ZWQ', '朱家窑': 'ZUJ', '曾家坪子': 'ZBW', '张兰': 'ZLV', '镇赉': 'ZLT',
            '枣林': 'ZIV', '扎鲁特': 'ZLD', '扎赉诺尔西': 'ZXX', '樟木头': 'ZOQ', '中牟': 'ZGF', '中宁东': 'ZDJ', '中宁': 'VNJ',
            '中宁南': 'ZNJ', '镇平': 'ZPF', '漳平': 'ZPS', '泽普': 'ZPR', '枣强': 'ZVP', '张桥': 'ZQY', '章丘': 'ZTK', '朱日和': 'ZRC',
            '泽润里': 'ZLM', '中山北': 'ZGQ', '樟树东': 'ZOG', '中山': 'ZSQ', '柞水': 'ZSY', '钟山': 'ZSZ', '樟树': 'ZSG', '珠窝': 'ZOP',
            '张维屯': 'ZWB', '彰武': 'ZWD', '棕溪': 'ZOY', '钟祥': 'ZTN', '资溪': 'ZXS', '镇西': 'ZVT', '张辛': 'ZIP', '正镶白旗': 'ZXC',
            '紫阳': 'ZVY', '枣阳': 'ZYN', '竹园坝': 'ZAW', '张掖': 'ZYJ', '镇远': 'ZUW', '朱杨溪': 'ZXW', '漳州东': 'GOS', '漳州': 'ZUS',
            '壮志': 'ZUX', '子洲': 'ZZY', '中寨': 'ZZM', '涿州': 'ZXP', '咋子': 'ZAL', '卓资山': 'ZZC', '株洲西': 'ZAQ', '安仁': 'ARG',
            '安阳东': 'ADF', '栟茶': 'FWH', '保定东': 'BMP', '滨海': 'FHP', '滨海北': 'FCP', '宝鸡南': 'BBY', '茶陵南': 'CNG',
            '长寿北': 'COW', '潮汕': 'CBQ', '长兴': 'CBH', '长阳': 'CYN', '潮阳': 'CNQ', '东安东': 'DCZ', '东戴河': 'RDD',
            '东二道河': 'DRB', '东莞': 'RTQ', '大苴': 'DIM', '大荔': 'DNY', '大青沟': 'DSD', '德清': 'DRH', '大冶北': 'DBN',
            '定州东': 'DOP', '鄂州东': 'EFN', '防城港北': 'FBZ', '富川': 'FDZ', '丰都': 'FUW', '涪陵北': 'FEW', '抚远': 'FYB',
            '抚州': 'FZG', '广安南': 'VUW', '高碑店东': 'GMP', '葛店南': 'GNN', '革居': 'GEM', '光明城': 'IMQ', '桂平': 'GAZ',
            '广通北': 'GPM', '高邑西': 'GNP', '鹤壁东': 'HFF', '寒葱沟': 'HKB', '邯郸东': 'HPP', '惠东': 'KDQ', '洪洞西': 'HTV',
            '合肥北城': 'COH', '黄冈': 'KGN', '黄冈东': 'KAN', '横沟桥东': 'HNN', '黄冈西': 'KXN', '洪河': 'HPB', '花湖': 'KHN',
            '鲘门': 'KMQ', '虎门': 'IUQ', '哈密南': 'HLR', '侯马西': 'HPV', '衡南': 'HNG', '淮南东': 'HOH', '合浦': 'HVZ', '霍邱': 'FBH',
            '怀仁东': 'HFV', '华容东': 'HPN', '华容南': 'KRN', '黄石北': 'KSN', '贺胜桥东': 'HLN', '花山南': 'KNN', '霍州东': 'HWV',
            '惠州南': 'KNQ', '军粮城北': 'JMP', '将乐': 'JLS', '建宁县北': 'JCS', '江宁': 'JJH', '句容西': 'JWH', '建水': 'JSM',
            '界首市': 'JUN', '介休东': 'JDV', '晋中': 'JZV', '库伦': 'KLD', '葵潭': 'KTQ', '来宾北': 'UCZ', '灵璧': 'GMH',
            '离堆公园': 'INW', '陆丰': 'LLQ', '禄丰南': 'LQM', '临汾西': 'LXV', '滦河': 'UDP', '漯河西': 'LBN', '灵石东': 'UDV',
            '龙市': 'LAG', '溧水': 'LDH', '黎塘西': 'UKZ', '溧阳': 'LEH', '明港东': 'MDN', '玛纳斯': 'MSR', '庙山': 'MSN',
            '蒙自北': 'MBM', '南城': 'NDG', '南昌西': 'NXG', '南丰': 'NFG', '南湖东': 'NDN', '尼木': 'NMO', '普安': 'PAN', '普宁': 'PEQ',
            '平南南': 'PAZ', '平遥古城': 'PDV', '彭州': 'PMW', '青岛北': 'QHK', '祁东': 'QMQ', '前锋': 'QFB', '岐山': 'QAY',
            '庆盛': 'QSQ', '曲水县': 'QSO', '祁县东': 'QGV', '祁阳': 'QWQ', '全州南': 'QNZ', '仁布': 'RUO', '如东': 'RIH',
            '日喀则': 'RKO', '饶平': 'RVQ', '泗洪': 'GQH', '三明北': 'SHS', '山坡东': 'SBN', '沈丘': 'SQN', '汕尾': 'OGQ',
            '绍兴北': 'SLH', '泗县': 'GPH', '泗阳': 'MPH', '上虞北': 'SSH', '山阴': 'SNV', '深圳北': 'IOQ', '神州': 'SRQ',
            '深圳坪山': 'IFQ', '石嘴山': 'QQJ', '石柱县': 'OSW', '土地堂东': 'TTN', '太谷西': 'TIV', '通海': 'TAM', '通化县': 'TXL',
            '泰宁': 'TNS', '汤逊湖': 'THN', '藤县': 'TAZ', '太原南': 'TNV', '乌龙泉南': 'WFN', '五女山': 'WET', '瓦屋山': 'WAH',
            '闻喜西': 'WOV', '梧州南': 'WBZ', '兴安北': 'XDZ', '许昌东': 'XVF', '项城': 'ERN', '西丰': 'XFT', '襄汾西': 'XTV',
            '孝感北': 'XJN', '咸宁东': 'XKN', '咸宁南': 'UNN', '协荣': 'ROO', '邢台东': 'EDP', '新乡东': 'EGF', '西阳村': 'XQF',
            '信阳东': 'OYN', '咸阳秦都': 'XOY', '迎宾路': 'YFW', '运城北': 'ABV', '岳池': 'AWW', '永福南': 'YBZ', '雨格': 'VTM',
            '洋河': 'GTH', '永济北': 'AJV', '炎陵': 'YAG', '杨陵南': 'YEY', '永泰': 'YTS', '尤溪': 'YXS', '云霄': 'YBS', '宜兴': 'YUH',
            '应县': 'YZV', '攸县南': 'YXG', '余姚北': 'CTH', '诏安': 'ZDS', '正定机场': 'ZHP', '纸坊东': 'ZMN', '织金': 'IZW',
            '左岭': 'ZSN', '驻马店西': 'ZLN', '漳浦': 'ZCS', '庄桥': 'ZQH', '涿州东': 'ZAP', '卓资东': 'ZDC', '郑州东': 'ZAF',
            "广州白云": "GBA", "北京丰台": "FTP"}
# 车次类型
TRAIN_TYPE_MAP = {
    'T': 'T-特快',
    'G': 'GC-高铁/城际',
    'D': 'D-动车',
    'Z': 'Z-直达',
    'K': 'K-快速',
}
# 票的映射关系
TICKET_MAP = {
    "成人票": "1",
    "儿童票": "2",
    "学生票": "3",
    "残军票": "4"
}
# 座位的映射关系
SEAT_MAP = {
    "硬座": "1",
    "硬卧": "3",
    "软卧": "4",
    "一等软座": "7",
    "二等软座": "8",
    "商务座": "9",
    "一等座": "M",
    "二等座": "O",
    "混编硬座": "B",
    "特等座": "P"
}
# 时间段范围
TIME_RANGE_MAP = {
    "00:00--24:00": "00002400",
    "00:00--06:00": "00000600",
    "06:00--12:00": "06001200",
    "12:00--18:00": "12001800",
    "18:00--24:00": "18002400",
}
# 默认的配置文件
DEFAULT_VALUE = ''
DEFAULTS_CONF = {
    'login.username': DEFAULT_VALUE,
    'login.password': DEFAULT_VALUE,
    'login.id_card_last_four_number': DEFAULT_VALUE,
    'login.is_show_browser': '0',

    'cookie_info.from': DEFAULT_VALUE,
    'cookie_info.to': DEFAULT_VALUE,
    'cookie_info.start_date': DEFAULT_VALUE,

    'scheduler.fetch_start_time': DEFAULT_VALUE,

    ## order：车次，选择第几趟，0则从上至下依次点击，必选参数，如果要特定车次，需要先找到车次在列表中的次序，有效值如下：
    #### 0->从上至下点击
    #### 1->第一个车次
    #### 2->第二个车次
    'order_item.order': '0',

    'user_info.users': DEFAULT_VALUE,

    'train_info.train_types': 'D,G',
    'train_info.start_time_range': '00:00--24:00',

    'ticket_info.ticket_type': '成人票',

    'confirm_info.seat_type': '二等座',
    'confirm_info-no_seat_allow': '1',

    'url_info.ticket_url': 'https://kyfw.12306.cn/otn/leftTicket/init',
    'url_info.login_url': 'https://kyfw.12306.cn/otn/resources/login.html',
    'url_info.init_url': 'https://kyfw.12306.cn/otn/view/index.html',
    'url_info.buy_url': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
    'url_info.pay_url': 'https://kyfw.12306.cn/otn/payOrder/init',

    'path_info.driver_name': 'edge',

}
# 必须设置的属性值
REQUIRES = ['login.username', 'login.password', 'cookie_info.from', 'cookie_info.to', 'cookie_info.start_date',
                'user_info.users']
