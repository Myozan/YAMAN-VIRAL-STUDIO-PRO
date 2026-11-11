
/* YAMAN VIRAL STUDIO PRO — minimal app-shell service worker */
const CACHE_NAME = "yaman-viral-studio-shell-v1.8.0-premium2";
const APP_SHELL = [
  "/",
  "/assets/manifest.webmanifest",
  "/assets/style.css?v=v180premium2",
  "/assets/app.js?v=v180premium",
  "/assets/favicon.ico",
  "/assets/favicon.svg",
  "/assets/favicon-32.png",
  "/assets/icons/icon-192.svg",
  "/assets/icons/icon-512.svg",
  "/assets/icons/icon-192.png",
  "/assets/icons/icon-512.png",
  "/assets/icons/apple-touch-icon.png",
  "/assets/icons/icon-16.png",
  "/assets/icons/icon-48.png",
  "/assets/sidebar-drawer.css?v=v180premium",
  "/assets/sidebar-drawer.js?v=v180premium",
  "/assets/update-center.js?v=v180premium"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key.startsWith("yaman-viral-studio-") && key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  // API responses and generated/private workspace files must never be cached.
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/workspace/")) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).then(response => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put("/", copy));
        }
        return response;
      }).catch(async () => (await caches.match("/")) || Response.error())
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(response => {
        if (response.ok && response.type === "basic") {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        }
        return response;
      });
    })
  );
});
