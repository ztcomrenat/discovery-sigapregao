"""Reusable route capture function for browser_exec sessions."""
import json, time, random, shutil, os

WEB = "C:/Users/ZT-CH1/discovery/web"
BASE = "https://app.sigapregao.com.br"
INTERCEPTOR = open("C:/Users/ZT-CH1/discovery/interceptor.js").read()
ELEMENTS_JS = open("C:/Users/ZT-CH1/discovery/elements.js").read()

ROUTES = [
    "/comprasnet", "/disputa/CN", "/disputa/PCP", "/disputas-maquina-de-lances",
    "/disputas-encerradas", "/logs-maquina-de-lances", "/orgaos", "/historico-compras",
    "/analise-empresa", "/analise-mercado", "/pagometro", "/pecas-juridicas",
    "/contratacao-futura", "/capacidade-pagamento", "/baixa-concorrencia", "/fornec-ia",
    "/agente-prospeccao", "/meus-documentos", "/meus-arquivos", "/minhas-empresas",
    "/produtos-marcas", "/ambientes", "/integracoes", "/b2g-monitor", "/b2g-prospecta",
    "/b2g-leitor", "/b2g-fornecedor", "/b2g-juridico", "/b2g-club", "/conector-ia",
    "/meus-dados", "/suporte", "/regra-plano", "/clientes", "/empresas",
    "/admin/activity-logs", "/admin/access-logs", "/admin/frontend-errors",
    "/request-logs", "/logs", "/feature-flags", "/notificacao-lote",
    "/admin/templates-de-tarefas", "/admin/chamados", "/admin/beta-features",
    "/admin/monitoramento-atas", "/dev/consumo-ia"
]

def slug_from_path(path):
    return path.strip('/').replace('/', '-').replace(':', '-') or 'root'

def capture_one(path):
    """Capture a single route. Returns the progress entry dict."""
    slug = slug_from_path(path)
    url = BASE + path
    entry = {"slug": slug, "url_final": "", "heading": "", "element_count": 0,
             "inputs": 0, "buttons": 0, "links": 0, "gate": "", "error": None}
    
    try:
        # Navigate with jitter
        time.sleep(random.uniform(0.8, 4.5))
        goto_url(url)
        time.sleep(random.uniform(3.0, 5.0))
        
        # Check title for 429
        title = js("document.title") or ""
        if '429' in title:
            print(f"[{slug}] 429 - backing off 30s")
            time.sleep(30)
            goto_url(url)
            time.sleep(random.uniform(3.0, 5.0))
        
        final_url = js("window.location.href") or ""
        entry["url_final"] = final_url
        
        # Auth redirect check
        if '/login' in final_url:
            entry["gate"] = "auth_redirect"
            entry["error"] = "redirected to login"
            _save_progress(entry)
            print(f"[{slug}] AUTH_REDIRECT -> {final_url}")
            return entry
        
        # 403 check
        body_start = js("document.body ? document.body.innerText.slice(0,500) : ''") or ""
        if '403' in title or 'forbidden' in body_start.lower():
            entry["gate"] = "role_block"
            entry["error"] = "403 forbidden"
            _save_progress(entry)
            print(f"[{slug}] ROLE_BLOCK (403)")
            return entry
        
        # Inject interceptor
        js(INTERCEPTOR)
        time.sleep(1)
        
        # Network capture
        net_data = js("JSON.stringify(window.__CAP__)") or '{"reqs":[],"ws":[]}'
        os.makedirs(f"{WEB}/net", exist_ok=True)
        with open(f"{WEB}/net/{slug}.json", "w", encoding="utf-8") as f:
            f.write(net_data)
        
        # Elements
        elements_json = js(ELEMENTS_JS) or '[]'
        os.makedirs(f"{WEB}/elements", exist_ok=True)
        with open(f"{WEB}/elements/{slug}.json", "w", encoding="utf-8") as f:
            f.write(elements_json)
        
        # HTML
        html = js("document.documentElement.outerHTML") or ""
        os.makedirs(f"{WEB}/routes", exist_ok=True)
        with open(f"{WEB}/routes/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Screenshot
        png_path = capture_screenshot()
        shutil.copy2(png_path, f"{WEB}/routes/{slug}.png")
        
        # Heading
        heading = js("(document.querySelector('h1')||document.querySelector('h2')||{}).innerText||''") or ""
        entry["heading"] = heading.replace('\n', ' ').strip()[:120]
        
        # Parse elements
        elements = json.loads(elements_json) if elements_json else []
        entry["element_count"] = len(elements)
        entry["inputs"] = len([e for e in elements if e.get('tag') in ('INPUT','SELECT','TEXTAREA')])
        entry["buttons"] = len([e for e in elements if e.get('tag')=='BUTTON' or e.get('role')=='button'])
        entry["links"] = len([e for e in elements if e.get('tag')=='A'])
        
        # Gate detection
        body_text = js("document.body.innerText.slice(0,3000)") or ""
        bt = body_text.lower()
        if any(kw in bt for kw in ['assine agora', 'fazer upgrade', 'indisponível no seu plano', 'upgrade seu plano']):
            entry["gate"] = "gate"
        elif any(kw in bt for kw in ['em breve', 'coming soon']):
            entry["gate"] = "coming_soon"
        
        _save_progress(entry)
        print(f"[{slug}] OK h1='{entry['heading'][:50]}' el={entry['element_count']} inp={entry['inputs']} btn={entry['buttons']} lnk={entry['links']} gate={entry['gate']}")
        return entry
        
    except Exception as e:
        entry["error"] = str(e)[:200]
        _save_progress(entry)
        print(f"[{slug}] ERROR: {e}")
        return entry

def _save_progress(entry):
    with open(f"{WEB}/progress.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
