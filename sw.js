// 오프라인에서도 마지막으로 본 메뉴가 열리게 합니다. menu.json은 항상 새로 받아오고, 실패하면 저장본을 씁니다.
const C="segos-menu-v2";
const SHELL=["./","index.html","manifest.webmanifest","icon-192.png","icon-512.png","icon-180.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)));self.skipWaiting();});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener("fetch",e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=="GET"||u.origin!==location.origin) return;
  e.respondWith(fetch(e.request).then(r=>{
    const copy=r.clone(); const key=u.pathname.endsWith("menu.json")?new Request(u.origin+u.pathname):e.request;
    caches.open(C).then(c=>c.put(key,copy)); return r;
  }).catch(()=>caches.match(u.pathname.endsWith("menu.json")?new Request(u.origin+u.pathname):e.request)));
});
