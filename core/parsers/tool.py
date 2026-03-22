import base64,requests,random,string,re,chardet,urllib.parse
import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=CryptographyDeprecationWarning)
    import paramiko
from scp import SCPClient

def get_encoding(file):
    with open(file,'rb') as f:
        return chardet.detect(f.read())['encoding']
    
def saveFile(path,content):
    file = open(path, mode='w',encoding='utf-8')
    file.write(content)
    file.close()

regex_patterns = {
    '🇭🇰': re.compile(r'香港|沪港|呼港|中港|HKT|HKBN|HGC|WTT|CMI|穗港|广港|京港|🇭🇰|HK|Hongkong|Hong Kong|HongKong|HONG KONG'),
    '🇹🇼': re.compile(r'台湾|台灣|臺灣|台北|台中|新北|彰化|台|CHT|HINET|TW|Taiwan|TAIWAN'),
    '🇲🇴': re.compile(r'澳门|澳門|(\s|-)?MO\d*|CTM|MAC|Macao|Macau'),
    '🇸🇬': re.compile(r'新加坡|狮城|獅城|沪新|京新|泉新|穗新|深新|杭新|广新|廣新|滬新|SG|Singapore|SINGAPORE'),
    '🇯🇵': re.compile(r'日本|东京|東京|大阪|埼玉|京日|苏日|沪日|广日|上日|穗日|川日|中日|泉日|杭日|深日|JP|Japan|JAPAN'),
    '🇺🇸': re.compile(r'美国|美國|京美|硅谷|凤凰城|洛杉矶|西雅图|圣何塞|芝加哥|哥伦布|纽约|广美|(\s|-)?(?<![AR])US\d*|USA|America|United States'),
    '🇰🇷': re.compile(r'韩国|韓國|首尔|首爾|韩|韓|春川|KOR|KR|Kr|(?<!North\s)Korea'),
    '🇰🇵': re.compile(r'朝鲜|KP|North Korea'),
    '🇷🇺': re.compile(r'俄罗斯|俄羅斯|毛子|俄国|RU|RUS|Russia'),
    '🇮🇳': re.compile(r'印度|孟买|(\s|-)?IN(?!FO)\d*|IND|India|INDIA|Mumbai'),
    '🇮🇩': re.compile(r'印尼|印度尼西亚|雅加达|ID|IDN|Indonesia'),
    '🇬🇧': re.compile(r'英国|英國|伦敦|UK|England|United Kingdom|Britain'),
    '🇩🇪': re.compile(r'德国|德國|法兰克福|(\s|-)?DE\d*|(\s|-)?GER\d*|🇩🇪|German|GERMAN'),
    '🇫🇷': re.compile(r'法国|法國|巴黎|FR(?!EE)|France'),
    '🇩🇰': re.compile(r'丹麦|丹麥|DK|DNK|Denmark'),
    '🇳🇴': re.compile(r'挪威|(\s|-)?NO\d*|Norway'),
    '🇮🇹': re.compile(r'意大利|義大利|米兰|(\s|-)?IT\d*|Italy|Nachash'),
    '🇻🇦': re.compile(r'梵蒂冈|梵蒂岡|(\s|-)?VA\d*|Vatican City'),
    '🇧🇪': re.compile(r'比利时|比利時|(\s|-)?BE\d*|Belgium'),
    '🇦🇺': re.compile(r'澳大利亚|澳洲|墨尔本|悉尼|(\s|-)?AU\d*|Australia|Sydney'),
    '🇨🇦': re.compile(r'加拿大|蒙特利尔|温哥华|多伦多|多倫多|滑铁卢|楓葉|枫叶|CA|CAN|Waterloo|Canada|CANADA'),
    '🇲🇾': re.compile(r'马来西亚|马来|馬來|MY|Malaysia|MALAYSIA'),
    '🇲🇻': re.compile(r'马尔代夫|馬爾代夫|(\s|-)?MV\d*|Maldives'),
    '🇹🇷': re.compile(r'土耳其|伊斯坦布尔|(\s|-)?TR\d|TR_|TUR|Turkey'),
    '🇵🇭': re.compile(r'菲律宾|菲律賓|(\s|-)?PH\d*|Philippines'),
    '🇹🇭': re.compile(r'泰国|泰國|曼谷|(\s|-)?TH\d*|Thailand'),
    '🇻🇳': re.compile(r'越南|胡志明市|(\s|-)?VN\d*|Vietnam'),
    '🇰🇭': re.compile(r'柬埔寨|(\s|-)?KH\d*|Cambodia'),
    '🇱🇦': re.compile(r'老挝|(\s|-)(?<!RE)?LA\d*|Laos'),
    '🇧🇩': re.compile(r'孟加拉|(\s|-)?BD\d*|Bengal'),
    '🇲🇲': re.compile(r'缅甸|緬甸|(\s|-)?MM\d*|Myanmar'),
    '🇱🇧': re.compile(r'黎巴嫩|(\s|-)?LB\d*|Lebanon'),
    '🇺🇦': re.compile(r'乌克兰|烏克蘭|(\s|-)?UA\d*|Ukraine'),
    '🇭🇺': re.compile(r'匈牙利|(\s|-)?HU\d*|Hungary'),
    '🇨🇭': re.compile(r'瑞士|苏黎世|(\s|-)?CH\d*|Switzerland'),
    '🇸🇪': re.compile(r'瑞典|SE|Sweden'),
    '🇱🇺': re.compile(r'卢森堡|(\s|-)?LU\d*|Luxembourg'),
    '🇦🇹': re.compile(r'奥地利|奧地利|维也纳|(\s|-)?AT\d*|Austria'),
    '🇨🇿': re.compile(r'捷克|(\s|-)?CZ\d*|Czechia'),
    '🇬🇷': re.compile(r'希腊|希臘|(\s|-)?GR(?!PC)\d*|Greece'),
    '🇮🇸': re.compile(r'冰岛|冰島|(\s|-)?IS\d*|ISL|Iceland'),
    '🇳🇿': re.compile(r'新西兰|新西蘭|(\s|-)?NZ\d*|New Zealand'),
    '🇮🇪': re.compile(r'爱尔兰|愛爾蘭|都柏林|(\s|-)?IE(?!PL)\d*|Ireland|IRELAND'),
    '🇮🇲': re.compile(r'马恩岛|馬恩島|(\s|-)?IM\d*|Mannin|Isle of Man'),
    '🇱🇹': re.compile(r'立陶宛|(\s|-)?LT\d*|Lithuania'),
    '🇫🇮': re.compile(r'芬兰|芬蘭|赫尔辛基|(\s|-)?FI\d*|Finland'),
    '🇦🇷': re.compile(r'阿根廷|(\s|-)(?<!W)?AR(?!P)\d*|Argentina'),
    '🇺🇾': re.compile(r'乌拉圭|烏拉圭|(\s|-)?UY\d*|Uruguay'),
    '🇵🇾': re.compile(r'巴拉圭|(\s|-)?PY\d*|Paraguay'),
    '🇯🇲': re.compile(r'牙买加|牙買加|(\s|-)?JM(?!S)\d*|Jamaica'),
    '🇸🇷': re.compile(r'苏里南|蘇里南|(\s|-)?SR\d*|Suriname'),
    '🇨🇼': re.compile(r'库拉索|庫拉索|(\s|-)?CW\d*|Curaçao'),
    '🇨🇴': re.compile(r'哥伦比亚|(\s|-)?CO\d*|Colombia'),
    '🇪🇨': re.compile(r'厄瓜多尔|(\s|-)?EC\d*|Ecuador'),
    '🇪🇸': re.compile(r'西班牙|\b(\s|-)?ES\d*|Spain'),
    '🇵🇹': re.compile(r'葡萄牙|Portugal'),
    '🇮🇱': re.compile(r'以色列|(\s|-)?IL\d*|Israel'),
    '🇸🇦': re.compile(r'沙特|利雅得|吉达|Saudi|Saudi Arabia'),
    '🇲🇳': re.compile(r'蒙古|(\s|-)?MN\d*|Mongolia'),
    '🇦🇪': re.compile(r'阿联酋|迪拜|(\s|-)?AE\d*|Dubai|United Arab Emirates'),
    '🇦🇿': re.compile(r'阿塞拜疆|(\s|-)?AZ\d*|Azerbaijan'),
    '🇦🇲': re.compile(r'亚美尼亚|亞美尼亞|(\s|-)?AM\d*|Armenia'),
    '🇰🇿': re.compile(r'哈萨克斯坦|哈薩克斯坦|(\s|-)?KZ\d*|Kazakhstan'),
    '🇰🇬': re.compile(r'吉尔吉斯坦|吉尔吉斯斯坦|(\s|-)?KG\d*|Kyrghyzstan'),
    '🇺🇿': re.compile(r'乌兹别克斯坦|烏茲別克斯坦|(\s|-)?UZ\d*|Uzbekistan'),
    '🇧🇷': re.compile(r'巴西|圣保罗|维涅杜|(?<!G)BR|Brazil'),
    '🇨🇱': re.compile(r'智利|(\s|-)?CL\d*|Chile|CHILE'),
    '🇵🇪': re.compile(r'秘鲁|祕魯|(\s|-)?PE\d*|Peru'),
    '🇨🇺': re.compile(r'古巴|Cuba'),
    '🇧🇹': re.compile(r'不丹|Bhutan'),
    '🇦🇩': re.compile(r'安道尔|(\s|-)?AD\d*|Andorra'),
    '🇲🇹': re.compile(r'马耳他|(\s|-)?MT\d*|Malta'),
    '🇲🇨': re.compile(r'摩纳哥|摩納哥|(\s|-)?MC\d*|Monaco'),
    '🇷🇴': re.compile(r'罗马尼亚|(\s|-)?RO\d*|Rumania'),
    '🇧🇬': re.compile(r'保加利亚|保加利亞|(\s|-)?BG(?!P)\d*|Bulgaria'),
    '🇭🇷': re.compile(r'克罗地亚|克羅地亞|(\s|-)?HR\d*|Croatia'),
    '🇲🇰': re.compile(r'北马其顿|北馬其頓|(\s|-)?MK\d*|North Macedonia'),
    '🇷🇸': re.compile(r'塞尔维亚|塞爾維亞|(\s|-)?RS\d*|Seville|Sevilla'),
    '🇨🇾': re.compile(r'塞浦路斯|(\s|-)?CY\d*|Cyprus'),
    '🇱🇻': re.compile(r'拉脱维亚|(\s|-)?LV\d*|Latvia|Latvija'),
    '🇲🇩': re.compile(r'摩尔多瓦|摩爾多瓦|(\s|-)?MD\d*|Moldova'),
    '🇸🇰': re.compile(r'斯洛伐克|(\s|-)?SK\d*|Slovakia'),
    '🇪🇪': re.compile(r'爱沙尼亚|(\s|-)?EE\d*|Estonia'),
    '🇧🇾': re.compile(r'白俄罗斯|白俄羅斯|(\s|-)?BY\d*|White Russia|Republic of Belarus|Belarus'),
    '🇧🇳': re.compile(r'文莱|汶萊|BRN|Negara Brunei Darussalam'),
    '🇬🇺': re.compile(r'关岛|關島|(\s|-)?GU\d*|Guam'),
    '🇫🇯': re.compile(r'斐济|斐濟|(\s|-)?FJ\d*|Fiji'),
    '🇯🇴': re.compile(r'约旦|約旦|(\s|-)?JO\d*|Jordan'),
    '🇬🇪': re.compile(r'格鲁吉亚|格魯吉亞|(\s|-)?GE(?!R)\d*|Georgia'),
    '🇬🇮': re.compile(r'直布罗陀|直布羅陀|(\s|-)(?<!CN2)?GI(?!A)\d*|Gibraltar'),
    '🇸🇲': re.compile(r'圣马力诺|聖馬利諾|(\s|-)?SM\d*|San Marino'),
    '🇳🇵': re.compile(r'尼泊尔|(\s|-)?NP\d*|Nepal'),
    '🇫🇴': re.compile(r'法罗群岛|法羅群島|(\s|-)(?<!IN)?FO\d*|Faroe Islands'),
    '🇦🇽': re.compile(r'奥兰群岛|奧蘭群島|(\s|-)?AX\d*|Åland'),
    '🇸🇮': re.compile(r'斯洛文尼亚|斯洛文尼亞|(\s|-)?SI\d*|Slovenia'),
    '🇦🇱': re.compile(r'阿尔巴尼亚|阿爾巴尼亞|(\s|-)?AL\d*|Albania'),
    '🇹🇱': re.compile(r'东帝汶|東帝汶|(\s|-)?TL(?!S)\d*|East Timor'),
    '🇵🇦': re.compile(r'巴拿马|巴拿馬|(\s|-)?PA\d*|Panama'),
    '🇧🇲': re.compile(r'百慕大|(\s|-)?BM\d*|Bermuda'),
    '🇬🇱': re.compile(r'格陵兰|格陵蘭|(\s|-)?GL\d*|Greenland'),
    '🇨🇷': re.compile(r'哥斯达黎加|(\s|-)?CR\d*|Costa Rica'),
    '🇻🇬': re.compile(r'英属维尔京|(\s|-)?VG\d*|British Virgin Islands'),
    '🇻🇮': re.compile(r'美属维尔京|(\s|-)?VI\d*|United States Virgin Islands'),
    '🇲🇽': re.compile(r'墨西哥|MX|MEX|MEX|MEXICO'),
    '🇲🇪': re.compile(r'黑山|(\s|-)?ME\d*|Montenegro'),
    '🇳🇱': re.compile(r'荷兰|荷蘭|尼德蘭|阿姆斯特丹|NL|Netherlands|Amsterdam'),
    '🇵🇱': re.compile(r'波兰|波蘭|(?<!I)(?<!IE)(\s|-)?PL\d*|POL|Poland'),
    '🇩🇿': re.compile(r'阿尔及利亚|(\s|-)?DZ\d*|Algeria'),
    '🇧🇦': re.compile(r'波黑共和国|波黑|(\s|-)?BA\d*|Bosnia and Herzegovina'),
    '🇱🇮': re.compile(r'列支敦士登|(\s|-)?LI\d*|Liechtenstein'),
    '🇷🇪': re.compile(r'留尼汪|留尼旺|(\s|-)?RE(?!LAY)\d*|Réunion|Reunion'),
    '🇿🇦': re.compile(r'南非|约翰内斯堡|(\s|-)?ZA\d*|South Africa|Johannesburg'),
    '🇪🇬': re.compile(r'埃及|(\s|-)?EG\d*|Egypt'),
    '🇬🇭': re.compile(r'加纳|(\s|-)?GH\d*|Ghana'),
    '🇲🇱': re.compile(r'马里|馬里|(\s|-)?ML\d*|Mali'),
    '🇲🇦': re.compile(r'摩洛哥|(\s|-)?MA\d*|Morocco'),
    '🇹🇳': re.compile(r'突尼斯|(\s|-)?TN\d*|Tunisia'),
    '🇱🇾': re.compile(r'利比亚|(\s|-)?LY\d*|Libya'),
    '🇰🇪': re.compile(r'肯尼亚|肯尼亞|(\s|-)?KE\d*|Kenya'),
    '🇷🇼': re.compile(r'卢旺达|盧旺達|(\s|-)?RW\d*|Rwanda'),
    '🇨🇻': re.compile(r'佛得角|維德角|(\s|-)?CV\d*|Cape Verde'),
    '🇦🇴': re.compile(r'安哥拉|(\s|-)?AO\d*|Angola'),
    '🇳🇬': re.compile(r'尼日利亚|尼日利亞|拉各斯|(\s|-)?NG\d*|Nigeria'),
    '🇲🇺': re.compile(r'毛里求斯|(\s|-)?MU\d*|Mauritius'),
    '🇴🇲': re.compile(r'阿曼|(\s|-)?OM\d*|Oman'),
    '🇧🇭': re.compile(r'巴林|(\s|-)?BH\d*|Bahrain'),
    '🇮🇶': re.compile(r'伊拉克|(\s|-)?IQ\d*|Iraq'),
    '🇮🇷': re.compile(r'伊朗|(\s|-)?IR\d*|Iran'),
    '🇦🇫': re.compile(r'阿富汗|(\s|-)?AF\d*|Afghanistan'),
    '🇵🇰': re.compile(r'巴基斯坦|(\s|-)?PK\d*|Pakistan|PAKISTAN'),
    '🇶🇦': re.compile(r'卡塔尔|卡塔爾|(\s|-)?QA\d*|Qatar'),
    '🇸🇾': re.compile(r'叙利亚|敘利亞|(\s|-)?SY\d*|Syria'),
    '🇱🇰': re.compile(r'斯里兰卡|斯里蘭卡|(\s|-)?LK\d*|Sri Lanka'),
    '🇻🇪': re.compile(r'委内瑞拉|(\s|-)?VE\d*|Venezuela'),
    '🇬🇹': re.compile(r'危地马拉|(\s|-)?GT\d*|Guatemala'),
    '🇵🇷': re.compile(r'波多黎各|(\s|-)?PR\d*|Puerto Rico'),
    '🇰🇾': re.compile(r'开曼群岛|開曼群島|盖曼群岛|凯门群岛|(\s|-)?KY\d*|Cayman Islands'),
    '🇸🇯': re.compile(r'斯瓦尔巴|扬马延|(\s|-)?SJ\d*|Svalbard|Mayen'),
    '🇭🇳': re.compile(r'洪都拉斯|Honduras'),
    '🇳🇮': re.compile(r'尼加拉瓜|(\s|-)?NI\d*|Nicaragua'),
    '🇦🇶': re.compile(r'南极|南極|(\s|-)?AQ\d*|Antarctica'),
    '🇨🇳': re.compile(r'中国|中國|江苏|北京|上海|广州|深圳|杭州|徐州|青岛|宁波|镇江|沈阳|济南|回国|back|(\s|-)?CN(?!2GIA)\d*|China'),
}
def rename(input_str):
    for country_code, pattern in regex_patterns.items():
        if input_str.startswith(country_code):
            return country_code + ' ' + input_str[len(country_code):].strip()
        if pattern.search(input_str):
            if input_str.startswith('🇺🇲'):
                return country_code + ' ' + input_str[len('🇺🇲'):].strip()
            else:
                return country_code + ' ' + input_str
    return input_str

def b64Decode(str):
    str = urllib.parse.unquote(str.strip())
    str += (len(str)%4)*'='
    return base64.urlsafe_b64decode(str)

def readFile(path):
    file = open(path,'rb')
    content = file.read()
    file.close()
    return content

def noblankLine(data):
    lines = data.splitlines()
    newdata = ''
    for index in range(len(lines)):
        line = lines[index]
        t = line.strip()
        if len(t)>0:
            newdata += t
            if index+1<len(lines):
                newdata += '\n'
    return newdata

def firstLine(data):
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        if line:
            return line

def genName(length=8):
    name = ''
    for i in range(length):
        name += random.choice(string.ascii_letters+string.digits)
    return name

def is_ip(str):
    return re.search(r'^\d+\.\d+\.\d+\.\d+$',str)

def get_protocol(s):
    try:
        m = re.search(r'^(.+?)://', s)
    except Exception as e:
        return None
    if m:
        if m.group(1) == 'hy2':
            s = re.sub(r'^(.+?)://', 'hysteria2://', s)
            m = re.search(r'^(.+?)://', s)
        if m.group(1) == 'wireguard':
            s = re.sub(r'^(.+?)://', 'wg://', s)
            m = re.search(r'^(.+?)://', s)
        if m.group(1) == 'http2':
            s = re.sub(r'^(.+?)://', 'http://', s)
            m = re.search(r'^(.+?)://', s)
        if m.group(1) == 'socks5':
            s = re.sub(r'^(.+?)://', 'socks://', s)
            m = re.search(r'^(.+?)://', s)
        return m.group(1)

def checkKeywords(keywords,str):
    if not keywords:
        return False
    for keyword in keywords:
        if str.find(keyword)>-1:
            return True
    return False

def filterNodes(nodelist,keywords):
    newlist = []
    if not keywords:
        return nodelist
    for node in nodelist:
        if not checkKeywords(keywords,node['name']):
            newlist.append(node)
        else:
            print('过滤节点名称 '+node['name'])
            print('Lọc tên proxy'+node['name'])
    return newlist

def replaceStr(nodelist,keywords):
    if not keywords:
        return nodelist
    for node in nodelist:
        for k in keywords:
            node['name'] = node['name'].replace(k,'').strip()
    return nodelist

def proDuplicateNodeName(nodes):
    names = []
    for key in nodes.keys():
        nodelist = nodes[key]
        for node in nodelist:
            index = 2
            s = node['tag']
            while node['tag'] in names:
                node['tag'] = s + ' ' + str(index)
                index += 1
            names.append(node['tag'])

def removeNodes(nodelist):
    newlist = []
    temp_list=[]
    i=0
    for node in nodelist:
        _node = {'server':node['server'],'port':node['port']}
        if _node in temp_list:
            i+=1
        else:
            temp_list.append(_node)
            newlist.append(node)
    print('去除了 '+str(i)+' 个重复节点')
    print('Đã xóa các proxy trùng lặp '+str(i))
    print('实际获取 '+str(len(newlist))+' 个节点')
    print('Thực tế nhận được '+str(len(newlist))+' proxy')
    return newlist

def prefixStr(nodelist,prestr):
    for node in nodelist:
        node['name'] = prestr+node['name'].strip()
    return nodelist

def getResponse(url, custom_user_agent=None):
    response = None
    headers = {
        'User-Agent': custom_user_agent if custom_user_agent else 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15'
        #'User-Agent': 'clash.meta'
    }
    try:
        response = requests.get(url,headers=headers,timeout=5000)
        if response.status_code==200:
            return response
        else:
            return None
    except:
        return None
    
class ConfigSSH:
    server = {'ip':None,'port':22,'user':None,'password':''}
    def __init__(self,server:dict) -> None:
        for k in self.server:
            if k != 'port' and not k in server.keys():
                return None
            if k in server.keys():
                self.server[k] = server[k]
    def connect(self):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.server['ip'],port=22, username=self.server['user'], password=self.server['password'])
        self.ssh = ssh

    def execCMD(self,command:str):
        stdin, stdout, stderr = self.ssh.exec_command(command) 
        print(stdout.read().decode('utf-8')) 

    def uploadFile(self,source:str,target:str):
        scp = SCPClient(self.ssh.get_transport())
        scp.put(source, recursive=True, remote_path=target)

    def getFile(self,remote:str,local:str):
        scp = SCPClient(self.ssh.get_transport())
        scp.get(remote,local)

    def close(self):
        self.ssh.close()
