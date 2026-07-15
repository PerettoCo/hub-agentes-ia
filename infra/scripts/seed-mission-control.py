#!/usr/bin/env python3
"""Seed mission_controls no Supabase de memória a partir do banco de dados de produção."""
import os, json, requests, sys

SUPABASE_MEM_URL = os.environ.get('SUPABASE_URL', 'https://bkenzsvexfayjcrqnmpx.supabase.co')
SUPABASE_MEM_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
SUPABASE_DADOS_URL = os.environ.get('SUPABASE_DADOS_URL', 'https://mhntycubvywjszweeuxs.supabase.co')
SUPABASE_DADOS_KEY = os.environ.get('SUPABASE_DADOS_KEY', '')

HEADERS_MEM = {'apikey': SUPABASE_MEM_KEY, 'Authorization': f'Bearer {SUPABASE_MEM_KEY}', 'Content-Type': 'application/json'}
HEADERS_DADOS = {'apikey': SUPABASE_DADOS_KEY, 'Authorization': f'Bearer {SUPABASE_DADOS_KEY}'}

def fetch_dados(table, params='select=*&limit=500'):
    r = requests.get(f'{SUPABASE_DADOS_URL}/rest/v1/{table}?{params}', headers=HEADERS_DADOS)
    return r.json() if r.ok else []

def fetch_dados_by(table, field, value):
    r = requests.get(f'{SUPABASE_DADOS_URL}/rest/v1/{table}?{field}=eq.{value}&limit=50', headers=HEADERS_DADOS)
    return r.json() if r.ok else []

def upsert_mission_control(cliente):
    cid = cliente.get('cardid')
    cname = cliente.get('nomedaempresa') or cliente.get('title', '')
    if not cid or not cname:
        return

    checkins = fetch_dados_by('50TranscricaoCheckin', 'cliente', cname)

    historico = []
    bets = []
    combinados = []
    ultimo_resumo = ''
    ultimo_checkin = None

    for ci in checkins:
        resumo = (ci.get('resumo') or '').strip()
        if resumo and resumo != 'Call vazia' and resumo != 'None':
            historico.append({
                'data': ci.get('criado_em'),
                'resumo': resumo,
                'dores': ci.get('dores_latentes'),
                'riscos': ci.get('riscos_e_obstaculos'),
                'recomendacoes': ci.get('recomendacoes_finais'),
                'oportunidades': ci.get('oportunidades_de_upsell'),
                'aderencia': ci.get('indice_aderencia_ao_roteiro_metodo'),
                'rigor': ci.get('indice_rigor_analitico_dados_conteudo'),
                'lideranca': ci.get('indice_lideranca_gestao_de_expectativa_futuro'),
            })
            ultimo_resumo = resumo
            ultimo_checkin = ci.get('criado_em')

    raiox = {
        'nome': cname,
        'cnpj': cliente.get('cnpj'),
        'cidade': cliente.get('cidade'),
        'uf': cliente.get('uf'),
        'setor': cliente.get('setor'),
        'segmento': cliente.get('segmento'),
        'faturamento': cliente.get('faturamentoanual'),
        'tier': cliente.get('tier'),
        'status': cliente.get('labels'),
        'stakeholder': cliente.get('nomedoprincipalstakeholder'),
        'contato': cliente.get('contatodostakeholder'),
        'email': cliente.get('emaildostakeholder'),
        'modelo_vendas': cliente.get('modelodevendas'),
        'canal_vendas': cliente.get('canaldevendas'),
        'modelo_negocio': cliente.get('modelodenegocio'),
        'closer': cliente.get('nomedocloser'),
        'data_inicio': cliente.get('datadeinicio'),
        'google_drive': cliente.get('google_drive_folder'),
        'ekyte_id': cliente.get('ekyte_id'),
        'contrato_url': cliente.get('contrato_url'),
        'poder_financeiro': cliente.get('poderfinanceiro'),
        'portfolio': cliente.get('portfolio'),
        'nivel_consciencia': cliente.get('nivelconsciencia'),
        'inadimplencia': cliente.get('inadimplencia'),
    }

    guardrails = [
        {'tipo': 'cor_proibida', 'valor': '', 'descricao': 'Cores proibidas da marca (preencher manualmente)'},
        {'tipo': 'tom_voz', 'valor': '', 'descricao': 'Tom de voz definido no brand book'},
        {'tipo': 'termos_proibidos', 'valor': '', 'descricao': 'Termos que não devem ser usados em comunicações'},
        {'tipo': 'segmento_proibido', 'valor': '', 'descricao': 'Segmentos/mercados que não devem ser abordados'},
    ]

    payload = {
        'cliente_id': cid,
        'cliente_nome': cname,
        'dados_raiox': json.dumps(raiox),
        'regras_guardrails': json.dumps(guardrails),
        'historico_resumo': json.dumps(historico[:10], ensure_ascii=False),
        'ultimo_checkin_resumo': ultimo_resumo,
        'ultimo_checkin': ultimo_checkin,
        'updated_at': 'NOW()',
    }

    r = requests.post(f'{SUPABASE_MEM_URL}/rest/v1/mission_controls', headers=HEADERS_MEM, json={
        **{k: v for k, v in payload.items() if k != 'updated_at'},
    })
    if r.status_code == 409:
        r2 = requests.patch(f'{SUPABASE_MEM_URL}/rest/v1/mission_controls?cliente_id=eq.{cid}', headers=HEADERS_MEM, json={
            'dados_raiox': payload['dados_raiox'],
            'historico_resumo': payload['historico_resumo'],
            'ultimo_checkin_resumo': payload['ultimo_checkin_resumo'],
            'ultimo_checkin': ultimo_checkin,
            'updated_at': 'NOW()',
        })
        if r2.ok:
            print(f'  Updated: {cname}')
        else:
            print(f'  Error updating {cname}: {r2.text[:200]}')
    elif r.ok:
        print(f'  Created: {cname}')
    else:
        print(f'  Error creating {cname}: {r.text[:200]}')

def main():
    print('Fetching clients from production DB...')
    clientes = fetch_dados('DBClientes', 'select=*&labels=eq.Atvomite=500')
    clientes2 = fetch_dados('DBClientes', 'select=*&labels=eq.Ativo&limit=500')
    clientes = clientes + [c for c in clientes2 if c not in clientes]
    print(f'Found {len(clientes)} active clients')
    for c in clientes:
        upsert_mission_control(c)
    print('Done.')

if __name__ == '__main__':
    main()
