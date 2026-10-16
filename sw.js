/* Breviarium Romanum — service worker */
const VERSION='0c20a73a';
const SHELL=['./','index.html','manifest.json','icon-32.png','icon-180.png','icon-192.png','icon-512.png',"fonts/cormorant-sc-latin-500-normal.woff2","fonts/cormorant-sc-latin-600-normal.woff2","fonts/eb-garamond-latin-400-italic.woff2","fonts/eb-garamond-latin-400-normal.woff2","fonts/eb-garamond-latin-600-normal.woff2","fonts/eb-garamond-latin-ext-400-italic.woff2","fonts/eb-garamond-latin-ext-400-normal.woff2","fonts/eb-garamond-latin-ext-600-normal.woff2"];
const DATA=["data/meta.json", "data/m-2026-10.json", "data/m-2026-11.json", "data/m-2026-12.json", "data/m-2027-01.json", "data/m-2027-02.json", "data/m-2027-03.json", "data/m-2027-04.json", "data/m-2027-05.json", "data/m-2027-06.json", "data/m-2027-07.json", "data/m-2027-08.json", "data/m-2027-09.json", "data/m-2027-10.json", "data/m-2027-11.json", "data/m-2027-12.json", "data/m-2028-01.json", "data/m-2028-02.json", "data/m-2028-03.json", "data/m-2028-04.json", "data/m-2028-05.json", "data/m-2028-06.json", "data/m-2028-07.json", "data/m-2028-08.json", "data/m-2028-09.json", "data/m-2028-10.json", "data/m-2028-11.json", "data/m-2028-12.json", "data/s-0.json", "data/s-1.json", "data/s-10.json", "data/s-2.json", "data/s-3.json", "data/s-4.json", "data/s-5.json", "data/s-6.json", "data/s-7.json", "data/s-8.json", "data/s-9.json"];
const CACHE='brev-'+VERSION;
self.addEventListener('install',e=>{
  e.waitUntil((async()=>{
    const c=await caches.open(CACHE);
    // cache:'reload' evita copiar al caché nuevo una versión antigua guardada por el navegador
    const get=u=>fetch(new Request(u,{cache:'reload'})).then(r=>{if(r.ok)return c.put(u,r)});
    await Promise.all(SHELL.map(get));
    // datos: en lotes para no saturar conexiones móviles
    for(let i=0;i<DATA.length;i+=8){await Promise.all(DATA.slice(i,i+8).map(u=>get(u).catch(()=>{})))}
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
