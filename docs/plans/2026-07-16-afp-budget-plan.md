# AFP 预算规划与系统提升路线图

> ⚠️ **已被 [`2026-07-16-final-plan.md`](2026-07-16-final-plan.md) 取代**（2026-07-16 第一性整合）。本文件保留作决策过程记录。
> 制定：2026-07-16 · 状态：~~待用户指令启动~~ → 已被整合方案取代
> 制定者：小敏（Claude Code）· 决策者：黄谦敏
> 关联记忆：`axiomatics-cost-optimization-plan`、`l2-bridge-stress-test-2026-07-16`、`cnbs-tools-system-improvement-plan`

## 一、背景：方舟 Agent Plan AFP 配额

方舟 Agent Plan 套餐采用 AFP（Agent Fuel Point）统一用量单位。当前配额：

| 滚动窗口 | 配额 | 已用（7/16 快照） |
|---|---|---|
| 近 5 小时 | 1 万 AFP | 43.25（0.4%） |
| 近一周 | 3.5 万 AFP | 43.25（0.1%） |
| 近一月 | 10 万 AFP | 43.25（<0.1%） |

**glm-5.2 限时 2.5 折活动**：2026-06-10 18:00 ~ **2026-08-08 23:59**。折后抵扣系数：

| 输入档 | 原系数 | 2.5 折后 |
|---|---|---|
| ≤32k | 3.015（4.5×0.67） | **0.754** |
| 32k–128k | 4.5（4.5×1） | **1.125** |
| >128k | 9.0（4.5×2） | **2.25** |
| 输出（统一） | 4.5 | **1.125** |

抵扣公式（文本生成）：`AFP = (输入token × 输入系数 + 输出token × 输出系数) / 10000`

## 二、核心判断

### 1. AFP 不是瓶颈

用 L2 压力测试实测（每桥 Review ≈ 87K token，deepseek-v4-pro ¥0.13/桥）反推 glm-5.2 折后单条全流程成本：

| 实体类型 | 全流程 AFP/条 | 构成 |
|---|---|---|
| L2 桥接 | ~8 | Revise 段免费，仅二轮 Review 花钱 |
| L3 推论 | ~24 | Author + 2 轮 Review |
| L4 复合 | ~45 | 多父推论，上下文大 |

**月 10 万 AFP 可买**：≈ 4000 条 L3 / 12500 条 L2 / 2200 条 L4。
**5 小时 1 万 AFP 突发**：≈ 410 条 L3 / 5h。

> AFP 预算远超研究吞吐能力。真正瓶颈是：①研究质量与经验锚点 ②人工过目带宽 ③8/8 折扣到期硬节点。

### 2. 折扣窗口是最大杠杆

8/8 后 glm-5.2 涨 4 倍回原价（4.5 档）。同样 10 万 AFP，折扣期能做的事是折扣后的 4 倍。**AFP 密集型工作（Author+Review）应尽量压进 7/16–8/8**。

### 3. 折扣后承重墙换模型

8/9 起 glm-5.2 原价 4.5 档，而 **doubao-seed-2.0-pro / minimax-m3 只要 2.5 档**（便宜近半）。折扣期用 glm-5.2，折扣后切豆包/minimax，全程不碰付费 deepseek。

## 三、deepseek 边界（用户 2026-07-16 确认）

| deepseek 来源 | 是否可用 | 说明 |
|---|---|---|
| DeepSeek 官方 API（deepseek-chat/v4-pro，付费） | ❌ 不用 | 用户明确排除 |
| 方舟套餐内 deepseek-v4-pro（5.5 档）/ deepseek-v4-flash（0.5 档） | ❌ 不用 | 属付费 deepseek |
| **SenseNova 网关 deepseek-v4-flash（免费）** | ✅ **可用** | 用户 2026-07-16 确认可用 |

SenseNova 免费 deepseek-v4-flash 优势：1M 上下文、1.3s、开箱即用、推理部分正确。适合长上下文场景（IEA/生成/预草稿）。与 sensenova-6.7-flash-lite（0.5s 最快、支持图片）互补。

## 四、模型选型矩阵

| 管线段 | 7/16–8/8（折扣期） | 8/9+（折扣后） | 费用 |
|---|---|---|---|
| Author 起草（承重墙） | glm-5.2（2.5 折） | doubao-seed-2.0-pro 或 minimax-m3（2.5 档） | AFP |
| Review 审查（承重墙） | glm-5.2（2.5 折） | doubao-seed-2.0-pro 或 minimax-m3（2.5 档） | AFP |
| IEA 调查 | sensenova-6.7-flash-lite / deepseek-v4-flash | 同 | **免费** |
| 生成 / 预草稿 | sensenova-6.7-flash-lite / deepseek-v4-flash | 同 | **免费** |
| Revise 整改 | flash_revise.py --cross-check（双厂商免费） | 同 | **免费** |
| Finalize 定论 | finalize.py（Python） | 同 | **免费** |
| 异血统投票 | blind_coder.py + Agnes | 同 | **免费** |

**红线**：Author/Review 两面承重墙永远 pro（不动），Finalize 永远脚本。预算再充裕不放水。

## 五、现状基线（⚠️ INDEX.md 过时，待 index.py 校正）

INDEX.md 显示 237 实体，但实际 candidate 比索引多。`grep status: candidate` 实测：

- **L3 candidate（2 条）**：DED-035、DED-039
- **L4 candidate（5 条）**：L4-014、L4-016、L4-017、L4-018、L4-019（后 4 条完全没进 INDEX.md）
- **L2 candidate（20 条）**：BR-L2-033~052（在 `L2-bridging/candidate/`，已 Review 全 needs_revision，待 Revise）
- **weakly_verified（5 条）**：DED-033、BR-L2-025、BR-L2-029、BR-L2-031、BR-L2-032

实际实体数 ≈ 261+。**开干前必须先跑 `python scripts/index.py` 校正基线**。

## 六、管线基建现状（成本优化 7 项进度）

| 措施 | 状态 | 落地物 |
|---|---|---|
| 1. Finalize 脚本化 | ✅ 已落地 | `scripts/finalize.py` |
| 2. resume 重跑习惯 | ⏳ 待做 | 需写入 CLAUDE.md 操作约束 |
| 3. 阅读包 | ✅ 已落地 | `docs/pipeline/author-pack.md`、`reviewer-pack.md` |
| 4. 红旗回灌作者清单 | ⏳ 持续 | 提高一轮过率 = 最大杠杆 |
| 5. Revise/机械段下放 flash | ✅ 已落地 | `scripts/flash_revise.py --cross-check` |
| 6. 异血统投票 | ✅ 已落地 | `scripts/blind_coder.py` |
| 7. 错峰批跑 | ⏳ 待核实 | 方舟是否有夜间折扣；AI-Assets cron 基建现成 |

## 七、三阶段路线图

### 阶段一：折扣窗口冲刺（7/16–8/8，23 天）— AFP 预算 ~3 万足矣

**P0 清存量（~520 AFP，3–5 天）**：
- 20 条 L2 新桥：`flash_revise --cross-check`（免费）-> 二轮 Review（~160 AFP）
- 2 条 L3 candidate（DED-035/039）走 `ded_pipeline`（~48 AFP）
- 5 条 L4 candidate（L4-014/016/017/018/019）走 `l4_pipeline`（~225 AFP）
- 5 条 weakly_verified 补锚升级（~60 AFP）
- CNBS 改造 P0–P3（~30 AFP）

**P1 补成本优化剩余（免费/低成本，2 天）**：
- 措施 2：resume 习惯写入 CLAUDE.md
- 措施 4：红旗回灌 author-checklist
- 措施 7：核实方舟夜间折扣 -> cron 批跑

**P2 增量扩展（富余 AFP，~2 万 AFP）**：
- 深度经验检验：EMP-TEST 从 4 条扩到 10+ 条
- 跨源验证模式落地（CNBS P3 方法论资产）
- 新推论补 L3/L4 缺口

**P3 收尾**：`index.py` + `export_graph.py` + 更新导读/术语表 + push 部署。

### 阶段二：折扣后转型（8/9–12 月）

- 承重墙切 doubao-seed-2.0-pro / minimax-m3（2.5 档），单条成本约为 glm-5.2 原价 56%
- 免费段已承担 IEA/Revise/Finalize/生成
- 增量放缓到质量打磨，日均 1–2 条推论吞吐
- 措施 7 错峰批跑若成立，夜间 cron 跑批量

### 阶段三：长期铺垫（全球历史图谱）

- 60+ 模块 baseline 扩展，方法论 + 基建已在 human-society 验证
- L5 暂不实现（休谟断头台，见 `human-society-L5-positioning`）

## 八、预期提升程度

| 维度 | 现状 | 折扣窗口末（8/8） | 年底（12/31） |
|---|---|---|---|
| 实体总数 | ~261 | ~280 | ~400 |
| L3 verified 率 | ~85% | ~95% | ~95% |
| L4 复合 | 14（5 candidate） | 19（全转正） | ~30 |
| L2 verified | 43（4 weakly） | 63（全 verified） | ~80 |
| 经验检验 EMP-TEST | 4 | 10+ | 20+ |
| 体系完整度 | L4 多缺口 | L4 主干闭合 | 为全球图谱铺好方法论 |

## 九、风险与红线

1. **8/8 折扣到期**：硬节点，倒排。存量清完优先于增量。
2. **glm-5.2 承重墙能力**：能否胜任 Author/Review 高质量产出需 A/B 验证（拿 1 条 L3 用 glm-5.2 跑，对比历史 deepseek-v4-pro 产出）。若不行，折扣期即切 minimax-m3（2.5 档，无折扣但更强）。
3. **5 小时 1 万 AFP 突发**：大批量批跑需分批，别一个 Workflow 跑 50 条撞上限。
4. **审查红线不动**：Review 永远 pro，Finalize 永远脚本。
5. **INDEX.md 过时**：开干前先跑 `index.py`。

## 十、执行状态

- [x] 规划制定（2026-07-16）
- [x] 用户确认 deepseek 边界（SenseNova 免费 deepseek-v4-flash 可用）
- [x] 用户确认落盘、暂不执行
- [ ] 用户指令启动
- [ ] 第一步：`python scripts/index.py` 校正基线
- [ ] 第二步：20 条 L2 桥 `flash_revise --cross-check`（免费，零风险起步）
