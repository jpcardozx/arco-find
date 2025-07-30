# 🗄️ ARCO-FIND BIGQUERY SCHEMA

## 📊 Dataset: arco_intelligence

### Table: qualified_leads

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| company_name | STRING | REQUIRED | Nome da empresa |
| website | STRING | NULLABLE | Website da empresa |
| industry | STRING | NULLABLE | Setor/indústria |
| employee_count | INTEGER | NULLABLE | Número de funcionários |
| monthly_ad_spend | FLOAT | NULLABLE | Gasto mensal estimado em ads |
| performance_score | INTEGER | NULLABLE | Score de performance (0-100) |
| message_match_score | FLOAT | NULLABLE | Score de match da mensagem (0-1) |
| qualification_score | INTEGER | REQUIRED | Score de qualificação (0-100) |
| urgency_level | STRING | NULLABLE | HOT, WARM, COLD |
| estimated_monthly_loss | FLOAT | NULLABLE | Perda mensal estimada |
| specific_pain_points | STRING | NULLABLE | Pain points (JSON string) |
| conversion_priority | STRING | NULLABLE | Prioridade de conversão |
| last_updated | TIMESTAMP | NULLABLE | Última atualização |
| discovery_source | STRING | NULLABLE | Fonte da descoberta |
| created_at | TIMESTAMP | NULLABLE | Data de criação |

## 🔍 Sample Queries

### Get Hot Leads
```sql
SELECT company_name, qualification_score, conversion_priority
FROM `prospection-463116.arco_intelligence.qualified_leads`
WHERE qualification_score >= 70
  AND urgency_level = 'HOT'
  AND last_updated >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY qualification_score DESC
```

### Get Recent Discoveries
```sql
SELECT company_name, industry, discovery_source, created_at
FROM `prospection-463116.arco_intelligence.qualified_leads`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY created_at DESC
```

## 🎯 Usage Notes

1. **qualification_score** is the primary ranking field
2. **last_updated** should be used for cache invalidation
3. **specific_pain_points** stores JSON array as string
4. **conversion_priority** determines follow-up strategy

## 🔧 Maintenance

- Run schema validation weekly
- Archive old records (>90 days) to cost optimize
- Monitor query performance and add indexes if needed
