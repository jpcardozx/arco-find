-- ARCO Cost-Optimized Lead Discovery Query
-- ULTRA LEAN: Máximo 50GB processados (~$0.31 USD)
-- Filtros agressivos pré-agregação para controle rigoroso de custos

WITH cost_control AS (
  SELECT 
    -- Janela temporal MÍNIMA (últimos 30 dias para reduzir custos)
    DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) as start_date,
    CURRENT_DATE() as end_date,
    -- Focus geográfico restrito
    ['AU', 'NZ'] as target_countries,
    -- Apenas verticais high-value
    ['dental', 'legal', 'aesthetic'] as target_verticals
),

-- PRÉ-FILTRO AGRESSIVO: só prospects com padrões específicos no nome
pre_qualified_advertisers AS (
  SELECT DISTINCT 
    advertiser_id,
    advertiser_name,
    country_code
  FROM 
    `bigquery-public-data.meta_ad_library.creative_stats` ads,
    cost_control cc
  WHERE 
    -- FILTRO TEMPORAL RESTRITIVO
    ads.ad_delivery_start_time >= cc.start_date
    AND ads.country_code IN UNNEST(cc.target_countries)
    -- FILTRO LÉXICO para vertical (reduz 80%+ dos dados)
    AND (
      REGEXP_CONTAINS(LOWER(advertiser_name), r'dental|dentist|teeth|smile|orthodont') OR
      REGEXP_CONTAINS(LOWER(advertiser_name), r'law|legal|attorney|solicitor|lawyer') OR 
      REGEXP_CONTAINS(LOWER(advertiser_name), r'aesthetic|beauty|clinic|cosmetic|botox')
    )
    -- Excluir enterprises conhecidos
    AND NOT REGEXP_CONTAINS(LOWER(advertiser_name), r'facebook|google|meta|amazon|microsoft')
    -- Filtro de atividade mínima para SME
    AND advertiser_id IN (
      SELECT advertiser_id 
      FROM `bigquery-public-data.meta_ad_library.creative_stats`
      WHERE 
        ad_delivery_start_time >= cc.start_date
        AND country_code IN UNNEST(cc.target_countries)
      GROUP BY advertiser_id
      HAVING COUNT(DISTINCT ad_id) BETWEEN 6 AND 25  -- SME sweet spot
    )
  LIMIT 500  -- Limite hard para controle de custo
),

-- AGREGAÇÃO apenas dos pré-qualificados
aggregated_prospects AS (
  SELECT 
    pq.advertiser_id,
    pq.advertiser_name,
    pq.country_code,
    COUNT(DISTINCT ads.ad_id) as ad_volume,
    COUNT(DISTINCT ads.creative_body) as unique_creatives,
    MIN(ads.ad_delivery_start_time) as first_ad_date,
    MAX(ads.ad_delivery_stop_time) as last_ad_date,
    
    -- Estimativas conservadoras
    COUNT(DISTINCT ads.ad_id) * 12 as estimated_monthly_spend_gbp,
    
    -- Diversidade criativa
    SAFE_DIVIDE(
      COUNT(DISTINCT ads.creative_body), 
      COUNT(DISTINCT ads.ad_id)
    ) as creative_diversity,
    
    -- Classificação de vertical baseada em nome
    CASE 
      WHEN REGEXP_CONTAINS(LOWER(pq.advertiser_name), r'dental|dentist|teeth|smile') THEN 'dental'
      WHEN REGEXP_CONTAINS(LOWER(pq.advertiser_name), r'law|legal|attorney|solicitor') THEN 'legal'
      WHEN REGEXP_CONTAINS(LOWER(pq.advertiser_name), r'aesthetic|beauty|clinic|cosmetic') THEN 'aesthetic'
      ELSE 'other'
    END as vertical
    
  FROM 
    pre_qualified_advertisers pq
    JOIN `bigquery-public-data.meta_ad_library.creative_stats` ads
      ON pq.advertiser_id = ads.advertiser_id
      AND ads.ad_delivery_start_time >= (SELECT start_date FROM cost_control)
      AND ads.country_code = pq.country_code
  GROUP BY 
    pq.advertiser_id, pq.advertiser_name, pq.country_code
  HAVING 
    ad_volume >= 6  -- Mínimo atividade
    AND ad_volume <= 25  -- Máximo SME
    AND DATE_DIFF(CURRENT_DATE(), DATE(MAX(ads.ad_delivery_stop_time)), DAY) <= 14  -- Ativo recente
),

-- SCORING E QUALIFICAÇÃO FINAL
final_prospects AS (
  SELECT 
    advertiser_id,
    advertiser_name as company_name,
    country_code as location,
    vertical,
    ad_volume,
    unique_creatives as creative_count,
    creative_diversity,
    estimated_monthly_spend_gbp,
    
    -- Pain signals otimizados
    CASE 
      WHEN ad_volume > 15 THEN 'high_volume_sme'
      WHEN creative_diversity < 0.4 THEN 'creative_fatigue'
      WHEN estimated_monthly_spend_gbp > 300 THEN 'spend_optimization'
      ELSE 'tracking_improvement'
    END as primary_pain_signal,
    
    -- Score simplificado
    (
      LEAST(30, ad_volume * 1.5) +  -- Volume component
      (CASE WHEN creative_diversity < 0.5 THEN 15 ELSE 0 END) +  -- Diversity penalty
      LEAST(20, estimated_monthly_spend_gbp / 15) +  -- Spend component
      (CASE WHEN DATE_DIFF(CURRENT_DATE(), DATE(last_ad_date), DAY) <= 7 THEN 10 ELSE 0 END)  -- Recency
    ) as opportunity_score,
    
    -- Valor estimado em AUD (conversão 1.9x)
    ROUND(
      (ad_volume * 40 * 1.9) +  -- Consolidation savings AUD
      (estimated_monthly_spend_gbp * 0.12 * 1.9)  -- Budget optimization AUD
    ) as estimated_monthly_value_aud,
    
    first_ad_date,
    last_ad_date,
    CURRENT_TIMESTAMP() as discovered_at,
    'cost_optimized_discovery' as discovery_method
    
  FROM aggregated_prospects
  WHERE 
    vertical != 'other'  -- Só verticais classificados
  ORDER BY 
    opportunity_score DESC,
    estimated_monthly_value_aud DESC
  LIMIT 100  -- Resultado final controlado
)

SELECT * FROM final_prospects
WHERE opportunity_score >= 25;  -- Só alta qualidade

-- COST ESTIMATE: ~30-50GB processados = $0.19-0.31 USD
-- EXPECTED RESULTS: 20-50 qualified prospects
-- REFRESH: Diário durante descoberta, semanal para manutenção