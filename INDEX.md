# INDEX.md — 实体紧凑索引

> 自动生成,**勿手改**。实体增删改后跑 `python scripts/index.py` 重生。
> 用途:未来 agent【先读本索引】了解已有实体与依赖,只在需核对时才开某几份全文——
> 把碰存量实体的读取成本封顶,不随实体增多滚雪球。
> 行格式:`id [status] · term — 摘要  ⟵ 承重依赖`

**78 实体**

## L0 物理约束 (3)
- PHY-001 — 东西放着不管就会自然变乱、变坏(这就是热力学第二定律);社会里的制度、组织、知识也一样——不持续投入精力去维护,就会自然松散、退化,不存在'一次…
- PHY-002 — 能量不会凭空冒出来,只能从别处搬来或从存货里取(即能量守恒);所以一个社会能干多少事,归根到底受制于它能弄到多少能量,没有'无中生有'的无限增长  ⟵ PHY-001
- PHY-003 — 物理世界的时空规矩管着一切社会活动:一个人不能同时出现在两个地方、东西要花时间才能运到、时间只能往前走(做了选择就没法反悔)、同一块地不能被两拨…

## L1 · 概念 concepts (16)
- CONCEPT-agent · 行动者 — 行动者'指任何有自己想达成的目标、能看清眼下处境、并会主动做事去接近目标的主体——可以是人、动物、组织甚至程序,不专指人类
- CONCEPT-choice · 选择 — 选择'就是在几条互相排斥、只能走一条的路里挑一条去做;因为时间和资源都有限,人根本躲不开选择——连'什么都不做'也是一种选择(等于选了维持现状)  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-resource, CONCEPT-information
- CONCEPT-competition · 竞争 — 竞争'指两个以上的主体都想要同一份不够分的资源,一方多拿另一方就少拿;它不需要双方认识、也不用真吵起来,只要资源有限、大家都要,竞争就客观存在  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-resource
- CONCEPT-conflict · 冲突 — 冲突'指双方直接较劲、至少一方存心要妨碍对方,比竞争更进一步(竞争可以互不知情,冲突必然是面对面对着干),而且打起来双方都得耗成本  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-interaction, CONCEPT-competition, CONCEPT-resource, CONCEPT-information
- CONCEPT-cooperation · 合作 — 合作'指几方自愿地配合彼此的行动,一起做成单靠自己做不成(或做不好)的事,而且合起来的总收益比各干各的更大;它可以纯粹出于自利,不必是无私奉献  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-choice, CONCEPT-interaction, CONCEPT-information
- CONCEPT-exchange · 交换 — 交换'指双方你情我愿地互相让出各自的东西(物品、服务、信息都行),换完后每一方都觉得自己更划算了;它不创造新资源,只是把已有资源挪到更需要它的人…  ⟵ CONCEPT-agent, CONCEPT-resource, CONCEPT-interaction, CONCEPT-choice, CONCEPT-relation, CONCEPT-information
- CONCEPT-goal · 目标 — 目标'就是一个主体想达到或想保住的某种状态;正是当前状态和目标之间的差距,驱使它去行动  ⟵ CONCEPT-agent
- CONCEPT-group · 群体 — 群体'指因为共享某种身份(血缘、语言、地域、信仰等)而聚成的一群人;它必然有边界,分得清谁是自己人、谁是外人,而且这份认同得靠仪式、符号、故事不…  ⟵ CONCEPT-agent, CONCEPT-information, CONCEPT-relation, CONCEPT-goal, CONCEPT-choice
- CONCEPT-hierarchy · 层级 — 层级'就是组织里把人分成上下级、上级对下级有更大决策权的安排;它存在的意义是省沟通成本——不用人人都参与每个决定,决策权往上收、执行往下分,组织…  ⟵ CONCEPT-organization, CONCEPT-choice, CONCEPT-resource, CONCEPT-information
- CONCEPT-information · 信息 — 信息'指关于世界某个情况的、可以传给别人的表示(比如'烟'代表'有火'),它帮主体减少不确定、做出更好的判断;信息必须依附在某种物理载体上(大脑…  ⟵ CONCEPT-agent, CONCEPT-resource
- CONCEPT-interaction · 交互 — 交互'指两个以上的主体之间发生的一次行为往来——一方的动作作用到另一方并产生看得见的影响(哪怕对方没回应,比如攻击也算);它是一次性的事件,反复…  ⟵ CONCEPT-agent, CONCEPT-information
- CONCEPT-norm · 规范 — 规范'指一群人之间共享的'该做/不该做'的行为默契,谁违反了会招来别人的反应(制裁、排挤、白眼);它可以在没人专门制定的情况下,靠大家反复打交道…  ⟵ CONCEPT-agent, CONCEPT-interaction, CONCEPT-relation, CONCEPT-information
- CONCEPT-organization · 组织 — 组织'指一群人为了共同目标搭起来的、有明确分工和协调规矩的长期结构(比如公司、军队);它比'群体'要求更高——光有共同身份不够,还得有分工和协调…  ⟵ CONCEPT-agent, CONCEPT-goal, CONCEPT-resource, CONCEPT-relation, CONCEPT-cooperation, CONCEPT-information, CONCEPT-norm
- CONCEPT-power · 权力 — 权力'指在一段关系里,甲能让乙做出'本来不会做'的事的能力;它不藏在某个人身上,而存在于人和人之间,靠暴力、钱、信息、地位或人多等某种本钱撑着  ⟵ CONCEPT-agent, CONCEPT-choice, CONCEPT-interaction, CONCEPT-relation, CONCEPT-resource, CONCEPT-information
- CONCEPT-relation · 关系 — 关系'指特定的两人(或多人)反复打交道后形成的、比较稳定、彼此能大致预料对方的互动套路;单次陌生人偶遇只是'交互',反复发生并沉淀下来才叫'关系…  ⟵ CONCEPT-agent, CONCEPT-interaction, CONCEPT-goal, CONCEPT-resource, CONCEPT-information
- CONCEPT-resource · 资源 — 资源'指主体用来缩小'现状'与'目标'之间差距的一切可支配的东西——不只是钱和物,知识、技能、人脉、甚至时间都算;它们的共同点是总量有限,所以必…  ⟵ CONCEPT-agent, CONCEPT-goal

## L1 · 公理 axioms (4)
- AXIOM-001 · 稀缺性-竞争公理 — 多个人都要同一份不够分的资源,竞争就必然存在——不是谁性格问题,是结构决定的
- AXIOM-002 · 信息熵增公理 — 记住的东西不时常温习、记录不去维护,就会随时间慢慢模糊、走样、最后没法用——信息会自然衰减,保鲜是要花力气的
- AXIOM-003 · 重复交互-规范涌现公理 — 两个人反复打交道、又都记得上回发生过什么,自然就会对'对方大概会怎么做'形成共同的默契和规矩——这不是文化教出来的,是打交道多了必然长出来的
- AXIOM-004 · 组织熵增命题 — 任何组织,只要不持续花精力去维护它的协调规矩(谁干什么、怎么配合),就会自然涣散——结构变乱、规矩失灵、人走光,最后散伙

## L1 · 定理 theorems (11)
- THEOREM-competition-norm · 竞争规范化定理 — 只要竞争的人反复碰面、彼此看得见，就会自发形成‘比赛该怎么打’的规矩——竞争不会消失，但会从没底线的乱斗变成守规则的较量；而彼此从不打交道的竞争…  ⟵ PHY-002, PHY-003-b, AXIOM-001, AXIOM-003
- THEOREM-conflict-cost · 冲突成本定理 — 直接开打比守规矩地竞争更费双方的资源，所以长期算下来，少打无谓之仗的一方更能攒下家底——这份成本差，就逼着大家慢慢形成‘别乱打’的规矩  ⟵ PHY-002, AXIOM-001, AXIOM-003, AXIOM-004, THEOREM-competition-norm
- THEOREM-cooperation-precondition · 合作前提定理 — 合作得靠双方都相信‘你会配合我、我也配合你’，而这份把握来自过去打交道攒下的了解；所以没有交情的陌生人之间，合作特别脆弱、容易散  ⟵ AXIOM-003
- THEOREM-exchange-competition-alternative · 交换替代竞争定理 — 当两个人各自握着对方想要的不同东西时，可以用‘交换’代替‘抢’——各取所需、都比抢更划算；但前提是两人擅长或拥有的东西得有差别，大家都一样就没得…  ⟵ PHY-002, PHY-003-c, AXIOM-001
- THEOREM-group-identity-decay · 群体身份衰减定理 — 一个群体‘我们是自己人’的共识只存在于成员的记忆里，如果不靠仪式、标志、共同故事不断重温，就会慢慢淡忘、各想各的，最后群体边界模糊、散伙  ⟵ PHY-001, PHY-002, PHY-003-a, AXIOM-002
- THEOREM-hierarchy-depth-limit · 层级深度极限定理 — 信息每往上汇报或往下传达一层就失真一点，所以组织的层级不能太深——层数一多，高层掌握的情况和基层实际就基本对不上了，这套层级也就不再管用  ⟵ PHY-001, PHY-002, AXIOM-002
- THEOREM-norm-energy-saver · 规范节能定理 — 有共同的规矩，大家每次打交道就不必从头商量‘该怎么办’，省下大量时间精力——规矩越稳，维持同样的秩序越省力；反过来，规矩一崩，维持秩序的成本会急…  ⟵ PHY-001, PHY-002, AXIOM-003, AXIOM-004
- THEOREM-organization-resource-competition · 组织资源竞争定理 — 在资源有限的同一环境里，多个组织为了‘养活自己’必然互相争抢资源——这不是偶然的市场现象，而是躲不掉的硬道理；而且组织太小竞争不过、太大又养不起…  ⟵ PHY-001, PHY-002, AXIOM-001, AXIOM-004
- THEOREM-position · 立场定理 — 只要一个人有想达成的目标，又碰上一件既影响这目标、又牵扯到别人的事，他就必然会对这事有‘希望往哪边走’的倾向（即立场）——这不需要额外理由，是有…  ⟵ PHY-002, PHY-003-c
- THEOREM-power-signal-decay · 权力信号衰减定理 — 甲能管住乙，靠的是乙心里记着‘甲有本事影响我’；这份记忆会自然淡忘，甲若长期不展示、不提醒，实际的支配力就会下滑——权力不只是‘拥有’，更得‘不…  ⟵ PHY-001, AXIOM-002
- THEOREM-relation-information-asset · 关系信息资产定理 — 两个人的‘关系’本质是一笔信息财富——存着彼此打交道攒下的了解，让往后每次合作都更省事；所以熟人办事比生人省力，而长期不来往，这份了解会变淡、关…  ⟵ PHY-001, AXIOM-002, AXIOM-003

## L2 桥接 bridges (12)
- BR-L2-001 [verified] · 有限理性 — 人的脑子算不过来所有选项、也想不清每个选择的长远后果，只能挑个‘够用就行’的方案，而不是理论上的最优解  ⟵ AXIOM-002
- BR-L2-002 [verified] · 亲缘利他 — 血缘越近的亲人，人越愿意为他付出、吃点亏也帮——共享的基因越多，愿意出手相助的门槛就越低
- BR-L2-003 [verified] · 大规模非亲缘合作 — 人类的独特之处，是能让成千上万素不相识的陌生人一起合作（国家、宗教、市场都是），靠的不是熟人互惠或血缘，而是大家共同相信的规矩和‘想象出来的秩序…  ⟵ AXIOM-003, THEOREM-cooperation-precondition
- BR-L2-004 [verified] · 层级普适性 — 人群一旦超过约150人（一个人能维持稳定社交关系的上限），就必然冒出某种‘少数人拍板’的层级——否则事事都要人人跟人人商量，协调成本根本扛不住  ⟵ AXIOM-002, THEOREM-hierarchy-depth-limit
- BR-L2-005 [verified] · 互惠利他 — 经常打交道的人，哪怕没有血缘，也会自然形成‘你帮我、我帮你’的默契——不用签合同、也不靠上头强制，来往多了自己就长出来了  ⟵ AXIOM-003, THEOREM-cooperation-precondition
- BR-L2-006 [verified] · 内群体偏好 — 人天生偏袒‘自己人’——分东西多给、更信任、有矛盾时也护着；哪怕‘自己人’只是随手按颜色标签这种没意义的方式分出来的，这种偏心照样出现  ⟵ AXIOM-001, THEOREM-group-identity-decay
- BR-L2-007 [verified] · 禀赋互补驱动贸易 — 两拨人手里的东西越是'你有我没、我有你没'(禀赋互补),他们之间越会做买卖;贸易的密度跟着这种互补程度走  ⟵ THEOREM-exchange-competition-alternative
- BR-L2-008 [verified] · 掠夺是真实且普遍的资源获取策略 — 人不是只会做买卖——当'抢的代价'低于'抢到的好处'时,靠武力直接夺取(劫掠、掠夺、征服)是一种真实存在、跨文化反复出现的策略  ⟵ AXIOM-001, THEOREM-conflict-cost
- BR-L2-009 [verified] · 人际信任有界且随社会距离衰减 — 一个人能真正'知根知底、放心托付'的对象是有限的——出了熟人圈,信任就随社会距离(血亲→熟人→同乡→匿名陌生人)一路陡降  ⟵ AXIOM-002, THEOREM-relation-information-asset, THEOREM-group-identity-decay, THEOREM-cooperation-precondition
- BR-L2-010 [verified] · 非人格化制度能替代人际信任支撑陌生人交换 — 熟人之间靠交情办事;陌生人之间没交情,怎么放心交易?答案是把'信任'外包给制度——第三方执法、声誉登记、标准合同、抵押/货币  ⟵ AXIOM-003, THEOREM-cooperation-precondition, THEOREM-relation-information-asset
- BR-L2-011 [verified] · 通货替代匿名交换中缺失的记忆/可追踪性 — 熟人赊账,靠双方记得谁欠谁、以后还见面;可跟一个【认不出、追不到、不会再见】的人打交道,没法赊账——没人记得住、也没'下次'惩罚  ⟵ AXIOM-003, THEOREM-relation-information-asset, THEOREM-cooperation-precondition
- BR-L2-012 [verified] · 多边结算成本催生通用媒介 — 就算大家彼此都认得、也记得住谁欠谁(记忆在场),但一大群人互相七拐八绕地欠来欠去,要把这张'谁欠谁'的多边大网记清、轧平,本身就很费劲  ⟵ AXIOM-003, THEOREM-relation-information-asset, THEOREM-exchange-competition-alternative

## L3 推论 corollaries (8)
- DED-001 [verified] · 组织深度天花板推论 — 光靠人嘴对嘴传话的组织，管理层级最多也就5到7层——再深，最高层掌握的情况就和基层实际严重脱节了；想再大，只能把信息写下来（官僚化）或把权力下放…  ⟵ AXIOM-002, THEOREM-hierarchy-depth-limit, BR-L2-001, BR-L2-004
- DED-002 [verified] · 规范成文化阈值推论 — 口口相传的规矩有个复杂度上限；社会一大、规矩一多，要么把规矩写下来、分层、或找专人记诵来突破上限，要么干脆分裂成一堆小单元、让每份规矩都不超上限…  ⟵ AXIOM-003, THEOREM-norm-energy-saver, THEOREM-cooperation-precondition, BR-L2-001, BR-L2-005
- DED-003 [verified*] · 内聚-外竞耦合推论 — 大群体的内部团结，和‘有没有一个外部对手’是绑在一起的——因为‘我们不同于他们’是最省力的团结方式；一旦外敌消失、又不肯改用别的方式（如民主参与…  ⟵ AXIOM-001, AXIOM-003, THEOREM-group-identity-decay, THEOREM-competition-norm, BR-L2-003, BR-L2-006
- DED-004 [rejected] · 信息外化不对称蕴含推论 — 曾猜‘把行政账目写下来’和‘把法律规矩写下来’这两件事会绑在一起出现，查了20个古代政体后发现站不住脚（很多大帝国只记账、不写成文法），已亲手否…  ⟵ AXIOM-002, BR-L2-001, DED-001, DED-002
- DED-005 [verified] · 贸易-劫掠边界推论 — 我想要你手里的东西,可以换也可以抢  ⟵ AXIOM-001, AXIOM-003, THEOREM-exchange-competition-alternative, THEOREM-conflict-cost, THEOREM-cooperation-precondition, BR-L2-005, BR-L2-007, BR-L2-008
- DED-006 [verified] · 信任天花板-制度外化推论 — 人只能对有限的熟人真正'放心托付',出了熟人圈信任就陡降(那是天花板)  ⟵ AXIOM-002, AXIOM-003, THEOREM-relation-information-asset, THEOREM-group-identity-decay, THEOREM-cooperation-precondition, THEOREM-exchange-competition-alternative, BR-L2-003, BR-L2-009, BR-L2-010
- DED-007 [rejected] · 通货三驱动解离推论 — 钱(通用交换媒介)从哪来?教科书给单一原因:门格尔说'为解决物物交换不便(你要的我没有)';另一派说'为替代记忆(陌生人之间没法赊账)  ⟵ AXIOM-003, THEOREM-relation-information-asset, THEOREM-cooperation-precondition, THEOREM-exchange-competition-alternative, BR-L2-005, BR-L2-009, BR-L2-011, BR-L2-012
- DED-008 [verified] · 裙带侵蚀与监督者独立性推论 — 血缘越近越愿意偏帮(那是本能,不是坏)  ⟵ AXIOM-001, THEOREM-relation-information-asset, THEOREM-norm-energy-saver, BR-L2-002, BR-L2-010

## L3 审查 reviews (14)
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
- META-REVIEW-001 — 这份文件记录了一次"自我审查":我(负责推理的 AI)先用第一性原理给整个体系挑了 四个毛病,然后请另一个独立的 AI 拼命反驳我

## L3 其它(经验检验/交叉验证等) (6)
- EMP-TEST-001 [conducted] — 拿 14 个前现代国家/帝国的真实历史去撞推论 DED-001（没有文字等记录系统辅助，组织的有效管理层级深不过 8 层）：数了每个的层级深度和…
- EMP-TEST-002 [conducted] — 拿 14 个前现代/无文字社会的真实历史去撞推论 DED-002（口头规矩承载不了大社会，必须靠写成文字、分层或专职人员之一来应对）：挑了冰岛、…
- EMP-TEST-003 [conducted] — 拿 12 个大型政体的兴衰历史去撞推论 DED-003（外部对手消失、又没补上别的凝聚手段，内部就会散）：追踪每个在失去外敌前后的凝聚力变化，大…
- EMP-TEST-004 [pre_registered] — 拿 20 个前现代政体、事先锁死方案做盲测，检验推论 DED-004 唯一的新意（'把行政记下来'和'把法律写下来'这两件事会绑在一起出现）：结…
- ICV-001 [conducted] — 请两个'血统不同'的免费 AI 独立盲打分，复核推论 DED-001 经验检验里那 14 个国家的层级数——不图它们更聪明，图它们'错得不一样'…
- L3-METHODOLOGY [canonical]
