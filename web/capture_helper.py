import json, time, random, shutil, os, csv, re

WEB = "C:/Users/ZT-CH1/discovery/web"
INTERCEPTOR = open("C:/Users/ZT-CH1/discovery/interceptor.js").read()
ELEMENTS_JS = open("C:/Users/ZT-CH1/discovery/elements.js").read()

def jitter():
    time.sleep(random.uniform(0.8, 4.5))

def slug_from_path(path):
    """Convert /foo/bar to foo-bar"""
    return path.strip('/').replace('/', '-').replace(':', '-') or 'root'

def capture_route(slug, url, matrix_rows, manifest, retries=3):
    """Full capture protocol for a single route"""
    for attempt in range(retries):
        try:
            jitter()
            goto_url(url)
            time.sleep(random.uniform(2.5, 4.5))
            
            # Check for 429
            status_check = js("document.title")
            if '429' in str(status_check):
                print(f"[{slug}] 429 detected, backing off 30s...")
                time.sleep(30)
                continue
            
            final_url = js("window.location.href")
            
            # Check for login redirect
            if '/login' in final_url and slug != 'login':
                print(f"[{slug}] REDIRECTED TO LOGIN: {final_url}")
                manifest['inaccessible'].append({
                    'slug': slug, 'url': url, 'reason': 'auth_redirect',
                    'final_url': final_url
                })
                return None
            
            # Inject interceptor
            js(INTERCEPTOR)
            time.sleep(1)
            
            # Flush network
            net_data = js("JSON.stringify(window.__CAP__)")
            with open(f"{WEB}/net/{slug}.json", "w", encoding="utf-8") as f:
                f.write(net_data if net_data else '{"reqs":[],"ws":[]}')
            
            # Elements inventory
            elements_json = js(ELEMENTS_JS)
            os.makedirs(f"{WEB}/elements", exist_ok=True)
            with open(f"{WEB}/elements/{slug}.json", "w", encoding="utf-8") as f:
                f.write(elements_json if elements_json else '[]')
            
            # HTML
            html = js("document.documentElement.outerHTML")
            with open(f"{WEB}/routes/{slug}.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            # Screenshot
            png_path = capture_screenshot()
            shutil.copy2(png_path, f"{WEB}/routes/{slug}.png")
            
            # Extract heading
            heading = js("(document.querySelector('h1') || document.querySelector('h2') || {}).innerText || ''")
            
            # Parse elements for classification
            elements = json.loads(elements_json) if elements_json else []
            inputs = [e for e in elements if e.get('tag') in ('INPUT', 'SELECT', 'TEXTAREA')]
            buttons = [e for e in elements if e.get('tag') == 'BUTTON' or e.get('role') == 'button']
            links = [e for e in elements if e.get('tag') == 'A']
            
            # Check for gates
            gate = ''
            body_text = js("document.body.innerText.slice(0, 3000)")
            if any(kw in (body_text or '').lower() for kw in ['upgrade', 'assine', 'plano', 'assinatura necessária']):
                if any(kw in (body_text or '').lower() for kw in ['assine agora', 'fazer upgrade', 'indisponível no seu plano']):
                    gate = 'gate'
            
            # Build matrix row
            row = {
                'slug': slug,
                'url_final': final_url,
                'tipo': 'rota',
                'heading': (heading or '').replace('\n', ' ').strip()[:120],
                'descricao': '',
                'inputs': len(inputs),
                'botoes': len(buttons),
                'links': len(links),
                'gate': gate,
                'notas': ''
            }
            matrix_rows.append(row)
            
            print(f"[{slug}] OK url={final_url} h1='{(heading or '')[:50]}' el={len(elements)} inp={len(inputs)} btn={len(buttons)}")
            return row
            
        except Exception as e:
            print(f"[{slug}] ERROR attempt {attempt+1}: {e}")
            if attempt < retries - 1:
                time.sleep(5)
    
    manifest['inaccessible'].append({'slug': slug, 'url': url, 'reason': 'error_after_retries'})
    return None
