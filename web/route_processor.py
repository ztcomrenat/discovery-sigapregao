"""Route processor - exec'd in browser_exec context. 
Usage: set SLUG and ROUTE before exec'ing this file."""
import json, os, time, re, shutil

ELEMENTS_DIR = 'C:/Users/ZT-CH1/discovery/web/elements'
STATES_DIR = 'C:/Users/ZT-CH1/discovery/web/states'
LOG_FILE = 'C:/Users/ZT-CH1/discovery/web/states-log.jsonl'

BKW = re.compile(r'filtro|filter|menu|exportar|novo|criar|adicionar|editar|excluir|a[çc][ãa]o|configurar|abrir|opcao|op[çc][õo]es|mais|limpar|aplicar|download|importar', re.IGNORECASE)

def sc(el):
    t,r,tx,c,l = el.get('tag','').upper(), el.get('role',''), el.get('text',''), el.get('cls',''), el.get('label','')
    cm = f"{tx} {l}".lower()
    if t == 'SELECT': return True
    if any(k in c.lower() for k in ['dropdown','modal','dialog','popover','menu-trigger','accordion']): return True
    if r in ('tab','menuitem'): return True
    if t == 'BUTTON' and BKW.search(cm): return True
    if t == 'A' and r == 'button' and BKW.search(cm): return True
    return False

def cs():
    return js('''(() => {
        const m=document.querySelector('.modal.show,[role="dialog"],.swal2-popup,.drawer.active,.sidebar-right.active,.ntf,.p-dialog,.p-sidebar');
        const d=document.querySelector('.dropdown-menu.show,[role="listbox"],.p-dropdown-panel,.p-multiselect-panel,.select-dropdown');
        const mn=document.querySelector('[role="menu"]:not([style*="display: none"]),.p-menu.p-menu-overlay');
        const p=document.querySelector('.popover.show,.p-overlaypanel,.tippy-box');
        if(m)return'modal';if(mn)return'menu';if(d)return'dropdown';if(p)return'popover';return'unknown';
    })()''')

def cv():
    return js('''(() => {
        const els=document.querySelectorAll('button,a,input,select,[role="tab"],[role="menuitem"],[role="option"],[role="button"]');
        const r=[];
        for(const el of els){const rect=el.getBoundingClientRect();if(rect.width===0||rect.height===0||rect.top>window.innerHeight||rect.bottom<0)continue;
        r.push({tag:el.tagName,role:el.getAttribute('role'),text:(el.textContent||'').trim().substring(0,100),cls:(el.className||'').toString().substring(0,200),x:Math.round(rect.x),y:Math.round(rect.y),w:Math.round(rect.width),h:Math.round(rect.height)});if(r.length>=80)break;}return r;
    })()''')

def co():
    js("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',code:'Escape',bubbles:true}))")
    time.sleep(0.3)
    cdp('Input.dispatchKeyEvent',type='keyDown',key='Escape',code='Escape',windowsVirtualKeyCode=27)
    cdp('Input.dispatchKeyEvent',type='keyUp',key='Escape',code='Escape',windowsVirtualKeyCode=27)
    time.sleep(0.5)

def process(slug, route):
    goto_url(f'https://app.sigapregao.com.br{route}')
    wait_for_load()
    time.sleep(2.5)
    
    p = os.path.join(ELEMENTS_DIR, f'{slug}.json')
    if not os.path.exists(p):
        print(f"{slug}: no elements file"); return 0
    with open(p,'r',encoding='utf-8-sig') as f: els=json.load(f)
    if not isinstance(els,list): els=els.get('elements',[])
    
    tgts=[e for e in els if sc(e)]
    seen=set(); uniq=[]
    for e in tgts:
        k=(e.get('tag'),(e.get('text','')or e.get('label',''))[:30],e.get('x',0)//20,e.get('y',0)//20)
        if k not in seen: seen.add(k); uniq.append(e)
    uniq=uniq[:10]
    print(f"{slug}: {len(els)} els, {len(tgts)} int, {len(uniq)} dedup")
    
    logs=[]; cap=0
    for tgt in uniq:
        ei=tgt['i']; tx=tgt.get('text','')or tgt.get('label',''); tt=tx[:60] if tx else f"el_{ei}"
        mt=json.dumps((tgt.get('text','')or'')[:40]); ml=json.dumps((tgt.get('label','')or'')[:40])
        ck=js(f'''(()=>{{const all=document.querySelectorAll('button,a,select,[role="tab"],[role="menuitem"],[role="button"]');for(const el of all){{const r=el.getBoundingClientRect();if(r.width<=0||r.height<=0)continue;const t=(el.textContent||'').trim(),l=el.getAttribute('aria-label')||'';if(({mt}&&t.includes({mt}))||({ml}&&l.includes({ml}))){{el.click();return'ok'}}}}return'nf'}})()''')
        if ck=='nf':
            x,y=tgt.get('x',0),tgt.get('y',0)
            if x>0 and y>0: click_at_xy(x+5,y+5)
            else: continue
        time.sleep(1.2)
        st=cs(); ve=cv()
        try:
            sp=capture_screenshot()
            shutil.copy2(sp,os.path.join(STATES_DIR,f'{slug}-{ei}.png'))
        except: pass
        sd={'slug':slug,'element_index':ei,'trigger':tgt,'trigger_text':tt,'state_type':st,'elements_found':len(ve),'elements':ve}
        with open(os.path.join(STATES_DIR,f'{slug}-{ei}.json'),'w',encoding='utf-8') as f: json.dump(sd,f,ensure_ascii=False,indent=2)
        co()
        logs.append({'slug':slug,'element_index':ei,'trigger_text':tt,'trigger_type':tgt.get('tag',''),'state_type':st,'elements_found':len(ve),'closed_with':'escape'})
        cap+=1; print(f"  [{ei}] {st}: {tt[:40]} ({len(ve)} els)")
    with open(LOG_FILE,'a',encoding='utf-8') as f:
        for e in logs: f.write(json.dumps(e,ensure_ascii=False)+'\n')
    print(f"  => {cap} captured"); return cap
