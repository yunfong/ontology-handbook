#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ontology Compendium —— 静态站点构建脚本

用法：
    python3 build.py            # 构建全部 HTML
    python3 build.py --clean    # 先清掉旧产物再构建

输入：
    src/*.md                  章节正文（Markdown 子集）
    data/projects.py          项目数据（78 条）
    assets/style.css, app.js

输出：
    *.html                    每个章节一页
    assets/search-index.js    全文搜索索引
    index.html                封面 + 目录
"""
import os
import glob
import re
import json
import html
import shutil
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
ASSETS = os.path.join(ROOT, "assets")

SITE = {
    "title": "本体论工程手册",
    "subtitle": "Ontology Engineering: A Research Compendium",
    "version": "1.0",
    "date": "2026-10-31",
}


CN_RE = re.compile(r"[\u4e00-\u9fff]")


def count_words():
    """统计正文汉字数（章节 md + 项目卡 + 分类导语），用于封面与页脚。"""
    total = 0
    for _s, _t, f, _g, _d in CHAPTERS:
        if f and os.path.exists(os.path.join(SRC, f)):
            total += len(CN_RE.findall(open(os.path.join(SRC, f), encoding="utf-8").read()))
    projects, meta = load_projects()
    for p in projects:
        total += len(CN_RE.findall(p["body"] + p["adopt"]))
    for m in meta.values():
        total += len(CN_RE.findall(m["intro"] + m.get("note", "")))
    return total


def hero_html():
    n_ch = sum(1 for c in CHAPTERS if c[2] is not None and c[0] != "index" and not c[1].startswith("附录"))
    n_app = sum(1 for c in CHAPTERS if c[1].startswith("附录"))
    n_cat = sum(1 for c in CHAPTERS if c[2] is None and not c[1].startswith("附录"))
    wan = round(count_words() / 10000.0, 1)
    return """<section class="hero">
  <div class="hero-kicker">Research Compendium · v{ver} · {date}</div>
  <h1 class="hero-title">本体论工程手册</h1>
  <div class="hero-sub">Ontology Engineering: A Research Compendium</div>
  <p class="hero-lede">78 个开源项目的逐个核验、六层技术栈的选型框架、八个趋势的独立判定、五周落地的完整案例，以及四次可复现的实测。写给需要判断「这件事该不该做、用什么做、做到什么程度」的技术决策者。</p>
  <div class="hero-meta">
    <span>78 个项目</span><span>{n_ch} 章</span><span>{n_app} 个附录</span><span>{n_cat} 个分类页</span><span>约 {wan} 万字</span><span>CC BY 4.0</span>
  </div>
</section>""".format(ver=SITE["version"], date=SITE["date"], n_ch=n_ch, n_app=n_app, n_cat=n_cat, wan=wan)

# ---------------------------------------------------------------- 章节清单
# (slug, 标题, 源文件, 分组, 摘要)
CHAPTERS = [
    ("index", "封面与导读", "00-cover.md", "导读", "研究问题、证据等级、阅读路径"),
    ("concepts", "一 · 四个被混用的「本体」", "01-concepts.md", "方法论", "哲学本体论 / 形式本体 / 语义层 / 操作本体"),
    ("methodology", "二 · 本体工程方法论谱系", "02-methodology.md", "方法论", "从 competency question 到 CI 的四件内核"),
    ("languages", "三 · 建模语言与约束选型", "03-languages.md", "方法论", "OWL / SHACL / LinkML / 属性图 / 对象类型"),
    ("reasoning", "四 · 推理与校验", "04-reasoning.md", "方法论", "四类推理、复杂度、三层校验"),
    ("governance", "五 · 治理：版本、变更与 CI", "05-governance.md", "方法论", "本体当代码：版本、兼容性、影响面、回滚"),
    ("kinetic", "六 · 动力学层：从名词到动词", "06-kinetic.md", "方法论", "动作、门控写入、状态所有权、预期值"),
    ("case", "七 · 一个完整案例：五周与三个事故", "07-case.md", "方法论", "18 个类、5 条约束、二十余人日、每周对账"),
    ("ecosystem", "八 · 开源生态地图", "08-ecosystem.md", "生态", "78 个项目、七个类别、四种采纳级别"),
    ("cat-platform", "8.1 企业本体平台", None, "生态", "Palantir 复刻派与操作本体实现"),
    ("cat-agent", "8.2 Agent 上下文与记忆", None, "生态", "给模型一份有类型、可追溯的语义"),
    ("cat-toolchain", "8.3 建模与工程工具链", None, "生态", "编写、校验、编译、发布"),
    ("cat-infra", "8.4 语义基础设施", None, "生态", "解析、推理、校验、存储"),
    ("cat-graphrag", "8.5 图谱检索与 GraphRAG", None, "生态", "邻居，不是本体"),
    ("cat-vocab", "8.6 领域词表与本体资产", None, "生态", "可直接借用的术语与标识符"),
    ("cat-beyond", "8.7 索引之外的系统", None, "生态", "趋势章节提到、但未被收录的 19 个系统"),
    ("trends", "九 · 八个趋势的独立核验", "09-trends.md", "实证", "逐条判定：成立 / 部分成立 / 证据不足"),
    ("stack", "十 · 技术栈分层与选型框架", "10-stack.md", "实证", "L0–L5 六层模型与决策树"),
    ("evidence", "十一 · 四次实测", "11-evidence.md", "实证", "SHACL 与 OWL 的行为差异；规模代价；41 个生成器"),
    ("antipatterns", "十二 · 反模式与落地判据", "12-antipatterns.md", "实证", "五种死法、六条判据、分阶段路线"),
    ("org", "十三 · 组织、角色与预算", "13-org.md", "实证", "三个角色、人月预算、KPI 与失败信号"),
    ("llm", "十四 · 本体与模型系统的边界", "14-llm.md", "实证", "三个真接触面、两个伪接触面、四条判据"),
    ("glossary", "十五 · 术语表", "15-glossary.md", "附录", "中英对照与一句话定义"),
    ("method", "附录 A · 方法与可复现性", "16-method.md", "附录", "核验方法、数据口径、局限"),
    ("cheatsheet", "附录 B · 选型速查表", "17-cheatsheet.md", "附录", "八张表：判断、选型、清单、纠偏"),
    ("appendix-projects", "附录 C · 78 个项目总表", None, "附录", "名称、仓库、星数、建库、许可、语言、分级"),
]


# ---------------------------------------------------------------- Markdown
def esc(s):
    return html.escape(s, quote=False)


def inline(text):
    """行内元素：`code` **bold** *italic* [text](url)"""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append("<code>" + esc(p[1:-1]) + "</code>")
            continue
        s = esc(p)
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                   lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\*\w])\*([^*\n]+)\*(?![\*\w])", r"<em>\1</em>", s)
        out.append(s)
    return "".join(out)


def slug_id(headings, level):
    return "h%d-%d" % (level, len(headings))


def md_to_html(text):
    """返回 (html, toc, headings_for_search)"""
    lines = text.split("\n")
    out = []
    toc = []
    headings = []
    i = 0
    n = len(lines)
    para = []

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>")
            para = []

    while i < n:
        line = lines[i]
        s = line.rstrip()

        # 代码块
        if s.startswith("```"):
            flush_para()
            lang = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].rstrip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = ' class="lang-%s"' % esc(lang) if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (cls, esc("\n".join(buf))))
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush_para()
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 1:
                # 章标题单独处理，不重复渲染
                i += 1
                continue
            hid = slug_id(headings, level)
            headings.append({"id": hid, "text": re.sub(r"[`*]", "", title), "level": level})
            if level in (2, 3):
                toc.append(headings[-1])
            out.append('<h%d id="%s">%s</h%d>' % (level, hid, inline(title), level))
            i += 1
            continue

        # 分隔线
        if re.match(r"^---+\s*$", s):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        # 表格
        if s.startswith("|") and i + 1 < n and re.match(r"^\|[\s:\-|]+\|?\s*$", lines[i + 1].strip()):
            flush_para()
            header = [c.strip() for c in s.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ['<div class="table-wrap"><table>', "<thead><tr>"]
            for h in header:
                t.append("<th>%s</th>" % inline(h))
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue

        # 引用块
        if s.startswith(">"):
            flush_para()
            buf = []
            while i < n and lines[i].rstrip().startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i].rstrip()))
                i += 1
            inner = md_to_html("\n".join(buf))[0]
            out.append('<blockquote>%s</blockquote>' % inner)
            continue

        # 列表
        if re.match(r"^\s*([-*]|\d+\.)\s+", s):
            flush_para()
            ordered = bool(re.match(r"^\s*\d+\.", s))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                raw = lines[i]
                indent = len(raw) - len(raw.lstrip())
                content = re.sub(r"^\s*([-*]|\d+\.)\s+", "", raw).rstrip()
                if indent >= 2 and items:
                    items[-1] = items[-1] + " " + content
                else:
                    items.append(content)
                i += 1
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(x) for x in items), tag))
            continue

        # 空行
        if not s.strip():
            flush_para()
            i += 1
            continue

        para.append(s)
        i += 1

    flush_para()
    return "\n".join(out), toc, headings


# ---------------------------------------------------------------- 模板
def nav_html(current):
    groups = []
    for slug, title, _f, group, _d in CHAPTERS:
        if not groups or groups[-1][0] != group:
            groups.append([group, []])
        groups[-1][1].append((slug, title))
    parts = ['<nav class="site-nav" aria-label="章节">']
    for group, items in groups:
        parts.append('<div class="nav-group"><div class="nav-group-title">%s</div><ul>' % esc(group))
        for slug, title in items:
            cls = ' class="is-active"' if slug == current else ""
            parts.append('<li><a href="%s.html"%s>%s</a></li>' % (slug, cls, esc(title)))
        parts.append("</ul></div>")
    parts.append("</nav>")
    return "".join(parts)


def page(title, body, current, toc, subtitle=""):
    idx = [c[0] for c in CHAPTERS].index(current) if current in [c[0] for c in CHAPTERS] else 0
    prev_c = CHAPTERS[idx - 1] if idx > 0 else None
    next_c = CHAPTERS[idx + 1] if idx + 1 < len(CHAPTERS) else None
    toc_html = ""
    if toc:
        toc_html = '<aside class="toc"><div class="toc-title">本页目录</div><ul>%s</ul></aside>' % "".join(
            '<li class="lvl%d"><a href="#%s">%s</a></li>' % (h["level"], h["id"], esc(h["text"])) for h in toc
        )
    pager = ['<div class="pager">']
    if prev_c:
        pager.append('<a class="pager-prev" href="%s.html"><span>上一篇</span><strong>%s</strong></a>' % (prev_c[0], esc(prev_c[1])))
    else:
        pager.append("<span></span>")
    if next_c:
        pager.append('<a class="pager-next" href="%s.html"><span>下一篇</span><strong>%s</strong></a>' % (next_c[0], esc(next_c[1])))
    pager.append("</div>")

    return """<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {site}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{site}">
<meta property="og:title" content="{title} · {site}">
<meta property="og:description" content="{desc}">
<meta name="theme-color" content="#14584c">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
</head>
<body data-page="{current}">
<a class="skip" href="#main">跳到正文</a>
<header class="topbar">
  <button class="icon-btn nav-toggle" aria-label="目录" data-action="nav">☰</button>
  <a class="brand" href="index.html"><span class="brand-mark">◈</span><span class="brand-text">{site}</span></a>
  <div class="topbar-right">
    <button class="search-btn" data-action="search"><svg class="icon-search" viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.6" cy="8.6" r="5.4" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12.8 12.8 17 17" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg><span>搜索</span><kbd>/</kbd></button>
    <button class="icon-btn" data-action="theme" aria-label="切换主题">◐</button>
  </div>
</header>
<div class="layout">
  <aside class="sidebar" id="sidebar">{nav}</aside>
  <main id="main" class="main">
    <article class="article">
      {subtitle}
      {body}
      {pager}
    </article>
  </main>
  {toc}
</div>
<div class="search-overlay" id="search-overlay" hidden>
  <div class="search-panel">
    <input id="search-input" type="search" placeholder="搜索章节、概念、项目…" autocomplete="off">
    <div class="search-results" id="search-results"></div>
    <div class="search-hint">↑↓ 选择 · Enter 打开 · Esc 关闭</div>
  </div>
</div>
<footer class="site-footer">
  <div>{site} v{version} · {date} · <a href="https://github.com/yunfong/ontology-handbook">yunfong</a></div>
  <div>个人研究整理，不代表所在机构观点；案例数据已通用化处理。内容以 CC BY 4.0 发布，引用数据核验于 2026-10-30。</div>
</footer>
<script src="assets/search-index.js"></script>
<script src="assets/app.js"></script>
</body>
</html>""".format(
        title=esc(title), site=esc(SITE["title"]), desc=esc(subtitle or SITE["subtitle"]),
        current=current, nav=nav_html(current), body=body, toc=toc_html, pager="".join(pager),
        subtitle=subtitle, version=SITE["version"], date=SITE["date"],
    )


# ---------------------------------------------------------------- 项目卡片
def load_projects():
    import importlib.util
    spec = importlib.util.spec_from_file_location("projects", os.path.join(ROOT, "data", "projects.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    meta = json.load(open(os.path.join(ROOT, "data", "meta.json"), encoding="utf-8"))
    out = []
    for p in mod.PROJECTS:
        m = meta.get(p["repo"], {})
        q = dict(p)
        q["stars"] = m.get("stars", 0)
        q["created"] = m.get("created", "")
        q["license"] = m.get("license", "")
        q["lang"] = m.get("lang", "")
        q["anchor"] = "p-" + p["repo"].replace("/", "-").replace(".", "-").lower()
        out.append(q)
    return out, mod.CATEGORY_META


TIER_LABEL = {
    "S": ("S", "核心必读", "tier-s"),
    "A": ("A", "重要参考", "tier-a"),
    "B": ("B", "观察备选", "tier-b"),
    "C": ("C", "仅作存档", "tier-c"),
}


def project_cards(projects):
    out = ['<div class="cards">']
    for p in projects:
        tier, label, cls = TIER_LABEL[p["tier"]]
        meta = []
        meta.append('<span class="stars">★ {:,}</span>'.format(p["stars"]))
        meta.append("<span>%s</span>" % esc(p["created"]))
        meta.append("<span>%s</span>" % esc(p["lang"] or "—"))
        meta.append("<span>%s</span>" % esc(p["license"] or "—"))
        out.append(
            """<article class="card" id="{anchor}">
  <div class="card-head">
    <h3 class="card-title">{name}</h3>
    <span class="tier {cls}" title="{label}">{tier}</span>
  </div>
  <div class="card-repo"><a href="https://github.com/{repo}">{repo}</a></div>
  <div class="card-meta">{meta}</div>
  <div class="card-body">{body}</div>
  <div class="card-adopt"><span class="adopt-label">何时采纳</span>{adopt}</div>
</article>""".format(
                anchor=p["anchor"], name=esc(p["name"]), cls=cls, tier=tier, label=label,
                repo=p["repo"], meta="".join(meta), body=inline(p["body"]), adopt=inline(p["adopt"]),
            )
        )
    out.append("</div>")
    return "".join(out)


def build_category_page(cat):
    projects, meta = load_projects()
    items = [p for p in projects if p["category"] == cat]
    m = meta[cat]
    body = ['<p class="lede">%s</p>' % inline(m["intro"])]
    if m.get("note"):
        body.append('<div class="note">%s</div>' % inline(m["note"]))
    body.append(project_cards(items))
    toc = [{"id": p["anchor"], "text": p["name"], "level": 3} for p in items]
    return page(
        title=m["title"],
        body="\n".join(body),
        current=m["slug"],
        toc=toc,
        subtitle='<div class="chapter-kicker">第八章 · 开源生态地图</div><h1 class="chapter-title">%s</h1><p class="chapter-sub">%s</p>'
        % (esc(m["title"]), inline(m["subtitle"])),
    )


# ---------------------------------------------------------------- 附录 C：项目总表
CAT_SLUGS = ["platform", "agent", "toolchain", "infra", "graphrag", "vocab", "beyond"]


def build_projects_table_page():
    projects, meta = load_projects()
    rows = []
    for cat in CAT_SLUGS:
        group = sorted([p for p in projects if p["category"] == cat], key=lambda x: -x["stars"])
        if not group:
            continue
        m = meta[cat]
        rows.append('<tr class="grp"><td colspan="6">%s <span>%d 个项目</span></td></tr>'
                    % (esc(m["title"]), len(group)))
        for p in group:
            url = "https://github.com/%s" % p["repo"]
            rows.append(
                "<tr><td><a href=\"%s\">%s</a><span class=\"sub\">%s</span></td>"
                "<td class=\"num\">%s</td><td class=\"nowrap\">%s</td><td class=\"nowrap\">%s</td>"
                "<td class=\"nowrap\">%s</td><td class=\"nowrap tier-%s\">%s</td></tr>"
                % (
                    esc(url), esc(p["repo"]), esc(p["name"]),
                    format(p["stars"], ","),
                    esc(str(p["created"])[:7]),
                    esc(p["license"] or "—"),
                    esc(p["lang"] or "—"),
                    esc(p["tier"].lower()), esc(p["tier"]),
                )
            )
    body = [
        '<p class="lede">78 个项目按七个类别分组，组内按星数降序。星数与建库时间为 2026-10-30 快照，'
        "许可取自仓库的 SPDX 标识。<strong>分级是编者判断，不是质量评分</strong>，判据见第八章。</p>",
        '<div class="table-wrap"><table class="tbl-projects">'
        '<colgroup><col style="width:41%"><col style="width:11%"><col style="width:11%">'
        '<col style="width:15%"><col style="width:14%"><col style="width:8%"></colgroup><thead><tr>'
        "<th>项目（仓库 / 名称）</th><th>星数</th><th>建库</th><th>许可</th><th>语言</th><th>级</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>",
        '<p class="note">「级」的含义：<strong>S</strong> 核心必读（能改变技术选型）、<strong>A</strong> 重要参考'
        "（某个环节的最优解）、<strong>B</strong> 场景相关（条件满足时值得看）、<strong>C</strong> 了解即可。"
        "同一级别不代表同等成熟度；星数只反映社区规模。</p>",
    ]
    subtitle = ('<div class="chapter-kicker">附录</div><h1 class="chapter-title">附录 C · 78 个项目总表</h1>'
                '<p class="chapter-sub">名称、仓库、星数、建库、许可、语言、分级</p>')
    return page(
        title="附录 C · 78 个项目总表",
        body="\n".join(body),
        current="appendix-projects",
        toc=[{"id": "tbl", "text": "总表", "level": 2}],
        subtitle=subtitle,
    )


# ---------------------------------------------------------------- 打印版
def build_print_document():
    """把所有章节串成一个长 HTML，供 Chrome 打印成单文件 PDF。"""
    projects, meta = load_projects()
    parts = []
    for slug, title, fname, group, desc in CHAPTERS:
        if slug == "appendix-projects":
            html_page = build_projects_table_page()
            body_html = re.search(r'<article class="article">(.*?)</article>', html_page, re.S).group(1)
            body_html = re.sub(r'<div class="pager">.*?</div>', "", body_html, flags=re.S)
            kicker, head, sub = "附录", "附录 C · 78 个项目总表", "名称、仓库、星数、建库、许可、语言、分级"
        elif fname is None:
            m = next(v for v in meta.values() if v["slug"] == slug)
            items = [p for p in projects if p["category"] == m["slug"]]
            body = ['<p class="lede">%s</p>' % inline(m["intro"])]
            if m.get("note"):
                body.append('<div class="note">%s</div>' % inline(m["note"]))
            body.append(project_cards(items))
            kicker, head, sub = "第八章 · 开源生态地图", m["title"], m["subtitle"]
            body_html = "\n".join(body)
        else:
            path = os.path.join(SRC, fname)
            if not os.path.exists(path):
                continue
            body_html, _toc, _h = md_to_html(open(path, encoding="utf-8").read())
            if slug == "index":
                body_html = hero_html() + body_html
                kicker, head, sub = "", "", ""
            else:
                kicker, head, sub = group, title, desc
        header = ""
        if head:
            header = ('<div class="chapter-kicker">%s</div><h1 class="chapter-title">%s</h1>'
                      '<p class="chapter-sub">%s</p>') % (esc(kicker), esc(head), inline(sub))
        parts.append('<section class="print-chapter">%s\n%s</section>' % (header, body_html))

    joined = "\n".join(parts)
    # 打印版去掉指向本地文件的相对链接，避免 PDF 里写入 file:// URI
    joined = re.sub(r'<a\s+href="(?!https?://)[^"]*"[^>]*>(.*?)</a>', r"\1", joined, flags=re.S)
    doc = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<title>%s（打印版）</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="print-doc">
<article class="article">
%s
</article>
</body>
</html>""" % (esc(SITE["title"]), joined)
    out = os.path.join(ROOT, "_print.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return out


# ---------------------------------------------------------------- 搜索索引
def check_links():
    """扫描生成的 html 里指向本地文件的链接与资源，返回缺失列表。"""
    broken = []
    seen = set()
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        html = open(path, encoding="utf-8").read()
        for attr, val in re.findall(r'(href|src)="([^"]+)"', html):
            if not val or val.startswith(("http://", "https://", "mailto:", "#", "data:", "javascript:")):
                continue
            target = val.split("#")[0].split("?")[0]
            target = __import__("urllib.parse", fromlist=["unquote"]).unquote(target)
            if not target:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
            key = (os.path.basename(path), target)
            if key in seen:
                continue
            seen.add(key)
            if not os.path.exists(resolved):
                broken.append((os.path.basename(path), val))
    return broken


def build_search_index(pages):
    rows = []
    for p in pages:
        for h in p["headings"]:
            rows.append({"p": p["slug"], "t": p["title"], "h": h["text"], "id": h["id"]})
    # 段落级摘要
    js = "window.__SEARCH__ = " + json.dumps(rows, ensure_ascii=False) + ";"
    with open(os.path.join(ASSETS, "search-index.js"), "w", encoding="utf-8") as f:
        f.write(js)
    return len(rows)


# ---------------------------------------------------------------- 主流程
def main():
    argv = __import__("sys").argv[1:]
    if "--print" in argv:
        print(build_print_document())
        return
    pages_meta = []

    for slug, title, fname, group, desc in CHAPTERS:
        if fname is None:
            continue
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            print("  ! 缺文件：%s" % path)
            continue
        raw = open(path, encoding="utf-8").read()
        body, toc, headings = md_to_html(raw)
        if slug == "index":
            body = hero_html() + body
        subtitle = ""
        if slug == "index":
            subtitle = ""
        else:
            subtitle = '<div class="chapter-kicker">%s</div><h1 class="chapter-title">%s</h1><p class="chapter-sub">%s</p>' % (
                esc(group), esc(title), inline(desc))
        out = page(title, body, slug, toc, subtitle)
        with open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(out)
        pages_meta.append({"slug": slug, "title": title, "headings": headings})
        print("  ✓ %-16s %s" % (slug, title))

    # 分类页
    _projects, meta = load_projects()
    for cat, m in meta.items():
        out = build_category_page(cat)
        with open(os.path.join(ROOT, m["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(out)
        print("  ✓ %-16s %s" % (m["slug"], m["title"]))
        pages_meta.append({
            "slug": m["slug"], "title": m["title"],
            "headings": [{"id": p["anchor"], "text": "%s（%s）" % (p["name"], p["repo"]), "level": 3}
                         for p in _projects if p["category"] == cat],
        })
    with open(os.path.join(ROOT, "appendix-projects.html"), "w", encoding="utf-8") as f:
        f.write(build_projects_table_page())
    print("  ✓ %-16s %s" % ("appendix-projects", "附录 C · 78 个项目总表"))
    pages_meta.append({"slug": "appendix-projects", "title": "附录 C · 78 个项目总表",
                       "headings": [{"id": p["anchor"], "text": "%s（%s）" % (p["name"], p["repo"]), "level": 3}
                                    for p in _projects]})

    n = build_search_index(pages_meta)
    print("  ✓ 搜索索引 %d 条" % n)

    total_cn = 0
    for slug, title, fname, group, desc in CHAPTERS:
        if fname and os.path.exists(os.path.join(SRC, fname)):
            total_cn += len(CN_RE.findall(open(os.path.join(SRC, fname), encoding="utf-8").read()))
    print("  ✓ 章节汉字 %s" % format(total_cn, ","))

    broken = check_links()
    if broken:
        print("  ! 断链 %d 处：" % len(broken))
        for src, href in broken:
            print("      %s -> %s" % (src, href))
    else:
        print("  ✓ 断链 0 处")


if __name__ == "__main__":
    main()
