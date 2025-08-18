#!/usr/bin/env python3
"""
BIGQUERY DRY RUN - REAL COST VERIFICATION
==========================================

Verifica o custo REAL da query sem executá-la
"""

from google.cloud import bigquery

def check_real_query_cost():
    """Dry run da query atual para verificar bytes processados e custo real"""
    
    client = bigquery.Client()
    
    # Query exata do engine atual
    query = """
    WITH prospect_analysis AS (
        SELECT 
            advertiser_disclosed_name,
            advertiser_location,
            
            -- Marketing metrics
            COUNT(*) as ad_volume,
            COUNT(DISTINCT creative_id) as creative_count,
            ROUND(COUNT(DISTINCT creative_id) / COUNT(*), 3) as creative_diversity,
            
            -- Performance indicators
            CASE 
                WHEN COUNT(*) > 40 AND (COUNT(DISTINCT creative_id) / COUNT(*)) < 0.3 
                THEN 0.85  -- High volume, low diversity = major waste
                WHEN COUNT(*) > 60 AND (COUNT(DISTINCT creative_id) / COUNT(*)) > 0.8
                THEN 0.75  -- Excessive testing without optimization
                WHEN COUNT(*) BETWEEN 20 AND 60 AND (COUNT(DISTINCT creative_id) / COUNT(*)) BETWEEN 0.3 AND 0.7
                THEN 0.45  -- Reasonable approach
                ELSE 0.65  -- Default moderate waste
            END as waste_probability,
            
            -- Creative age estimation (approximate)
            COUNT(*) / 4 as estimated_creative_age,  -- Rough proxy: more ads = longer campaign
            
            -- Vertical classification
            CASE 
                WHEN LOWER(advertiser_disclosed_name) LIKE '%clinic%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%aesthetic%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%beauty%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%cosmetic%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%dermal%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%laser%'
                THEN 'aesthetic'
                WHEN LOWER(advertiser_disclosed_name) LIKE '%estate%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%property%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%homes%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%lettings%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%realty%'
                THEN 'estate'
                WHEN LOWER(advertiser_disclosed_name) LIKE '%law%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%legal%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%solicitor%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%barrister%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%attorney%'
                THEN 'legal'
                WHEN LOWER(advertiser_disclosed_name) LIKE '%dental%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%dentist%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%orthodontist%'
                     OR LOWER(advertiser_disclosed_name) LIKE '%implant%'
                THEN 'dental'
                ELSE 'other'
            END as vertical
            
        FROM `bigquery-public-data.google_ads_transparency_center.creative_stats`
        WHERE advertiser_location IN ('GB', 'IE', 'AU', 'NZ', 'CA')  -- English-speaking markets
            AND (
                -- Aesthetic keywords
                LOWER(advertiser_disclosed_name) LIKE '%clinic%'
                OR LOWER(advertiser_disclosed_name) LIKE '%aesthetic%' 
                OR LOWER(advertiser_disclosed_name) LIKE '%beauty%'
                OR LOWER(advertiser_disclosed_name) LIKE '%cosmetic%'
                OR LOWER(advertiser_disclosed_name) LIKE '%dermal%'
                OR LOWER(advertiser_disclosed_name) LIKE '%laser%'
                -- Estate keywords
                OR LOWER(advertiser_disclosed_name) LIKE '%estate%'
                OR LOWER(advertiser_disclosed_name) LIKE '%property%'
                OR LOWER(advertiser_disclosed_name) LIKE '%homes%'
                OR LOWER(advertiser_disclosed_name) LIKE '%lettings%'
                OR LOWER(advertiser_disclosed_name) LIKE '%realty%'
                -- Legal keywords  
                OR LOWER(advertiser_disclosed_name) LIKE '%law%'
                OR LOWER(advertiser_disclosed_name) LIKE '%legal%'
                OR LOWER(advertiser_disclosed_name) LIKE '%solicitor%'
                OR LOWER(advertiser_disclosed_name) LIKE '%barrister%'
                -- Dental keywords
                OR LOWER(advertiser_disclosed_name) LIKE '%dental%'
                OR LOWER(advertiser_disclosed_name) LIKE '%dentist%'
                OR LOWER(advertiser_disclosed_name) LIKE '%orthodontist%'
            )
            -- Exclude large corporations and platforms
            AND NOT (
                LOWER(advertiser_disclosed_name) LIKE '%rightmove%'
                OR LOWER(advertiser_disclosed_name) LIKE '%zoopla%'
                OR LOWER(advertiser_disclosed_name) LIKE '%hospital%'
                OR LOWER(advertiser_disclosed_name) LIKE '%nhs%'
                OR LOWER(advertiser_disclosed_name) LIKE '%university%'
                OR LOWER(advertiser_disclosed_name) LIKE '%college%'
                OR LOWER(advertiser_disclosed_name) LIKE '%group%'
                OR LOWER(advertiser_disclosed_name) LIKE '%holdings%'
                OR LOWER(advertiser_disclosed_name) LIKE '%international%'
                OR LOWER(advertiser_disclosed_name) LIKE '%global%'
                OR LOWER(advertiser_disclosed_name) LIKE '%network%'
                OR LOWER(advertiser_disclosed_name) LIKE '%platform%'
            )
        GROUP BY advertiser_disclosed_name, advertiser_location
        HAVING ad_volume BETWEEN 15 AND 150  -- SME sweet spot
            AND vertical != 'other'
            AND waste_probability >= 0.5  -- Focus on real opportunities
    )
    
    SELECT * FROM prospect_analysis
    ORDER BY waste_probability DESC, ad_volume DESC
    LIMIT 20
    """
    
    print("=== BIGQUERY DRY RUN - CUSTO REAL ===")
    print("Query: ARCO Discovery Engine")
    print()
    
    # Configurar dry run
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    
    try:
        # Executar dry run
        job = client.query(query, job_config=job_config)
        
        # Calcular custos
        bytes_processed = job.total_bytes_processed
        gb_processed = bytes_processed / (1024**3)
        tb_processed = bytes_processed / (1024**4)
        
        # Preços BigQuery (US East)
        cost_per_tb_usd = 6.25  # $6.25 per TB
        cost_usd = tb_processed * cost_per_tb_usd
        
        print(f">> Bytes processados: {bytes_processed:,} bytes")
        print(f">> GB processados: {gb_processed:.2f} GB")  
        print(f">> TB processados: {tb_processed:.6f} TB")
        print()
        print(f">> Custo por execucao: ${cost_usd:.6f} USD")
        print(f">> Custo mensal (1x/dia): ${cost_usd * 30:.4f} USD")
        print(f">> Custo mensal (3x/semana): ${cost_usd * 12:.4f} USD")
        print()
        
        # Verificar se é realmente barato
        if cost_usd > 0.1:
            print(">> ALERTA: Custo acima de $0.10 por execucao")
        elif cost_usd > 0.01:
            print(">> AVISO: Custo acima de $0.01 por execucao")
        else:
            print(">> Custo otimizado: <$0.01 por execucao")
        
        return {
            'bytes_processed': bytes_processed,
            'gb_processed': gb_processed,
            'cost_usd': cost_usd,
            'monthly_cost_daily': cost_usd * 30,
            'monthly_cost_3x_week': cost_usd * 12
        }
        
    except Exception as e:
        print(f">> Erro no dry run: {e}")
        return None

def check_table_size():
    """Verifica o tamanho da tabela BigQuery"""
    
    client = bigquery.Client()
    
    try:
        table = client.get_table("bigquery-public-data.google_ads_transparency_center.creative_stats")
        
        print("=== INFORMAÇÕES DA TABELA ===")
        print(f">> Total de linhas: {table.num_rows:,}")
        print(f">> Tamanho em bytes: {table.num_bytes:,}")
        print(f">> Tamanho em GB: {table.num_bytes / (1024**3):.2f} GB")
        print(f">> Ultima modificacao: {table.modified}")
        print()
        
        return {
            'total_rows': table.num_rows,
            'size_bytes': table.num_bytes,
            'size_gb': table.num_bytes / (1024**3)
        }
        
    except Exception as e:
        print(f">> Erro ao obter informacoes da tabela: {e}")
        return None

if __name__ == "__main__":
    print("VERIFICAÇÃO DE CUSTOS BIGQUERY - ARCO DISCOVERY ENGINE")
    print("=" * 60)
    
    # Verificar informações da tabela
    table_info = check_table_size()
    print()
    
    # Verificar custo da query
    cost_info = check_real_query_cost()
    
    if cost_info:
        print("=" * 60)
        print("CONCLUSÃO:")
        
        if cost_info['cost_usd'] < 0.001:
            print(">> Engine esta otimizado para custos minimos")
        elif cost_info['cost_usd'] < 0.01:
            print(">> Custos aceitaveis para uso regular") 
        else:
            print(">> Custos podem ser elevados para uso frequente")
            
        print(f">> Recomendacao: Maximo {int(1.0 / cost_info['cost_usd'])} execucoes por $1 USD")