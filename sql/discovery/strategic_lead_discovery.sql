-- ARCO Strategic Lead Discovery Query
-- Filtros pré-agregação otimizados para custo e precisão
-- Target: SME com alto volume/spend em verticais específicos

WITH cost_control AS (
  SELECT 
    -- Limitar escopo temporal para controle de custos (últimos 90 dias)
    DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) as start_date,
    CURRENT_DATE() as end_date,
    -- Limitar regiões para focus geográfico
    ['AU', 'NZ', 'GB', 'US', 'CA'] as target_countries
),

pre_filtered_ads AS (
  SELECT 
    advertiser_id,
    advertiser_name,
    country_code,
    -- Agregações estratégicas pré-filtro
    COUNT(DISTINCT ad_id) as total_ads,
    COUNT(DISTINCT creative_body) as unique_creatives,
    MIN(ad_delivery_start_time) as first_ad_date,
    MAX(ad_delivery_stop_time) as last_ad_date,
    -- Estimativa de spend baseada em atividade
    COUNT(DISTINCT ad_id) * 15 as estimated_daily_spend,
    -- Diversidade criativa
    SAFE_DIVIDE(
      COUNT(DISTINCT creative_body), 
      COUNT(DISTINCT ad_id)
    ) as creative_diversity_ratio
  FROM 
    `bigquery-public-data.meta_ad_library.creative_stats` ads,
    cost_control cc
  WHERE 
    -- FILTROS PRÉ-AGREGAÇÃO (reduzem custos drasticamente)
    ads.ad_delivery_start_time >= cc.start_date
    AND ads.ad_delivery_start_time <= cc.end_date
    AND ads.country_code IN UNNEST(cc.target_countries)
    -- Filtros de volume mínimo (só SME com atividade relevante)
    AND ads.advertiser_id IN (
      SELECT advertiser_id 
      FROM `bigquery-public-data.meta_ad_library.creative_stats`
      WHERE ad_delivery_start_time >= cc.start_date
      GROUP BY advertiser_id
      HAVING COUNT(DISTINCT ad_id) BETWEEN 8 AND 100  -- Sweet spot SME
    )
  GROUP BY 
    advertiser_id, 
    advertiser_name, 
    country_code
  -- Filtro pós-agregação para qualidade
  HAVING 
    total_ads >= 8  -- Mínimo para ter dados significativos
    AND total_ads <= 100  -- Máximo para evitar grandes enterprises
    AND DATE_DIFF(CURRENT_DATE(), DATE(first_ad_date), DAY) <= 90  -- Atividade recente
),

vertical_classification AS (
  SELECT 
    *,
    -- Classificação de vertical baseada em padrões de nome
    CASE 
      WHEN REGEXP_CONTAINS(LOWER(advertiser_name), r'dental|dentist|orthodont|smile|teeth') THEN 'dental'
      WHEN REGEXP_CONTAINS(LOWER(advertiser_name), r'law|legal|attorney|solicitor|lawyer') THEN 'legal'  
      WHEN REGEXP_CONTAINS(LOWER(advertiser_name), r'aesthetic|beauty|clinic|cosmetic|botox|filler') THEN 'aesthetic'
      WHEN REGEXP_CONTAINS(LOWER(advertiser_name), r'estate|property|real estate|realty|homes') THEN 'estate'
      WHEN REGEXP_CONTAINS(LOWER(advertiser_name), r'gym|fitness|personal training|pt|crossfit') THEN 'fitness'
      ELSE 'other'
    END as vertical,
    
    -- Pain signals estratégicos
    CASE 
      WHEN total_ads > 25 THEN 'high_volume_inefficiency'
      WHEN creative_diversity_ratio < 0.4 THEN 'creative_fatigue_risk'  
      WHEN estimated_daily_spend > 500 THEN 'budget_optimization_opportunity'
      ELSE 'tracking_enhancement'
    END as primary_pain_signal
    
  FROM pre_filtered_ads
),

qualified_prospects AS (
  SELECT 
    *,
    -- Score estratégico baseado em oportunidade
    (
      -- Volume score (0-40 pontos)
      LEAST(40, total_ads * 2) +
      -- Diversity penalty (0-20 pontos)
      (CASE WHEN creative_diversity_ratio < 0.5 THEN 20 ELSE 0 END) +
      -- Spend opportunity (0-30 pontos)  
      LEAST(30, estimated_daily_spend / 20) +
      -- Recency bonus (0-10 pontos)
      (CASE WHEN DATE_DIFF(CURRENT_DATE(), DATE(last_ad_date), DAY) <= 7 THEN 10 ELSE 0 END)
    ) as opportunity_score,
    
    -- Estimativa de valor mensal em AUD
    ROUND(
      (total_ads * 45 * 1.9) +  -- Consolidation savings in AUD
      (estimated_daily_spend * 0.15 * 30 * 1.9)  -- Budget optimization in AUD
    ) as estimated_monthly_value_aud
    
  FROM vertical_classification
  WHERE 
    vertical != 'other'  -- Só verticais conhecidos
    AND country_code IN ('AU', 'NZ', 'GB')  -- Focus geográfico
),

final_prospects AS (
  SELECT 
    advertiser_id,
    advertiser_name as company_name,
    country_code as location,
    vertical,
    total_ads as ad_volume,
    unique_creatives as creative_count,
    creative_diversity_ratio as creative_diversity,
    estimated_daily_spend as estimated_monthly_spend,
    primary_pain_signal,
    opportunity_score,
    estimated_monthly_value_aud,
    first_ad_date,
    last_ad_date,
    -- Metadata para tracking
    CURRENT_TIMESTAMP() as discovered_at,
    'bigquery_strategic_discovery' as discovery_method,
    'high' as confidence_level
  FROM qualified_prospects
  WHERE 
    opportunity_score >= 50  -- Só alta qualidade
  ORDER BY 
    opportunity_score DESC,
    estimated_monthly_value_aud DESC
  LIMIT 1000  -- Controle de volume e custo
)

SELECT * FROM final_prospects;

-- Query cost estimate: ~$5-15 USD dependendo do volume
-- Expected results: 50-200 qualified prospects por execução
-- Refresh frequency: Weekly para manter frescor sem explodir custos