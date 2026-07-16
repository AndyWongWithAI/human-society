# Author Reading Pack（作者阅读包）

> 自动生成于 2026-07-16 16:51。跑 `python scripts/index.py` 重生。
> 用途：起草推论前**只读这一份**——实体速览 + 前置清单 + 瘦身格式，全在这里。
> 不再需要分别读 INDEX.md + author-checklist.md + 方法论文件。

---

## 1. 实体速览

**239 实体**（同 INDEX.md，一行一条）


## L0 物理约束 (3)
- PHY-001 — 东西放着不管就会自然变乱、变坏(这就是热力学第二定律);社会里的制度、组织、知识也一样——不持续投入精力去维护,就会自然松散、退化,不存在'一次…
- PHY-002 — 能量不会凭空冒出来,只能从别处搬来或从存货里取(即能量守恒);所以一个社会能干多少事,归根到底受制于它能弄到多少能量,没有'无中生有'的无限增长  ⟵ PHY-001
- PHY-003 — 物理世界的时空规矩管着一切社会活动:一个人不能同时出现在两个地方、东西要花时间才能运到、时间只能往前走(做了选择就没法反悔)、同一块地不能被两拨…

## L1 · 概念 concepts (20)
- CONCEPT-agent · 行动者 — 行动者'指任何有自己想达成的目标、能看清眼下处境、并会主动做事去接近目标的主体——可以是人、动物、组织甚至程序,不专指人类
- CONCEPT-choice · 选择 — 选择'就是在几条互相排斥、只能走一条的路里挑一条去做;因为时间和资源都有限,人根本躲不开选择——连'什么都不做'也是一种选择(等于选了维持现状)  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-resource, CONCEPT-information
- CONCEPT-competition · 竞争 — 竞争'指两个以上的主体都想要同一份不够分的资源,一方多拿另一方就少拿;它不需要双方认识、也不用真吵起来,只要资源有限、大家都要,竞争就客观存在  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-resource
- CONCEPT-conflict · 冲突 — 冲突'指双方直接较劲、至少一方存心要妨碍对方,比竞争更进一步(竞争可以互不知情,冲突必然是面对面对着干),而且打起来双方都得耗成本  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-interaction, CONCEPT-competition, CONCEPT-resource, CONCEPT-information
- CONCEPT-cooperation · 合作 — 合作'指几方自愿地配合彼此的行动,一起做成单靠自己做不成(或做不好)的事,而且合起来的总收益比各干各的更大;它可以纯粹出于自利,不必是无私奉献  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-choice, CONCEPT-interaction, CONCEPT-information
- CONCEPT-exchange · 交换 — 交换'指双方你情我愿地互相让出各自的东西(物品、服务、信息都行),换完后每一方都觉得自己更划算了;它不创造新资源,只是把已有资源挪到更需要它的人…  ⟵ CONCEPT-agent, CONCEPT-resource, CONCEPT-interaction, CONCEPT-choice, CONCEPT-relation, CONCEPT-information
- CONCEPT-fairness · 公平 — 公平'不是指'每个人都拿一样多'——那只是公平的一种  ⟵ CONCEPT-agent, CONCEPT-norm, CONCEPT-relation, CONCEPT-competition, CONCEPT-cooperation, CONCEPT-exchange, CONCEPT-power, CONCEPT-resource
- CONCEPT-goal · 目标 — 目标'就是一个主体想达到或想保住的某种状态;正是当前状态和目标之间的差距,驱使它去行动  ⟵ CONCEPT-agent
- CONCEPT-group · 群体 — 群体'指因为共享某种身份(血缘、语言、地域、信仰等)而聚成的一群人;它必然有边界,分得清谁是自己人、谁是外人,而且这份认同得靠仪式、符号、故事不…  ⟵ CONCEPT-agent, CONCEPT-information, CONCEPT-relation, CONCEPT-goal, CONCEPT-choice
- CONCEPT-hierarchy · 层级 — 层级'就是组织里把人分成上下级、上级对下级有更大决策权的安排;它存在的意义是省沟通成本——不用人人都参与每个决定,决策权往上收、执行往下分,组织…  ⟵ CONCEPT-organization, CONCEPT-choice, CONCEPT-resource, CONCEPT-information
- CONCEPT-information · 信息 — 信息'指关于世界某个情况的、可以传给别人的表示(比如'烟'代表'有火'),它帮主体减少不确定、做出更好的判断;信息必须依附在某种物理载体上(大脑…  ⟵ CONCEPT-agent, CONCEPT-resource
- CONCEPT-interaction · 交互 — 交互'指两个以上的主体之间发生的一次行为往来——一方的动作作用到另一方并产生看得见的影响(哪怕对方没回应,比如攻击也算);它是一次性的事件,反复…  ⟵ CONCEPT-agent, CONCEPT-information
- CONCEPT-measurement-independence · 测量独立性 — 两个数据点是不是各自独立测量出来的——不由'几个机构发布了数据'决定,而由'它们的测量链从哪一步开始分叉'决定  ⟵ CONCEPT-information
- CONCEPT-morality · 道德 — 道德'不是一套特定的行为清单——它是规范的一个子类  ⟵ CONCEPT-norm, CONCEPT-agent, CONCEPT-group, CONCEPT-cooperation, CONCEPT-competition, CONCEPT-conflict
- CONCEPT-norm · 规范 — 规范'指一群人之间共享的'该做/不该做'的行为默契,谁违反了会招来别人的反应(制裁、排挤、白眼);它可以在没人专门制定的情况下,靠大家反复打交道…  ⟵ CONCEPT-agent, CONCEPT-interaction, CONCEPT-relation, CONCEPT-information
- CONCEPT-organization · 组织 — 组织'指一群人为了共同目标搭起来的、有明确分工和协调规矩的长期结构(比如公司、军队);它比'群体'要求更高——光有共同身份不够,还得有分工和协调…  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-resource, CONCEPT-relation, CONCEPT-cooperation, CONCEPT-information, CONCEPT-norm
- CONCEPT-power · 权力 — 权力'指在一段关系里,甲能让乙做出'本来不会做'的事的能力;它不藏在某个人身上,而存在于人和人之间,靠暴力、钱、信息、地位或人多等某种本钱撑着  ⟵ CONCEPT-agent, CONCEPT-choice, CONCEPT-interaction, CONCEPT-relation, CONCEPT-resource, CONCEPT-information
- CONCEPT-relation · 关系 — 关系'指特定的两人(或多人)反复打交道后形成的、比较稳定、彼此能大致预料对方的互动套路;单次陌生人偶遇只是'交互',反复发生并沉淀下来才叫'关系…  ⟵ CONCEPT-agent, CONCEPT-interaction, CONCEPT-goal, CONCEPT-resource, CONCEPT-information
- CONCEPT-resource · 资源 — 资源'指主体用来缩小'现状'与'目标'之间差距的一切可支配的东西——不只是钱和物,知识、技能、人脉、甚至时间都算;它们的共同点是总量有限,所以必…  ⟵ CONCEPT-agent, CONCEPT-goal
- CONCEPT-value · 价值 — 价值'不是东西自己带的属性——它是'谁想要、有多想要、愿意为它付出什么代价'的三方关系  ⟵ CONCEPT-agent, CONCEPT-resource, CONCEPT-goal, CONCEPT-choice, CONCEPT-competition

## L1 · 公理 axioms (4)
- AXIOM-001 · 稀缺性-竞争公理 — 多个人都要同一份不够分的资源,竞争就必然存在——不是谁性格问题,是结构决定的
- AXIOM-002 · 信息熵增公理 — 记住的东西不时常温习、记录不去维护,就会随时间慢慢模糊、走样、最后没法用——信息会自然衰减,保鲜是要花力气的
- AXIOM-003 · 重复交互-规范涌现公理 — 两个人反复打交道、又都记得上回发生过什么,自然就会对'对方大概会怎么做'形成共同的默契和规矩——这不是文化教出来的,是打交道多了必然长出来的
- AXIOM-004 · 组织熵增命题 — 任何组织,只要不持续花精力去维护它的协调规矩(谁干什么、怎么配合),就会自然涣散——结构变乱、规矩失灵、人走光,最后散伙

## L1 · 定理 theorems (14)
- THEOREM-competition-norm · 竞争规范化定理 — 只要竞争的人反复碰面、彼此看得见，就会自发形成‘比赛该怎么打’的规矩——竞争不会消失，但会从没底线的乱斗变成守规则的较量；而彼此从不打交道的竞争…  ⟵ PHY-002, PHY-003-b, AXIOM-001, AXIOM-003
- THEOREM-conflict-cost · 冲突成本定理 — 直接开打比守规矩地竞争更费双方的资源，所以长期算下来，少打无谓之仗的一方更能攒下家底——这份成本差，就逼着大家慢慢形成‘别乱打’的规矩  ⟵ PHY-002, AXIOM-001, AXIOM-003, AXIOM-004, THEOREM-competition-norm
- THEOREM-cooperation-precondition · 合作前提定理 — 合作得靠双方都相信‘你会配合我、我也配合你’，而这份把握来自过去打交道攒下的了解；所以没有交情的陌生人之间，合作特别脆弱、容易散  ⟵ AXIOM-003
- THEOREM-exchange-competition-alternative · 交换替代竞争定理 — 当两个人各自握着对方想要的不同东西时，可以用‘交换’代替‘抢’——各取所需、都比抢更划算；但前提是两人擅长或拥有的东西得有差别，大家都一样就没得…  ⟵ PHY-002, PHY-003-c, AXIOM-001
- THEOREM-group-identity-decay · 群体身份衰减定理 — 一个群体‘我们是自己人’的共识只存在于成员的记忆里，如果不靠仪式、标志、共同故事不断重温，就会慢慢淡忘、各想各的，最后群体边界模糊、散伙  ⟵ PHY-001, PHY-002, PHY-003-a, AXIOM-002
- THEOREM-hierarchy-depth-limit · 层级深度极限定理 — 信息每往上汇报或往下传达一层就失真一点，所以组织的层级不能太深——层数一多，高层掌握的情况和基层实际就基本对不上了，这套层级也就不再管用  ⟵ PHY-001, PHY-002, AXIOM-002
- THEOREM-moral-internalization · 道德内化定理 — 人为什么会'心里过不去'？因为一直靠别人盯着你太贵了——进化给每个人装了个免费的'内部警察  ⟵ PHY-001, PHY-002, AXIOM-002
- THEOREM-moral-third-party-enforcement · 道德第三方执行定理 — 一个人欺负另一个人，你没被欺负为什么会生气、甚至想出手管？因为这两人之间的规矩如果坏了，你也跟着倒霉——它维护的不只是他们两个之间的交易，而是一…  ⟵ PHY-002, PHY-003-b, AXIOM-001, AXIOM-003
- THEOREM-norm-energy-saver · 规范节能定理 — 有共同的规矩，大家每次打交道就不必从头商量‘该怎么办’，省下大量时间精力——规矩越稳，维持同样的秩序越省力；反过来，规矩一崩，维持秩序的成本会急…  ⟵ PHY-001, PHY-002, AXIOM-003, AXIOM-004
- THEOREM-organization-resource-competition · 组织资源竞争定理 — 在资源有限的同一环境里，多个组织为了‘养活自己’必然互相争抢资源——这不是偶然的市场现象，而是躲不掉的硬道理；而且组织太小竞争不过、太大又养不起…  ⟵ PHY-001, PHY-002, AXIOM-001, AXIOM-004
- THEOREM-position · 立场定理 — 只要一个人有想达成的目标，又碰上一件既影响这目标、又牵扯到别人的事，他就必然会对这事有‘希望往哪边走’的倾向（即立场）——这不需要额外理由，是有…  ⟵ PHY-002, PHY-003-c
- THEOREM-power-signal-decay · 权力信号衰减定理 — 甲能管住乙，靠的是乙心里记着‘甲有本事影响我’；这份记忆会自然淡忘，甲若长期不展示、不提醒，实际的支配力就会下滑——权力不只是‘拥有’，更得‘不…  ⟵ PHY-001, AXIOM-002
- THEOREM-relation-information-asset · 关系信息资产定理 — 两个人的‘关系’本质是一笔信息财富——存着彼此打交道攒下的了解，让往后每次合作都更省事；所以熟人办事比生人省力，而长期不来往，这份了解会变淡、关…  ⟵ PHY-001, AXIOM-002, AXIOM-003
- THEOREM-value-attribution · 价值归属定理 — 一个东西对你有多值钱，取决于两条路加在一起再乘以稀缺度——第一条路是这东西对你自己有用（使用价值），第二条路是别人愿意为它付出什么（交换网络价值…  ⟵ PHY-001, PHY-002, PHY-003-c, AXIOM-001, AXIOM-003

## L2 桥接 bridges (43)
- ADV-REVIEW-BR-L2-004
- ADV-REVIEW-BR-L2-006
- ADV-REVIEW-BR-L2-010 [verified]
- ADV-REVIEW-BR-L2-013 — 对 BR-L2-013(不公平厌恶)的 round-1 独立对抗审查
- ADV-REVIEW-BR-L2-014 — 对 BR-L2-014(代价第三方惩罚)的 round-1 独立对抗审查
- ADV-REVIEW-BR-L2-025
- ADV-REVIEW-BR-L2-028 — 对 BR-L2-028(预防性储蓄)的 round-1 独立对抗审查
- ADV-REVIEW-BR-L2-029 — 对 BR-L2-029(边际消费倾向的收入梯度)的 round-1 独立对抗审查
- ADV-REVIEW-BR-L2-030 — 对 BR-L2-030(现时偏向——人心里那杆秤天生偏向"现在")的 round-1 独立对抗审查
- ADV-REVIEW-BR-L2-031 — 对 BR-L2-031(制度信任不对称衰减——掉得快涨得慢)的 round-1 独立对抗审查
- ADV-REVIEW-BR-L2-032 — 对 BR-L2-032(算法对交易成本的断崖式下降——≥10000x)的 round-1 独立对抗审查
- BR-L2-001 [verified] · 有限理性 — 人的脑子算不过来所有选项、也想不清每个选择的长远后果，只能挑个‘够用就行’的方案，而不是理论上的最优解  ⟵ AXIOM-002
- BR-L2-002 [verified] · 亲缘利他 — 血缘越近的亲人，人越愿意为他付出、吃点亏也帮——共享的基因越多，愿意出手相助的门槛就越低
- BR-L2-003 [verified] · 大规模非亲缘合作 — 人类的独特之处，是能让成千上万素不相识的陌生人一起合作（国家、宗教、市场都是），靠的不是熟人互惠或血缘，而是大家共同相信的规矩和‘想象出来的秩序…  ⟵ AXIOM-003, THEOREM-cooperation-precondition
- BR-L2-004 [verified] · 层级普适性 — 人群一旦超过约150人(Dunbar数——一个人能维持稳定社交关系的上限),在所有已知案例中都会冒出某种'少数人拍板'的层级——两条独立的链在此…  ⟵ AXIOM-002, THEOREM-hierarchy-depth-limit
- BR-L2-005 [verified] · 互惠利他 — 经常打交道的人，哪怕没有血缘，也会自然形成‘你帮我、我帮你’的默契——不用签合同、也不靠上头强制，来往多了自己就长出来了  ⟵ AXIOM-003, THEOREM-cooperation-precondition
- BR-L2-006 [verified] · 内群体偏好 — 人很容易偏袒’自己人’——分东西多给、更信任、有矛盾时也护着；哪怕’自己人’只是随手按颜色标签这种没意义的方式分出来的,这种偏心照样出现  ⟵ AXIOM-001, THEOREM-group-identity-decay
- BR-L2-007 [verified] · 禀赋互补驱动贸易 — 两拨人手里的东西越是'你有我没、我有你没'(禀赋互补),他们之间越会做买卖;贸易的密度跟着这种互补程度走  ⟵ THEOREM-exchange-competition-alternative
- BR-L2-008 [verified] · 掠夺是真实且普遍的资源获取策略 — 人不是只会做买卖——当'抢的代价'低于'抢到的好处'时,靠武力直接夺取(劫掠、掠夺、征服)是一种真实存在、跨文化反复出现的策略  ⟵ AXIOM-001, THEOREM-conflict-cost
- BR-L2-009 [verified] · 人际信任有界且随社会距离衰减 — 一个人能真正'知根知底、放心托付'的对象是有限的——出了熟人圈,信任就随社会距离(血亲→熟人→同乡→匿名陌生人)一路陡降  ⟵ AXIOM-002, THEOREM-relation-information-asset, THEOREM-group-identity-decay, THEOREM-cooperation-precondition
- BR-L2-010 [verified] · 非人格化制度能替代人际信任支撑陌生人交换 — 熟人之间靠交情办事;陌生人之间没交情,怎么放心交易?答案是把'信任'外包给制度——第三方执法、声誉登记、标准合同、抵押/货币  ⟵ AXIOM-003, THEOREM-cooperation-precondition, THEOREM-relation-information-asset
- BR-L2-011 [verified] · 通货替代匿名交换中缺失的记忆/可追踪性 — 熟人赊账,靠双方记得谁欠谁、以后还见面;可跟一个【认不出、追不到、不会再见】的人打交道,没法赊账——没人记得住、也没'下次'惩罚  ⟵ AXIOM-003, THEOREM-relation-information-asset, THEOREM-cooperation-precondition
- BR-L2-012 [verified] · 多边结算成本催生通用媒介 — 就算大家彼此都认得、也记得住谁欠谁(记忆在场),但一大群人互相七拐八绕地欠来欠去,要把这张'谁欠谁'的多边大网记清、轧平,本身就很费劲  ⟵ AXIOM-003, THEOREM-relation-information-asset, THEOREM-exchange-competition-alternative
- BR-L2-013 [verified] · 不公平厌恶 — 人讨厌自己吃亏(不利不公平)——这是刻在脑子里的,连猴子都有,三四岁小孩就会  ⟵ AXIOM-001, THEOREM-competition-norm, THEOREM-cooperation-precondition
- BR-L2-014 [verified] · 代价第三方惩罚 — 人不光自己吃亏了要讨公道,看见陌生人欺负另一个陌生人也会气得掏自己的腰包去罚那个欺负人的——这种'多管闲事'的冲动是公平规矩在没人管的情况下还能…  ⟵ AXIOM-001, AXIOM-003, THEOREM-competition-norm, THEOREM-cooperation-precondition, THEOREM-conflict-cost
- BR-L2-015 [verified] · 程序公平可替结果公平 — 结果输了但过程让人服气,人就能接受;过程不透明又偏袒,就算结果赚了人也觉得不对  ⟵ AXIOM-003, THEOREM-competition-norm, THEOREM-conflict-cost
- BR-L2-016 [verified] · 报应比例性 — 人不光觉得做坏事该罚,还觉得'罚多少得跟罪配'——太轻了不解恨、太重了又成欺负人  ⟵ AXIOM-003, THEOREM-conflict-cost, THEOREM-competition-norm
- BR-L2-017 [verified] · 分配规范随语境切换 — 同一家人,分'晚饭'是平均盛,分'谁继承祖宅'就不是平均了  ⟵ AXIOM-001, THEOREM-exchange-competition-alternative
- BR-L2-018 [verified] · 旁观者利益关联 — 人为什么更愿意管家门口的事而不是地球另一边的事？不是远方的破事不重要，而是你在家门口那个系统里的股份占比高  ⟵ AXIOM-001, AXIOM-003, THEOREM-moral-third-party-enforcement, THEOREM-competition-norm
- BR-L2-019 [verified] · 道德内化发育窗口 — 人不是一生下来就有良心——良心需要在对的条件下长出来  ⟵ AXIOM-002, THEOREM-moral-internalization
- BR-L2-020 [verified] · 道德领域多样性 — 不同文化把不同的事当成'道德问题'——有的文化把吃什么肉当成道德问题，有的不当回事  ⟵ AXIOM-001, AXIOM-003, THEOREM-moral-third-party-enforcement
- BR-L2-021 [verified] · 一般等价物的物理筛选 — 为什么是金，不是贝壳、盐巴、或铁钉当全世界的钱？因为'当钱用'的东西需要同时满足六个物理条件——分得开、放不坏、带着走、认得出、每块都一样、供应…  ⟵ AXIOM-001, THEOREM-exchange-competition-alternative, THEOREM-value-attribution
- BR-L2-022 [verified] · 价值储藏作为货币的独立功能维度 — 钱'其实做了三件不同的事——买东西（交易媒介）、标价格（记账单位）、存起来以后用（价值储藏）  ⟵ AXIOM-002, AXIOM-003, THEOREM-value-attribution
- BR-L2-023 [verified] · 金的非货币需求基底与冷启动 — 金在变成'钱'之前，已经有人想要它了——不是因为它能买东西，而是因为它好看、闪亮、做首饰戴在身上就是地位的象征  ⟵ AXIOM-003, THEOREM-value-attribution
- BR-L2-024 [verified] · 法币信用的连续可逆性与记忆滞后 — 法币的信用不是开关——不是'信任'或'不信任'二选一  ⟵ AXIOM-002, THEOREM-value-attribution
- BR-L2-025 [weakly_verified] · 数字媒介可处理性 — 纸上的字要人读了才有用,屏幕上的字机器自己就能读、能搜、能改、能跟别处的信息自动合成——这不是'变快了',是信息从'死物'变成了'活物  ⟵ AXIOM-002
- BR-L2-026 [verified] · AI Agent 信息处理不对称 — AI 不是'更聪明的人'——它在某些事上远超人类(无限记忆、不累、能同时处理海量信息),但在另一些事上根本缺失(没有身体体验、没有真感情、不怕死…  ⟵ AXIOM-002
- BR-L2-027 [verified] · 注意力稀缺与信息过载 — 脑子只能同时想几件事——信息太少当然不行,但信息太多、被信息淹了,判断力反而下降  ⟵ AXIOM-002
- BR-L2-028 [verified] · 预防性储蓄 — 天有不测风云,又没人给你兜底,你就得自己留后手——少花点,存点粮
- BR-L2-029 [weakly_verified] · 边际消费倾向的收入梯度 — 意外多发一块钱,穷人几乎全花掉,富人大多存起来——不是穷人大手大脚,是他们本来就有一堆想买而买不起的东西,钱一到手就去补窟窿;富人想买的早买了,…
- BR-L2-030 [verified] · 跨期选择的现时偏向 — 明知道下月开始存钱更好,但到了下月还是推到下下月——人天生就是'现在'比'以后'看得重,近的特别重、远的特别轻,不是算不清账,是心里那杆秤本身就…  ⟵ AXIOM-001, AXIOM-002
- BR-L2-031 [weakly_verified] · 制度信任的不对称衰减 — 对制度的信任有个扎心的规律——掉得快、涨得慢  ⟵ AXIOM-002, THEOREM-relation-information-asset
- BR-L2-032 [weakly_verified] · 算法驱动的搜索/匹配/监控成本断崖 — 算法不是让交易'更快'——它把搜索成本压低了上万倍、把匹配和监控成本压到了从前在大规模匿名交易中无法企及的水平,压低到了没有算法时不管花多少钱都…  ⟵ AXIOM-002

## L3 推论 corollaries (55)
- DED-001 [verified] · 组织深度天花板推论 — 光靠人嘴对嘴传话的组织，管理层级最多也就5到7层——再深，最高层掌握的情况就和基层实际严重脱节了；想再大，只能把信息写下来（官僚化）或把权力下放…  ⟵ AXIOM-002, THEOREM-hierarchy-depth-limit, BR-L2-001, BR-L2-004
- DED-002 [verified] · 规范成文化阈值推论 — 口口相传的规矩有个复杂度上限；社会一大、规矩一多，要么把规矩写下来、分层、或找专人记诵来突破上限，要么干脆分裂成一堆小单元、让每份规矩都不超上限…  ⟵ AXIOM-003, THEOREM-norm-energy-saver, THEOREM-cooperation-precondition, BR-L2-001, BR-L2-005
- DED-003 [verified*] · 内聚-外竞耦合推论 — 大群体的内部团结，和‘有没有一个外部对手’是绑在一起的——因为‘我们不同于他们’是最省力的团结方式；一旦外敌消失、又不肯改用别的方式（如民主参与…  ⟵ AXIOM-001, AXIOM-003, THEOREM-group-identity-decay, THEOREM-competition-norm, BR-L2-003, BR-L2-006
- DED-004 [rejected] · 信息外化不对称蕴含推论 — 曾猜‘把行政账目写下来’和‘把法律规矩写下来’这两件事会绑在一起出现，查了20个古代政体后发现站不住脚（很多大帝国只记账、不写成文法），已亲手否…  ⟵ AXIOM-002, BR-L2-001, DED-001, DED-002
- DED-005 [verified] · 贸易-劫掠边界推论 — 我想要你手里的东西,可以换也可以抢  ⟵ AXIOM-001, AXIOM-003, THEOREM-exchange-competition-alternative, THEOREM-conflict-cost, THEOREM-cooperation-precondition, BR-L2-005, BR-L2-007, BR-L2-008
- DED-006 [verified] · 信任天花板-制度外化推论 — 人只能对有限的熟人真正'放心托付',出了熟人圈信任就陡降(那是天花板)  ⟵ AXIOM-002, AXIOM-003, THEOREM-relation-information-asset, THEOREM-group-identity-decay, THEOREM-cooperation-precondition, THEOREM-exchange-competition-alternative, BR-L2-003, BR-L2-009, BR-L2-010
- DED-007 [rejected] · 通货三驱动解离推论 — 钱(通用交换媒介)从哪来?教科书给单一原因:门格尔说'为解决物物交换不便(你要的我没有)';另一派说'为替代记忆(陌生人之间没法赊账)  ⟵ AXIOM-003, THEOREM-relation-information-asset, THEOREM-cooperation-precondition, THEOREM-exchange-competition-alternative, BR-L2-005, BR-L2-009, BR-L2-011, BR-L2-012
- DED-008 [verified] · 裙带侵蚀与监督者独立性推论 — 血缘越近越愿意偏帮(那是本能,不是坏)  ⟵ AXIOM-001, THEOREM-relation-information-asset, THEOREM-norm-energy-saver, BR-L2-002, BR-L2-010
- DED-009 [verified] · 亲缘组织的规模天花板推论 — 纯靠血缘维系的合作组织有规模上限  ⟵ AXIOM-003, THEOREM-group-identity-decay, THEOREM-cooperation-precondition, BR-L2-002, BR-L2-003, BR-L2-010
- DED-010 [verified] · 权力维持成本与制度化推论 — 纯靠个人威慑的权力(乙服从系于"怕甲这个人")会不断流失——乙心里"甲能影响我"这份 记忆按信息熵增自然淡忘,甲得靠越来越贵的展示(仪式/阅兵/…  ⟵ PHY-002, AXIOM-002, THEOREM-power-signal-decay, THEOREM-hierarchy-depth-limit, BR-L2-010, BR-L2-004
- DED-011 [verified] · 派系必然性与轮替抑制推论 — 只要一群人要长期分'不够分'的东西,就必然分裂成派系——有目标又牵涉利益的人对'怎么分' 必有立场(立场定理),稀缺(AXIOM-001)使立场…  ⟵ AXIOM-001, THEOREM-position, BR-L2-006, BR-L2-005
- DED-012 [verified] · 掠夺-保护同源与坐寇化推论 — 能抢的力量也能保护——同一种暴力两用  ⟵ AXIOM-001, THEOREM-conflict-cost, BR-L2-008, BR-L2-010
- DED-013 [verified] · 稀缺度-分配公平标准位移推论 — 东西越少,'平均分'越撑不住——不是人变坏了,是分配本身的逻辑变了  ⟵ AXIOM-001, BR-L2-013, BR-L2-017
- DED-014 [verified] · 程序公平的轮替天花板推论 — 过程再透明、裁判再中立，只要输家永远没机会翻盘——程序就不是'公道'而是'赢家的遮羞布  ⟵ BR-L2-015, DED-011
- DED-015 [verified] · 对等报复演化稳态 — 以眼还眼'不是圣人发明,是博弈逼的——罚太重两家一起死,罚太轻被当软柿子;只有跟罪等量的惩罚能把信号发稳、把架停住  ⟵ AXIOM-001, AXIOM-003, THEOREM-conflict-cost, THEOREM-competition-norm, BR-L2-016, BR-L2-014, BR-L2-005
- DED-016 [verified] · 面对面公平-制度化公平相变推论 — 150人以下,公平靠'我认识你、下次还得见'维持;一超过这个数,要么各群自己玩自己的公平(碎片化),要么把公平外包给法院/契约/法官(制度化)—…  ⟵ AXIOM-003, THEOREM-group-identity-decay, THEOREM-cooperation-precondition, BR-L2-004, BR-L2-009, BR-L2-010, BR-L2-015
- DED-017 [verified] · 感知不公-集体行动临界推论 — 单感到不公不会闹——得三个条件同时到位才会炸:不公都集中在看得见的一群人头上、这群人不是散沙能彼此通气、且没别的合法途径能翻盘  ⟵ AXIOM-001, THEOREM-position, BR-L2-013, BR-L2-014, BR-L2-006
- DED-018 [verified] · 亲缘-绩效分配切换推论 — 自家人分东西不计较谁干多干少——不是觉悟高,是血缘纽带让追踪贡献没必要; 但跟外人合作还按平均分?没人干  ⟵ AXIOM-001, THEOREM-cooperation-precondition, BR-L2-002, BR-L2-013, BR-L2-017
- DED-019 [verified] · 内群体扭曲公平感知推论 — 同一个规矩,判给'自己人'就觉得公道,判给'外人'就觉得不公——不是装傻,是人真心觉得自己没偏  ⟵ AXIOM-001, BR-L2-006, BR-L2-013, BR-L2-015
- DED-020 [verified] · 程序透明×裁决独立交互推论 — 程序透明不是万灵药，是放大器——裁判独立时，透明让公道更亮；裁判跟你不是一路人但跟对方是，透明反而把偏私曝光、让人更难咽  ⟵ BR-L2-015, BR-L2-006, BR-L2-002, DED-014, DED-008
- DED-021 [verified] · 第三方惩罚严重度校准 — 不光是'坏人该罚'——罚多重还得跟干了多大坏事配得上  ⟵ AXIOM-001, AXIOM-003, THEOREM-conflict-cost, THEOREM-competition-norm, THEOREM-cooperation-precondition, BR-L2-014, BR-L2-016, BR-L2-013
- DED-022 [verified] · 大规模社会多层公平冲突推论 — 一个人既是家人又是职员又是公民——这三个身份各自的'公道'不是同一回事,而且经常打架  ⟵ AXIOM-001, AXIOM-003, THEOREM-position, THEOREM-group-identity-decay, BR-L2-004, BR-L2-006, BR-L2-017
- DED-023 [verified] · 道德-习俗迁移判据 — 规范在道德与习俗之间迁移的秘密不在内容里，在两件事的变化里：有人看时罚不罚、没人看时心里过不过得去  ⟵ AXIOM-001, AXIOM-003, THEOREM-moral-third-party-enforcement, THEOREM-moral-internalization, BR-L2-014, BR-L2-018, BR-L2-019
- DED-024 [verified] · 道德内化瓦解动力学 — 良心不是一下子没的——合理化→比较→认知重组→情绪脱钩，崩了重建比建立难得多  ⟵ AXIOM-002, THEOREM-moral-internalization, BR-L2-019, BR-L2-014
- DED-025 [verified] · 道德标准通胀-紧缩 — 道德变严靠故事+有人推（受害叙事+道德创业者），变松靠放手（旁观者不管了+新一代不内化了）——紧缩是默认状态，通胀需要刻意维持能量投入  ⟵ PHY-001, THEOREM-moral-third-party-enforcement, THEOREM-moral-internalization, BR-L2-014, BR-L2-018, BR-L2-019
- DED-026 [verified] · 道德群体边界推论 — 对'自己人'和'外人'用两套道德不是双标——是第三方惩罚机制天然绑在群体边界上：你在一个合作系统里的利益占比决定了你愿花多大力气维护它的规矩，而…  ⟵ AXIOM-001, THEOREM-moral-third-party-enforcement, BR-L2-006, BR-L2-014, BR-L2-018
- DED-027 [verified] · 一般等价物的物理筛选机制 — 一般等价物的涌现是必然的——交换网络足够密时，总会有某种商品被所有人接受当钱用  ⟵ AXIOM-001, AXIOM-003, THEOREM-exchange-competition-alternative, THEOREM-value-attribution, THEOREM-relation-information-asset, THEOREM-cooperation-precondition, BR-L2-021, BR-L2-007, BR-L2-011, BR-L2-012
- DED-028 [verified] · 价值储藏-交易媒介的功能解耦动力学 — 交易媒介和价值储藏走两条独立轨道——法币信用下滑时，储蓄先跑（价值储藏迁移），支付后崩（交易媒介瓦解），中间的时间差可以长达数年  ⟵ AXIOM-002, AXIOM-003, THEOREM-value-attribution, THEOREM-relation-information-asset, THEOREM-cooperation-precondition, THEOREM-exchange-competition-alternative, BR-L2-022, BR-L2-024, BR-L2-011, BR-L2-012
- DED-029 [verified] · 金价单因素驱动机制 — 金价有四个独立驱动的方向性引擎——实际利率(-)、通胀预期(+)、法币信用(-)、不确定性(+)——各自可独立检验，不互相绑定  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, THEOREM-value-attribution, BR-L2-021, BR-L2-022, BR-L2-024
- DED-030 [verified] · 金的存量-流量不对称与价格弹性 — 金价不由开采成本定——每年新挖出来的金子只占地上存量的1-2%  ⟵ AXIOM-001, THEOREM-value-attribution, BR-L2-021, BR-L2-022, BR-L2-023
- DED-031 [verified] · 指标治理下的策略性上报失真 — 上级用数字考核下级、数字又是下级自己报的、上级还查不过来——这三件事凑齐，报上来的数字就会朝着'对下级有利'的方向系统性走样  ⟵ AXIOM-001, AXIOM-002, THEOREM-hierarchy-depth-limit, BR-L2-001, BR-L2-010, DED-001
- DED-032 [verified] · 消费信贷的自噬循环 — 让借钱变容易，头一两年大家确实多花了；但天生看重'现在'的人会借过头，接下来几年工资一到手先还债，手头反而更紧——而且吃过紧日子的人还会额外多存…  ⟵ AXIOM-001, BR-L2-028, BR-L2-030
- DED-033 [weakly_verified] · 社保-消费释放的信任约束 — 国家把医保、养老金铺开了，按说老百姓后顾之忧少了、就敢花钱了——这是教科书上的'无摩擦'预测  ⟵ AXIOM-001, AXIOM-002, BR-L2-028, BR-L2-031, BR-L2-024
- DED-034 [verified] · AI代理决策与个体判断力退化 — AI帮你做决定做多了,你自己做判断的能力会退化——不是AI坏,是用进废退  ⟵ AXIOM-002, BR-L2-026, BR-L2-027
- DED-035 [candidate] · 数据协调成本不对称冲击与企业边界分叉 — 数字数据+算法让做买卖和管公司都变便宜了,但便宜的程度不一样——能标准化、能量化的事,做买卖的成本降得比管公司更狠,所以企业把这类事外包出去;但…  ⟵ AXIOM-002, THEOREM-hierarchy-depth-limit, THEOREM-cooperation-precondition, BR-L2-001, BR-L2-009, BR-L2-010, DED-001, DED-006
- DED-036 [verified] · 算法成本断崖×货币物理筛选：从发现到设计 — 算法把搜索和评估成本压低了上万倍之后，'什么东西适合当钱'这件事的玩法彻底变了——以前是大自然花上千年慢慢筛选（金、银、铜，试了无数种东西才找到…  ⟵ AXIOM-001, AXIOM-002, THEOREM-exchange-competition-alternative, THEOREM-value-attribution, BR-L2-021, BR-L2-032
- DED-037 [candidate] · AI陪伴×道德发育窗口：道德他者模型偏移 — 小孩子怎么学会'伤害别人是不对的'？不是大人讲道理讲会的——是看到别人被自己弄疼时脸上的表情、听到对方声音发抖，这些真实的情绪反馈慢慢在孩子心里…
- DED-038 [candidate] · 制度信任崩解×法币功能解耦：恶性通胀的双重时间不对称 — 制度信任崩了之后，钱的两样功能各跑各的——'存钱'功能因为信任掉得快先跑（大家赶紧把钱换成金条、外币），但'标价'功能因为记忆惯性还留在原地（工…  ⟵ AXIOM-002, THEOREM-value-attribution, THEOREM-relation-information-asset, BR-L2-031, BR-L2-024
- DED-039 [candidate] · AI共享代码×大规模合作：想象秩序的必要性降级 — 人类大规模合作一直靠'大家都信同一个故事'——国家、宗教、市场都是靠人们共同相信一套叙事才让陌生人愿意合作  ⟵ AXIOM-002, AXIOM-003, THEOREM-cooperation-precondition, BR-L2-003, BR-L2-026
- DED-040 [candidate] · 算法监控成本断崖×第三方惩罚：惩罚通胀与惩罚疲劳的分叉 — 算法让发现别人违规的成本断崖式下降后,大量以前看不见的小违规全进了'可罚池'——这触发两种相反的走向:要么举报太多、每条举报越来越不值钱(惩罚通…  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, THEOREM-competition-norm, THEOREM-cooperation-precondition, THEOREM-conflict-cost, THEOREM-moral-third-party-enforcement, BR-L2-014, BR-L2-032
- DED-041 [verified] · 数字可处理性×道德内化：具身共情的系统性削弱 — 屏幕上的伤害没有血肉、没有颤抖的声音、没有真实的眼神接触——你知道对方受伤了，但你感受不到
- DED-042 [candidate] · 算法监控×制度信任不对称：修复斜率的系统性拉陡 — 制度信任有个扎心规律——掉得快、涨得慢
- DED-043 [candidate] · AI协调与层级压缩：150人阈值的条件化 — 一群人超过150人就得出领导、分上下级——因为人脑的社交关系和处理信息的能力有天花板
- DED-044 [candidate] · 掠夺策略×制度信任替代：共生性双向塑造 — 抢别人东西和建立制度管住抢劫，这两件事不是简单的'制度强了就不抢了'单向关系——它们是互相塑造的  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, AXIOM-004, THEOREM-conflict-cost, THEOREM-cooperation-precondition, THEOREM-relation-information-asset, BR-L2-008, BR-L2-010
- DED-045 [verified] · AI承诺装置×现时偏向：财务命运的分叉放大器 — AI同时是帮人存钱的最强工具和诱人花钱的最强工具——同一套技术,用在帮你管钱上能自动存、自动锁、自动盯着预算,比你自己咬牙坚持靠谱得多;但用在让…  ⟵ AXIOM-001, AXIOM-002, BR-L2-026, BR-L2-030
- DED-046 [verified] · 注意力稀缺xMPC收入梯度：注意力-消费的恶性螺旋 — 穷人不是大手大脚——是脑子被生存焦虑占满了,没余力抵抗算法精准推送的消费诱惑  ⟵ AXIOM-001, AXIOM-002, BR-L2-027, BR-L2-029
- DED-047 [candidate] · AI货币功能解耦×社会共识生成：优化器而非奠基者 — AI可以把货币的三大功能（买东西、标价格、存钱）拆开再拼回去的技术做到极致——算法能让钱在不同功能之间无缝切换、自动优化  ⟵ AXIOM-002, AXIOM-003, THEOREM-value-attribution, THEOREM-cooperation-precondition, THEOREM-group-identity-decay, BR-L2-022, BR-L2-026
- DED-048 [candidate] · 算法结算成本×通用媒介收敛：从技术必然到制度选择 — 以前大家非得用同一种钱,不是因为'用同一种钱方便',而是因为不用同一种钱的话,算清楚'我欠你、你欠他、他又欠她'这笔七拐八绕的账实在太贵了——人…  ⟵ AXIOM-002, THEOREM-exchange-competition-alternative, THEOREM-value-attribution, THEOREM-relation-information-asset, BR-L2-012, BR-L2-032
- DED-049 [candidate] · 制度信任不对称衰减×金非货币需求：金价的阶梯式棘轮 — 每次大的制度信任危机（金融海啸、主权违约恐慌、法币信用动摇）都会把金价永久性地推上一个新台阶——危机来时金价急涨，危机过后金价回落，但再也回不到…
- DED-050 [verified] · 数字可处理性x制度信任不对称：失信信号永久化与修复信号噪声化 — 对制度的信任有个扎心规律——掉得快、涨得慢  ⟵ AXIOM-002, THEOREM-relation-information-asset, BR-L2-025, BR-L2-031
- DED-051 [candidate] · 人际信任衰减梯度×通货必要性：社区货币的生态位边界 — 熟人之间不用钱——谁帮了谁、谁欠了谁，大家都记在心里，跑不掉  ⟵ AXIOM-002, AXIOM-003, THEOREM-relation-information-asset, THEOREM-group-identity-decay, THEOREM-cooperation-precondition, BR-L2-009, BR-L2-011
- DED-052 [candidate] · MPC收入梯度×不公平厌恶：消费Gini作为财富Gini的掩码器 — 富人和穷人的收入差N倍,但花的钱只差M倍(M<N)——因为富人大多存起来了  ⟵ AXIOM-001, AXIOM-002, BR-L2-013, BR-L2-029
- DED-053 [candidate] · AI无群体身份与内群体偏好消解 — AI既不是'自己人'也不是'外人'——它根本没有群体身份
- DED-054 [verified] · 数字可处理性×法币记忆滞后：双向效应与治理条件 — 法币的信用有个惯性——人对通胀的记忆消退得比实际通胀下降慢，大家不信政策、只信自己经历过的（BR-L2-024）  ⟵ AXIOM-002, THEOREM-value-attribution, BR-L2-024, BR-L2-025
- DED-055 [candidate] · 现时偏向×法币记忆滞后：前瞻指引效力的双重折扣 — 央行说'两年后通胀会降到2%',但老百姓听了并不会当真去买两年后的国债锁定收益——因为人天生就觉得'两年后的事太远了,先顾眼前'(现时偏向)  ⟵ AXIOM-001, AXIOM-002, THEOREM-value-attribution, BR-L2-024, BR-L2-030

## L3 审查 reviews (61)
- ADV-REVIEW-001 [needs_revision] — 这是对推论 DED-001（组织层级深到一定程度，高层就再也管不清底层）的第一轮挑刺审查：审查者挑出四个毛病——关键数字（信息每传一层损耗多少）…
- ADV-REVIEW-002 [needs_revision] — 这是对推论 DED-002（纯靠口口相传的规矩，社会一大就承载不下、必须借助文字等手段）的第一轮挑刺审查：审查者搬出冰岛这类反例、质疑'一条规矩…
- ADV-REVIEW-003 [needs_revision] — 这是对推论 DED-003（外部没有对手了，内部凝聚力就会慢慢松散）的第一轮挑刺审查，也是三条推论里被批得最狠的一次：瑞士等一批长期和平却依旧团…
- ADV-REVIEW-004 [verified] — 这是对推论 DED-001 修订版的第二轮审查：上一轮四个毛病都补好了（关键数字补了实验依据、三种结局给了各自独立的判定标准），新提的三个是小问…
- ADV-REVIEW-005 [verified] — 这是对推论 DED-002 修订版的第二轮审查：上一轮五个毛病（冰岛反例、'一条规矩怎么数'等）都补好了，新提的三个只是改进建议，最终从'候选'…
- ADV-REVIEW-006 [verified*] — 这是对推论 DED-003 修订版的第二轮审查：上一轮的大问题都补好了（把'能量'改成可测量的'维护投入'、堵住了怎么都推不翻的漏洞），但瑞士这…
- ADV-REVIEW-007 [verified] — 经验检验发现推论 DED-002 漏了第四种应对方式——'分裂'（社会太大就拆成很多个口头管得住的小单元，如索马里、伊博），作者据此把它补进推论…
- ADV-REVIEW-008 [needs_revision] — 这是对推论 DED-004（本体系第一条'两条规律合起来才成立'的推论）的对抗式审查：特意派独立 AI 拼命找茬，发现作者自称的三块新意有三分之…
- ADV-REVIEW-009 [rejected] — 经验检验推翻了推论 DED-004 仅剩的那点新意，作者又从同一批数据里捞出一个'打折版'命题想继续救，这是对'打折版'的第三轮审查：独立 AI…
- ADV-REVIEW-010 [needs_revision] — 这是对新推论 DED-005(贸易vs劫掠)的第一轮挑刺
- ADV-REVIEW-011 [needs_revision] — 对新推论 DED-006(信任天花板→制度外化)的第一轮挑刺
- ADV-REVIEW-012 [needs_revision] — 对 DED-007(通货=记忆替代)的第一轮挑刺,是本系列最狠的一轮,判'需强修订、逼近归零
- ADV-REVIEW-013 — 对 DED-008(裙带侵蚀×监督者独立)的独立对抗审查记录
- ADV-REVIEW-014 — 对 DED-009(亲缘组织的规模天花板 → 拟制亲缘 or 制度外化)的独立对抗审查记录
- ADV-REVIEW-015 — 对 DED-010(权力维持成本与制度化:纯人格化支配随规模上升须付递增展示成本、撞天花板 ⇒ 二选一 递增展示 or 制度化)的独立对抗审查
- ADV-REVIEW-016 — 对 DED-011(派系必然性 → 轮替/退出/申诉抑制固化-撕裂)的独立对抗审查记录
- ADV-REVIEW-017 — 对 DED-012(掠夺-保护同源 + 坐寇化:领地固定性↑ ⇒ 抽税-供秩序↑、掠夺烈度↓,单调+可逆, 招牌是"高固定性 × 长期控制 × …
- ADV-REVIEW-018 — 对 DED-013(稀缺度-分配公平标准位移:资源越少,分配逻辑从平等到贡献/需要单调位移, 物理可行性塌缩机制+空格预测)的独立对抗审查记录
- ADV-REVIEW-019 — 对 DED-014(程序公平的轮替天花板推论)的独立对抗审查记录 round-1
- ADV-REVIEW-020 — 对 DED-015(对等报复演化稳态:在无中心权威+重复交互下,'以眼还眼'不是法律发明而是唯一演化稳定惩罚规范, 因过度被冲突成本淘汰、不足被…
- ADV-REVIEW-021 — 对 DED-016(面对面公平-制度化公平相变推论)的 round-1 独立对抗审查
- ADV-REVIEW-022 — 对 DED-017(感知不公-集体行动临界推论:不公集中在可辨识群体 × 预存组织 × 无改革渠道, 三者缺一不公转犬儒不转行动)的独立对抗审查…
- ADV-REVIEW-023 — 对 DED-018(亲缘-绩效分配切换推论:亲缘度 moderates 分配标准——血缘越近平等/ 需要权重越高、血缘越远绩效权重越高;非亲缘+…
- ADV-REVIEW-024 — 对 DED-019(内群体扭曲公平感知推论:同一个规矩判给自己人=公道、判给外人=不公,且人真心 觉得自己没偏)的 round-1 独立对抗审查
- ADV-REVIEW-025 — 对 DED-020(程序透明x裁决独立交互推论:透明不是万灵药是放大器——裁判独立时透明让公道更亮, 裁判不独立时透明反成羞辱放大器)的独立对抗…
- ADV-REVIEW-026 — 对 DED-021(第三方惩罚严重度校准:惩罚力度跟踪违规严重度+失配惩罚触发反惩罚+自校准闭合循环) 的 round-1 独立对抗审查
- ADV-REVIEW-027 — 对 DED-022(大规模社会多层公平冲突推论)的 round_1 独立对抗审查
- ADV-REVIEW-027-DED-027 — DED-027（一般等价物的物理筛选机制）对抗审查全过程的单一存档，含 round_1 与 round_2 两轮
- ADV-REVIEW-028 — 对 DED-023(道德-习俗结构判据:Moral-Convention Structural Criterion)的 round_1 独立对抗…
- ADV-REVIEW-029 — 对 DED-024(道德内化瓦解动力学:四阶段剥洋葱顺序刚性+阶段3不可逆+替代路径+能量不对称) 的 round-1 独立对抗审查
- ADV-REVIEW-030 — 对 DED-026(道德群体边界推论:TP强度在群体边界处结构性陡降+边界可移动+旁观者效应结构重解释+ 道德帝国主义)的 round-1 独立…
- ADV-REVIEW-031 — 对 DED-025（道德标准通胀-紧缩：通胀靠叙事+创业者推，紧缩靠放手——旁观者不管+新一代不内化， 紧缩是默认状态）的 round-1 独立…
- ADV-REVIEW-032 — 对 DED-030(金的存量-流量不对称与价格弹性)的 round-1 独立对抗审查
- ADV-REVIEW-034 — 对 DED-028(价值储藏-交易媒介的功能解耦动力学:法币信用下滑时 SOV 先逃逸、 MOE 后崩塌,中间的时间差随信用下滑速度非线性变化)…
- ADV-REVIEW-035 — 对 DED-029(金价单因素驱动机制:Single-Factor Drivers of Gold Price)的 round_1 独立对抗审查
- ADV-REVIEW-036 — 对 DED-031(指标治理下的策略性上报失真)的 round_1 独立对抗审查
- ADV-REVIEW-037 — 对 DED-032(消费信贷的自噬循环)的 round_1 独立对抗审查
- ADV-REVIEW-038 — 对 DED-033(社保-消费释放的信任约束)的 round_1 独立对抗审查
- ADV-REVIEW-039 — 对 DED-034(AI代理决策与个体判断力退化)的 round_1 独立对抗审查
- ADV-REVIEW-040 — 对 DED-035(数据协调成本不对称冲击与企业边界分叉)的 round_1 独立对抗审查
- ADV-REVIEW-041-DED-036 — DED-036（算法成本断崖×货币物理筛选：从发现到设计）round_1 独立对抗审查—— needs_revision
- ADV-REVIEW-042 — 对 DED-037(AI陪伴×道德发育窗口：道德他者模型偏移)的 round_1 独立对抗审查
- ADV-REVIEW-043 — 对 DED-038(制度信任崩解×法币功能解耦:恶性通胀的双重时间不对称)的 round_1 独立对抗审查
- ADV-REVIEW-044 — 对 DED-039(AI共享代码×大规模合作:想象秩序的必要性降级)的 round_1 独立对抗审查
- ADV-REVIEW-045 — 对 DED-040(算法监控成本断崖×第三方惩罚:惩罚通胀与惩罚疲劳的分叉)的 round_1 独立对抗审查
- ADV-REVIEW-046 — 对 DED-041(数字可处理性×道德内化:具身共情的系统性削弱)的 round_1 独立对抗审查
- ADV-REVIEW-047 — 对 DED-042(算法监控×制度信任不对称:修复斜率的系统性拉陡)的 round_1 独立对抗审查
- ADV-REVIEW-048 — 对 DED-043(AI协调与层级压缩:150人阈值的条件化)的独立对抗审查记录
- ADV-REVIEW-049 — 对 DED-044(掠夺策略×制度信任替代:共生性双向塑造)的 round_1 独立对抗审查
- ADV-REVIEW-050-DED-045 — DED-045（AI承诺装置×现时偏向：财务命运的分叉放大器）对抗审查 round_1 存档
- ADV-REVIEW-051 — 对 DED-046(注意力稀缺xMPC收入梯度:注意力-消费恶性螺旋)的 round_1 独立对抗审查
- ADV-REVIEW-052 — 对 DED-047(AI货币功能解耦×社会共识生成:优化器而非奠基者)的 round_1 独立对抗审查
- ADV-REVIEW-053 — 对 DED-048(算法结算成本×通用媒介收敛:从技术必然到制度选择)的 round_1 独立对抗审查
- ADV-REVIEW-054-DED-049 — DED-049（制度信任不对称衰减×金非货币需求：金价的阶梯式棘轮）对抗审查 round_1 存档
- ADV-REVIEW-055 [verified] — DED-050 是新推论'数字可处理性x制度信任不对称：失信信号永久化与修复信号噪声化'的首轮独立对抗审查
- ADV-REVIEW-056 — 对 DED-051(人际信任衰减梯度×通货必要性：社区货币的生态位边界)的第一轮独立对抗审查
- ADV-REVIEW-057 — 对 DED-052(MPC收入梯度作为财富Gini的消费掩码器)的 round_1 独立对抗审查
- ADV-REVIEW-058 — 对 DED-053(AI无群体身份与内群体偏好消解)的 round_1 独立对抗审查
- ADV-REVIEW-059-DED-054 — DED-054（数字可处理性×法币记忆滞后：双向效应与治理条件）对抗审查 round_1 存档
- ADV-REVIEW-060 — 对 DED-055(现时偏向×法币记忆滞后：前瞻指引效力的双重折扣)的第一轮独立对抗审查
- META-REVIEW-001 — 这份文件记录了一次"自我审查":我(负责推理的 AI)先用第一性原理给整个体系挑了 四个毛病,然后请另一个独立的 AI 拼命反驳我

## L3 其它(经验检验/交叉验证等) (6)
- EMP-TEST-001 [conducted] — 拿 14 个前现代国家/帝国的真实历史去撞推论 DED-001（没有文字等记录系统辅助，组织的有效管理层级深不过 8 层）：数了每个的层级深度和…
- EMP-TEST-002 [conducted] — 拿 14 个前现代/无文字社会的真实历史去撞推论 DED-002（口头规矩承载不了大社会，必须靠写成文字、分层或专职人员之一来应对）：挑了冰岛、…
- EMP-TEST-003 [conducted] — 拿 12 个大型政体的兴衰历史去撞推论 DED-003（外部对手消失、又没补上别的凝聚手段，内部就会散）：追踪每个在失去外敌前后的凝聚力变化，大…
- EMP-TEST-004 [pre_registered] — 拿 20 个前现代政体、事先锁死方案做盲测，检验推论 DED-004 唯一的新意（'把行政记下来'和'把法律写下来'这两件事会绑在一起出现）：结…
- ICV-001 [conducted] — 请两个'血统不同'的免费 AI 独立盲打分，复核推论 DED-001 经验检验里那 14 个国家的层级数——不图它们更聪明，图它们'错得不一样'…
- L3-METHODOLOGY [canonical]

## L4 复合推论 composites (14)
- L4-001 [verified*] · 国家形成轨迹：从流寇到国家的多条路径 — 流寇变坐寇只是第一步——坐寇最终交出制度型国家、采掘型帝国、还是退化回碎片化， 取决于三股力量的同时拉扯：外面有没有敌人、税是从商人身上收还是农…  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, THEOREM-conflict-cost, THEOREM-power-signal-decay, THEOREM-relation-information-asset, THEOREM-group-identity-decay, THEOREM-cooperation-precondition, THEOREM-exchange-competition-alternative, THEOREM-hierarchy-depth-limit, BR-L2-008, BR-L2-010, BR-L2-004, BR-L2-009, BR-L2-003, BR-L2-006, DED-012, DED-010, DED-006, DED-003
- L4-002 [verified] · 政体稳定相图 — 政权稳不稳，不是看它"民主不民主"一个指标——是三股力量的同时博弈：输了的人还有没有路走、 裁判是不是自己人、不公平有没有集中到某个群体且让他们…  ⟵ AXIOM-001, THEOREM-position, BR-L2-015, BR-L2-006, BR-L2-013, BR-L2-014, DED-011, DED-014, DED-020, DED-017
- L4-003 [verified] · 制度共演锁定 — 一个社会用什么样的公平规矩分东西，不是某个人拍板定的——是亲缘远近、人多不多、 资源够不够这三股力量在历史关口上一起决定的  ⟵ AXIOM-001, AXIOM-003, THEOREM-position, THEOREM-group-identity-decay, THEOREM-cooperation-precondition, BR-L2-002, BR-L2-004, BR-L2-006, BR-L2-009, BR-L2-013, BR-L2-015, BR-L2-017, DED-013, DED-016, DED-018, DED-022
- L4-004 [verified] · 信息技术-社会形态相变推论 — 文字、印刷、数字——三次信息成本崩塌，每次崩塌都让社会能'长'出之前物理上不可能的组织形态  ⟵ AXIOM-002, THEOREM-hierarchy-depth-limit, THEOREM-norm-energy-saver, THEOREM-cooperation-precondition, THEOREM-power-signal-decay, BR-L2-001, BR-L2-004, BR-L2-009, BR-L2-010, DED-001, DED-002, DED-006, DED-010
- L4-005 [verified*] · 民族国家的未来：功能分化轨迹 — 民族国家不会消亡、也不会永恒——它在被四个方向同时拉扯：往上交（跨国税基→超国家）、 往下放（数字让小群体自组织）、往外包（市场/网络替代制度）…  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, THEOREM-hierarchy-depth-limit, THEOREM-norm-energy-saver, THEOREM-cooperation-precondition, THEOREM-power-signal-decay, THEOREM-group-identity-decay, THEOREM-exchange-competition-alternative, THEOREM-relation-information-asset, THEOREM-conflict-cost, THEOREM-position, BR-L2-003, BR-L2-004, BR-L2-006, BR-L2-008, BR-L2-009, BR-L2-010, BR-L2-013, BR-L2-015, BR-L2-017, DED-022, DED-006, DED-020, DED-003
- L4-006 [verified] · 道德-制度共演 — 法律和道德互相兜底也互相腐蚀——法律太强人就不内化了（'反正有警察管'），道德太碎法律跟不上（每个小群体都有自己的道德→法律不知道该保护谁）  ⟵ AXIOM-001, AXIOM-003, PHY-001, THEOREM-moral-third-party-enforcement, THEOREM-moral-internalization, THEOREM-norm-energy-saver, BR-L2-014, BR-L2-018, BR-L2-019, DED-023, DED-025, DED-016, DED-024
- L4-007 [verified] · 数字时代道德碎片化 — 算法让邻居活在两个道德宇宙——TP默契崩了，一个社会挤着好几个互不通气的道德部落  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, PHY-001, THEOREM-moral-third-party-enforcement, THEOREM-moral-internalization, THEOREM-group-identity-decay, BR-L2-006, BR-L2-014, BR-L2-018, BR-L2-019, DED-026, DED-025
- L4-008 [verified*] · 道德绑架 — 道德绑架劫持的不是人的善良，是道德执行机制的自动化回路——A指控→C自动惩罚→B屈从  ⟵ AXIOM-002, THEOREM-moral-third-party-enforcement, THEOREM-moral-internalization, BR-L2-014, BR-L2-006, BR-L2-018, DED-023, DED-026, DED-021, DED-024
- L4-009 [rejected] · 金价体制切换 — 金价有两套定价规则来回切换——平时它是'商品'，跟着实际利率走（利率高金价跌）；法币信用出问题时它切回'钱'，实际利率失灵、央行和储户抢存量、价…  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, THEOREM-value-attribution, BR-L2-021, BR-L2-022, BR-L2-023, BR-L2-024, DED-027, DED-028, DED-029, DED-030
- L4-010 [rejected] · 价值储藏放大器的需求部门门控 — 金价对增量需求的'放大器'不是常开的——央行和储户抢金子时放大器全开、等量买盘能掀翻价格；ETF玩家主导时放大器休眠、买卖更'讲道理  ⟵ AXIOM-001, THEOREM-value-attribution, BR-L2-021, BR-L2-022, BR-L2-024, DED-029, DED-030
- L4-011 [rejected] · 主权信用事件的储蓄端传导链 — 当一个大国储备资产被冻结（≥全球储备1%），钱跑的路线是可预测的——央行先动（换黄金、调结构），老百姓后跟（买金条金币），最后金价重估  ⟵ AXIOM-001, AXIOM-002, THEOREM-value-attribution, BR-L2-022, BR-L2-024, DED-028, DED-029
- L4-012 [verified] · 储备资产地位变迁的网络效应动力学 — 储备货币的改朝换代不是各国各自算账的独立决策——它是网络效应驱动的体制切换  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, THEOREM-value-attribution, THEOREM-exchange-competition-alternative, THEOREM-relation-information-asset, THEOREM-cooperation-precondition, BR-L2-021, BR-L2-022, BR-L2-024, BR-L2-007, BR-L2-011, BR-L2-012, DED-027, DED-028, DED-029
- L4-013 [verified] · 数字时代价值储藏媒介竞争格局 — 数字交换网络把'什么东西适合当钱/当储备'的六条老规矩重新洗牌了——可分割、可验证、可携带这三条在数字世界里彻底变了含义  ⟵ AXIOM-001, AXIOM-002, AXIOM-003, THEOREM-value-attribution, THEOREM-exchange-competition-alternative, THEOREM-relation-information-asset, THEOREM-cooperation-precondition, BR-L2-021, BR-L2-022, BR-L2-024, DED-027, DED-029
- L4-014 [candidate] · 平台作为第三组织形态 — 平台(Uber/淘宝/Airbnb)既不是公司(层级命令),也不是菜市场(纯买卖关系)——它是第三种组织:算法当'中层管理'来协调、评分系统当'…  ⟵ AXIOM-002, THEOREM-hierarchy-depth-limit, THEOREM-cooperation-precondition, BR-L2-001, BR-L2-009, BR-L2-010, BR-L2-025, DED-001, DED-006

## L4 审查 reviews (14)
- ADV-REVIEW-L4-001 — 对 L4-001(国家形成轨迹:从流寇到国家的多条路径,status=candidate)的 round_1 独立对抗审查
- ADV-REVIEW-L4-002 — 对 L4-002(政体稳定相图:三股力量的同时博弈——轮替开放度×裁决独立度×透明度×不公集中度 →四区+相变边界)的独立对抗审查记录
- ADV-REVIEW-L4-003 — 对 L4-003(公平制度演化推论)的 round_1 独立对抗审查
- ADV-REVIEW-L4-004 [needs_revision] — L4-004 有真东西——找到四条父推论共享的信息技术成本这一共同驱动量——但核心弱点有三: (1) 逐格判空只找到一个弱合力格 (Digita…
- ADV-REVIEW-L4-005 [verified] — Round 1 五条 required 修复全部落地——空格参数限定、合取/交互诚实区分、 L4-001 verified* 置信度天花板声明、…
- ADV-REVIEW-L4-006 [needs_revision] — L4-006 有真正的理论野心——把四条独立发展的道德/法律推论合成为双向共演系统
- ADV-REVIEW-L4-007 [needs_revision] — L4-007 有真东西——DED-026 的边界增殖与 DED-025 的熵增通道并行化产生'多道德空间各自独立演化→不可通约'这一新预测，合取…
- ADV-REVIEW-L4-008 [needs_revision] — L4-008 有真实的新颖贡献——道德绑架的 A→B→C 三角结构作为武器化路径，Type I（信息劫持） 与 Type II（结构劫持）的区分…
- ADV-REVIEW-L4-009 [needs_revision] — L4-009 是一条有真涌现的复合推论——招牌格（重定价×高利率）确实需要 DED-029+028+030 三父合力，相关性断裂作为体制指示器是…
- ADV-REVIEW-L4-010 — L4-010 把 L4-009 里最硬的交互（放大器被需求构成门控）剥出来单独提案，操作化确实比 L4-009 干净得多——连续 gate、无阈…
- ADV-REVIEW-L4-011 — 对 L4-011（主权信用事件的储蓄端传导链，status=candidate）的 round_1 独立对抗审查
- ADV-REVIEW-L4-012 — 对 L4-012（储备资产地位变迁的网络效应动力学）的 round_1 独立对抗审查
- ADV-REVIEW-L4-013 — L4-013 说的是"数字资产可能在下次信用危机里抢走原本流向黄金的避险钱
- ADV-REVIEW-L4-014 — L4-014 说"平台(Uber/淘宝)是公司和市场之外的第三种组织

## L4 其它(经验检验/交叉验证等) (1)
- L4-METHODOLOGY [canonical]


---

## 2. 作者前置清单（A–E 段 + 瘦身 canonical 格式）

## A. 非平凡性(最先自查)

- [ ] **逐格判空**:把推论的核心画成 2×N 判据表(自变量档 × 被预测量档)。**每一格问:是被承重砖【平凡地】强制的吗?** 至少要有一个格是【预测为空/非空可满足】的真经验主张(不是同义反复)。空格必须可被现实反例填上才算数。
- [ ] **brick=conclusion**:推论的非平凡内核,是否【原文或近义】已写在某块承重砖里?若是 → 这不是推论,是砖的复述。特别警惕"专为这条推论窄化的砖"。
- [ ] **砖的边际贡献诚实**:每块承重砖各自单独给出什么?哪块偏"近定义"(只界定概念)、哪块是真发动机?点明,别让近定义砖冒充非平凡来源。

## B. 操作化(防不可证伪)

- [ ] **条件是下定义还是做预测**:核心命题里每个关键条件——是在偷偷下定义(必然为真),还是可证伪的预测?定义不算能力。
- [ ] **测量轴正交**(DED-007 死因):自变量与被预测量,是否在【彼此独立】的轴上测?有没有隐藏焊点——某个自变量偷偷用结果来测?典型:分母别用"实际获授者"(混入结果),要用"合格候选池"。
- [ ] **anti-talisman 真兑现**:判定"是否发生 X"(突破/俘获/侵蚀)时,必须【独立于结果】结构测,不得由"结果发生了"反推"前件成立"。而且——至少一个承重锚要像 DED-005 卡拉哈里、DED-006 集市、DED-008 科举回避那样,**真的独立测出了驱动量**,不是嘴上说说。
- [ ] **分类判据档位匹配**(DED-006):若做分档/分类,档位数要匹配被救对象的档位(连续量别用二分判据)。
- [ ] **阈值连口径一次性注册**(L4-009 判例):任何阈值/判据必须连同分子、分母、测量口径在起草时一并写死,不得只注册数字留口径空白。为什么:口径若留到边界反例出现后再定,选择方向必被结果污染——届时凡靠事后口径救活的边界案例,审查一律按不利于推论方向计,对应闸门不得计为守住。
- [ ] **枚举穷尽 + species 按判据定义**(DED-007/008):若声称"N 类可枚举/可解离"——(1) 每类必须按【伞级判据本身】定义,不能按某个相关但【不等价】的表征(DED-008:按"是否分享偏私收益"而非"亲缘网内外");(2) 主动猎"第 N+1 类";(3) 先证各测量维度正交。

## C. 射程与判别

- [ ] **射程/排除钩子独立于结果**(DED-005):excluded_outcomes 按【可事前测的渠道】划,不是事后按结果开脱。排除的东西要能事前认出。
- [ ] **primary_suspect 指对**:诚实点名最弱的承重环节(招牌预测压在哪条腿上),并写进 `falsification_trace`。
- [ ] **判别效度 + 防平凡化**:相对相邻已知理论(韦伯/North/委托-代理…),本推论【独有的可证伪预测】是什么?写一条"防平凡化守卫":把非平凡内核精确定位(通常在驱动量归因 / 可逆单调 / 特定失败渠道),别把权重压在会被吸收进常识的卖点上。

## D. 现实锚(防事实错)

- [ ] **事实核查**:每个历史/经验锚,核对基本事实(DED-007 死在战俘营锚的事实反转)。宁可少锚,不可错锚。
- [ ] **至少一个锚独立测出驱动量**(呼应 anti-talisman):`independent_*_evidence` 字段兑现"不看结果也能测出前件"。
- [ ] **反例猎捕先自己做一遍**:主动找一个能证伪核心的干净反例,消化或诚实认伤。别把这活全留给审查者。
- [ ] **数据源独立性核查**:每个经济/统计类锚点,核查底层测量链是否分叉。同一套国家账户由不同机构(CNBS/WB/IMF)分别发布 ≠ 多源独立验证。引用前先查 `sources/independence-model.yaml` 的 `data_source_origin` 节——若多个发布机构共享同一底层数据源,独立系数 ≤0.1,不得将"三源一致"当作"三重独立验证"。

## E. 诚实与依赖

- [ ] **人话摘要**:在场、忠实、非架构人也能懂。
- [ ] **新砖的 IEA/status 诚实**:若顺带建 L2 砖,IEA 权重与独立系数照实,不为凑 verified 灌水。
- [ ] **API 可及性 ≠ 数据独立性**:能通过 API/MCP 工具查到多个来源的数据,不等于这些数据来自独立测量链。工具可靠性分层(某 API 稳定、某 API 有限流)是工程信息,不是认识论信息。不得将"调通了三个 API"当作"三个独立证据"。诚实标注哪些数据源共享底层测量链(见上"数据源独立性核查")。
- [ ] **依赖闭合**:depends_on 里的 axioms/theorems/bridging/concepts 全部真实存在(跑 validate.py)。

---

## 瘦身 canonical DED 格式(单一存档,审查史不双存)

DED 文件**只放规范 claim**,审查全过程**只存 ADV-REVIEW-NNN 一处**,DED 里留 3 行摘要 + 指针。目标 ~120–160 行,不是 350+。

```yaml
id: DED-NNN
type: deduction
layer: L3-deductions
status: candidate            # 定论后 → verified / verified* / rejected
term: "中文名 (English Name)"

人话摘要: "..."              # 一段,非架构人也能懂

statement: |                 # 规范陈述:核心 / 驱动量 / 预测 / 与现有理论判别
  【核心】... 【驱动量】... 【预测】(i)(ii)(iii) ... 【判别】...

operationalization:          # 规则 A:每个量 definition / measurement / limitations
  <自变量>: {definition, measurement, limitations}
  <被预测量>: {definition, measurement, limitations}

derivation:
  from_l1: {axioms: [...], theorems: [...]}
  from_l2: {bridging: [...]}
  steps: |                    # ← 必须用 | 字面块标量(见下 YAML 陷阱)
    1. "..." ...
    2. "..." ...
    ...非平凡性(逐格判空)写在最后一步...

falsifiability: |            # (a)(b)(c) 可证伪条件;必要时标注适用区间
falsification_trace: {primary_suspect, secondary_suspect, unlikely_suspect, note}
excluded_outcomes: [...]     # 射程外,按渠道划
anti_talisman_clause: |      # 防不可证伪护身符,独立于结果测量
nontriviality_test: |        # 逐格判空的结论:哪一格预测为空、为何非空可满足
real_world_anchors: {supporting: [...], counterexamples: [...], boundary_cases: [...]}
discriminant_validity: |     # 独有可证伪预测 + 防平凡化守卫

review_summary: |            # ← 只留 3 行,不放全过程
  r1 <verdict> → r2 <verdict> → r3 <verdict>。全档见 ADV-REVIEW-NNN。
  一句话:<最终为何 verified/rejected>。

depends_on: {axioms, theorems, bridging, concepts}
domain: [...]
created: YYYY-MM-DD
```

### YAML 陷阱(踩过两次,务必守)

- **多行叙述段一律用 `|` 字面块标量**(statement / derivation.steps / falsifiability / anti_talisman_clause / …)。
- **别在裸标量里写 ASCII 冒号+空格或行尾冒号**——`达成有三 species:` 这种会被 YAML 当成 mapping,静默把整块顶飞、实体少一个还报"✅通过"。中文冒号"："或用 `|` 块规避。
- 改完**必跑** `cd <repo> && python scripts/validate.py`,确认实体数 +1 且无 `❌ YAML`。
