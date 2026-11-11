"""
Helper functions for state capture - to be used via exec in browser_exec calls.
"""
import json, os, re, time

ELEMENTS_DIR = 'C:/Users/ZT-CH1/discovery/web/elements'
STATES_DIR = 'C:/Users/ZT-CH1/discovery/web/states'
LOG_FILE = 'C:/Users/ZT-CH1/discovery/web/states-log.jsonl'

ROUTE_MAP = {
    'dashboard': '/dashboard',
    'oportunidades': '/oportunidades',
    'meus-negocios': '/meus-negocios',
    'disputa-CN': '/disputa/CN',
    'analise-empresa': '/analise-empresa',
    'analise-mercado': '/analise-mercado',
    'orgaos': '/orgaos',
    'pecas-juridicas': '/pecas-juridicas',
    'minhas-empresas': '/minhas-empresas',
    'produtos-marcas': '/produtos-marcas',
    'minha-agenda': '/minha-agenda',
    'fornec-ia': '/fornec-ia',
    'agente-prospeccao': '/agente-prospeccao',
}

# Keywords to match for interactive elements
BUTTON_KEYWORDS = re.compile(
    r'filtro|filter|menu|exportar|novo|criar|adicionar|editar|excluir|a[çc][ãa]o|configurar|abrir|fechar|opcao|op[çc][õo]es|mais|limpar|aplicar|salvar|cancelar|download|importar',
    re.IGNORECASE
)

def should_capture(el):
    """Check if element is an interactive trigger we want to capture."""
    tag = el.get('tag', '').upper()
    role = el.get('role', '')
    text = el.get('text', '')
    classes = el.get('class', '')
    aria_label = el.get('aria-label', '')
    aria_haspopup = el.get('aria-haspopup', '')
    combined_text = f"{text} {aria_label}".lower()

    # SELECT elements
    if tag == 'SELECT':
        return True
    
    # Elements with dropdown/modal/dialog/popover classes
    if any(kw in classes.lower() for kw in ['dropdown', 'modal', 'dialog', 'popover', 'menu-trigger', 'accordion']):
        return True
    
    # aria-haspopup
    if aria_haspopup and aria_haspopup != 'false':
        return True
    
    # role=tab, role=menuitem
    if role in ('tab', 'menuitem', 'menu'):
        return True
    
    # Buttons with keyword text
    if tag == 'BUTTON' and BUTTON_KEYWORDS.search(combined_text):
        return True
    
    # Links/buttons that look like they open things
    if tag in ('BUTTON', 'A') and any(kw in classes.lower() for kw in ['btn', 'trigger', 'toggle', 'action']):
        if BUTTON_KEYWORDS.search(combined_text):
            return True
    
    return False

def load_elements(slug):
    """Load elements inventory for a route."""
    path = os.path.join(ELEMENTS_DIR, f'{slug}.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get('elements', data.get('items', []))
    return data if isinstance(data, list) else []
