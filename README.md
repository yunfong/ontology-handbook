# 本体论工程手册（Ontology Engineering: A Research Compendium）

一份可离线阅读的静态 HTML 研究合集：**78 个开源项目的逐个核验、15 章方法论、7 个分类地图、3 个附录、4 组可复现实测**。

面向对象是需要判断「这件事该不该做、用什么做、做到什么程度」的技术决策者。不含任何具体机构的内部数据、系统名或组织信息，可直接对外分发。

> **免责声明**：本文为个人研究整理，不代表所在机构观点。案例章节的数据为真实项目的量级与结构，企业名、系统名与具体数字均已做通用化或区间化处理。作者：[yunfong](https://github.com/yunfong)。

---

## 一、怎么打开

不需要服务器、不需要联网、没有外部依赖（字体用系统字体，图标是内联 SVG，搜索索引是本地 JS）。

```
双击 index.html
```

HTML 是唯一发布的版本，任何浏览器都能直接打开、缩放、搜索。若需要一份可打印或可私下转发的 PDF，可用下文「重新生成 PDF」的命令在本地生成（**站点不发布 PDF**，以免旧版本在网盘与群里长期流通）。

如果浏览器对 `file://` 下的相对链接有限制（个别浏览器策略较严），在该目录下起一个静态服务：

```bash
python3 -m http.server 8080
# 然后访问 http://localhost:8080/
```

**推荐阅读顺序**（封面页也写了三条路径）：

- 只有 10 分钟：封面 → 附录 B 速查表（`cheatsheet.html`）。
- 决定要不要做：封面 → 第二章方法论 → 第七章案例 → 第十二章反模式。
- 已经决定要做：第三章语言选型 → 第四章校验 → 第五章治理 → 第十章技术栈 → 附录 B。

交互提示：按 `/` 唤起全文搜索（支持 ↑↓ 选择、Enter 跳转、Esc 关闭）；右上角可切换暗色主题；宽屏右侧有本页目录。

---

## 二、目录结构

```
ontology-compendium/
├── index.html            封面与导读
├── concepts.html         一 · 四个被混用的「本体」
├── methodology.html      二 · 本体工程方法论谱系
├── languages.html        三 · 建模语言与约束选型
├── reasoning.html        四 · 推理与校验
├── governance.html       五 · 治理：版本、变更与 CI
├── kinetic.html          六 · 动力学层：从名词到动词
├── case.html             七 · 一个完整案例：五周与三个事故
├── ecosystem.html        八 · 开源生态地图
├── cat-*.html            8.1–8.7 七个分类页（78 个项目卡片）
├── trends.html           九 · 八个趋势的独立核验
├── stack.html            十 · 技术栈分层与选型框架
├── evidence.html         十一 · 四次实测
├── antipatterns.html     十二 · 反模式与落地判据
├── org.html              十三 · 组织、角色与预算
├── llm.html              十四 · 本体与模型系统的边界
├── glossary.html         十五 · 术语表
├── method.html           附录 A · 方法与可复现性
├── cheatsheet.html       附录 B · 选型速查表
├── appendix-projects.html 附录 C · 78 个项目总表（由 data/ 生成）
├── LICENSE              CC BY 4.0（正文）/ MIT（代码）
├── assets/               style.css / app.js / search-index.js / favicon.svg
├── build.py              构建脚本（纯标准库）
├── data/projects.py      78 个项目的卡片文案与分类元信息
├── data/meta.json        78 个仓库的快照数据（星数/建库时间/许可/语言）
└── src/*.md              18 个章节源文件（Markdown 子集）
```

`*.html` 是构建产物，`src/` 与 `data/` 是源。改内容请改源，别改 HTML。

---

## 三、如何重建

只需要 Python 3.9+，无第三方依赖：

```bash
cd ontology-compendium
python3 build.py
```

输出会打印每个章节的生成情况、字数统计与断链检查（正常应为 `0 断链`）。构建同时会重新生成 `assets/search-index.js`，所以**新增章节后不必手工改搜索索引**。

字数与页面数由脚本扫描 `src/*.md` 自动统计，封面上的「约 N 万字」不是硬编码的。

### 重新生成 PDF（可选，不随站点发布）

PDF 不是手工排的，而是把全部章节串成一个长文档再打印。生成的 PDF 请只在本地保存或私下转发，不要提交到仓库：

```bash
python3 build.py --print          # 生成 _print.html（临时文件）
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-sandbox \
  --user-data-dir=/tmp/chrome-pdf --no-pdf-header-footer \
  --print-to-pdf="本体论工程手册-v1.0.pdf" --virtual-time-budget=8000 \
  "file://$PWD/_print.html"
```

任何浏览器里对 `_print.html` 用「打印 → 存为 PDF」也能得到同样的结果（记得勾掉页眉页脚）。

### 格式支持范围

`build.py` 内置的 Markdown 解析器只支持子集，够用但不要期待完整实现：

- `#` 到 `####`（一级标题不渲染，章标题来自 `CHAPTERS` 清单的配置）
- 段落、`>` 引用、`---` 分隔线
- 有序/无序列表（含一层缩进续行）
- 表格（GFM 管道语法，支持对齐标记）
- 围栏代码块（```` ``` ````）
- 行内：`` `code` ``、`**粗体**`、`*斜体*`、`[文字](链接.md)`

不支持原始 HTML 嵌入、脚注、任务列表、图片。要加新章节，在 `build.py` 的 `CHAPTERS` 里加一条 `(slug, 标题, 源文件名, 分组, 摘要)` 即可，导航、翻页、搜索索引都会自动跟上。

---

## 四、数据口径

- **仓库数据**为 2026-10-30 的快照，取自 GitHub REST `/repos/{owner}/{repo}`（`stargazers_count` / `created_at` / `pushed_at` / `license.spdx_id` / `language` / `archived`）。星数会变，结论不会因为几千颗星的变化而改变，但引用具体数字时请标注日期。
- **78 个项目** = 原始索引里的 59 个 + 为补全七类地图另查的 19 个（GitHub 与 Agent 记忆生态里当时被漏掉的系统）。分类与分级（S/A/B/C）是编者的判断，判据写在第八章开头。
- **实测数据**（第十一章）为 2026-10-31 实际执行，环境为 `pyshacl 0.40.2` / `rdflib 7.6.0` / `owlrl 7.6.2`。工具版本变了数字会变，量级和相对关系不会。复现步骤与命令见附录 A。
- **每条判断标注了证据等级**：实测（我跑过）、核验（查过一手来源）、推断（明确标注为推断）。原文摘引用「」逐字引用，未逐字核到的一律降级为推断。

要更新数据：改 `data/meta.json` 里对应条目的字段，重跑 `build.py`。第七章、第九章引用了若干星数与建库时间，改动后建议一并核对。

---

## 五、许可与引用

文字内容采用 **CC BY 4.0**（署名即可商用与再分发）。`build.py`、`assets/app.js`、`assets/style.css` 可视为 MIT。

建议引用格式：

```
《本体论工程手册：78 个开源项目的核验与方法论汇编》，v1.0，2026-10。
```

文中引用的开源项目各自遵循其原许可（以 `data/meta.json` 记录的 SPDX 标识为准），本项目只做描述与评价，不包含其代码。

---

## 六、发布

本站以 GitHub Pages 托管，发布方式是把 `build.py` 生成的 HTML 提交到仓库根目录，由 Pages 直接对外提供（不经过 Actions，因此线上内容与仓库内容逐字一致）：

```bash
python3 build.py                 # 重建全部页面 + 搜索索引 + 断链检查
git add -A && git commit -m "content: ..."
git push origin main             # Pages 自动重新发布，约 1 分钟
```

仓库里只放产物与说明（HTML、`assets/`、README、LICENSE、`.nojekyll`、`robots.txt`）；`src/`、`data/`、`build.py` 是否公开取决于仓库策略——公开它们可以让别人复核数据来源并自行重建。

## 七、免责与边界

- 这是一份**研究汇编**，不是实施承诺，也不代表任何机构（包括作者所在机构）的观点或立场。
- 案例章节（第七章）的数据为真实项目的量级与结构，企业名、系统名与具体数字均做过通用化或区间化处理；文中「××」为脱敏占位符。
- 星数不是质量指标。书中用它只做两件事：估计社区规模、判断趋势真伪。用它选型的部分都配了别的判据。
- 分类与分级带编者偏好；如果你不同意某个项目被放在 B 级，判据是公开的，可以直接改 `data/projects.py` 后重建。
- 已知局限（数据快照、样本偏差、实测规模上限等）在附录 A 里逐条列了，没有藏起来。
