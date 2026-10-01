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
  // Each language is its own static page (/ and /en/), built by tools/build.py.
  const lang = window.I18N[document.documentElement.lang] ? document.documentElement.lang : "fr";
  const t = (k) => {
    const d = window.I18N[lang];
    return d[k] != null ? d[k] : window.I18N.fr[k];
  };

  /* ================= Reveal ================= */
  const revealIO = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      revealIO.unobserve(e.target);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

  function setupReveal() {
    [".who-grid", ".steps", ".promise-list", ".sp-items"].forEach((g) => {
      $$(g + " .reveal").forEach((el, i) => { el.style.transitionDelay = i * 0.1 + "s"; });
    });
    $$(".svc-grid .reveal").forEach((el, i) => { el.style.transitionDelay = (i % 4) * 0.08 + "s"; });
    $$(".reveal").forEach((el) => {
      if (!el.closest(".hero, .sp-hero")) revealIO.observe(el);
    });
    // hero: reveal immediately with a stagger
    $$(".hero .reveal, .sp-hero .reveal").forEach((el, i) => {
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

  /* ================= 3D carousels (photos, reviews) ================= */
  // Each .carousel-stage holds a .carousel ring of .car-item cards, optional .car-prev/.car-next buttons
  // and an optional .carousel-caption that shows the front card's caption.
  function makeCarousel(stage) {
    const ring = $(".carousel", stage);
    const items = $$(".car-item", ring);
    if (!items.length) return null;
    const car = { rot: 0, vel: 0, dragging: false, lastX: 0, auto: true, front: -1, visible: false };
    const caption = $(".carousel-caption", stage);
    const fade = stage.classList.contains("reviews-stage"); // light cards: fade instead of darken

    function layout() {
      const n = items.length;
      const w = ring.offsetWidth;
      car.step = 360 / n;
      car.radius = Math.round(w / 2 / Math.tan(Math.PI / n)) + (w > 260 ? 70 : 40);
      items.forEach((el, i) => { el.style.transform = `rotateY(${i * car.step}deg) translateZ(${car.radius}px)`; });
    }
    function draw() {
      ring.style.transform = `translateZ(${-car.radius}px) rotateY(${-car.rot}deg)`;
      let front = 0, best = 999;
      items.forEach((el, i) => {
        const a = Math.abs(((i * car.step - car.rot) % 360 + 540) % 360 - 180);
        if (a < best) { best = a; front = i; }
        const k = Math.max(0, 1 - a / 180);
        if (fade) el.style.opacity = (0.18 + 0.82 * k * k).toFixed(3);
        else el.style.filter = `brightness(${0.35 + 0.65 * k * k})`;
      });
      if (caption && car.front !== front) {
        car.front = front;
        const it = items[front];
        caption.textContent = it.dataset.caption || (it.querySelector("figcaption") || it).textContent;
      }
    }
    function tick() {
      if (!car.visible) return;
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
      draw();
    }
    function pauseAuto(ms) {
      car.auto = false;
      clearTimeout(car.resume);
      car.resume = setTimeout(() => { car.auto = true; }, ms);
    }
    function snapTo(dir) {
      const base = Math.round(car.rot / car.step) * car.step;
      car.target = base + dir * car.step;
      car.vel = 0;
      pauseAuto(6000);
    }

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
      pauseAuto(5000);
    };
    stage.addEventListener("pointerup", end);
    stage.addEventListener("pointercancel", end);
    const prev = $(".car-prev", stage), next = $(".car-next", stage);
    if (prev) prev.addEventListener("click", () => snapTo(-1));
    if (next) next.addEventListener("click", () => snapTo(1));
    window.addEventListener("resize", layout);
    new IntersectionObserver((en) => { car.visible = en[0].isIntersecting; }).observe(stage);
    layout();
    draw();
    return { tick };
  }

  const carousels = [];
  function setupCarousels() {
    $$(".carousel-stage").forEach((stage) => {
      const c = makeCarousel(stage);
      if (c) carousels.push(c);
    });
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
      ["Bagnolet · Paris", 2.42, 48.87, 1], ["Lille", 3.06, 50.63], ["Strasbourg", 7.75, 48.58], ["Lyon", 4.84, 45.76],
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
  if (burger && links) {
    burger.addEventListener("click", () => { burger.classList.toggle("open"); links.classList.toggle("open"); });
    $$("a", links).forEach((a) => a.addEventListener("click", () => { burger.classList.remove("open"); links.classList.remove("open"); }));
  }
  const onScroll = () => nav && nav.classList.toggle("scrolled", scrollY > 30);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ================= Form → email ================= */
  const form = $("#quoteForm");
  if (form) form.addEventListener("submit", (e) => {
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
    const openMailApp = () => {
      location.href = `mailto:${CFG.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
    };
    if (!CFG.web3formsKey) { openMailApp(); return; }

    // send directly through Web3Forms → arrives by email, no email app needed
    form.classList.add("sending");
    const sendLabel = $("#formSend span");
    const label = sendLabel.textContent;
    sendLabel.textContent = t("f.sending");
    fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        access_key: CFG.web3formsKey,
        subject,
        from_name: "RENOVA MM – site web",
        name,
        email,
        replyto: email,
        [t("f.type")]: type,
        [t("f.phone")]: tel || "–",
        [t("f.city")]: city || "–",
        [t("f.service")]: service || "–",
        message: msg,
        page: location.href,
        botcheck: f.botcheck.checked
      })
    })
      .then((r) => r.json().catch(() => ({})).then((d) => ({ ok: r.ok && d.success !== false })))
      .then(({ ok }) => {
        if (!ok) throw new Error("send failed");
        form.reset();
        $("#formSuccess").hidden = false;
      })
      .catch(() => {
        note.textContent = t("f.fail");
        note.style.color = "#e57373";
        setTimeout(openMailApp, 1200);
      })
      .finally(() => {
        form.classList.remove("sending");
        sendLabel.textContent = label;
      });
  });
  const again = $("#formAgain");
  if (again) again.addEventListener("click", () => {
    $("#formSuccess").hidden = true;
    const note = $("#formNote");
    note.textContent = t("f.note");
    note.style.color = "";
  });

  $$("#year").forEach((el) => { el.textContent = new Date().getFullYear(); });

  /* ================= Boot ================= */
  setupReveal();
  setupMap();
  setupCarousels();

  (function loop() {
    carousels.forEach((c) => c.tick());
    requestAnimationFrame(loop);
  })();
})();
