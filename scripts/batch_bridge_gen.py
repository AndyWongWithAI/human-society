#!/usr/bin/env python3
"""batch_bridge_gen.py — 批量生成 L2 bridge YAML（免费模型起草，供 l2_verify 管线消费）。

20 条 bridge 选题原则:
  1. 优先覆盖低引用 L1 概念(conflict/hierarchy/power/goal/measurement/morality)
  2. 优先跨概念对(从 L2 组合缺口扫描)
  3. 每个 bridge 配有 2-3 个 applicable_sources(确保 IEA ≥ 1.2)
  4. 可证伪、有经验锚点

用法:
    python scripts/batch_bridge_gen.py              # 生成全部 20 条
    python scripts/batch_bridge_gen.py --dry-run    # 只列选题
    python scripts/batch_bridge_gen.py --start 0 --count 5  # 生成第 0-4 条
"""

import sys, os, json, subprocess, argparse, time, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS_PATH = os.path.expanduser("~/.claude/secrets.json")

# ── 20 条 Bridge Briefs ──────────────────────────────────────
BRIDGES = [
    # === 低引用概念覆盖 ===
    {
        "id": "BR-L2-033", "slug": "conflict-escalation-loss-aversion",
        "title": "冲突升级中的损失厌恶不对称",
        "domain": ["冲突研究", "行为经济学"],
        "bridges_to": ["CONCEPT-conflict", "CONCEPT-agent", "CONCEPT-value"],
        "thesis": "当冲突双方感知到'已有损失'时，继续冲突的意愿显著强于'已有收益'时——因为损失厌恶(Kahneman-Tversky 1979)使撤回被视为'实现损失'而继续被视为'可能挽回'。该机制预测:冲突持续时间与已沉没成本正相关，且第三方调解在冲突早期介入的成功率显著高于后期。",
        "sources": [
            "behavioral_economics — 损失厌恶 + 沉没成本谬误的实验室与田野证据(Kahneman-Tversky 1979; Arkes-Blumer 1985; Staw 1976 escalation of commitment)",
            "conflict_studies — 内战持续时间与资源沉没的实证(Fearon 2004; Collier-Hoeffler-Ward 2009);调解时机的成功率分布",
        ],
    },
    {
        "id": "BR-L2-034", "slug": "hierarchy-span-of-control",
        "title": "层级深度与管理幅度的认知约束",
        "domain": ["组织理论", "认知科学"],
        "bridges_to": ["CONCEPT-hierarchy", "CONCEPT-agent", "CONCEPT-information"],
        "thesis": "人类层级的有效管理幅度受认知约束——Dunbar数(~150)是社会关系上限，组织层级中一个人的直接有效下属数(~5-9)受工作记忆限制。超出此幅度时，上级对下级的信息处理从'逐一关注'切换为'统计抽样'，控制精度非线性下降。",
        "sources": [
            "organizational_behavior — Urwick(1956)管理幅度原则;Simon(1947)有限理性在组织设计中的应用;Graicunas(1937)互动关系数公式",
            "cognitive_science — Miller(1956)7±2;Dunbar(1992)社会脑假说;工作记忆容量个体差异与领导效能的相关研究",
        ],
    },
    {
        "id": "BR-L2-035", "slug": "goal-shielding-under-scarcity",
        "title": "稀缺状态下的目标屏蔽效应",
        "domain": ["认知科学", "行为经济学"],
        "bridges_to": ["CONCEPT-goal", "CONCEPT-agent", "CONCEPT-resource"],
        "thesis": "当资源稀缺(时间/金钱/注意力)时，个体自动激活'目标屏蔽'(goal shielding)——将认知资源集中于最紧迫目标，同时抑制次要目标。此效应的适应价值在于短期生存优化，但代价是长期目标被系统性忽略(隧道效应)。",
        "sources": [
            "cognitive_science — Shah-Friedman-Kruglanski(2002)目标屏蔽理论;Bargh-Gollwitzer(1994)自动目标激活",
            "behavioral_economics — Mullainathan-Shafir(2013)稀缺的认知税;Mani et al.(2013)贫困对认知带宽的因果效应(农田实验)",
        ],
    },
    {
        "id": "BR-L2-036", "slug": "power-empathy-reduction",
        "title": "权力对共情能力的系统性削弱",
        "domain": ["社会心理学", "权力研究"],
        "bridges_to": ["CONCEPT-power", "CONCEPT-agent", "CONCEPT-cooperation"],
        "thesis": "权力(对他人资源的非对称控制力)系统性降低个体的共情准确性——高权力者对面部表情的识别准确率下降、对他人视角的采纳减少。机制:权力降低了个体'需要他人'的感知→共情作为一种社交信息收集工具被闲置→用进废退。这不是人格特质——同一个体在获得权力后共情下降，失去权力后恢复。",
        "sources": [
            "social_psychology — Galinsky et al.(2006)权力与视角采纳;Kraus et al.(2010)社会经济地位与共情准确性;Van Kleef et al.(2008)权力与情绪识别",
            "neuroscience — Hogeveen et al.(2014)权力启动对镜像神经元活动的抑制;Obbi et al.(2015)经颅磁刺激(TMS)研究",
        ],
    },
    {
        "id": "BR-L2-037", "slug": "quantification-erodes-qualitative-judgment",
        "title": "量化指标的引入削弱定性判断能力",
        "domain": ["组织社会学", "认知科学"],
        "bridges_to": ["CONCEPT-measurement", "CONCEPT-agent", "CONCEPT-goal"],
        "thesis": "当一个组织对某领域引入量化绩效指标后，个体对该领域的定性专业判断能力随时间下降——因为'看数字'替代了'看现场'。此为Goodhart法则的认知版本:当度量成为目标，它不仅扭曲行为(经典Goodhart)，还萎缩了度量之外的感知能力。",
        "sources": [
            "organizational_sociology — Campbell(1979)定量化的社会代价;Power(1997)审计社会;Espeland-Sauder(2007)排名与量化的反身性效应",
            "cognitive_science — 技能退化的认知机制(用进废退);专业知识的隐性维度(Polyani 1966 默会知识;Dreyfus-Dreyfus 1986 技能习得模型)",
        ],
    },
    {
        "id": "BR-L2-038", "slug": "moral-dumbfounding-universal",
        "title": "道德 dumbfounding 的跨文化普遍性",
        "domain": ["道德心理学", "文化人类学"],
        "bridges_to": ["CONCEPT-morality", "CONCEPT-norm", "CONCEPT-agent"],
        "thesis": "'道德 dumbfounding'(个体坚持某行为是错的但无法给出理性理由——Haidt 2001)具有跨文化普遍性。此现象的普遍性不是因为所有文化共享同一套道德直觉，而是因为道德判断的双加工结构(快速直觉+慢速理性化)是人类认知架构的普遍特征——不同文化填充不同的具体禁忌，但'直觉先行、理性追认'的加工顺序是跨文化不变的。",
        "sources": [
            "moral_psychology — Haidt(2001)道德dumbfounding经典实验;Greene et al.(2001,2004)fMRI道德判断双加工证据;Cushman et al.(2006)道德判断的双系统模型",
            "cultural_anthropology — Shweder et al.(1997)道德三分理论(autonomy/community/divinity);Haidt-Joseph(2004)道德基础理论跨文化验证;Henrich et al.(2010)WEIRD样本偏差警示",
        ],
    },
    {
        "id": "BR-L2-039", "slug": "tournament-incentives-effort-distribution",
        "title": "锦标赛激励下的努力分布不均",
        "domain": ["组织经济学", "博弈论"],
        "bridges_to": ["CONCEPT-competition", "CONCEPT-agent", "CONCEPT-goal"],
        "thesis": "在锦标赛式激励(相对排名决定报酬)中，参与者的努力分布呈现'极度右偏'——少数顶尖竞争者投入超量努力，大量中等竞争者提前放弃(Cuiet)、底部竞争者搭便车。这不是参与者'不努力'——是锦标赛结构使边际努力的期望回报在能力分布中段出现'死亡谷':对中等能力者而言，追上顶部的成本远超预期收益，而跌出中段的风险已经无关紧要。",
        "sources": [
            "organizational_economics — Lazear-Rosen(1981)锦标赛理论;Prendergast(1999)激励契约综述;Bandiera et al.(2011)田野实验中锦标赛vs固定工资的努力分布",
            "game_theory — 竞赛博弈(Tullock 1980 rent-seeking contests);全支付拍卖(all-pay auction)均衡中努力随能力差异的极化",
        ],
    },
    {
        "id": "BR-L2-040", "slug": "group-identity-boundary-morality",
        "title": "群体身份作为道德边界的心理标记",
        "domain": ["社会心理学", "道德心理学"],
        "bridges_to": ["CONCEPT-group", "CONCEPT-morality", "THEOREM-group-identity-decay"],
        "thesis": "个体对群内成员的道德考量(关怀/公平/忠诚)显著强于群外成员——且这一'道德折扣'的大小随群体身份的心理距离(亲缘<族群<国家<物种)单调递增。THEOREM-group-identity-decay预测群体身份随互动频率衰减;本桥接将此定理延伸到道德域——当群体边界因身份衰减而模糊时，对应的道德折扣也随之松动。",
        "sources": [
            "social_psychology — Tajfel-Turner(1979)社会认同理论;Brewer(1999)内群偏爱;Opotow(1990)道德排斥(moral exclusion)理论",
            "moral_psychology — Singer(1981)道德圈的扩展;Graham et al.(2017)道德基础理论中'忠诚/背叛'基础的群体边界功能;Cikara et al.(2011)群际Schadenfreude的神经基础",
            "evolutionary_biology — Hamilton(1964)亲缘选择;Choi-Bowles(2007)parochial altruism的群际战争共生演化",
        ],
    },

    # === 跨概念对(组合缺口) ===
    {
        "id": "BR-L2-041", "slug": "information-asymmetry-power-gradient",
        "title": "信息不对称作为权力梯度",
        "domain": ["权力研究", "信息经济学"],
        "bridges_to": ["CONCEPT-information", "CONCEPT-power", "CONCEPT-exchange"],
        "thesis": "信息不对称不仅是市场失灵的原因(Akerlof 1970)，更是人际和组织权力差异的基础机制——当A拥有B需要但无法独立验证的信息时，A对B拥有非对称影响力。此权力形式的独特之处在于:它不依赖强制或资源控制，而依赖'认知依赖'——B无法判断A的建议是否符合B的利益，因此B必须在信任和怀疑之间做不可验证的权衡。信息权力随信息可替代性下降而上升(信息越独特=权力越大)，随验证成本下降而下降(验证越便宜=权力越小)。",
        "sources": [
            "information_economics — Akerlof(1970)柠檬市场;Stiglitz(2000)信息不对称对权力关系的贡献;principal-agent theory中的信息租金",
            "social_psychology — French-Raven(1959)专家权力(expert power);Fiske(1993)权力-as-control理论中信息控制维度",
        ],
    },
    {
        "id": "BR-L2-042", "slug": "norm-violation-contagion",
        "title": "规范违反的传染效应",
        "domain": ["社会规范", "行为经济学"],
        "bridges_to": ["CONCEPT-norm", "CONCEPT-conflict", "AXIOM-003"],
        "thesis": "当个体观察到他人违反社会规范而未受惩罚时，自身违反同一规范的概率显著上升——'破窗效应'的行为经济学版本。机制并非'学习到规范不存在'(因为个体通常知道规范存在)，而是'观察到惩罚概率的更新'(Bayesian updating on enforcement likelihood)加上'违反的道德成本下降'(规范违反的'社会证明'——其他人也这么做)。AXIOM-003(规范从互动中涌现)的逆过程:规范不仅从遵守中涌现，也从观察到的违反中消解。",
        "sources": [
            "behavioral_economics — Keizer et al.(2008, Science)破窗效应的田野实验;Cialdini et al.(1990)社会规范与乱丢垃圾;Gino et al.(2009)不道德行为的 contagion 实验",
            "criminology — Wilson-Kelling(1982)破窗理论;Sampson-Raudenbush(1999)集体效能与 disorder;Weisburd et al.(2011)破窗效应的准实验证据",
        ],
    },
    {
        "id": "BR-L2-043", "slug": "gift-exchange-hierarchy-formation",
        "title": "礼物交换中的层级自发形成",
        "domain": ["经济人类学", "组织理论"],
        "bridges_to": ["CONCEPT-exchange", "CONCEPT-hierarchy", "CONCEPT-power"],
        "thesis": "在持续的非对称礼物交换中(一方持续给予超过其收到的价值)，层级关系自发涌现——给予多的一方积累'信用债权'，转化为非正式权力。此过程不同于市场的等价交换(银货两讫)和再分配(中央收集+分配):礼物层级是非契约的、嵌入社会关系的、不依赖第三方执行的。Mauss(1925)的'礼物之灵'在此框架下可被操作化为'未偿还的信用差额产生不对称义务感知'。",
        "sources": [
            "economic_anthropology — Mauss(1925)礼物;Malinowski(1922)库拉圈;Gregory(1982)礼物vs商品;Graeber(2011)债的人类学",
            "organizational_behavior — Blau(1964)社会交换理论;Cropanzano-Mitchell(2005)社会交换理论的现代综述;Shore et al.(2009)非对称交换与权力差异",
        ],
    },
    {
        "id": "BR-L2-044", "slug": "coopetition-stability-conditions",
        "title": "竞合关系的稳定性条件",
        "domain": ["博弈论", "组织理论"],
        "bridges_to": ["CONCEPT-cooperation", "CONCEPT-competition", "CONCEPT-goal"],
        "thesis": "'竞合'(coopetition——同一对参与者同时进行合作和竞争)的稳定性取决于两个维度的'分离度':(i)价值创造(合作域)与价值分配(竞争域)能否在认知和组织上分离;(ii)短期竞争收益与长期合作收益的时间分离度。当两域高度重叠(合作的果实立刻变成竞争的筹码)时，竞合崩塌为纯竞争或伪合作。稳定竞合需要制度性防火墙——参与者互相知道对方在竞争域是对手、在合作域是伙伴，且两类互动发生在可区分的时间/空间/项目上。",
        "sources": [
            "game_theory — Brandenburger-Nalebuff(1996)竞合理论(co-opetition);Axelrod(1984)重复博弈中的合作条件在竞合域的扩展;多市场接触(multimarket contact)对竞争强度的抑制效应",
            "organizational_behavior — Bengtsson-Kock(2000)竞合的商业案例研究;Raza-Ullah et al.(2014)竞合中的张力管理;Gnyawali-Park(2011)中小企业的竞合创新",
        ],
    },
    {
        "id": "BR-L2-045", "slug": "goal-interference-multitasking",
        "title": "多任务目标干扰效应",
        "domain": ["认知科学", "组织行为"],
        "bridges_to": ["CONCEPT-agent", "CONCEPT-goal", "CONCEPT-resource"],
        "thesis": "当个体同时持有多个竞争性目标时，目标间干扰导致总体效能低于序列执行——不是因为'注意力分散'(可并行任务确实可以并行)，而是因为竞争性目标共享同一评判标准时产生的'目标冲突成本':个体会在目标间反复切换评判框架(criteria switching cost)、在执行一个目标时被另一个目标的'未完成感'侵入(intrusive goal activation)。此效应在目标间资源竞争不严重但评判标准冲突严重时最强——恰恰是直觉上认为'这些事不冲突'的场景。",
        "sources": [
            "cognitive_science — Kruglanski et al.(2002)目标系统理论;Shah-Kruglanski(2002)目标屏蔽失败的条件;Orehek-Vazeou-Nieuwenhuis(2015)多目标追求的认知成本",
            "organizational_behavior — Locke-Latham(2002)目标设置理论;Ordóñez et al.(2009)目标设置的阴暗面(goal-setting as a double-edged sword);多目标绩效评估的认知负荷",
        ],
    },
    {
        "id": "BR-L2-046", "slug": "information-decay-measurement",
        "title": "信息衰减速率的经验测量方法",
        "domain": ["信息理论", "方法论"],
        "bridges_to": ["AXIOM-002", "CONCEPT-measurement", "CONCEPT-information"],
        "thesis": "AXIOM-002声称信息在复制/存储/传输中单向衰减——本桥接为这一公理提供可操作化的经验测量框架:信息衰减速率可通过(i)代际口传实验(serial reproduction paradigm, Bartlett 1932)中信息保真度随传递代数的衰减曲线；(ii)档案重复抄写中异体字/错误的累计速率；(iii)数字存储中位翻转率(bit error rate)与纠错码冗余率的关系——三种独立方法测量。三者指向同一个操作化定义:信息衰减速率 = 单位时间/代际/复制中不可恢复信息比特的丢失比例。",
        "sources": [
            "cognitive_science — Bartlett(1932)系列再生实验;Mesoudi-Whiten(2008)文化传输链实验;Kalish et al.(2007)迭代学习的收敛与信息丢失",
            "information_theory — Shannon(1948)信道容量与噪声;Hamming(1950)纠错码;Landauer(1961)不可逆计算与信息物理擦除",
            "archival_science — 中世纪手稿抄写错误的定量研究(Büring 2014);抄本谱系学(stemmatology)中错误累计的树模型",
        ],
    },
    {
        "id": "BR-L2-047", "slug": "norm-emergence-catalyzed-by-conflict",
        "title": "冲突作为规范涌现的催化剂",
        "domain": ["社会规范", "冲突研究"],
        "bridges_to": ["AXIOM-003", "CONCEPT-conflict", "CONCEPT-norm"],
        "thesis": "AXIOM-003声称规范从反复互动中涌现——本桥接精确化一个被忽视的涌现条件:冲突加速规范的涌现速度。当两个群体在共享资源上发生重复冲突且无法消灭对方时，规范(关于'谁在什么条件下可以使用多少资源'的非正式规则)的涌现速度显著快于无冲突情境。机制:冲突使先前无需协调的'默认状态'变得不可持续→强制双方投入认知资源寻找稳定均衡→加速了规范的试错-收敛过程。和平情境下规范涌现慢不是因为'不需要规范'——而是因为当前默认状态无需改变即可维持。",
        "sources": [
            "conflict_studies — Ostrom(1990)公共资源治理中冲突与规则涌现的关系;Ellickson(1991)夏斯塔县牧场纠纷与规范的田野证据;Knight(1992)制度与分配冲突",
            "evolutionary_game_theory — Young(1993)规范涌现的随机稳定均衡;Bowles-Gintis(2011)合作物种中冲突与合作的共演化",
        ],
    },
    {
        "id": "BR-L2-048", "slug": "power-diffusion-deep-hierarchy",
        "title": "深层层级中的权力扩散",
        "domain": ["组织理论", "权力研究"],
        "bridges_to": ["THEOREM-hierarchy-depth-limit", "CONCEPT-power", "CONCEPT-hierarchy"],
        "thesis": "THEOREM-hierarchy-depth-limit预测层级深度存在认知上限——本桥接延展该定理到权力分配域:当组织层级超过有效管理幅度上限时，高层的'名义权力'(formal authority)与'实际控制力'(effective control)之间出现剪刀差——深层级使信息上传失真(在每一层被压缩和美化)和指令下达衰减(在每一层被重新解释和选择性执行)，导致顶层对基层的实际控制力随层级深度非线性衰减。此机制不依赖于顶层的能力或意愿——是层级信息传输的物理约束。",
        "sources": [
            "organizational_sociology — Michels(1911)寡头铁律的'组织规模→权力集中'一面;Weber(1922)官僚制的控制困境;Blau(1968)组织层级与信息失真的经验研究",
            "political_science — Tsebelis(2002)否决者理论中层级数对政策控制力的影响;Huber-Shipan(2002)委托-代理链中的控制衰减",
        ],
    },
    {
        "id": "BR-L2-049", "slug": "moral-internalization-group-identity",
        "title": "道德内化与群体认同的绑定",
        "domain": ["道德心理学", "社会心理学"],
        "bridges_to": ["THEOREM-moral-internalization", "CONCEPT-group", "CONCEPT-morality"],
        "thesis": "THEOREM-moral-internalization描述道德规范从外压到自驱的内化过程——本桥接精确化该过程的一个关键放大器:群体认同强度。个体会选择性地内化其认同群体的道德规范，而对非认同群体的同等规范产生'免疫'——不是不理解该规范(认知上可理解)，而是不将其内化为个人道德标准(动机上排斥)。群体认同作为道德内化的门控机制，解释了为什么同一道德规范(如'诚信')在不同群体中的内化深度差异巨大——不是因为该规范固有的说服力不同，而是因为承载该规范的群体在个体心中的认同强度不同。",
        "sources": [
            "moral_psychology — Haidt(2012)道德矩阵与群体绑定;Graham et al.(2017)道德基础理论的忠诚/背叛维度;Ellemers-van der Toorn(2015)群体认同作为道德动机",
            "social_psychology — Hogg-Terry(2000)社会认同理论中的规范内化;Turner(1991)自我归类理论;Abrams-Hogg(1990)群体认同与从众",
        ],
    },
    {
        "id": "BR-L2-050", "slug": "identity-decay-digital-communication",
        "title": "数字通信对群体认同衰减速率的抑制",
        "domain": ["数字社会学", "社会心理学"],
        "bridges_to": ["THEOREM-group-identity-decay", "CONCEPT-information", "CONCEPT-group"],
        "thesis": "THEOREM-group-identity-decay预测群体认同随互动频率下降而衰减——本桥接将该定理置于数字通信情境中:数字通信(即时消息/社交网络/视频通话)通过降低维持身份信号的边际成本，系统性减缓了群体认同的衰减速率。前数字时代，群体认同的维持需要物理共在或信件往来的高成本互动→不在场=不互动=身份衰减。数字时代，低成本的'微互动'(点赞/评论/状态更新)可维持'仍在群体中'的感知→身份衰减的时间常数被拉长。但此维持效应仅适用于'表达性身份'(expressive identity——通过信号传递即可维持的归属感)，对'工具性身份'(instrumental identity——依赖实质性互助的身份)无效。",
        "sources": [
            "digital_sociology — boyd(2014)网络化公众与身份维持;Baym(2010)数字通信与关系维系;Rainie-Wellman(2012)网络化个体主义",
            "social_psychology — Latané(1981)社会影响理论中的物理距离vs心理距离;Walther(1996)超人际计算机媒介通信;McKenna-Bargh(1998)虚拟群体的身份效应",
        ],
    },
    {
        "id": "BR-L2-051", "slug": "fairness-preferences-cross-cultural",
        "title": "公平偏好的跨文化差异性",
        "domain": ["行为经济学", "文化人类学"],
        "bridges_to": ["CONCEPT-fairness", "CONCEPT-exchange", "CONCEPT-value"],
        "thesis": "公平偏好(个体愿付出代价惩罚不公平行为的倾向)具有跨文化系统性差异——不是'有些文化在乎公平、有些不在乎'的二元差异，而是'什么是公平'的文化定义差异驱动了惩罚行为的差异。最后通牒博弈中，提议者的出价和回应者的拒绝阈值在不同社会中与当地的市场整合度(market integration)和参与世界宗教(world religion)正相关(Henrich et al. 2001, 2010)——但这不是'市场社会更公平'的证据，而是'市场社会更习惯匿名交易中的等值交换'→将这一模式投射到实验情境中。公平偏好的心理机制(对不公平的厌恶)是跨文化普遍的，但触发该机制的'不公平'是通过文化透镜判定的。",
        "sources": [
            "behavioral_economics — Güth et al.(1982)最后通牒博弈;Fehr-Schmidt(1999)不公平厌恶模型;Henrich et al.(2001, 2010)15个小规模社会的跨文化最后通牒实验",
            "cultural_anthropology — Fiske(1992)关系模型理论(communal sharing/authority ranking/equality matching/market pricing);Henrich et al.(2005)WEIRD被试问题",
        ],
    },
    {
        "id": "BR-L2-052", "slug": "value-pluralism-market-boundary",
        "title": "价值多元主义与市场边界",
        "domain": ["经济社会学", "道德哲学"],
        "bridges_to": ["CONCEPT-value", "CONCEPT-exchange", "CONCEPT-morality"],
        "thesis": "社会共享一套有限的核心价值维度(Schwartz 1992的10种基本价值;Hofstede的文化维度)且不同社会对这些维度的权重排序不同。当市场交换(以价格为协调机制)从'可 commodify 的物品'扩展到'价值排序中高权重维度所依附的物品/关系'(如器官/教育机会/政治影响力)时，触发的社会抵抗强度与该维度的权重正相关。这不是'市场vs道德'的抽象对立——是可操作化的预测:在同一社会内，对'价值权重前30%的域被市场化'的抵抗将系统性强于'后30%的域被市场化'的抵抗。",
        "sources": [
            "economic_sociology — Zelizer(1979, 1994)货币的 earmarking 与不可通约性;Sandel(2012)金钱不能买什么;Fourcade(2011)道德化的市场",
            "cross_cultural_psychology — Schwartz(1992, 2012)基本人类价值理论;Inglehart-Welzel(2005)世界价值观调查中的价值变迁",
        ],
    },
]

TOTAL = len(BRIDGES)

# ── API ────────────────────────────────────────────────────

def load_sensenova():
    with open(SECRETS_PATH) as f:
        secrets = json.load(f)
    cfg = secrets["sensenova"]
    return cfg["api_key"], cfg["base_url"], cfg.get("model", "deepseek-v4-flash")


def call_free_model(api_key, base_url, model, system, user, max_tokens=6000):
    import requests
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        },
        timeout=180,
    )
    if resp.status_code != 200:
        return None, f"API error {resp.status_code}: {resp.text[:300]}"
    data = resp.json()
    return data["choices"][0]["message"]["content"], data.get("usage", {})


def extract_yaml(text):
    text = text.strip()
    for prefix in ["```yaml", "```"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def generate_bridge(brief, dry_run=False):
    """用免费模型生成一条 bridge YAML。"""
    system = (
        "你是 L2 桥接砖的作者。L2 桥接砖是把 L1 抽象概念(如 CONCEPT-power/CONCEPT-hierarchy)接到"
        "真实人类社会的经验命题——它可错、可证伪、有跨学科经验来源支撑。\n\n"
        "## 桥接砖格式\n"
        "```yaml\n"
        "id: BR-L2-NNN\n"
        "type: bridge\n"
        "layer: L2-bridging\n"
        "status: candidate\n"
        "term: 中文术语名\n"
        "人话摘要: 一句非黑话解释\n"
        "statement: |\n"
        "  核心经验命题:机制描述+预测\n"
        "bridges_to:\n"
        "  concepts:\n"
        "  - CONCEPT-xxx\n"
        "applicable_sources:\n"
        "- source_name:\n"
        "    rationale: |\n"
        "      该学科通道提供的具体证据\n"
        "falsifiability: |\n"
        "  具体的证伪条件(a)(b)(c)...\n"
        "domain: [域1, 域2]\n"
        "created: YYYY-MM-DD\n"
        "author: free model draft\n"
        "```\n\n"
        "## 硬要求\n"
        "1. statement 必须包含:核心机制+一个可检验的预测+一个限制(不声称什么)\n"
        "2. applicable_sources 每条 rationale 必须引用具体的研究/文献/数据,不能只写'某领域证据'\n"
        "3. falsifiability 必须给出具体的、可事前观测的证伪条件\n"
        "4. 人话摘要必须零黑话\n"
        "5. YAML 多行用 | 块标量,缩进2空格\n"
        "6. status: candidate(所有新桥接砖都从 candidate 开始)\n"
        "7. 不要输出解释,只输出完整 YAML"
    )

    sources_str = "\n".join(f"  - {s}" for s in brief["sources"])
    bridges_str = "\n".join(f"  - {c}" for c in brief["bridges_to"])
    user = (
        f"## Bridge Brief\n"
        f"id: {brief['id']}\n"
        f"slug: {brief['slug']}\n"
        f"title: {brief['title']}\n"
        f"domain: {brief['domain']}\n"
        f"bridges_to:\n{bridges_str}\n\n"
        f"## 核心论点\n{brief['thesis']}\n\n"
        f"## 经验来源\n{sources_str}\n\n"
        "请输出完整的 bridge YAML 文件。"
    )

    if dry_run:
        return None, f"dry-run: {len(system)}c sys + {len(user)}c user"

    api_key, base_url, model = load_sensenova()
    response, usage_or_error = call_free_model(api_key, base_url, model, system, user)
    if response is None:
        return None, usage_or_error
    yaml_text = extract_yaml(response)
    tokens = usage_or_error.get("total_tokens", "?")
    return yaml_text, f"{tokens} tokens"


def main():
    parser = argparse.ArgumentParser(description="批量生成 L2 bridge YAML(免费模型)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=TOTAL)
    args = parser.parse_args()

    end = min(args.start + args.count, TOTAL)
    out_dir = REPO / "L2-bridging" / "candidate"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    t0 = time.time()

    for i in range(args.start, end):
        brief = BRIDGES[i]
        bid = brief["id"]
        fname = f"{bid}-{brief['slug']}.yaml"
        fpath = out_dir / fname
        label = f"[{i+1}/{TOTAL}] {bid}"

        if args.dry_run:
            _, note = generate_bridge(brief, dry_run=True)
            print(f"📋 {label} — {note}")
            results.append({"id": bid, "ok": False, "note": note})
            continue

        print(f"🤖 {label} — {brief['title']}", file=sys.stderr, flush=True)
        t1 = time.time()
        yaml_text, note = generate_bridge(brief)
        dt = time.time() - t1

        if yaml_text is None:
            print(f"  ❌ 失败: {note}", file=sys.stderr)
            results.append({"id": bid, "ok": False, "note": note, "time": dt})
            continue

        # 安全检查
        if f"id: {bid}" not in yaml_text:
            print(f"  ❌ 输出不含正确 id", file=sys.stderr)
            results.append({"id": bid, "ok": False, "note": "missing id", "time": dt})
            continue

        fpath.write_text(yaml_text, encoding="utf-8")
        print(f"  ✅ {fname} ({note}, {dt:.1f}s)", file=sys.stderr)
        results.append({"id": bid, "ok": True, "note": note, "time": dt, "path": str(fpath.relative_to(REPO))})

    # 汇总
    ok = sum(1 for r in results if r["ok"])
    total_time = time.time() - t0
    print(f"\n{'='*60}")
    print(f"生成: {ok}/{len(results)} 成功, 总耗时 {total_time:.0f}s")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
