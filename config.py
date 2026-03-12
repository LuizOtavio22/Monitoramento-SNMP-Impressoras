
TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"

CAPACIDADE_MAXIMA = {
    "Lexmark M5270": {"Toner Preto": 55000, "Imagem Preto": 150000, "Kit": 225000},
    "Lexmark M3350": {"Toner Preto": 31000, "Imagem Preto": 75000, "Kit": 200000},
    "Lexmark 1246": {"Toner Preto": 25000, "Imagem Preto": 60000, "Kit": 200000}, 
    "Konica": {"Toner Preto": 28000, "Toner Colorido": 26000, "Imagem Preto": 120000, "Imagem Colorida": 90000, "Kit": 300000}, 
    "Epson Grande": {"Toner Preto": 86000, "Toner Colorido": 50000, "Kit": 100000},
    "Epson Pequena": {"Toner Preto": 10000, "Toner Colorido": 5000, "Kit": 60000} 
}

IMPRESSORAS=[
    ("192.168.0.10", "RH - Recrutamento"),
    ("192.168.0.11", "Logística - Galpão A"),
    ("192.168.0.12", "Diretoria Executiva"),
    ("192.168.0.13", "Qualidade e Testes")
]

# --- OIDs DO SNMP (Os endereços das gavetas da MIB) ---
OID_MODELO = '1.3.6.1.2.1.1.1.0'
OID_SERIAL = '1.3.6.1.2.1.43.5.1.1.17.1'
OID_ODOMETRO = '1.3.6.1.2.1.43.10.2.1.4.1.1'