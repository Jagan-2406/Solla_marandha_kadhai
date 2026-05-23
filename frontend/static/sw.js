const CACHE_NAME = 'tamil-nlp-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js'
];

// Install Service Worker and cache core static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened static assets cache');
        return cache.addAll(ASSETS_TO_CACHE);
      })
  );
});

// Cache-first falling back to network strategy
self.addEventListener('fetch', event => {
  // Do not intercept API requests (like /generate, /save, etc.) or TTS audio files
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/generate') || 
      event.request.url.includes('/save') ||
      event.request.url.includes('/chat') ||
      event.request.url.includes('/variations') ||
      event.request.url.includes('/tts')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return cached response
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
