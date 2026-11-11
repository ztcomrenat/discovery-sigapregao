(() => {
  const out = [];
  const sel = 'a,button,input,select,textarea,[role=button],[role=tab],[role=menuitem],[role=option],[data-v-app] [class*=btn]';
  document.querySelectorAll(sel).forEach((el, i) => {
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) return;
    out.push({
      i, tag: el.tagName, role: el.getAttribute('role'),
      type: el.getAttribute('type'), label: (el.getAttribute('aria-label') || '').slice(0,120),
      text: (el.innerText || '').replace(/\s+/g,' ').trim().slice(0,120),
      href: el.getAttribute('href'), disabled: el.disabled === true,
      cls: (el.className || '').toString().slice(0,160),
      x: Math.round(r.x), y: Math.round(r.y)
    });
  });
  return JSON.stringify(out);
})()