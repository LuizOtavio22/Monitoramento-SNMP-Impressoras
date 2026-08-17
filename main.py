import webbrowser
import os
import asyncio
import requests
from services.snmp_service import SNMPService
from models.database_manager import DatabaseManager
from views.dashboard_view import DashboardView
from datetime import datetime
import config


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": config.CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

def classificar_modelo(descricao_snmp):
    desc = descricao_snmp.upper() if descricao_snmp else ""
    if "M5270" in desc or "5370" in desc or "722" in desc: return "Lexmark M5270"
    elif "M3350" in desc: return "Lexmark M3350"
    elif "1246" in desc: return "Lexmark 1246"
    elif "KONICA" in desc or "BIZHUB" in desc: return "Konica"
    else: return "Lexmark M5270" 

def traduzir_para_estoque(nome_sujo):
    n = nome_sujo.lower()
    if any(x in n for x in ["waste", "residuos"]): return "Caixa de Manutenção (Resíduos)"
    if any(x in n for x in ["maintenance", "kit", "fuser"]): return "Kit de Manutenção (Fusor/Roletes)"
    if any(x in n for x in ["drum", "cilindro"]): return "Unidade de Imagem (Cilindro)"
    if "cyan" in n: return "Tinta Ciano (Azul)"
    if "magenta" in n: return "Tinta Magenta (Rosa)"
    if "yellow" in n: return "Tinta Amarelo"
    return "Toner / Tinta Preto"



async def rodar_erp():
    agora_completo = datetime.now()
    agora_str = agora_completo.strftime("%d/%m/%Y às %H:%M:%S")
    data_banco = agora_completo.strftime("%Y-%m-%d %H:%M:%S") 
    
    print("🚀 Iniciando Motor ERP (Clean Architecture)...")
    
    
    db = DatabaseManager()
    snmp = SNMPService()
    
    alertas_telegram = []
    html_blocos = ""
    html_hoje = ""
    demanda_virtual = {} 

    for ip, setor in config.IMPRESSORAS:
        try:
            # 1. Busca info física na rede (Isolado no snmp_service)
            desc_modelo, serial, contador_total = await snmp.obter_info_basica(ip)
            if not desc_modelo: continue
            modelo_oficial = classificar_modelo(desc_modelo)

            # 2. Busca histórico no banco (Isolado no database_manager)
            primeira, ultima = db.obter_primeira_e_ultima_leitura(ip)
            media_diaria = 0
            texto_media = "Analisando..."
            
            if primeira and ultima:
                dt_primeira = datetime.strptime(primeira[0], "%Y-%m-%d %H:%M:%S")
                dt_ultima = datetime.strptime(ultima[0], "%Y-%m-%d %H:%M:%S")
                dias_passados = (dt_ultima - dt_primeira).days
                if dias_passados >= 1:
                    media_diaria = (ultima[1] - primeira[1]) / dias_passados
                    texto_media = f"{int(media_diaria)} pág/dia"

            linhas_sub_tabela = ""
            status_geral = "success"

            for idx in range(1, 16):
                # Busca peça a peça na rede
                nome, max_cap, atual = await snmp.obter_niveis_suprimentos(ip, idx)
                if not nome or max_cap <= 0: continue
                
                nome_limpo = nome[:30]
                porcentagem = int((atual / max_cap) * 100)
                
                # Regra de negócio: Salvar a leitura no banco
                db.salvar_leitura(data_banco, ip, setor, modelo_oficial, nome_limpo, porcentagem, 0, contador_total, serial)
                
                # --- Lógica de Alertas e Estoque ---
                if porcentagem <= 20:
                    status_geral = "warning"
                    nome_estoque = traduzir_para_estoque(nome_limpo)
                    chave_estoque = (modelo_oficial, nome_estoque)
                    if chave_estoque not in demanda_virtual: demanda_virtual[chave_estoque] = []
                    demanda_virtual[chave_estoque].append(f"▸ {setor} ({porcentagem}%)")
                    
                if porcentagem <= 10:
                    status_geral = "danger"

                linhas_sub_tabela += f"<tr><td>{nome_limpo}</td><td>{porcentagem}%</td><td>{texto_media}</td></tr>"

            if linhas_sub_tabela:
                id_linha = f"detalhe_{ip.replace('.', '_')}"
                html_blocos += f"""
                <tr class="printer-row" data-status="{status_geral}" onclick="toggleDetail('{id_linha}')">
                    <td><strong>{setor}</strong></td><td>{modelo_oficial} (IP: {ip})</td><td>Status</td>
                </tr>
                <tr id="{id_linha}" style="display:none;"><td colspan="3"><table>{linhas_sub_tabela}</table></td></tr>
                """
        except Exception as e:
            print(f"Erro ao processar {ip}: {e}")

    
    estoque_real = db.obter_estoque_real()
    html_compras = ""
    
    for (mod, peca), lista in demanda_virtual.items():
        necessidade = len(lista)
        saldo = estoque_real.get((mod, peca), 0) - necessidade
        if saldo < 0:
            html_compras += f"<li class='card-item urgente'>🚨 Faltam {abs(saldo)}x {peca} ({mod})</li>"
        else:
            html_compras += f"<li class='card-item ok'>✅ Suficiente: {peca} ({mod})</li>"

    if not html_compras: html_compras = "<li class='card-item ok'>Nenhuma compra necessária!</li>"
    if not html_hoje: html_hoje = "<li class='card-item ok'>Nenhuma quebra prevista para hoje.</li>"

 
    DashboardView.gerar_html(html_blocos, html_compras, html_hoje, agora_str)
    
    print("✅ Leitura concluída e HTML gerado com sucesso!")
    # Descobre o caminho completo do arquivo e manda o Windows abrir o navegador
    caminho_completo = "file://" + os.path.realpath("dashboard_impressoras.html")
    webbrowser.open(caminho_completo)

if __name__ == '__main__':
    asyncio.run(rodar_erp())