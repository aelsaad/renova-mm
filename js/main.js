/* RENOVA MM — page interactions */
(function () {
  "use strict";

  const CFG = window.RENOVA || {};
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const canHover = matchMedia("(hover: hover)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  /* ================= Contact details ================= */
  function applyContact() {
    $$("[data-phone]").forEach((el) => { el.textContent = CFG.phone; });
    $$("[data-phone-link]").forEach((el) => { el.href = "tel:" + String(CFG.phone).replace(/[^\d+]/g, ""); });
    $$("[data-email]").forEach((el) => { el.textContent = CFG.email; });
    $$("[data-email-link]").forEach((el) => { el.href = "mailto:" + CFG.email; });
  }
  applyContact();

  /* ================= Social networks ================= */
  const SOCIAL = {
    facebook: { label: "Facebook", svg: '<path fill="currentColor" stroke="none" d="M13.5 21.5v-8h2.7l.4-3.2h-3.1V8.3c0-.9.3-1.6 1.6-1.6h1.7V3.9c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.3H7.5v3.2h2.7v8z"/>' },
    instagram: { label: "Instagram", svg: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/>' },
    tiktok: { label: "TikTok", svg: '<path fill="currentColor" stroke="none" d="M16.2 2.5c.3 2.3 1.6 3.8 3.9 4v3.1a7 7 0 0 1-3.9-1.2v6.3a5.9 5.9 0 1 1-5.9-5.9h.6v3.2a2.7 2.7 0 1 0 2.1 2.7V2.5z"/>' },
    linkedin: { label: "LinkedIn", svg: '<path fill="currentColor" stroke="none" d="M4.6 8.6h3.1V20H4.6zM6.2 3.6a1.8 1.8 0 1 1 0 3.6 1.8 1.8 0 0 1 0-3.6zM9.9 8.6h3v1.6c.4-.8 1.5-1.8 3.1-1.8 3.3 0 3.9 2.2 3.9 5V20h-3.1v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9V20H9.9z"/>' },
    whatsapp: { label: "WhatsApp", svg: '<path d="M12 2.2a9.8 9.8 0 0 0-8.4 14.8L2.3 21.7l4.8-1.3A9.8 9.8 0 1 0 12 2.2z"/><path fill="currentColor" stroke="none" d="M8.6 7.3c.2-.4.4-.4.7-.4h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .6l-.5.7c-.1.2-.2.3 0 .6.5.9 1.2 1.6 2 2.1.3.2.5.1.6 0l.7-.8c.2-.2.3-.2.6-.1l1.8.9c.3.1.4.2.4.4 0 .6-.2 1.3-.7 1.7-.6.5-1.5.7-2.6.3a10 10 0 0 1-5-4.4c-.7-1.2-.6-2.4.1-3z"/>' }
  };

  function whatsappUrl() {
    let digits = String(CFG.phone || "").replace(/\D/g, "");
    if (digits.startsWith("0")) digits = "33" + digits.slice(1); // French local number -> international
    return digits ? "https://wa.me/" + digits : "";
  }

  function renderSocial() {
    const links = CFG.social || {};
    const html = Object.keys(SOCIAL).map((key) => {
      const url = key === "whatsapp" ? (links.whatsapp ? whatsappUrl() : "") : links[key];
      if (!url) return "";
      return `<a href="${url}" target="_blank" rel="noopener" aria-label="${SOCIAL[key].label}" title="${SOCIAL[key].label}"><svg viewBox="0 0 24 24">${SOCIAL[key].svg}</svg></a>`;
    }).join("");
    $$("[data-social]").forEach((el) => { el.innerHTML = html; });
    const wa = $("#waFloat");
    const waUrl = whatsappUrl();
    if (wa) { if (waUrl && links.whatsapp) wa.href = waUrl; else wa.remove(); }
  }
  renderSocial();

  /* ================= Language ================= */
  let lang = "fr";
  const t = (k) => {
    const d = window.I18N[lang];
    return d[k] != null ? d[k] : window.I18N.fr[k];
  };
  function readLang() { try { return localStorage.getItem("renova-lang"); } catch (e) { return null; } }
  function saveLang(l) { try { localStorage.setItem("renova-lang", l); } catch (e) { /* private mode */ } }

  function setLang(l) {
    lang = window.I18N[l] ? l : "fr";
    document.documentElement.lang = lang;
    document.title = t("meta.title");
    $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
    $$("[data-i18n-ph]").forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
    $$(".lang button").forEach((b) => b.classList.toggle("active", b.dataset.lang === lang));
    renderServices();
    renderServiceSelect();
    renderCarousel();
    saveLang(lang);
  }

  /* ================= Services ================= */
  const ICONS = [
    '<path d="m15 12-8.4 8.4a2.1 2.1 0 1 1-3-3L12 9"/><path d="m18 15 4-4"/><path d="m21.5 11.5-1.9-1.9a2 2 0 0 1-.6-1.4V7l-2.3-2.3a6 6 0 0 0-4.2-1.7H9l.9.8A6.2 6.2 0 0 1 12 8.4V10l2 2h1.2a2 2 0 0 1 1.4.6l1.9 1.9"/>',
    '<path d="M11 21.7a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7z"/><path d="M12 22V12"/><path d="m3.3 7 7.7 4.7a2 2 0 0 0 2 0L20.7 7"/><path d="m7.5 4.3 9 5.1"/>',
    '<rect x="4" y="3" width="16" height="16" rx="1.5"/><path d="M12 3v16M10 10v2M14 10v2M6 19v2M18 19v2"/>',
    '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.4 2.4 0 0 1 0-3.4l2.6-2.6a2.4 2.4 0 0 1 3.4 0z"/><path d="m14.5 12.5 2-2M11.5 9.5l2-2M8.5 6.5l2-2M17.5 15.5l2-2"/>',
    '<path d="M12 2.7s6 6.2 6 11.3a6 6 0 0 1-12 0c0-5.1 6-11.3 6-11.3z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
    '<path d="M12 22v-5M9 8V2M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8z"/>',
    '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6M10 22h4"/>'
  ];

  function renderServices() {
    const grid = $("#svcGrid");
    const list = t("services");
    grid.innerHTML = list.map((s, i) => `
      <article class="svc tilt reveal">
        <div class="svc-ico"><svg viewBox="0 0 24 24">${ICONS[i]}</svg></div>
        <h3>${s.t}</h3>
        <ul>${s.items.map((it) => `<li>${it}</li>`).join("")}</ul>
      </article>`).join("") + `
      <article class="svc more tilt reveal">
        <div><h3>${t("svc.more.t")}</h3><p>${t("svc.more.d")}</p></div>
        <a href="#contact" class="btn btn-gold btn-sm">${t("svc.more.b")}<svg class="arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      </article>`;
    $$(".reveal", grid).forEach((el, i) => {
      el.style.transitionDelay = (i % 4) * 0.08 + "s";
      if (grid.dataset.seen) el.classList.add("in"); else revealIO.observe(el);
    });
  }

  function renderServiceSelect() {
    const sel = $("#serviceSelect");
    const keep = sel.selectedIndex;
    sel.innerHTML = `<option value="">${t("f.choose")}</option>` +
      t("services").map((s) => `<option>${s.t}</option>`).join("") +
      `<option>${t("f.other")}</option>`;
    if (keep > 0) sel.selectedIndex = keep;
  }

  /* ================= Reveal ================= */
  const revealIO = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      const grid = e.target.closest("#svcGrid");
      if (grid) grid.dataset.seen = "1";
      revealIO.unobserve(e.target);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

  function setupReveal() {
    [".who-grid", ".steps", ".promise-list"].forEach((g) => {
      $$(g + " .reveal").forEach((el, i) => { el.style.transitionDelay = i * 0.1 + "s"; });
    });
    $$(".reveal").forEach((el) => {
      if (el.closest(".hero")) return;
      if (!el.closest("#svcGrid")) revealIO.observe(el);
    });
    // hero: reveal immediately with a stagger
    $$(".hero .reveal").forEach((el, i) => {
      el.style.transitionDelay = 0.15 + i * 0.12 + "s";
      requestAnimationFrame(() => el.classList.add("in"));
    });
    // clear stagger once shown, so hover effects stay snappy
    document.addEventListener("transitionend", (e) => {
      if (e.propertyName === "opacity" && e.target.classList && e.target.classList.contains("in")) {
        e.target.style.transitionDelay = "";
      }
    });
  }

  /* ================= 3D tilt (delegated) ================= */
  if (canHover && !reduceMotion) {
    document.addEventListener("pointermove", (e) => {
      const card = e.target.closest && e.target.closest(".tilt");
      $$(".tilt.tilting").forEach((c) => { if (c !== card) resetTilt(c); });
      if (!card) return;
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width;
      const y = (e.clientY - r.top) / r.height;
      card.classList.add("tilting");
      card.style.setProperty("--ry", ((x - 0.5) * 12).toFixed(2) + "deg");
      card.style.setProperty("--rx", ((0.5 - y) * 12).toFixed(2) + "deg");
      card.style.setProperty("--mx", (x * 100).toFixed(1) + "%");
      card.style.setProperty("--my", (y * 100).toFixed(1) + "%");
    }, { passive: true });
  }
  function resetTilt(c) {
    c.classList.remove("tilting");
    c.style.setProperty("--rx", "0deg");
    c.style.setProperty("--ry", "0deg");
  }

  /* ================= 3D carousel ================= */
  const car = { rot: 0, vel: 0, dragging: false, lastX: 0, auto: true, items: [] };
  const stage = $("#carouselStage");
  const ring = $("#carousel");

  function renderCarousel() {
    const photos = CFG.gallery || [];
    if (!photos.length) { $("#work").style.display = "none"; return; }
    if (!car.items.length) {
      ring.innerHTML = photos.map((p) => `<figure class="car-item"><img src="${p.src}" alt="" loading="lazy" /><span></span></figure>`).join("");
      car.items = $$(".car-item", ring);
    }
    car.items.forEach((el, i) => {
      const cap = photos[i][lang] || photos[i].fr;
      el.querySelector("span").textContent = cap;
      el.querySelector("img").alt = cap;
    });
    layoutCarousel();
  }

  function layoutCarousel() {
    const n = car.items.length;
    if (!n) return;
    const w = ring.offsetWidth;
    car.step = 360 / n;
    car.radius = Math.round(w / 2 / Math.tan(Math.PI / n)) + (w > 260 ? 70 : 40);
    car.items.forEach((el, i) => {
      el.style.transform = `rotateY(${i * car.step}deg) translateZ(${car.radius}px)`;
    });
  }

  function drawCarousel() {
    ring.style.transform = `translateZ(${-car.radius}px) rotateY(${-car.rot}deg)`;
    const n = car.items.length;
    let front = 0, best = 999;
    car.items.forEach((el, i) => {
      let d = ((i * car.step - car.rot) % 360 + 540) % 360 - 180; // -180..180
      const a = Math.abs(d);
      if (a < best) { best = a; front = i; }
      const k = Math.max(0, 1 - a / 180);
      el.style.filter = `brightness(${0.35 + 0.65 * k * k})`;
    });
    const photos = CFG.gallery || [];
    const cap = $("#carCaption");
    if (photos[front] && car.front !== front + lang) {
      car.front = front + lang;
      cap.textContent = photos[front][lang] || photos[front].fr;
    }
    return n;
  }

  function carouselLoop() {
    if (!car.dragging) {
      if (car.target != null) {
        const diff = car.target - car.rot;
        car.rot += diff * 0.12;
        if (Math.abs(diff) < 0.05) { car.rot = car.target; car.target = null; }
      } else {
        car.rot += car.vel;
        car.vel *= 0.95;
        if (car.auto && Math.abs(car.vel) < 0.05 && !reduceMotion) car.rot += 0.08;
      }
    }
    drawCarousel();
  }

  function snapTo(dir) {
    const base = Math.round(car.rot / car.step) * car.step;
    car.target = base + dir * car.step;
    car.vel = 0;
    car.auto = false;
    clearTimeout(car.resume);
    car.resume = setTimeout(() => { car.auto = true; }, 6000);
  }

  if (stage) {
    stage.addEventListener("pointerdown", (e) => {
      if (e.target.closest("button")) return;
      car.dragging = true; car.lastX = e.clientX; car.vel = 0; car.target = null; car.auto = false;
      stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener("pointermove", (e) => {
      if (!car.dragging) return;
      const dx = e.clientX - car.lastX;
      car.lastX = e.clientX;
      car.rot -= dx * 0.25;
      car.vel = -dx * 0.25;
    });
    const end = () => {
      if (!car.dragging) return;
      car.dragging = false;
      clearTimeout(car.resume);
      car.resume = setTimeout(() => { car.auto = true; }, 5000);
    };
    stage.addEventListener("pointerup", end);
    stage.addEventListener("pointercancel", end);
    $("#carPrev").addEventListener("click", () => snapTo(-1));
    $("#carNext").addEventListener("click", () => snapTo(1));
    window.addEventListener("resize", layoutCarousel);
  }

  /* ================= 3D map of France ================= */
  function setupMap() {
    const host = $("#map3d");
    if (!host) return;
    const K = 30.5, LAT0 = 51.4, LON0 = -5.3, CX = 0.695;
    const P = (lon, lat) => [40 + (lon - LON0) * CX * K, 44 + (LAT0 - lat) * K];
    const hex = [[2.37, 51.03], [8.23, 48.97], [7.5, 43.77], [3.17, 42.44], [-1.78, 43.36], [-4.75, 48.2]].map((c) => P(...c));
    const poly = hex.map((p) => p.map((v) => v.toFixed(1)).join(",")).join(" ");
    const [cx, cy] = P(9.1, 42.15);
    const pins = [
      ["Paris", 2.35, 48.86, 1], ["Lille", 3.06, 50.63], ["Strasbourg", 7.75, 48.58], ["Lyon", 4.84, 45.76],
      ["Marseille", 5.37, 43.3], ["Bordeaux", -0.58, 44.84], ["Nantes", -1.55, 47.22], ["Toulouse", 1.44, 43.6]
    ];
    const dots = [[-1.68, 48.11], [-4.49, 48.39], [7.26, 43.7], [3.88, 43.61], [5.04, 47.32], [3.08, 45.78], [0.69, 47.39],
      [1.1, 49.44], [4.03, 49.26], [1.26, 45.83], [6.18, 48.69], [-0.37, 49.18], [0.34, 46.58], [2.3, 49.89], [6.03, 47.24], [5.72, 45.19]];

    const layers = 14;
    let html = "";
    for (let i = layers; i >= 1; i--) {
      const shade = i === 1 ? "#E8C067" : (i < 4 ? "#C99A3A" : "#7d5a1d");
      html += `<svg viewBox="0 0 400 400" style="position:absolute;inset:0;transform:translateZ(${-i * 1.6}px)"><polygon points="${poly}" fill="${shade}" stroke="${shade}" stroke-width="2" stroke-linejoin="round"/><ellipse cx="${cx}" cy="${cy}" rx="6" ry="14" transform="rotate(12 ${cx} ${cy})" fill="${shade}"/></svg>`;
    }
    html += `<svg viewBox="0 0 400 400" style="position:absolute;inset:0;transform:translateZ(-60px)" class="map-shadow"><polygon points="${poly}" fill="#000"/></svg>`;
    html += `<svg viewBox="0 0 400 400" style="position:absolute;inset:0">
      <defs>
        <linearGradient id="mapTop" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2d3034"/><stop offset="1" stop-color="#191b1e"/></linearGradient>
        <pattern id="mapDots" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M16 0H0V16" fill="none" stroke="rgba(232,192,103,.13)" stroke-width=".6"/></pattern>
        <clipPath id="mapClip"><polygon points="${poly}"/></clipPath>
      </defs>
      <polygon points="${poly}" fill="url(#mapTop)" stroke="#E8C067" stroke-width="1.6" stroke-linejoin="round"/>
      <rect width="400" height="400" fill="url(#mapDots)" clip-path="url(#mapClip)"/>
      <ellipse cx="${cx}" cy="${cy}" rx="6" ry="14" transform="rotate(12 ${cx} ${cy})" fill="url(#mapTop)" stroke="#E8C067" stroke-width="1.4"/>
      ${dots.map(([lo, la], i) => { const [x, y] = P(lo, la); return `<circle class="city-dot" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.6" opacity=".7"/><circle class="city-pulse" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3" style="animation-delay:${(i * 0.37) % 2.6}s"/>`; }).join("")}
    </svg>`;
    html += pins.map(([name, lo, la, main]) => {
      const [x, y] = P(lo, la);
      return `<div class="pin${main ? " main" : ""}" style="left:${x / 4}%;top:${y / 4}%"><div class="pin-up"><span class="pin-label">${name}</span><span class="pin-head"></span><span class="pin-stem"></span></div><span class="pin-base"></span></div>`;
    }).join("");
    host.innerHTML = html;

    const st = $("#mapStage");
    if (canHover && !reduceMotion) {
      st.addEventListener("pointermove", (e) => {
        const r = st.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        host.style.setProperty("--ty", (x * 18).toFixed(2) + "deg");
        host.style.setProperty("--tx", (y * -10).toFixed(2) + "deg");
      });
      st.addEventListener("pointerleave", () => {
        host.style.setProperty("--ty", "0deg");
        host.style.setProperty("--tx", "0deg");
      });
    }
  }

  /* ================= Nav ================= */
  const nav = $("#nav");
  const burger = $("#burger");
  const links = $("#navLinks");
  burger.addEventListener("click", () => { burger.classList.toggle("open"); links.classList.toggle("open"); });
  $$("a", links).forEach((a) => a.addEventListener("click", () => { burger.classList.remove("open"); links.classList.remove("open"); }));
  const onScroll = () => nav.classList.toggle("scrolled", scrollY > 30);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ================= Form → email ================= */
  $("#quoteForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const f = e.target;
    const name = f.name.value.trim();
    const email = f.email.value.trim();
    const msg = f.message.value.trim();
    const okMail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    f.name.classList.toggle("invalid", !name);
    f.email.classList.toggle("invalid", !okMail);
    f.message.classList.toggle("invalid", !msg);
    const note = $("#formNote");
    if (!name || !okMail || !msg) { note.textContent = t("f.err"); note.style.color = "#e57373"; return; }
    note.textContent = t("f.note"); note.style.color = "";
    const type = t("f.type." + f.type.value);
    const service = f.service.value;
    const tel = f.tel.value.trim();
    const city = f.city.value.trim();
    const lines = [
      `${t("f.type")}: ${type}`,
      `${t("f.name")}: ${name}`,
      tel ? `${t("f.phone")}: ${tel}` : null,
      `${t("f.email")}: ${email}`,
      city ? `${t("f.city")}: ${city}` : null,
      service ? `${t("f.service")}: ${service}` : null,
      "",
      msg
    ].filter((l) => l !== null);
    const subject = `${t("f.subject")} – ${service || type} – ${name}`;
    location.href = `mailto:${CFG.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
  });

  $("#year").textContent = new Date().getFullYear();

  /* ================= Boot ================= */
  setupReveal();
  setupMap();
  const urlLang = new URLSearchParams(location.search).get("lang");
  setLang(urlLang || readLang() || "fr");
  $$(".lang button").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));

  let carVisible = false;
  if (stage) new IntersectionObserver((en) => { carVisible = en[0].isIntersecting; }).observe(stage);
  (function loop() {
    if (carVisible && car.items.length) carouselLoop();
    requestAnimationFrame(loop);
  })();
})();
