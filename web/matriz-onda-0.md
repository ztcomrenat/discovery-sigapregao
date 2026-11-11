# Matriz Funcional — Onda 0 (Auth & Onboarding)

| # | Slug | URL final | Redirect? | Heading | Inputs | Botões | Links relevantes | Gate? | Notas |
|---|------|-----------|-----------|---------|--------|--------|-----------------|-------|-------|
| 1 | login | /login | — | "Entrar" | email `username` (placeholder: "Seu e-mail cadastrado") | "Continuar", "Fazer login com a Apple" | → /cadastro ("Criar conta"), mailto:suporte | — | Fluxo magic-link ou senha em etapa 2; login Apple como alternativa |
| 2 | cadastro | /cadastro | — | "Criar sua conta" | text `name`, email `email`, tel `tel`, checkbox (aceite termos) | "Criar conta" | → /termos-de-uso, /politica-de-privacidade, /login ("Entrar") | — | Requer aceite de Termos + Política; campos: nome, e-mail, telefone |
| 3 | recuperar-senha | /recuperar-senha | — | "Recuperar acesso" | email `username` | "Enviar" | → /login ("Entrar") | — | Envia link de recuperação por e-mail |
| 4 | redefinir-senha | /redefinir-senha | — | "Redefinir acesso" | password `password`, password `passwordConfirm` | "Mostrar", "Enviar" | mailto:suporte | — | Precisa de token na URL (vindo do e-mail); campos senha + confirmação |
| 5 | primeiro-acesso | /primeiro-acesso | — | "Primeiro acesso" | password `password`, password `passwordConfirm` | "Mostrar", "Enviar" | → /login ("Entrar") | — | Definição de senha para primeiro acesso (link do e-mail de convite) |
| 6 | planos | /planos | — | "Assine o SIGA Pregão e comece hoje mesmo" | — | "Assinar por — Disponível no app iOS" | → /, /termos-de-uso, /politica-de-privacidade | **GATE** | Upsell: Módulo Oportunidade + Módulo Meus Negócios. Assinatura via iOS app. Sem input de cartão no web. |
| 7 | termos-de-uso | /termos-de-uso | — | "Termos e Condições de Uso" | — | — | → /, gov.br/compras, mailto:suporte | — | Documento legal. Seções: Serviços Oferecidos, etc. Refs: Comprasnet (gov.br) |
| 8 | politica-de-privacidade | /politica-de-privacidade | — | "Política de Privacidade" | — | — | → /, /termos-de-uso | — | Documento legal. Seção sobre Cookies. |
| 9 | aceitar-termos | /login?reason=expired | **→ login** | "Entrar" (redirect) | email `username` | "Continuar", "Fazer login com a Apple" | → /cadastro?redirect=/aceitar-termos | **AUTH-GATE** | Rota protegida: redireciona para login com reason=expired. Após login, retorna para aceite de termos. |
| 10 | reative-assinatura | /reative-assinatura | — | "Reative sua assinatura do SIGA Pregão" | — | "Sair" | WhatsApp (5561998417005) | **GATE-UPSELL** | Tela de bloqueio: assinatura expirada. Ação: contato via WhatsApp para reativar. Botão "Sair" desloga. |
| 11 | ative-assinatura | /ative-assinatura | — | "Chegou a hora de ativar sua assinatura SIGA PREGÃO." | — | "Sair" | WhatsApp (5561998417005) | **GATE-UPSELL** | Tela de bloqueio: conta sem assinatura ativa. Ação: contato via WhatsApp. Botão "Sair" desloga. |

## Resumo de Gates

| Gate | Rota | Tipo | Mecanismo |
|------|------|------|-----------|
| AUTH-GATE | /aceitar-termos | Sessão expirada | Redirect → /login?reason=expired, preserva redirect back |
| GATE-UPSELL | /planos | Paywall | Tela de planos, assinatura apenas via iOS app |
| GATE-UPSELL | /reative-assinatura | Assinatura expirada | Bloqueio total, contato WhatsApp (61) 99841-7005 |
| GATE-UPSELL | /ative-assinatura | Sem assinatura | Bloqueio total, contato WhatsApp (61) 99841-7005 |

## Fluxo de Auth identificado

```
[/login] ─ email ─→ [etapa 2: senha ou magic-link]
   │                        │
   ├─ Apple Sign-In         ├─→ [/dashboard] (sucesso)
   │                        │
   └─ /cadastro ────────────┤
       (nome, email, tel,   │
        aceite termos)       │
                             │
[/recuperar-senha] ─ email → link no e-mail → [/redefinir-senha?token=xxx]
[/primeiro-acesso?token=xxx] → define senha → [/dashboard]
```

## Arquivos gerados

- `routes/*.html` — HTML completo de cada rota (11 arquivos)
- `routes/*.png` — Screenshot de cada rota (11 arquivos)
- `net/*.json` — Requests capturados pelo interceptor (11 arquivos)
- `matriz-onda-0.md` — Esta matriz
