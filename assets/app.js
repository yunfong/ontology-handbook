/* 本体论工程手册 · 交互脚本
   - 主题切换（localStorage）
   - 移动端目录
   - 客户端搜索（索引由 build.py 生成）
   - 目录滚动高亮
*/
(function () {
  "use strict";

  /* ---------- 主题 ---------- */
  var root = document.documentElement;
  function applyTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("oc-theme", t); } catch (e) {}
  }
  try {
    var saved = localStorage.getItem("oc-theme");
    if (saved) root.setAttribute("data-theme", saved);
    else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      root.setAttribute("data-theme", "dark");
    }
  } catch (e) {}

  /* ---------- 顶栏按钮 ---------- */
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-action]");
    if (!btn) return;
    var action = btn.getAttribute("data-action");
    if (action === "theme") {
      applyTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    } else if (action === "nav") {
      document.body.classList.toggle("nav-open");
    } else if (action === "search") {
      openSearch();
    }
  });

  // 移动端点击导航后关闭
  document.querySelectorAll(".site-nav a").forEach(function (a) {
    a.addEventListener("click", function () {
      document.body.classList.remove("nav-open");
    });
  });

  /* ---------- 搜索 ---------- */
  var index = window.__SEARCH__ || [];
  var overlay, input, results, selected = -1, matches = [];

  function openSearch() {
    overlay = document.getElementById("search-overlay");
    input = document.getElementById("search-input");
    results = document.getElementById("search-results");
    if (!overlay) return;
    overlay.hidden = false;
    input.value = "";
    render("");
    setTimeout(function () { input.focus(); }, 10);
  }

  function closeSearch() {
    if (overlay) overlay.hidden = true;
  }

  function norm(s) { return (s || "").toLowerCase(); }

  function render(q) {
    q = q.trim();
    if (!q) {
      matches = index.slice(0, 12);
    } else {
      var terms = norm(q).split(/\s+/);
      matches = index.filter(function (row) {
        var hay = norm(row.h + " " + row.t);
        return terms.every(function (t) { return hay.indexOf(t) >= 0; });
      }).slice(0, 40);
    }
    selected = matches.length ? 0 : -1;
    if (!matches.length) {
      results.innerHTML = '<div class="sr-empty">没有匹配。试试「证据」「SHACL」「记忆」「治理」。</div>';
      return;
    }
    results.innerHTML = matches.map(function (m, i) {
      return '<a class="sr-item' + (i === 0 ? " is-sel" : "") + '" href="' + m.p + '.html#' + m.id + '">' +
        '<span class="sr-page">' + escapeHtml(m.t) + '</span>' +
        '<div class="sr-title">' + escapeHtml(m.h) + '</div></a>';
    }).join("");
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }

  function move(delta) {
    if (!matches.length) return;
    selected = (selected + delta + matches.length) % matches.length;
    var items = results.querySelectorAll(".sr-item");
    items.forEach(function (el, i) { el.classList.toggle("is-sel", i === selected); });
    var el = items[selected];
    if (el) el.scrollIntoView({ block: "nearest" });
  }

  document.addEventListener("keydown", function (ev) {
    var ov = document.getElementById("search-overlay");
    var isOpen = ov && !ov.hidden;

    if (ev.key === "/" && !isOpen && !/input|textarea/i.test(document.activeElement.tagName)) {
      ev.preventDefault(); openSearch(); return;
    }
    if (ev.key === "Escape" && isOpen) { closeSearch(); return; }
    if (!isOpen) return;

    if (ev.key === "ArrowDown") { ev.preventDefault(); move(1); }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); move(-1); }
    else if (ev.key === "Enter") {
      if (matches[selected]) { window.location.href = matches[selected].p + ".html#" + matches[selected].id; }
    }
  });

  document.addEventListener("input", function (ev) {
    if (ev.target && ev.target.id === "search-input") render(ev.target.value);
  });

  document.addEventListener("click", function (ev) {
    var ov = document.getElementById("search-overlay");
    if (ov && ev.target === ov) closeSearch();
  });

  /* ---------- 目录滚动高亮 ---------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) {
      var id = decodeURIComponent(a.getAttribute("href").slice(1));
      map[id] = a;
    });
    var heads = document.querySelectorAll(".article h2[id], .article h3[id]");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("active"); });
          var a = map[en.target.id];
          if (a) a.classList.add("active");
        }
      });
    }, { rootMargin: "-72px 0px -70% 0px", threshold: 0 });
    heads.forEach(function (h) { io.observe(h); });
  }
})();
