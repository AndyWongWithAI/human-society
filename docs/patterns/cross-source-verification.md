# 跨源验证模式 (Cross-Source Verification Pattern)

> 资产类型：可复用方法论模式
> 建立日期：2026-07-16
> 来源：CNBS 工具实证 (iter-002/cnbs-empirical-memo.md + cnbs-empirical-memo-2.md)
> 适用场景：任何涉及经济/统计指标的经验检验

---

## 一、问题

当一条推论声称"多源数据验证了某预测"时，隐含假设是这些数据源彼此独立。但这个假设经常不成立——不同机构发布的数据可能共享同一套底层测量链。

**核心教训**："多源"不等于"独立"。

---

## 二、操作模式：三源对照 + 同根折扣

### 步骤 1：三角对照

用三个互补工具同时拉取同一指标：

| 工具 | 覆盖 | 稳定性 |
|------|------|--------|
| `cnbs_search` | 中国官方统计（国家统计局） | 稳定，有限流 |
| `ext_world_bank` | 全球发展指标（World Bank WDI） | 始终稳定 |
| `ext_imf` | 世界经济展望（IMF WEO） | 始终稳定，含预测 |

一次调用获得三个口径的同一指标值，快速判断一致性程度。

### 步骤 2：判定数据源独立性

**关键问题**：这三个机构的数据是否来自独立测量链？

对于中国 GDP 增速：
- CNBS 是国家统计局自己发布 → **原始源**
- World Bank 的 `NY.GDP.MKTP.KD.ZG` 以 CNBS 发布值为底层输入 → **同根**
- IMF 的 `NGDP_RPCH` 同理 → **同根**

**结论**：三源一致 ≠ 三重独立验证。三个机构的一致性只说明"同一份数据被不同机构复述时保持一致"——这是发布口径的一致性，不是独立验证。

### 步骤 3：计算有效独立票数

应用 `sources/independence-model.yaml` 的 `data_source_origin` 折扣规则：

```
原始源 (CNBS)     = 1.0 票（锚源）
WB (同根折扣 0.1)  = 0.1 票
IMF (同根折扣 0.1) = 0.1 票
─────────────────────────
有效独立票数       ≈ 1.2 票（而非 naive 的 3 票）
```

### 步骤 4：寻找真正的独立基准

真正独立的验证需要底层测量链分叉：

| 类型 | 示例 | vs CNBS 独立系数 |
|------|------|-----------------|
| 卫星遥感 | 夜间灯光强度（NASA MODIS） | ~0.8 |
| 物理量指标 | 用电量、铁路货运量（克强指数成分） | ~0.5 |
| 税务数据 | 增值税发票汇总 | ~0.7 |
| 第三方调查 | 家庭追踪调查（CFPS） | ~0.6 |

---

## 三、诚实标注模板

在推论的 `real_world_anchors` 中引用跨源数据时，使用以下诚实标注：

```yaml
# 正确写法
- title: "GDP增速三源对照"
  evidence: "CNBS(官方)≈WB≈IMF GDP增速 Δ<0.04pp"
  confidence: moderate
  independence_note: |
    三源共享中国国家账户底层数据，有效独立票数≈1.2。
    此为"发布口径一致性"锚，非"独立多源验证"锚。
    见 sources/independence-model.yaml §data_source_origin。
```

**禁止写法**：
```yaml
# ❌ 错误——将同根三源当作三重独立验证
- title: "GDP增速被三个独立来源验证"
  evidence: "CNBS、World Bank、IMF 数据一致"
  confidence: high
```

---

## 四、适用范围与限制

**适用**：
- 任何涉及宏观经济指标（GDP、CPI、贸易、就业等）的经验检验
- 任何引用多个国际机构数据作为"多源验证"的场景

**不适用**：
- 物理测量（卫星、用电量等本身就有独立测量链）
- 微观调查数据（不同调查团队独立抽样）
- 历史档案（不同档案来源可能真正独立）

**已知限制**：
- CNBS 分省/分市数据当前无法通过 API 自动获取（`cnbs_fetch_series`/`cnbs_fetch_nodes` 不稳定）
- 卫星数据 API（Google Earth Engine、Sentinel Hub）尚未接入本体系工具链
- 三步法中的"有效独立票数"是定性估计，非精确计量

---

## 五、相关资产

- `sources/independence-model.yaml` — `data_source_origin` 折扣规则的精确定义
- `L1-definitions/concepts/CONCEPT-measurement-independence.yaml` — 测量独立性的 L1 语义地基
- `docs/pipeline/author-checklist.md` — 作者清单中的"数据源独立性核查"项
- `docs/pipeline/review-rubric.md` — 评分卡红旗 #12（数据源同根冒充多源独立）
