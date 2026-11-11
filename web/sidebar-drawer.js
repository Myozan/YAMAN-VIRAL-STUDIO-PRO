/* Accessible responsive sidebar: desktop collapse + mobile drawer */
(() => {
  const root = document.querySelector(".layout");
  const aside = root?.querySelector(":scope > aside");
  const main = root?.querySelector(":scope > main");
  const nav = document.getElementById("sidebarNav");
  if (!root || !aside || !main || !nav) return;

  const isMobile = () => window.matchMedia("(max-width: 760px)").matches;
  const storedCollapsed = () => {
    try { return localStorage.getItem("yaman-sidebar-collapsed") === "1"; }
    catch { return false; }
  };
  let collapsed = storedCollapsed();
  let overlay = document.querySelector(".sidebar-overlay");
  if (!overlay) {
    overlay = document.createElement("button");
    overlay.type = "button";
    overlay.className = "sidebar-overlay";
    overlay.setAttribute("aria-label", "Menüyü kapat");
    overlay.hidden = true;
    document.body.append(overlay);
  }

  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "sidebar-toggle";
  toggle.id = "sidebarToggle";
  toggle.setAttribute("aria-controls", "sidebarPanel");
  toggle.setAttribute("aria-expanded", "true");
  toggle.innerHTML = '<span class="toggle-glyph" aria-hidden="true">‹</span><span class="toggle-text">Menüyü daralt</span>';
  toggle.title = "Menüyü daralt";
  toggle.addEventListener("click", () => {
    if (isMobile()) setDrawer(!root.classList.contains("drawer-open"));
    else setCollapsed(!collapsed);
  });
  aside.id = "sidebarPanel";
  aside.setAttribute("aria-label", "Ana menü");

  const mobileHeader = document.createElement("div");
  mobileHeader.className = "mobile-drawer-head";
  mobileHeader.innerHTML = '<strong>MENÜ</strong><button type="button" class="drawer-close" aria-label="Menüyü kapat">✕</button>';
  aside.prepend(mobileHeader);
  mobileHeader.querySelector("button").addEventListener("click", () => setDrawer(false));

  const brand = aside.querySelector(".brand");
  if (brand) brand.append(toggle);
  const topbar = main.querySelector(".topbar");
  const mobileTrigger = document.createElement("button");
  mobileTrigger.type = "button";
  mobileTrigger.id = "mobileMenuToggle";
  mobileTrigger.className = "mobile-menu-toggle";
  mobileTrigger.innerHTML = '<span aria-hidden="true">☰</span><span>Menü</span>';
  mobileTrigger.setAttribute("aria-label", "Ana menüyü aç");
  mobileTrigger.setAttribute("aria-expanded", "false");
  if (topbar) topbar.prepend(mobileTrigger);
  mobileTrigger.addEventListener("click", () => setDrawer(true));

  function setCollapsed(value) {
    collapsed = Boolean(value);
    root.classList.toggle("sidebar-collapsed", collapsed);
    const expanded = String(!collapsed);
    toggle.setAttribute("aria-expanded", expanded);
    toggle.title = collapsed ? "Menüyü genişlet" : "Menüyü daralt";
    toggle.querySelector(".toggle-glyph").textContent = collapsed ? "›" : "‹";
    toggle.querySelector(".toggle-text").textContent = collapsed ? "Menüyü genişlet" : "Menüyü daralt";
    try { localStorage.setItem("yaman-sidebar-collapsed", collapsed ? "1" : "0"); } catch {}
  }
  function setDrawer(open) {
    const active = Boolean(open) && isMobile();
    root.classList.toggle("drawer-open", active);
    overlay.hidden = !active;
    mobileTrigger.setAttribute("aria-expanded", String(active));
    document.body.classList.toggle("drawer-lock", active);
    if (active) {
      const first = nav.querySelector("a");
      window.setTimeout(() => first?.focus(), 80);
    } else {
      mobileTrigger.focus({ preventScroll: true });
    }
  }

  overlay.addEventListener("click", () => setDrawer(false));
  nav.querySelectorAll("a[data-page]").forEach(link => {
    link.addEventListener("click", () => { if (isMobile()) setDrawer(false); });
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && root.classList.contains("drawer-open")) setDrawer(false);
  });
  window.addEventListener("resize", () => {
    if (!isMobile()) {
      root.classList.remove("drawer-open");
      overlay.hidden = true;
      document.body.classList.remove("drawer-lock");
      setCollapsed(collapsed);
    } else {
      root.classList.remove("sidebar-collapsed");
      toggle.setAttribute("aria-expanded", "true");
    }
  }, { passive: true });
  setCollapsed(collapsed);
})();
