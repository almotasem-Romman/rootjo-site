(function () {
  var h = document.documentElement, $ = function (s) { return document.querySelector(s); }, $$ = function (s) { return [].slice.call(document.querySelectorAll(s)); };
  function en() { return h.lang === "en"; }

  /* language: WhatsApp links, placeholders and select options follow the page language */
  function applyLang() {
    $$("[data-href-en]").forEach(function (a) { if (!a.dataset.hrefAr) a.dataset.hrefAr = a.getAttribute("href"); a.setAttribute("href", en() ? a.dataset.hrefEn : a.dataset.hrefAr); });
    $$("[data-ph-en]").forEach(function (i) { i.placeholder = en() ? i.dataset.phEn : i.dataset.phAr; });
    $$("select[data-opts-en]").forEach(function (s) { var v = s.value; s.innerHTML = en() ? s.dataset.optsEn : s.dataset.optsAr; s.value = v; });
    if (window.__filter) window.__filter();
    if (window.__rq) window.__rq();
  }
  $("#langBtn").addEventListener("click", function () {
    var l = en() ? "ar" : "en"; h.lang = l; h.dir = l === "en" ? "ltr" : "rtl";
    try { localStorage.setItem("root-lang", l); } catch (e) {}
    applyLang();
  });

  /* mobile menu */
  var bg = $("#burger"), nav = $("#mainnav");
  bg.addEventListener("click", function () { var o = nav.classList.toggle("open"); bg.setAttribute("aria-expanded", o); });

  /* search */
  var data = []; try { data = JSON.parse($("#sdata").textContent); } catch (e) {}
  var q = $("#q"), box = $("#sres"), sel = -1;
  function norm(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim(); }
  function render() {
    var v = norm(q.value); sel = -1;
    if (!v) { box.hidden = true; return; }
    var words = v.split(" ");
    var hits = data.filter(function (p) { var n = norm(p.n); return words.every(function (w) { return n.indexOf(w) > -1; }); }).slice(0, 7);
    box.innerHTML = hits.length ? hits.map(function (p) {
      return '<a href="' + p.u + '"><img src="' + p.i + '" alt=""><b>' + p.n.replace(/</g, "&lt;") + "</b><small>" + (p.s === "sold" ? (en() ? "Sold" : "غير متوفر") : p.p + " JD") + "</small></a>";
    }).join("") : '<div class="none">' + (en() ? "No matches. Ask us on WhatsApp and we'll source it." : "ما في نتائج. اسألنا على واتساب ومنوفره لك.") + "</div>";
    box.hidden = false;
  }
  q.addEventListener("input", render);
  q.addEventListener("focus", render);
  q.addEventListener("keydown", function (e) {
    var a = [].slice.call(box.querySelectorAll("a")); if (!a.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + a.length) % a.length; a.forEach(function (x, i) { x.classList.toggle("on", i === sel); }); }
    if (e.key === "Enter") { e.preventDefault(); location.href = a[Math.max(sel, 0)].getAttribute("href"); }
    if (e.key === "Escape") { box.hidden = true; }
  });
  document.addEventListener("click", function (e) { if (!e.target.closest(".search")) box.hidden = true; });

  /* section page: filter by condition, sort */
  var grid = $("#grid");
  if (grid) {
    var cards = [].slice.call(grid.querySelectorAll(".pc")), extra = [].slice.call(grid.children).filter(function (c) { return !c.classList.contains("pc"); });
    cards.forEach(function (c, i) { c.dataset.i = i; });
    window.__filter = function () {
      var c = $("#fCond").value, s = $("#fSort").value;
      var list = cards.slice().sort(function (a, b) {
        var sa = +a.dataset.sold, sb = +b.dataset.sold; if (sa !== sb) return sa - sb;
        if (s === "lo") return a.dataset.price - b.dataset.price;
        if (s === "hi") return b.dataset.price - a.dataset.price;
        if (s === "new") return (b.dataset.added || "").localeCompare(a.dataset.added || "") || a.dataset.i - b.dataset.i;
        return a.dataset.i - b.dataset.i;
      });
      var n = 0;
      list.forEach(function (x) { var show = !c || x.dataset.cond === c; x.hidden = !show; if (show && x.dataset.sold === "0") n++; grid.appendChild(x); });
      extra.forEach(function (x) { grid.appendChild(x); });
      $("#shown").textContent = en() ? n + " available" : n + " متوفر";
    };
    $("#fCond").addEventListener("change", window.__filter);
    $("#fSort").addEventListener("change", window.__filter);
  }

  /* request form with live summary */
  var rq = $("#rq");
  if (rq) {
    var L = {
      ar: { type: "نوع الجهاز", use: "الاستخدام", budget: "الميزانية", cond: "الحالة", del: "التوصيل", dv: "3 عمّان · 5 خارجها", none: "ما حددت", hi: "مرحباً Root، بدي أطلب جهاز:", notes: "تفاصيل", name: "الاسم" },
      en: { type: "Device", use: "Use", budget: "Budget", cond: "Condition", del: "Delivery", dv: "3 JD Amman · 5 JD outside", none: "Not set", hi: "Hi Root, I'd like to request a device:", notes: "Details", name: "Name" }
    };
    function vals(n) { return [].map.call(rq.querySelectorAll('input[name="' + n + '"]:checked'), function (x) { return x.getAttribute(en() ? "data-en" : "data-ar"); }); }
    window.__rq = function () {
      var T = en() ? L.en : L.ar, sep = en() ? ", " : "، ";
      var rows = [[T.type, vals("t").join("") || T.none], [T.use, vals("u").join(sep) || T.none], [T.budget, vals("b").join("") || T.none], [T.cond, vals("c").join("") || T.none]];
      $("#rqsum").innerHTML = rows.concat([[T.del, T.dv]]).map(function (r) { return "<div><dt>" + r[0] + "</dt><dd>" + r[1] + "</dd></div>"; }).join("");
      var lines = [T.hi].concat(rows.map(function (r) { return "• " + r[0] + ": " + r[1]; }));
      var nt = $("#rq-notes").value.trim(), nm = $("#rq-name").value.trim();
      if (nt) lines.push("• " + T.notes + ": " + nt);
      if (nm) lines.push("• " + T.name + ": " + nm);
      lines.push("rootjo.com");
      $("#rqsend").href = "https://wa.me/962799167971?text=" + encodeURIComponent(lines.join("\n"));
    };
    rq.addEventListener("input", window.__rq); rq.addEventListener("change", window.__rq);
    rq.addEventListener("submit", function (e) { e.preventDefault(); });
  }
  applyLang();
})();
