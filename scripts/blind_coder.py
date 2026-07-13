#!/usr/bin/env python3
"""blind_coder.py — 独立盲编码实验

目的：用与主循环模型(deepseek-v4-pro)不同血统的免费模型，对 EMP-TEST-001
的 14 个案例做独立盲编码（有效层级数 + 形式化信息系统），计算 intercoder
reliability，检验"笨但独立的模型能否充当承重墙的独立对抗源"。

设计纪律：
- 蒙住：只给操作化定义 + 角色表，不给作者的层级数/判定。
- 血统分级：glm-5.2/sensenova-lite 独立；deepseek-v4-flash 同血统对照。
- 输出是信号不是裁决：模型编码 → 算 κ/一致率 → 人来解读。
"""
import json, re, time, sys, urllib.request, urllib.error
from pathlib import Path

SECRETS = json.loads(Path.home().joinpath(".claude/secrets.json").read_text())
SN = SECRETS["sensenova"]
BASE, KEY = SN["base_url"], SN["api_key"]

MODELS = [
    {"id": "sensenova-6.7-flash-lite", "lineage": "商汤",   "independent": True,  "sleep": 0},
    {"id": "glm-5.2",                  "lineage": "智谱",   "independent": True,  "sleep": 6},
    {"id": "deepseek-v4-flash",        "lineage": "DeepSeek","independent": False, "sleep": 0},
]

# === 操作化定义（原样取自 DED-001，蒙住编码者能看到的唯一"标准"） ===
DEFINITION = """
【有效层级 (effective hierarchy level) 的判定标准】
上级 N 做出的决策对下属 N-1 的决策空间构成"实质性约束"（不是建议、不是
咨询）时，N 和 N-1 之间存在一个有效层级。计数时：
- 只数构成实质性决策约束的层级。
- 平行系统（如军事与民政、领土链与氏族链、正副职、共治者）各自独立，
  不叠加进同一条链——取主要治理链条中最长的一条。
- 从最高决策者数到最底层被治理单元（家庭/户/平民）。

【形式化信息系统 (formal information system) 的判定标准】
外在于人脑的、用于存储/传输/处理组织状态信息的系统。
- 是：存在书面文档/标准化表格/统计汇总/数据库/符号记录系统（含结绳、
  图画文字等非文字符号记录）用于行政信息。
- 部分：存在某种外部记录但仅限狭窄用途（如仅占卜/仪式/纪念），未普遍
  用于日常行政。
- 否：无任何外部记录系统，行政信息全靠口头与个人记忆。
"""

# === 14 案例：只有角色表 + 信息描述，删除作者的层级数与判定 ===
CASES = [
    ("印加帝国", "皇帝(Sapa Inca) / 四地区总督(Apu) / 行省总督(约80省) / 巡查官(Okoyrikoq,皇室血亲) / 地方酋长(Kuraka) / 十进制单位首领(1000/500/100/50/10户) / 家庭户",
     "存在 quipu 结绳记事：十进制数值编码、多色分类，各级配专用记录员 quipucamayoc。"),
    ("布干达王国", "国王(Kabaka) / 首相(Katikkiro) / 首席法官与财政官(Omulamuzi/Omuwanika) / 郡长(Abamasaza,10郡) / 副郡长(Abagombolola) / 教区酋长(Abamiluka) / 村长(Abatongole) / 氏族长(Bataka,管氏族土地与征税) / 家庭",
     "无文字系统，行政靠系谱专家、口头法律、议事会辩论。19世纪末阿拉伯文字传入但未用于王国行政。"),
    ("阿散蒂王国", "大王(Asantehene) / 太后(Asantehemaa,共治者) / 联邦区酋长(Amanhene) / 邦国酋长(Omanhene) / 镇区酋长(Ohene) / 长老议事会(Mpanyimfo) / 村长(Odikro) / 血统首领(Abusua Panyin)",
     "纯口头，靠仪式性宣誓、议事会、鼓语历史、口传金凳叙事维持治理。"),
    ("祖鲁王国", "国王(Inkosi) / 太后(Indlovukazi,独立宫廷) / 大酋长兼将军(Induna) / 区域酋长(Amakhosi) / 地方头人(Izinduna) / 家户长(Abanumzane) / 同龄兵团(Amabutho)",
     "纯口头，赞颂诗人(izimbongi)保存王室系谱与法律。"),
    ("蒙古帝国(早期1206-1220)", "大汗 / 万户长 / 千户长 / 百户长 / 十户长 / 户",
     "早期法律(Yassa)与命令口头传承；1220年代后采用回鹘文字、引入书记官开始书面行政。"),
    ("加洛林帝国", "皇帝 / 巡查使(Missi Dominici) / 伯爵与主教(约250-300郡) / 子爵与代理官 / 陪审员(Scabini) / 地方社区",
     "敕令(capitularies)书面颁布，巡查使书面报告；但中央无档案、文件由个人保管、读写不普遍、命令常口头传达。"),
    ("阿兹特克帝国", "大帝(Huey Tlatoani) / 三方联盟伙伴(Tetzcoco,Tacuba) / 城邦统治者(Altepetl) / 土地社会单位首领(Calpulli) / 家庭",
     "图画文字贡赋记录(Codex Mendoza/Matrícula de Tributos)，20进制数值，贡赋按省份×商品逐项记录。"),
    ("古埃及古王国", "法老 / 维齐尔(Vizier) / 诺姆长(约42省) / 地方官员 / 村长 / 农民",
     "圣书体+僧侣体文字，庞大书记官阶层，税收记录、土地登记、劳动力征用、粮库管理。"),
    ("商朝中国", "王 / 区域领主(侯/伯) / 地方官(田) / 聚落首领(邑) / 平民(众)",
     "甲骨文用于占卜和记录王的活动，未扩展为全面行政文书；行政多靠口头与贵族个人关系。"),
    ("夏威夷王国(接触前)", "大王(Ali'i Nui) / 高级酋长(Ali'i,管Moku大区) / 土地管理人(Konohiki,管Ahupua'a流域社区) / 平民(Maka'āinana)",
     "纯口头，系谱吟唱者保存酋长血统，禁忌(Kapu)体系口头传承。"),
    ("吴哥高棉帝国", "神王(提婆罗阇) / 王室家族与高级祭司 / 省级总督 / 地方官员 / 村长 / 农民",
     "梵文与古高棉文碑铭记土地赠与、劳动义务、税收；但碑铭主用于宗教纪念，日常行政多口头。"),
    ("达荷美王国", "国王 / 首相(Migan) / 省级酋长 / 村长 / 家户",
     "纯口头；年度仪式作口头普查问责，国王集会接收各地报告；用 cowrie 贝壳结绳计数；晚期有限阿拉伯文字。"),
    ("罗马帝国(元首制)", "皇帝 / 行省总督与皇帝使节 / 财务官(Procurator) / 城市元老院(Decurions) / 地方长官(Magistri) / 市民",
     "拉丁文行政文书，行省普查、税收记录、军事文书、罗马法书面体系、帝国邮政。"),
    ("松海帝国", "皇帝(Askia) / 中央部长(财政/司法/海军等) / 行省总督 / 地方酋长 / 村长 / 家庭",
     "使用阿拉伯文字，学者阶层提供行政支持；但日常行政多靠口头，文字主用于外交、法律裁决、宗教。"),
]

# === 作者(主循环 deepseek-v4-pro)的编码，用作参照。区间表示模型落入即算一致。===
AUTHOR = [
    {"lv": (6,6),   "info": "是"},   # 印加
    {"lv": (7,7),   "info": "否"},   # 布干达
    {"lv": (6,7),   "info": "否"},   # 阿散蒂
    {"lv": (5,6),   "info": "否"},   # 祖鲁
    {"lv": (5,5),   "info": "部分"}, # 蒙古早期
    {"lv": (4,5),   "info": "是"},   # 加洛林
    {"lv": (4,4),   "info": "是"},   # 阿兹特克
    {"lv": (5,5),   "info": "是"},   # 古埃及
    {"lv": (4,4),   "info": "部分"}, # 商朝
    {"lv": (3,4),   "info": "否"},   # 夏威夷
    {"lv": (5,5),   "info": "是"},   # 吴哥
    {"lv": (4,5),   "info": "否"},   # 达荷美
    {"lv": (5,5),   "info": "是"},   # 罗马
    {"lv": (5,5),   "info": "部分"}, # 松海
]

PROMPT_TMPL = """你是一名独立的历史行政结构编码员。严格按给定的判定标准，对下面这个前现代政体编码。不要依赖你对"标准答案"的猜测，只依据标准和角色表推理。

{definition}

【待编码政体】{name}
角色链（从高到低）：{roles}
信息系统事实描述：{info}

请只输出一个 JSON 对象，不要任何多余文字：
{{"effective_levels": <整数,有效层级数>, "info_system": "<是|部分|否>", "reason": "<一句话依据>"}}"""


def call(model, prompt, timeout=40):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "reasoning_effort": "none",  # 关掉 sensenova-lite/glm 的默认思维链
        "max_tokens": 800,
    }
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"]


def parse(text):
    m = re.search(r"\{[^{}]*\}", text, re.S)
    if not m:
        return None
    try:
        o = json.loads(m.group(0))
        return {"lv": int(o["effective_levels"]), "info": str(o["info_system"]).strip()}
    except Exception:
        return None


def ping():
    print("=== 存活探测 ===")
    alive = []
    for m in MODELS:
        try:
            t = time.time()
            call(m["id"], "回复一个字：好", timeout=15)
            print(f"  ✅ {m['id']:28s} ({m['lineage']}, {'独立' if m['independent'] else '同血统对照'})  {time.time()-t:.1f}s")
            alive.append(m)
        except Exception as e:
            print(f"  ❌ {m['id']:28s} 失效: {str(e)[:60]}")
    return alive


def code_all(models):
    print("\n=== 盲编码（14 案例 × %d 模型） ===" % len(models))
    results = {m["id"]: [] for m in models}
    for m in models:
        print(f"\n-- {m['id']} ({m['lineage']}) --")
        for i, (name, roles, info) in enumerate(CASES):
            prompt = PROMPT_TMPL.format(definition=DEFINITION, name=name, roles=roles, info=info)
            got = None
            for attempt in range(2):
                try:
                    got = parse(call(m["id"], prompt))
                    if got:
                        break
                except Exception as e:
                    time.sleep(3)
            results[m["id"]].append(got)
            tag = f"lv={got['lv']} info={got['info']}" if got else "解析失败"
            print(f"  {i+1:2d}. {name:18s} {tag}")
            if m["sleep"]:
                time.sleep(m["sleep"])
    return results


def kappa(a, b, cats):
    """Cohen's κ，a/b 为等长标签列表。"""
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for x, y in pairs if x == y) / n
    pe = 0.0
    for c in cats:
        pa = sum(1 for x, _ in pairs if x == c) / n
        pb = sum(1 for _, y in pairs if y == c) / n
        pe += pa * pb
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def report(models, results):
    print("\n" + "=" * 60)
    print("一致性分析（对照作者 = 主循环 deepseek-v4-pro）")
    print("=" * 60)
    for m in models:
        rs = results[m["id"]]
        lv_hit = lv_within1 = info_hit = valid = 0
        model_info, author_info = [], []
        absdev = []
        for got, au in zip(rs, AUTHOR):
            if not got:
                continue
            valid += 1
            lo, hi = au["lv"]
            if lo <= got["lv"] <= hi:
                lv_hit += 1
            if lo - 1 <= got["lv"] <= hi + 1:
                lv_within1 += 1
            mid = (lo + hi) / 2
            absdev.append(abs(got["lv"] - mid))
            if got["info"] == au["info"]:
                info_hit += 1
            model_info.append(got["info"])
            author_info.append(au["info"])
        k = kappa(model_info, author_info, ["是", "部分", "否"])
        tag = "独立" if m["independent"] else "同血统对照"
        print(f"\n{m['id']} ({m['lineage']}, {tag})  有效样本 {valid}/14")
        print(f"  层级 落入作者区间 : {lv_hit}/{valid}")
        print(f"  层级 ±1 内       : {lv_within1}/{valid}")
        print(f"  层级 平均绝对偏差: {sum(absdev)/len(absdev):.2f}" if absdev else "  层级偏差: —")
        print(f"  信息系统 完全一致: {info_hit}/{valid}")
        print(f"  信息系统 Cohen's κ: {k:.3f}" if k is not None else "  κ: —")

    # 独立模型之间的一致性（错误是否真的不相关）
    inds = [m for m in models if m["independent"]]
    if len(inds) >= 2:
        a, b = results[inds[0]["id"]], results[inds[1]["id"]]
        ai = [x["info"] if x else None for x in a]
        bi = [x["info"] if x else None for x in b]
        k = kappa(ai, bi, ["是", "部分", "否"])
        lv_agree = sum(1 for x, y in zip(a, b) if x and y and x["lv"] == y["lv"])
        print(f"\n独立模型互检 {inds[0]['id']} vs {inds[1]['id']}:")
        print(f"  层级完全相同: {lv_agree}/14   信息系统 κ: {k:.3f}" if k is not None else f"  层级完全相同: {lv_agree}/14")


if __name__ == "__main__":
    alive = ping()
    if not alive:
        print("\n无可用模型，终止。")
        sys.exit(1)
    results = code_all(alive)
    report(alive, results)
    # 存盘供报告引用
    out = Path(__file__).parent.parent / "L3-deductions" / "empirical-tests" / "blind-coding-raw.json"
    out.write_text(json.dumps({m["id"]: results[m["id"]] for m in alive}, ensure_ascii=False, indent=2))
    print(f"\n原始编码已存: {out}")
