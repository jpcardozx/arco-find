-- ARCO BigQuery Cost Control & Estimation
-- Controla custos de queries antes da execução

-- 1. Estimativa de custo por query
WITH query_cost_analysis AS (
  SELECT 
    -- Estimativa de bytes processados por período
    '90_days' as time_period,
    
    -- Estimativa conservadora baseada no schema
    CASE 
      WHEN @scan_period = '30_days' THEN 50 * 1024 * 1024 * 1024  -- 50GB
      WHEN @scan_period = '90_days' THEN 150 * 1024 * 1024 * 1024 -- 150GB  
      WHEN @scan_period = '180_days' THEN 300 * 1024 * 1024 * 1024 -- 300GB
      ELSE 150 * 1024 * 1024 * 1024
    END as estimated_bytes_processed,
    
    -- Custo por TB ($6.25 USD por TB)
    6.25 as cost_per_tb_usd,
    
    -- Filtros aplicados (redução de custo)
    CASE 
      WHEN @apply_country_filter = TRUE THEN 0.2  -- 80% redução
      WHEN @apply_volume_filter = TRUE THEN 0.3   -- 70% redução  
      WHEN @apply_date_filter = TRUE THEN 0.1     -- 90% redução
      ELSE 1.0  -- Sem filtros
    END as cost_reduction_factor
),

cost_estimate AS (
  SELECT 
    time_period,
    estimated_bytes_processed,
    estimated_bytes_processed * cost_reduction_factor as filtered_bytes,
    (estimated_bytes_processed * cost_reduction_factor / (1024 * 1024 * 1024 * 1024)) * cost_per_tb_usd as estimated_cost_usd,
    
    -- Limites de segurança
    CASE 
      WHEN (estimated_bytes_processed * cost_reduction_factor / (1024 * 1024 * 1024 * 1024)) * cost_per_tb_usd > 25 
        THEN 'ABORT_QUERY_TOO_EXPENSIVE'
      WHEN (estimated_bytes_processed * cost_reduction_factor / (1024 * 1024 * 1024 * 1024)) * cost_per_tb_usd > 10 
        THEN 'WARNING_HIGH_COST'
      ELSE 'APPROVED'
    END as cost_approval_status
    
  FROM query_cost_analysis
)

SELECT 
  *,
  CONCAT('Estimated cost: $', ROUND(estimated_cost_usd, 2), ' USD') as cost_summary,
  
  -- Recomendações de otimização
  CASE 
    WHEN cost_approval_status = 'ABORT_QUERY_TOO_EXPENSIVE' 
      THEN 'Apply more filters: date range, country, advertiser volume'
    WHEN cost_approval_status = 'WARNING_HIGH_COST'
      THEN 'Consider narrowing date range or adding geographic filters'
    ELSE 'Query approved for execution'
  END as optimization_recommendation

FROM cost_estimate;

-- 2. Query para monitorar gastos diários
CREATE OR REPLACE VIEW `project.dataset.daily_query_costs` AS
SELECT 
  DATE(creation_time) as query_date,
  user_email,
  query,
  total_bytes_processed,
  (total_bytes_processed / (1024 * 1024 * 1024 * 1024)) * 6.25 as cost_usd,
  job_id,
  labels
FROM 
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE 
  creation_time >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
  AND total_bytes_processed > 0
ORDER BY 
  creation_time DESC;

-- 3. Alertas de custo por projeto
WITH daily_spending AS (
  SELECT 
    DATE(creation_time) as date,
    SUM((total_bytes_processed / (1024 * 1024 * 1024 * 1024)) * 6.25) as daily_cost_usd
  FROM 
    `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
  WHERE 
    creation_time >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    AND job_type = 'QUERY'
    AND state = 'DONE'
  GROUP BY DATE(creation_time)
),

cost_alerts AS (
  SELECT 
    date,
    daily_cost_usd,
    CASE 
      WHEN daily_cost_usd > 50 THEN 'CRITICAL_OVERSPEND'
      WHEN daily_cost_usd > 25 THEN 'WARNING_HIGH_SPEND' 
      WHEN daily_cost_usd > 10 THEN 'MONITOR_SPEND'
      ELSE 'NORMAL'
    END as alert_level
  FROM daily_spending
)

SELECT 
  *,
  CASE 
    WHEN alert_level = 'CRITICAL_OVERSPEND' 
      THEN 'STOP all non-essential queries immediately'
    WHEN alert_level = 'WARNING_HIGH_SPEND'
      THEN 'Review query efficiency and add more filters'
    ELSE 'Continue normal operations'
  END as recommended_action
FROM cost_alerts
ORDER BY date DESC;