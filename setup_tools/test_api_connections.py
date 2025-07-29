"""
TESTE DE CONECTIVIDADE: SearchAPI + BigQuery + PageSpeed
========================================================
Validação completa das conexões com APIs reais
"""

import asyncio
import aiohttp
import os
import json
from dotenv import load_dotenv

# Tentar importar BigQuery
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

load_dotenv()

class APIConnectionTester:
    def __init__(self):
        self.searchapi_key = os.getenv('SEARCHAPI_KEY')
        self.pagespeed_key = os.getenv('PAGESPEED_KEY')
        
        # BigQuery credentials
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
    async def test_searchapi(self):
        """Testar conexão com SearchAPI"""
        print("🔍 TESTANDO SEARCHAPI...")
        
        if not self.searchapi_key:
            print("❌ SEARCHAPI_KEY não encontrada no .env")
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.searchapi.io/api/v1/search"
                params = {
                    'api_key': self.searchapi_key,
                    'engine': 'google',
                    'q': 'test query',
                    'num': 1
                }
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ SearchAPI: Conectado - Status {response.status}")
                        return True
                    else:
                        print(f"❌ SearchAPI: Erro {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ SearchAPI: Exceção - {e}")
            return False
    
    async def test_pagespeed(self):
        """Testar conexão com PageSpeed API"""
        print("🚀 TESTANDO PAGESPEED API...")
        
        if not self.pagespeed_key:
            print("❌ PAGESPEED_KEY não encontrada no .env")
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
                params = {
                    'url': 'https://example.com',
                    'key': self.pagespeed_key,
                    'category': 'performance'
                }
                
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ PageSpeed API: Conectado - Status {response.status}")
                        return True
                    else:
                        print(f"❌ PageSpeed API: Erro {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ PageSpeed API: Exceção - {e}")
            return False
    
    def test_bigquery(self):
        """Testar conexão com BigQuery"""
        print("📊 TESTANDO BIGQUERY...")
        
        if not BIGQUERY_AVAILABLE:
            print("❌ BigQuery SDK não instalado")
            return False
            
        if not self.project_id:
            print("⚠️ GOOGLE_CLOUD_PROJECT não configurado")
            return False
            
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            print("⚠️ Credenciais do BigQuery não encontradas")
            return False
            
        try:
            credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
            client = bigquery.Client(credentials=credentials, project=self.project_id)
            
            # Teste simples de query
            query = "SELECT 1 as test_connection"
            job = client.query(query)
            results = list(job.result())
            
            if results:
                print(f"✅ BigQuery: Conectado ao projeto {self.project_id}")
                return True
            else:
                print("❌ BigQuery: Sem resultados no teste")
                return False
                
        except Exception as e:
            print(f"❌ BigQuery: Exceção - {e}")
            return False
    
    async def run_all_tests(self):
        """Executar todos os testes de conectividade"""
        print("🧪 INICIANDO TESTES DE CONECTIVIDADE API")
        print("=" * 50)
        
        results = {
            'searchapi': await self.test_searchapi(),
            'pagespeed': await self.test_pagespeed(),
            'bigquery': self.test_bigquery()
        }
        
        print("\n📋 RESUMO DOS TESTES:")
        print("=" * 30)
        
        total_apis = len(results)
        connected_apis = sum(results.values())
        
        for api, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {api.upper()}: {'CONECTADO' if status else 'FALHOU'}")
        
        print(f"\n🎯 RESULTADO GERAL: {connected_apis}/{total_apis} APIs conectadas")
        
        if connected_apis >= 2:
            print("✅ SISTEMA PRONTO PARA PRODUÇÃO")
        elif connected_apis >= 1:
            print("⚠️ FUNCIONALIDADE LIMITADA - algumas APIs offline")
        else:
            print("❌ SISTEMA NÃO OPERACIONAL - todas APIs falharam")
        
        return results

async def main():
    tester = APIConnectionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
