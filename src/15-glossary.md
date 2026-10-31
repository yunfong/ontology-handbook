术语混乱是本体领域最大的隐性成本。「本体」「知识图谱」「语义层」「图数据库」在不同团队口中指不同的东西，讨论往往在术语层就分裂了。这张表给每个词一句话定义，并标注它在本书中的用法。

### 一、本体与语义

| 术语 | 英文 | 一句话定义 |
|---|---|---|
| 本体 | Ontology | 对某个领域中「有哪些东西、它们怎么关联、什么必须为真」的显式规定。本书默认指**可执行**的那一类，即操作本体。 |
| 操作本体 | Operational Ontology | 能被机器校验、被流水线拒绝写入的本体。与「写给人看的文档本体」相对。 |
| 分类体系 | Taxonomy | 只有层级（is-a）没有公理与约束的树。是本体最弱的一种形式，常被误称为本体。 |
| 词表 | Vocabulary | 一组受控术语及其定义，通常不含类之间的逻辑关系。SKOS 是它的标准表达。 |
| 公理 | Axiom | 断言为真的陈述，是所有推论的起点。例如「每个指标必有责任人」。 |
| 推理 | Reasoning | 从已有断言推出新断言的过程。**它不检查对错，只展开蕴含。** |
| 蕴含 | Entailment | 若 A 为真则 B 必为真。推理机的全部工作就是算这个关系。 |
| 闭包 | Closure | 把能推出的事实全部物化后的图。实测中体积膨胀 2.1–2.3 倍。 |
| 开放世界假设 | Open World Assumption (OWA) | 「没写」等于「未知」，不等于「不存在」。这是 OWL 与所有校验技术分歧的根源。 |
| 封闭世界假设 | Closed World Assumption (CWA) | 「没写」等于「没有」。SHACL、SQL、所有业务校验都建立在这个假设上。 |
| 唯一命名假设 | Unique Name Assumption (UNA) | 不同名字指不同对象。OWL 默认不成立，因此常出现意外的「同一实体」合并。 |
| 可满足性 | Satisfiability | 一个模型是否存在任何合法实例。不可满足意味着模型自相矛盾。 |
| 不一致 | Inconsistency | 数据与公理冲突。推理机能发现它，但通常只在分类时暴露，且不指出具体哪条数据错。 |
| 本体工程 | Ontology Engineering | 把领域知识转成上述形式化产物的方法、流程与工具的总称。 |
| competency question | Competency Question (CQ) | 模型必须能回答的问句。它是需求的形式化，也是验收标准。本书建议从 20 条起步。 |

### 二、语言与标准

| 术语 | 英文 | 一句话定义 |
|---|---|---|
| RDF | Resource Description Framework | 「主语—谓语—宾语」三元组的数据模型。所有语义技术的公共底座。 |
| Turtle | Terse RDF Triple Language | RDF 的可读文本语法。本书示例一律用 Turtle。 |
| RDFS | RDF Schema | 最轻的词汇表语言：类、子类、定义域、值域。只能做很弱的推理。 |
| OWL | Web Ontology Language | 重表达力的本体语言，有 EL / QL / RL / DL 等不同权衡的轮廓（profile）。 |
| OWL 2 RL | Rule Language profile | 可用规则引擎实现的 OWL 子集。**不含 `minCardinality` 规则**，这是实测确认的关键限制。 |
| SHACL | Shapes Constraint Language | W3C 的数据形状校验标准。封闭世界、有明确违规报告、有退出码。**本书推荐的校验层。** |
| ShEx | Shape Expressions | SHACL 的同类竞品，语法更简洁，生态更小。 |
| SPARQL | SPARQL Protocol and RDF Query Language | RDF 的查询语言，含 CONSTRUCT 可用于转换。 |
| JSON-LD | JSON for Linked Data | 用 JSON 表达 RDF 的方式，Web 集成的事实标准。 |
| SKOS | Simple Knowledge Organization System | 词表/叙词表的标准，适合「标签与同义词」而非结构建模。 |
| R2RML | RDB to RDF Mapping Language | 把关系表映射成虚拟 RDF 图的标准。 |
| OBDA | Ontology-Based Data Access | 不搬数据、用映射把已有库「当成」知识图来查的架构。 |
| SHACL-AF | SHACL Advanced Features | SHACL 的扩展：规则、函数、推理。谨慎使用，会重新引入推理的复杂度。 |

### 三、工程与治理

| 术语 | 英文 | 一句话定义 |
|---|---|---|
| 单一源 | Single Source of Truth | 一份模型源文件，其他产物（建表、文档、约束、API）全部生成。 |
| 生成器 | Generator | 从模型源产出某一目标格式的模块。本书实测的一个项目有 41 个。 |
| 校验闸门 | Validation Gate | 会让流水线变红的校验。没有非零退出码的校验不算闸门。 |
| 严重级别 | Severity | 违规的分级（如 fatal / warn / info），决定是阻断、告警还是记录。 |
| 带期限豁免 | Time-boxed Waiver | 允许已知违规存在，但必须写明负责人与到期日。防止豁免变成永久。 |
| 影响面 | Blast Radius | 一次变更会波及哪些下游（表、报表、API、模型）。 |
| 双时态 | Bitemporal | 同时记录「业务发生时间」与「系统记录时间」，用于回答「当时我们以为是什么」。 |
| 本体当代码 | Ontology-as-Code | 把模型源纳入版本控制、评审、CI 的做法。本书的基本主张。 |
| 弃用 | Deprecation | 不删除、只标记并给出替代与期限。兼容性的核心手段。 |
| 分级 | Tier (S/A/B/C) | 本书对项目成熟度的粗分：S 可作基础设施、A 可生产采用、B 可借鉴、C 仅观察。 |
| 活跃度 | Activity | 按最后提交时间分四档（活跃/放缓/停滞/死库）。**不等于质量**。 |

### 四、动作与状态

| 术语 | 英文 | 一句话定义 |
|---|---|---|
| 动作 | Action | 一个有名字、有参数、有前置条件、有副作用的业务操作。 |
| 前置条件 | Precondition | 动作执行前必须为真的断言。可被校验，因此可被拒绝。 |
| 后置条件 | Postcondition | 动作完成后必须为真的断言，用于对账与回归。 |
| 状态所有权 | State Ownership | 每个状态字段归属三方之一：源系统（source-backed）、本体（ontology-owned）、派生（derived）。 |
| 对账 | Reconciliation | 比较「应该有」与「实际有」，产出差异清单。 |
| 审计 | Audit | 记录谁在何时以什么理由改了什么。五个必备字段：who / when / what / why / result。 |

### 五、生态与相邻概念

| 术语 | 英文 | 一句话定义 |
|---|---|---|
| 知识图谱 | Knowledge Graph (KG) | 用图结构组织的、带语义的事实集合。**比本体宽泛**：没有公理与约束的图也叫 KG。 |
| 图数据库 | Graph Database | 存储与查询图结构的系统（属性图或 RDF 图）。**是存储，不是语义。** |
| 属性图 | Property Graph | 节点与边都可挂属性的图模型。Cypher/GQL 生态。 |
| 语义层 | Semantic Layer | 业务指标与维度的统一定义层。BI 语境下常指这个，与本体有交集但不相同。 |
| GraphRAG | Graph Retrieval-Augmented Generation | 用图结构辅助检索增强生成的做法。与本体共享「结构化」但不共享「约束」。 |
| 向量库 | Vector Store | 存 embedding、按相似度检索的系统。与本体是互补而非替代关系。 |
| 本体优先 | Ontology-First | 先建模型再建应用的开发顺序。本书实测显示该提法在 2026 年缺乏规模证据。 |
| 结构索引 | Structural Index | 对代码/文档的语法结构做索引（非语义）。近年星数最高的几个「图谱」项目属于此类。 |
| 数据契约 | Data Contract | 生产者与消费者之间关于字段、类型、约束的显式约定。与本体高度重叠，常可互译。 |
| 元数据管理 | Metadata Management | 更宽的治理范畴：血缘、目录、质量、权限。本体是其中「语义」那一块。 |

### 一句话区分三个最容易混的词

- **本体**回答「什么必须为真」——它有约束，会拒绝。
- **知识图谱**回答「有什么、怎么连」——它有结构，不拒绝。
- **图数据库**回答「怎么存、怎么查得快」——它是引擎，不懂业务。

三者可以叠在一套系统里，但**不能互相替代**。把它们混为一谈的项目，通常在第六个月发现「图建好了，但没人能说清什么算错」。
