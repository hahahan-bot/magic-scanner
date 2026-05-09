const CACHE = 'scanner-v1';

function dataRootFromSw() {
  return new URL('..', self.location.href).href;
}

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(async c => {
      const root = dataRootFromSw();
      const assets = [
        './index.html',
        './manifest.json',
        './icon-192.png',
        './icon-512.png',
        root + 'relay_universe.json',
        root + 'sp500_universe.json',
      ];
      try {
        await c.addAll(assets);
      } catch (_err) {
        await c.addAll(['./index.html', './manifest.json', './icon-192.png', './icon-512.png']);
      }
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;

  e.respondWith(
    fetch(req)
      .then(res => {
        if (res && res.status === 200) {
          const clone = res.clone();
          caches.open(CACHE).then(cache => cache.put(req, clone));
        }
        return res;
      })
      .catch(() =>
        caches.match(req).then(hit => hit || caches.match(new URL('./index.html', self.location.href)))
      )
  );
});
