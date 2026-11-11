(() => {
  if (window.__CAP__) return 'ja injetado';
  window.__CAP__ = { reqs: [], ws: [] };
  const oOpen = XMLHttpRequest.prototype.open, oSend = XMLHttpRequest.prototype.send,
        oHdr = XMLHttpRequest.prototype.setRequestHeader;
  XMLHttpRequest.prototype.open = function(m, u, ...r) {
    this.__c = { method: m, url: u, headers: {}, at: Date.now() };
    return oOpen.call(this, m, u, ...r);
  };
  XMLHttpRequest.prototype.setRequestHeader = function(k, v) {
    if (this.__c) this.__c.headers[k] = v;
    return oHdr.call(this, k, v);
  };
  XMLHttpRequest.prototype.send = function(b) {
    if (this.__c) {
      this.__c.body = typeof b === 'string' ? b.slice(0, 20000) : null;
      this.addEventListener('loadend', () => {
        this.__c.status = this.status;
        try { this.__c.response = (this.responseText || '').slice(0, 50000); } catch (e) {}
        window.__CAP__.reqs.push(this.__c);
      });
    }
    return oSend.call(this, b);
  };
  const oFetch = window.fetch;
  window.fetch = async function(i, n) {
    const rec = { method: (n && n.method) || 'GET',
                  url: typeof i === 'string' ? i : i.url, headers: {}, at: Date.now(),
                  body: n && n.body ? String(n.body).slice(0, 20000) : null };
    const res = await oFetch.apply(this, arguments);
    try { rec.status = res.status; rec.response = (await res.clone().text()).slice(0, 50000); } catch (e) {}
    window.__CAP__.reqs.push(rec);
    return res;
  };
  const OWS = window.WebSocket;
  window.WebSocket = function(u, p) {
    const ws = new OWS(u, p);
    window.__CAP__.ws.push({ dir: 'meta', at: Date.now(), data: 'open ' + u });
    ws.addEventListener('message', e =>
      window.__CAP__.ws.push({ dir: 'in', at: Date.now(), data: String(e.data).slice(0, 5000) }));
    const s = ws.send.bind(ws);
    ws.send = d => { window.__CAP__.ws.push({ dir: 'out', at: Date.now(), data: String(d).slice(0, 5000) }); return s(d); };
    return ws;
  };
  window.WebSocket.prototype = OWS.prototype;
  return 'ok';
})()