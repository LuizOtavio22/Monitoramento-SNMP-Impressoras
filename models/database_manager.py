
import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, nome_banco='historico.db'):
        self.nome_banco = nome_banco
        self._criar_tabelas()

    def _conectar(self):
        return sqlite3.connect(self.nome_banco)

    def _criar_tabelas(self):
        """Cria a estrutura inicial da base de dados caso não exista."""
        conexao = self._conectar()
        cursor = conexao.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS leituras_impressoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data_leitura DATETIME, ip_impressora TEXT, 
            setor TEXT, modelo TEXT, peca TEXT, nivel_porcentagem INTEGER, 
            folhas_restantes INTEGER, contador_paginas INTEGER, numero_serie TEXT)''')
            
        cursor.execute('''CREATE TABLE IF NOT EXISTS estoque_pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, modelo TEXT, peca TEXT, quantidade INTEGER)''')
            
        cursor.execute('''CREATE TABLE IF NOT EXISTS historico_trocas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ip_impressora TEXT, setor TEXT, 
            modelo TEXT, peca TEXT, data_troca DATETIME)''')
            
        conexao.commit()
        conexao.close()

    def obter_primeira_e_ultima_leitura(self, ip):
        """Calcula a média de consumo baseada na primeira e última leitura registada."""
        conexao = self._conectar()
        cursor = conexao.cursor()
        
        cursor.execute('''SELECT data_leitura, contador_paginas FROM leituras_impressoras 
            WHERE ip_impressora = ? AND contador_paginas IS NOT NULL AND contador_paginas > 0
            ORDER BY data_leitura ASC LIMIT 1''', (ip,))
        primeira = cursor.fetchone()
        
        cursor.execute('''SELECT data_leitura, contador_paginas FROM leituras_impressoras 
            WHERE ip_impressora = ? AND contador_paginas IS NOT NULL AND contador_paginas > 0
            ORDER BY data_leitura DESC LIMIT 1''', (ip,))
        ultima = cursor.fetchone()
        
        conexao.close()
        return primeira, ultima

    def obter_ultimo_nivel_peca(self, ip, peca):
        conexao = self._conectar()
        cursor = conexao.cursor()
        cursor.execute('''SELECT nivel_porcentagem FROM leituras_impressoras 
            WHERE ip_impressora = ? AND peca = ? ORDER BY data_leitura DESC LIMIT 1''', (ip, peca))
        resultado = cursor.fetchone()
        conexao.close()
        return resultado[0] if resultado else None

    def salvar_leitura(self, data, ip, setor, modelo, peca, nivel, folhas_restantes, contador, serial):
        conexao = self._conectar()
        cursor = conexao.cursor()
        cursor.execute('''INSERT INTO leituras_impressoras 
            (data_leitura, ip_impressora, setor, modelo, peca, nivel_porcentagem, folhas_restantes, contador_paginas, numero_serie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (data, ip, setor, modelo, peca, nivel, folhas_restantes, contador, serial))
        conexao.commit()
        conexao.close()

    def obter_estoque_real(self):
        conexao = self._conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT modelo, peca, quantidade FROM estoque_pecas")
        estoque = {(m, p): q for m, p, q in cursor.fetchall()}
        conexao.close()
        return estoque