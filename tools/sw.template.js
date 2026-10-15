/* Breviarium Romanum — service worker */
const VERSION='__VERSION__';
const SHELL=['./','index.html','manifest.json','icon-32.png','icon-180.png','icon-192.png','icon-512.png',__FONTS__];
const DATA=__DATA__;
const CACHE='brev-'+VERSION;
self.addEventListener('install',e=>{
  e.waitUntil((async()=>{
    const c=await caches.open(CACHE);
    await c.addAll(SHELL);
    // datos: en lotes para no saturar conexiones móviles
    for(let i=0;i<DATA.length;i+=8){await Promise.all(DATA.slice(i,i+8).map(u=>c.add(u).catch(()=>{})))}
    self.skipWaiting();
  })());
});
self.addEventListener('activate',e=>{
  e.waitUntil((async()=>{
    for(const k of await caches.keys())if(k!==CACHE)await caches.delete(k);
    await self.clients.claim();
  })());
});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=='GET'||u.origin!==location.origin)return;
  // index.html: red primero (para recibir actualizaciones), caché si no hay conexión
  if(e.request.mode==='navigate'){
    e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(CACHE).then(c=>c.put('index.html',cp));return r}).catch(()=>caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request).then(res=>{
    if(res.ok){const cp=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cp))}return res})));
});
self.addEventListener('notificationclick',e=>{
  e.notification.close();
  const url=(e.notification.data&&e.notification.data.url)||'#/';
  e.waitUntil((async()=>{
    const all=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    for(const c of all){if('focus' in c){c.postMessage({url});return c.focus()}}
    return self.clients.openWindow('./'+url);
  })());
});
