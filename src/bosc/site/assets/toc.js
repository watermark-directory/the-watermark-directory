// Highlight the on-this-page TOC entry for the section currently in view.
// Dependency-free: an IntersectionObserver over the headings the toc links to.
(function () {
  "use strict";
  var toc = document.querySelector(".toc");
  if (!toc || !("IntersectionObserver" in window)) return;

  var links = {};
  toc.querySelectorAll('a[href^="#"]').forEach(function (a) {
    links[decodeURIComponent(a.getAttribute("href").slice(1))] = a;
  });
  var ids = Object.keys(links);
  if (!ids.length) return;

  var visible = {};
  function update() {
    var current = null;
    for (var i = 0; i < ids.length; i++) {
      if (visible[ids[i]]) { current = ids[i]; break; }
    }
    ids.forEach(function (id) { links[id].classList.toggle("active", id === current); });
  }

  var obs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
      update();
    },
    // Trip a heading "active" once it reaches the upper third of the viewport.
    { rootMargin: "0px 0px -66% 0px" }
  );
  ids.forEach(function (id) {
    var el = document.getElementById(id);
    if (el) obs.observe(el);
  });
})();
