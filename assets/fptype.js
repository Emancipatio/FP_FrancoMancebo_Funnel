// Founder Personality Type: shared quiz + remembered result (landing, kit, thank-you and booking pages).
// The result lives only in this browser (localStorage), so later pages can greet the founder by type.
(function (w) {
  var KEY = "fp-franco-type";
  var SPLIT = {focus: "big picture vs detail", control: "hands-off vs hands-on", contact: "written vs live updates", pace: "fast vs checked drafts"};

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }

  // Answer a = first end (Big picture, Hands-off, Async, Fast). Both answers in a dimension
  // must agree on "a"; a split takes the safer start (Detail, Hands-on, Live, Deliberate).
  function compute(S, a) {
    var dims = {}, split = [];
    S.questions.forEach(function (x, i) { (dims[x.dim] = dims[x.dim] || []).push(a[i]); });
    var end = function (d) { var v = dims[d]; if (v[0] !== v[1]) split.push(d); return v.every(function (k) { return k === "a"; }); };
    var big = end("focus"), off = end("control"), as = end("contact"), fast = end("pace");
    return {
      style: big ? (off ? "visionary" : "captain") : (off ? "systems" : "craftsman"),
      contact: as ? "async" : "live",
      pace: fast ? "fast" : "deliberate",
      split: split
    };
  }

  function save(r) {
    try { localStorage.setItem(KEY, JSON.stringify({style: r.style, contact: r.contact, pace: r.pace, split: r.split || [], t: Date.now()})); } catch (e) {}
  }

  function load(S) {
    try {
      var r = JSON.parse(localStorage.getItem(KEY) || "null");
      if (r && S.styles[r.style] && S.contact[r.contact] && S.pace[r.pace]) { r.split = Array.isArray(r.split) ? r.split : []; return r; }
    } catch (e) {}
    return null;
  }

  function clear() { try { localStorage.removeItem(KEY); } catch (e) {} }

  // Everything a page needs to show a result.
  function describe(S, r) {
    var st = S.styles[r.style], ty = S.types[r.style][r.pace];
    return {
      id: ty.id, name: ty.name, tag: ty.tag, line: ty.line, pain: ty.pain, gain: ty.gain, rh: st.rh,
      chips: st.axes.split(" · ").concat([S.pace[r.pace].label, S.contact[r.contact].label + " updates"]),
      kit: r.style + "-" + r.contact + "-" + r.pace,
      split: r.split.map(function (d) { return SPLIT[d] || d; })
    };
  }

  // Slide quiz. els: {qcount, back, qbar, slide}. onDone(result) runs when "See my type" is clicked.
  function mount(S, els, onDone) {
    var n = S.questions.length, a = [], cur = 0, sl = els.slide, busy = false;
    var still = w.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    function paint() {
      els.back.hidden = cur === 0;
      els.qbar.style.width = (Math.min(cur, n) / n * 100) + "%";
      if (cur >= n) {
        els.qcount.textContent = "All done";
        sl.innerHTML = '<div class="done"><h3 style="min-height:0;margin:0">Your type is ready.</h3><button class="btn" type="button" data-see>See my type →</button></div>';
        sl.querySelector("[data-see]").addEventListener("click", function () { var r = compute(S, a); save(r); onDone(r); });
        return;
      }
      var x = S.questions[cur];
      els.qcount.textContent = "Question " + (cur + 1) + " of " + n;
      sl.innerHTML = '<h3>' + esc(x.q) + '</h3><div class="opts">' + ["a", "b"].map(function (k) {
        return '<button type="button" class="opt' + (a[cur] === k ? " on" : "") + '" data-k="' + k + '"><b>' + k.toUpperCase() + '</b><span>' + esc(x[k]) + '</span></button>';
      }).join("") + '</div>';
    }
    function go(to) {
      if (still) { cur = to; paint(); return; }
      busy = true; sl.classList.add("out");
      setTimeout(function () {
        cur = to; paint();
        sl.classList.remove("out"); sl.classList.add("in");
        void sl.offsetWidth; sl.classList.remove("in");
        setTimeout(function () { busy = false; }, 250);
      }, 250);
    }
    sl.addEventListener("click", function (e) {
      var b = e.target.closest(".opt"); if (!b || busy) return;
      a[cur] = b.dataset.k;
      Array.prototype.forEach.call(sl.querySelectorAll(".opt"), function (o) { o.classList.toggle("on", o === b); });
      busy = true; setTimeout(function () { busy = false; go(cur + 1); }, 220);
    });
    els.back.addEventListener("click", function () { if (!busy && cur > 0) go(cur - 1); });
    paint();
    return { restart: function () { a = []; cur = 0; paint(); } };
  }

  function getStyles(path) { return fetch(path).then(function (r) { if (!r.ok) throw 0; return r.json(); }); }

  w.FPType = {compute: compute, save: save, load: load, clear: clear, describe: describe, mount: mount, getStyles: getStyles, esc: esc};
})(window);
