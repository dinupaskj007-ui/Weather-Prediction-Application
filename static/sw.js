const CACHE_NAME = 'sl-weather-v35';
const ASSETS_TO_CACHE = [
  '/',
  '/static/manifest.json',
  '/static/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) {
    return;
  }

  const cache = caches.open(CACHE_NAME);
  const cached = cache.then(store => store.match(request));
  const network = fetch(request);
  event.waitUntil(network.then(response => {
    if (response.ok) {
      const copy = response.clone();
      return cache.then(store => store.put(request, copy));
    }
  }).catch(() => {}));

  if (request.mode === 'navigate') {
    event.respondWith(network.then(async response => response.ok ? response : (await cached) || response)
      .catch(async () => (await cached) || Response.error()));
  } else {
    event.respondWith(cached.then(response => response || network).catch(() => Response.error()));
  }
});
