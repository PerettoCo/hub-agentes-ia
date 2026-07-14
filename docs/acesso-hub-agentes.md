# Hub de Agentes — Acesso

**Portal de login:** https://ia.fvmarketing.com.br

Turma, segue a lista de usuários e senhas para os primeiros testes.
Nós vamos liberando aos poucos para mensurarmos o uso de recursos
simultâneos com precisão para ampliar de forma progressiva para
garantir a escala.

Estou finalizando uma tela de saída mas por padrão a sessão expira
depois de um tempo ou você pode renovar. Bota ia.fvmarketing.com.br
na barra de endereço.

---

## Usuários e Senhas

| Usuário          | Senha                 | Subdomínio                    |
| ---------------- | --------------------- | ----------------------------- |
| `marcos.luciano` | `P3R3TT0M4RK3T1NGxxx` | marcos.fvmarketing.com.br     |
| `fhelipe.aranha` | `P3R3TT0M4RK3T1NGxxx` | fhelipe.fvmarketing.com.br    |
| `lucas.nunes`    | `P3R3TT0M4RK3T1NGbuf` | lucasnunes.fvmarketing.com.br |
| `paolo.carmine`  | `P3R3TT0M4RK3T1NGmw7` | paolo.fvmarketing.com.br      |
|                  |                       |                               |

---

## Infraestrutura

| Componente       | Tecnologia                           |
| ---------------- | ------------------------------------ |
| Proxy/Auth       | Nginx + Node.js (Express)            |
| Autenticação     | Cookie `connect.sid` + bcrypt        |
| Agente IA        | OpenCode Web (instância por usuário) |
| Proxy de Modelos | LiteLLM                              |
| Modelo padrão    | deepseek-v4-flash-free (ZenCode)     |
| Modelos pagos    | Claude Sonnet 5, GPT 5.4, Gemini     |

*Documento gerado em 13/07/2026 · V4 Company*
