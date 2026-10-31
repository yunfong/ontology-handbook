这一章是全书唯一有「实测」标记的部分。三组实验，目标只有一个：把三条被反复引用、却很少有人真跑一遍的主张，从判断降级为事实——或者证伪。

三条主张是：

1. 「用 OWL 做数据校验」是可行的。
2. 「一份源、多目标编译」只是宣传语。
3. 「推理只是慢一点，可以放进流水线」。

三组实验的结论分别是：**不可行**、**是真的、且有 41 个生成器为证**、**慢 16 倍且一条违规都不多报**。

## 环境

```
Python 3.14.7（venv）
pyshacl 0.40.2
rdflib 7.6.0
owlrl 7.6.2
```

复现：`uv venv && uv pip install pyshacl owlrl`，然后把下面的文件与命令照抄。

## 实测一：同一份数据，两种世界观

### 语料

一个极小的模型：四类对象（指标 Metric、特征 Feature、人群 Segment、结论 Finding），三条约束。选择这个例子是因为它对应任何一个数据团队都有的三类真实错误：**没有责任人**、**引用了不存在的东西**、**枚举值越界**。

约束文件 `shapes.ttl`：

```turtle
ex:MetricShape a sh:NodeShape ;
  sh:targetClass ex:Metric ;
  sh:property [ sh:path ex:hasOwner ; sh:minCount 1 ;
                sh:message "Metric 必须有 owner（责任人）" ] ;
  sh:property [ sh:path ex:unit ; sh:minCount 1 ;
                sh:message "Metric 必须有单位" ] .

ex:SegmentShape a sh:NodeShape ;
  sh:targetClass ex:Segment ;
  sh:property [ sh:path ex:derivedFrom ; sh:minCount 1 ; sh:class ex:Feature ;
                sh:message "Segment 必须至少 derivedFrom 一个存在的 Feature" ] ;
  sh:property [ sh:path ex:tagType ; sh:in ( "offline" "realtime" "hybrid" ) ;
                sh:message "tagType 只能是 offline / realtime / hybrid" ] .

ex:FindingShape a sh:NodeShape ;
  sh:targetClass ex:Finding ;
  sh:property [ sh:path ex:cites ; sh:minCount 1 ; sh:class ex:Metric ;
                sh:message "Finding 必须引用至少一个存在的 Metric" ] .
```

一个值得注意的写法：`sh:class ex:Feature` 同时检验了「引用存在」和「被引用者类型正确」——悬空 IRI 因为「没有类型」而失败。**一条约束解决了引用完整性与类型正确性两件事**，这是 SHACL 相对外键的优势。

数据 `data.ttl` 有 17 个三元组，含三个违规样本、一个合法样本：

```turtle
ex:metric_ead_norm a ex:Metric ; ex:sql "select avg(ead_norm) from t" .
ex:segment_8821 a ex:Segment ; ex:derivedFrom ex:feature_missing ; ex:tagType "batch" .
ex:finding_rpt_01 a ex:Finding ; ex:cites ex:metric_missing .
```

### 结果 A：SHACL

```bash
pyshacl -s shapes.ttl data.ttl -f human
```

```
Validation Report
Conforms: False
Results (5):
Constraint Violation in ClassConstraintComponent:
	Focus Node: ex:segment_8821   Value Node: ex:feature_missing
	Message: Segment 必须至少 derivedFrom 一个存在的 Feature
Constraint Violation in ClassConstraintComponent:
	Focus Node: ex:finding_rpt_01   Value Node: ex:metric_missing
	Message: Finding 必须引用至少一个存在的 Metric
Constraint Violation in InConstraintComponent:
	Focus Node: ex:segment_8821   Value Node: Literal("batch")
	Message: tagType 只能是 offline / realtime / hybrid
Constraint Violation in MinCountConstraintComponent:
	Focus Node: ex:metric_ead_norm   Result Path: ex:hasOwner
	Message: Metric 必须有 owner（责任人）
Constraint Violation in MinCountConstraintComponent:
	Focus Node: ex:metric_ead_norm   Result Path: ex:unit
	Message: Metric 必须有单位

退出码 = 1
```

三个违规样本一共报出 5 条违规，每条都指到了具体的焦点节点、路径、以及一句人能读的理由。**退出码是 1**——这一点比输出格式重要得多：它意味着这条命令可以直接当 CI 闸门，不需要解析任何文本。

### 结果 B：OWL-RL 闭包，同一份数据

```python
g = load("onto.ttl", "data.ttl")
DeductiveClosure(OWLRL_Semantics).expand(g)
```

```
原始三元组数: 42
RL 闭包后:   259   新增: 217
耗时:        0.013 s
是否报告错误/不一致: 无
metric_ead_norm 的 hasOwner 三元组数: 0
```

三条观察：

1. **零报错。** 那个缺少责任人的指标，在推理后多出了 5 个类型断言（`Entity`、`Metric`、`owl:Thing` 等）和一条 `sameAs`，但 `hasOwner` 依然是 0 条。**机器知道它没有责任人，但它不认为这是个问题。**
2. **新增的 217 条与违规无关。** 它们全是公理层的展开：类型继承、定义域值域、等价类。
3. **两者回答的不是同一个问题。** 推理机回答「能推出什么」，校验器回答「缺了什么」。业务系统问的永远是后者。

### 这一组的结论

**用 OWL 做数据校验，不是「效果差一点」，而是范畴错误。** 开放世界假设下，「没有」等于「未知」，因此不存在「不合规」这个概念。

## 实测二：RL 根本表达不了「至少一个」

如果坚持用 OWL，能不能把「至少一个责任人」写成公理？

```turtle
ex:Metric rdfs:subClassOf [ a owl:Restriction ;
  owl:onProperty ex:hasOwner ; owl:minCardinality 1 ] .
```

加上这条公理后重跑，结果：

```
RL 闭包完成，无异常。新增: 231
metric_ead_norm 是否被推出 hasOwner: False
是否有任何「违反最小基数」的标记: False
```

**原因**：OWL 2 RL 的规则集只覆盖 `maxCardinality` 为 0 或 1 的那部分基数限制，**没有 `minCardinality` 对应的规则**。这条公理在 RL 里等于不存在。

升级到 OWL 2 DL 能写，但结果一样：

- 推理机会推出「存在一个未知的 owner」（存在性断言），而不是「缺少 owner」。
- 它依然不报错。

两条路都到不了「拒绝」。**「至少一个」是业务里最常见的约束，而它在 OWL 2 RL 里不存在。** 这一条足以解释为什么那么多「用 OWL 做校验」的项目最后都转回了 SHACL 或 SQL 断言。

## 实测三：规模与代价

第三组实验换了问题：如果只用 SHACL，规模上去会不会扛不住？如果打开推理，代价是多少？

生成三档数据（每档约 1% 的违规率），分别测「不做推理」与「开启 OWL-RL 预推理」的校验耗时：

| 三元组数 | 违规数 | 校验耗时（无推理） | 校验耗时（开 RL） | 倍数 |
|---|---|---|---|---|
| 8,005 | 30 | 0.07 s | 1.19 s | 17× |
| 39,925 | 150 | 0.36 s | 5.75 s | 16× |
| 159,625 | 600 | 1.41 s | 23.69 s | 17× |

**两个结论，都很硬：**

**一、校验本身很便宜，且线性。** 约 9 微秒/三元组；16 万三元组 1.4 秒。这个量级意味着**可以在每次提交时对全量样本跑校验**，不需要增量策略。

**二、打开推理的代价是 16 倍，而它一条违规都没有多报。** 三档数据的违规数完全相同（30 / 150 / 600）。多花的 90% 时间，全部用于计算一个校验根本用不到的闭包。

闭包本身的代价（单独测）：

| 三元组数 | 闭包后 | 膨胀 | 闭包耗时 |
|---|---|---|---|
| 8,005 | 18,688 | 2.3× | 1.09 s |
| 39,925 | 86,608 | 2.2× | 5.56 s |
| 159,625 | 341,308 | 2.1× | 21.15 s |

23.69 秒里有 21.15 秒是闭包——**推理的开销几乎等于全部额外开销**。膨胀率稳定在 2.1–2.3 倍，意味着内存占用同比例上升；闭包耗时超线性增长（16 万三元组 21 秒，按此斜率，百万级会进入分钟级且内存压力显著）。

### 这一组的结论

**如果校验和推理在同一个流程里，把它们拆开。** 校验每次提交都跑（便宜、线性、有退出码）；推理按周或按发布跑（贵、膨胀、不产生校验价值）。

这条结论直接对应第 4 章那个「推理该放在哪」的三选一：**构建期跑推理，写入期跑校验**，不要反过来，也不要同时。

## 实测四：41 个生成器（文件级证据）

第二个待验证的主张是「一份源、多目标编译」——某建模语言宣称能从一份 YAML 生成多种格式。

**先说不成立的尝试**：`pip install` 在默认源上 15 分钟未完成任何包，镜像不可达，两次失败。所以没有跑通任何 `gen-*` 命令。

改用文件级证据：对该仓库 `main` 分支做 Git Tree 递归列举，在生成器目录下数出 **41 个模块**：

```
bigquerygen   csvgen        dbmlgen      docgen        dotgen
erdiagramgen  excelgen      golanggen    golrgen       graphqlgen
javagen       jsonldcontextgen  jsonldgen  jsonschemagen  linkmlgen
markdowndatadictgen  mermaidclassdiagramgen  namespacegen  oocodegen
openapigen    owlgen        plantumlgen  prefixmapgen  projectgen
protogen      pythongen     rdfgen       shaclgen      shexgen
sparqlgen     sqlalchemygen sqltablegen  sqlvalidationgen  sssomgen
summarygen    terminusdbgen typedbgen    typescriptgen  yamlgen
yarrrmlgen
```

三条结论：

1. **「一份源、多目标」是架构，不是话术。** 每个目标一个独立模块，由同一份 YAML 元模型驱动。这比 README 的一句话硬得多。
2. **文档与代码不完全一致。** 文档里列了某个目标，仓库里没有对应模块（可能已拆到独立包）。**不要照文档假定它存在**——这条经验适用于所有「生成器很多」的项目。
3. **一个意外发现**：存在 `yarrrmlgen`，能生成 YARRRML（R2RML 的 YAML 方言），而 OBDA 系统吃 R2RML。这意味着理论上有一条链：

```
建模 YAML ──→ sqltablegen  ──→ 数仓建表
          └─→ yarrrmlgen   ──→ R2RML ──→ Ontop ──→ 虚拟知识图（不搬数据）
```

如果这条链成立，「用编译器管模型」和「用 OBDA 接已有库」就不是两个方案，而是同一个方案的两段。

**但这是推断，不是实测**：没有验证生成的 YARRRML 能被 Ontop 直接接受，也没有验证目标数据仓库的方言。**这是全书最值得再花半天验证的一件事。**

## 五条可以带走的事实

1. **SHACL 会拒绝，OWL 不会。** 前者退出码 1，后者零报错。
2. **OWL 2 RL 没有 `minCardinality` 规则**，「至少一个」这类约束在 RL 里写不出来；升级 DL 也只能推出「存在未知值」。
3. **校验便宜且线性**（约 9 μs/三元组），可以在每次提交时全量跑。
4. **推理贵 16 倍、闭包膨胀 2.1 倍，且不增加任何校验价值。** 放在写入路径是设计错误。
5. **「一份源、多目标编译」是真的**，证据是 41 个生成器模块；但文档与代码会漂移，以仓库为准。

## 未验证的部分

诚实清单——以下都没有测，任何引用这些结论的场合都应标注：

- **并发与分布式**：单机单线程，未测并行校验。
- **超大图**：最大 16 万三元组；百万级只有外推，没有实测。
- **推理机的选择**：只测了 owlrl（Python）；ELK、Konclude 的性能特征不同，尤其 ELK 为大规模分类设计。
- **输出可读性**：`-f human` 的输出业务方仍读不懂，需要一层「人话」包装——那是产品工作量，不是工具能力。
- **编译器质量**：41 个生成器只数了数量，没有验证生成物的正确性与方言兼容性。
