

import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
import config 

class SNMPService:
    def __init__(self):
       
        self.snmp_engine = SnmpEngine()
        self.community = CommunityData('public', mpModel=0)

    async def obter_info_basica(self, ip):
        """Busca o Modelo, Serial e Odômetro (Páginas impressas) da máquina"""
        try:
            target = await UdpTransportTarget.create((ip, 161), timeout=2, retries=1)
            
            resultado = await get_cmd(
                self.snmp_engine, self.community, target, ContextData(),
                ObjectType(ObjectIdentity(config.OID_MODELO)),
                ObjectType(ObjectIdentity(config.OID_SERIAL)),
                ObjectType(ObjectIdentity(config.OID_ODOMETRO))
            )
            
            errIndication, errStatus, errIndex, varBinds = resultado
            
            if not errIndication and not errStatus:
                modelo = str(varBinds[0][1])
                serial = str(varBinds[1][1])
                try: 
                    odometro = int(varBinds[2][1])
                except ValueError: 
                    odometro = 0
                    
                return modelo, serial, odometro
        except Exception as e:
            return None, None, 0
            
        return None, None, 0

    async def obter_niveis_suprimentos(self, ip, index):
        """Busca o nome da peça, capacidade máxima e nível atual baseado no index da gaveta"""
        try:
            target = await UdpTransportTarget.create((ip, 161), timeout=2, retries=1)
            resultado = await get_cmd(
                self.snmp_engine, self.community, target, ContextData(),
                ObjectType(ObjectIdentity(f'1.3.6.1.2.1.43.11.1.1.6.1.{index}')), # Nome
                ObjectType(ObjectIdentity(f'1.3.6.1.2.1.43.11.1.1.8.1.{index}')), # Capacidade Max
                ObjectType(ObjectIdentity(f'1.3.6.1.2.1.43.11.1.1.9.1.{index}'))  # Nível Atual
            )
            
            errIndication, errStatus, errIndex, varBinds = resultado
            
            if not errIndication and not errStatus:
                nome = str(varBinds[0][1])
                # Se a peça não existir, retorna None
                if not nome or "No Such" in nome:
                    return None, 0, 0
                    
                max_cap = int(varBinds[1][1])
                atual = int(varBinds[2][1])
                return nome, max_cap, atual
                
        except Exception:
            return None, 0, 0
            
        return None, 0, 0