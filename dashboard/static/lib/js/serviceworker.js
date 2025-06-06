const CACHE_NAME = 'pwa-cache-v1';
const urlsToCache = [
  '/',                    // homepage
  '/offline/',            // fallback page
  '/static/css/styles.css',
  '/static/js/app.js',
  // Add more URLs as needed
];

// Install event: cache required assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting();
});

// Activate event: cleanup old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event: serve cached content if offline
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request).then(response => {
        // fallback to offline page for HTML requests
        if (!response && event.request.headers.get('accept')?.includes('text/html')) {
          return caches.match('/offline/');
        }
        return response;
      });
    })
  );
});
