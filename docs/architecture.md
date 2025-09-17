# System Architecture: Arco-Find V2.0

## Executive Overview

Arco-Find V2.0 implements a sophisticated **Growth Efficiency Optimization Platform** with multiple specialized intelligence engines, data validation systems, and strategic reporting capabilities. The architecture supports the "Financial Audit Trojan Horse" methodology with enterprise-grade reliability and scalability.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ARCO-FIND V2.0 PLATFORM                     │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface (main.py) → Integrated ARCO Engine               │
│                                ↓                                │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  Intelligence   │  │   Data Pipeline   │  │   Strategic     │ │
│  │    Engines      │  │   & Validation   │  │   Reporting     │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   External      │  │   Data Storage   │  │   Export &      │ │
│  │   Connectors    │  │   & Caching      │  │   Integration   │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Intelligence Engines

### 1. Integrated ARCO Engine (`src/core/integrated_arco_engine.py`)

**Purpose**: Master orchestrator for comprehensive lead generation with data validation and strategic intelligence.

**Key Capabilities**:

```python
class IntegratedARCOEngine:
    """Complete ARCO system with all components integrated"""

    def generate_comprehensive_leads(self, business_type: str, location: str,
                                   target_count: int = 5) -> List[Dict]:
        """8-phase lead generation with validation and enrichment"""

        # Phase 1: Business Discovery
        # Phase 2: Basic Qualification
        # Phase 3: Intelligence Gathering
        # Phase 4: Website Analysis
        # Phase 5: Performance Analysis
        # Phase 6: Data Enrichment
        # Phase 7: Strategic Intelligence
        # Phase 8: Comprehensive Compilation
```

**Processing Pipeline**:

1. **Business Discovery**: Automated prospect identification
2. **Qualification Engine**: Multi-criteria scoring (0-100)
3. **Intelligence Gathering**: Competitive and market analysis
4. **Website Analysis**: Technical and performance audit
5. **Data Enrichment**: Profile completion and validation
6. **Strategic Reports**: 3-tier report generation
7. **Export & Integration**: Multiple format delivery

### 2. ARCO Engine (`src/core/arco_engine.py`)

**Purpose**: Core optimization engine for SaaS, website performance, and ads analysis.

**Specialized Functions**:

```python
class ARCOEngine:
    """Core optimization insights generator"""

    async def _analyze_saas_costs(self, saas_spend: float) -> OptimizationInsight
    async def _analyze_website_performance(self, website_url: str) -> OptimizationInsight
    async def _analyze_google_ads_performance(self, customer_id: str) -> OptimizationInsight
    async def _analyze_meta_business_performance(self, ad_account_id: str) -> OptimizationInsight
```

**Integration Points**:

- Google PageSpeed Insights API
- Google Ads API
- Meta Business API
- Custom SaaS analysis algorithms

### 3. Strategic Intelligence Engine (`src/core/strategic_intelligence_engine.py`)

**Purpose**: Senior-level marketing intelligence and competitive positioning framework.

**Market Intelligence Framework**:

```python
class MarketIntelligenceEngine:
    """Engine de inteligência de mercado usando fontes públicas"""

    async def analyze_industry_context(self, business_type: str, location: str) -> MarketIntelligence
    async def assess_competitive_position(self, business_intelligence: BusinessIntelligence,
                                        market_intelligence: MarketIntelligence) -> CompetitivePosition
    async def generate_executive_insights(self, competitive_position: CompetitivePosition,
                                        market_intelligence: MarketIntelligence) -> List[ExecutiveInsight]
```

**Strategic Capabilities**:

- Industry trend analysis and implications
- Competitive gap identification
- Digital maturity assessment
- Executive-level insight generation
- Strategic recommendation framework

### 4. Ads Intelligence Engine (`src/ads/ads_intelligence_engine.py`)

**Purpose**: Multi-channel advertising intelligence with leak detection and ROI optimization.

**Platform Coverage**:

```python
class AdsIntelligenceEngine:
    """Engine principal de inteligência de ads - integra todos os canais"""

    def __init__(self):
        self.meta_intel = MetaAdsIntelligence()
        self.google_intel = GoogleAdsIntelligence()
        self.tiktok_intel = TikTokAdsIntelligence()

    def comprehensive_ads_audit(self, company_name: str, domain: str,
                               contact_info: Dict = None) -> AdsProfile
```

**Intelligence Capabilities**:

- **Tech Tax Score**: 0-10 efficiency rating
- **Leak Detection**: Performance and spend inefficiencies
- **ROI Optimization**: Savings opportunity identification
- **Quick Win Reports**: Immediate optimization recommendations

### 5. Stack Economics Engine (`src/specialist/mature_stack_economics_workflow.py`)

**Purpose**: Advanced SaaS stack analysis for R$ 1,997 optimization package targeting.

**Economic Analysis Framework**:

```python
class MatureStackEconomicsEngine:
    """Engine amadurecido seguindo strategic review"""

    def analyze_stack_waste_advanced(self, website: str) -> StackWasteAnalysis
    def estimate_business_profile(self, business_data: Dict) -> BusinessSizeProfile
    def calculate_roi_advanced(self, stack_analysis: StackWasteAnalysis,
                             business_profile: BusinessSizeProfile) -> ROICalculation
    def qualify_for_package(self, stack_analysis: StackWasteAnalysis,
                           business_profile: BusinessSizeProfile,
                           roi_calculation: ROICalculation) -> QualificationProfile
```

**Specialization Features**:

- Business size profiling (5-50 employees sweet spot)
- ROI calculation with confidence levels
- Package qualification scoring
- Sales intelligence generation

---

## Data Pipeline & Validation

### Data Validation Engine

**Purpose**: Critical data validation and consistency checking to ensure report accuracy.

```python
class DataValidationEngine:
    """Critical data validation and consistency checking"""

    def validate_business_profile(self, profile: Dict) -> Dict:
        """Validate business profile for critical inconsistencies"""

        # 1. Employee count vs business size consistency
        # 2. Tech stack conflict resolution
        # 3. Market signals temporal consistency
        # 4. Cross-field sanity checks
```

**Validation Components**:

- Size consistency checks (employees vs revenue)
- Technology stack conflict resolution
- Temporal data consistency verification
- Cross-field sanity validation

### Deduplication Engine

**Purpose**: Prevents processing of already analyzed prospects to optimize API usage.

```python
class DeduplicationEngine:
    """Prevents processing of already analyzed prospects"""

    def is_already_processed(self, business: Dict) -> bool
    def mark_as_processed(self, business: Dict)
    def get_processing_stats(self) -> Dict
```

### Prospect Tracking

**Purpose**: Prevents API waste by tracking recently analyzed prospects.

```python
class ProspectTracker:
    """🔥 PREVENTS API WASTE by tracking analyzed prospects"""

    def was_analyzed_recently(self, business: Dict, days: int = 30) -> bool
    def get_previous_analysis(self, business: Dict) -> Optional[Dict]
    def save_analysis(self, business: Dict, analysis_result: Dict)
```

---

## Strategic Reporting System

### Report Generator (`src/core/strategic_intelligence_engine.py`)

**Purpose**: Multi-tier strategic report generation based on qualification levels.

**Report Tiers**:

1. **Tier 1: Diagnostic Teaser** (Always generated)

   - Basic optimization opportunities
   - Performance overview
   - Cost savings preview

2. **Tier 2: Strategic Brief** (Qualification score >50)

   - Competitive analysis
   - Market positioning insights
   - Detailed optimization roadmap

3. **Tier 3: Executive Report** (Qualification score >75)
   - Executive summary and strategic implications
   - Comprehensive competitive intelligence
   - Implementation timeline and ROI projections

```python
class StrategicReportGenerator:
    """Generate strategic reports based on intelligence data"""

    def generate_diagnostic_teaser(self, website_analysis: Dict, performance_data: Dict) -> Dict
    def generate_strategic_brief(self, website_analysis: Dict, performance_data: Dict,
                               business_type: str, location: str) -> Dict
    def generate_executive_report(self, website_analysis: Dict, performance_data: Dict,
                                business_type: str, location: str, estimated_size: str) -> Dict
```

---

## External Connectors & APIs

### Core API Integrations

**Google Services**:

```python
# Google PageSpeed Insights API
class GooglePageSpeedAPI:
    def analyze_performance(self, url: str) -> Dict

# Google Ads API
class GoogleAdsAPI:
    def get_campaign_performance(self, customer_id: str) -> Dict
```

**Meta Business Platform**:

```python
class MetaBusinessAPI:
    def get_ad_account_insights(self, ad_account_id: str) -> Dict
    def analyze_campaign_performance(self, campaign_id: str) -> Dict
```

**Web Intelligence**:

```python
class WebScrapingConnector:
    def analyze_website_stack(self, domain: str) -> Dict
    def get_business_intelligence(self, company_name: str) -> Dict
```

### Data Enrichment Services

**Business Intelligence Scraper** (`src/scrapers/business_intelligence_scraper.py`):

```python
class BusinessIntelligenceEngine:
    """Main engine for business intelligence gathering"""

    async def gather_intelligence(self, company_name: str, website_url: str,
                                business_type: str, location: str) -> BusinessIntelligence
```

**Data Enrichment Orchestrator** (`src/utils/data_enrichment.py`):

```python
class DataEnrichmentOrchestrator:
    """Complete data enrichment pipeline"""

    def enrich_business_profile(self, basic_profile: Dict, website_analysis: Dict,
                              performance_data: Dict, intelligence_data: Dict) -> Dict
```

---

## Configuration & Security

### Configuration Management (`src/config/`)

**Centralized Configuration**:

```python
class ConfigurationManager:
    """Centralized configuration management"""

    def load_api_credentials(self) -> Dict
    def get_analysis_thresholds(self) -> Dict
    def get_qualification_criteria(self) -> Dict
```

**Environment-Based Configuration**:

```yaml
# .env configuration
GOOGLE_PAGESPEED_API_KEY=your_key_here
GOOGLE_ADS_DEVELOPER_TOKEN=your_token_here
META_BUSINESS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### Security & Rate Limiting

**API Service Management** (`src/api_service.py`):

```python
class APIService:
    """Centralized API management with rate limiting"""

    def register_api(self, api_name: str, calls_per_second: float, max_concurrent: int)
    async def make_request(self, api_name: str, request_func: callable, *args, **kwargs)
```

**Rate Limiting Strategy**:

- Google PageSpeed: 1 call/second, 3 concurrent max
- Google Ads: 0.5 calls/second, 2 concurrent max
- Meta Business: 0.5 calls/second, 2 concurrent max
- Web Scraping: 2-second delays between requests

---

## Performance & Scalability

### Caching Strategy

**Multi-Level Caching**:

```python
class CacheManager:
    """Multi-level caching for performance optimization"""

    def cache_website_analysis(self, domain: str, analysis: Dict, ttl: int = 3600)
    def cache_business_intelligence(self, company: str, intelligence: Dict, ttl: int = 86400)
    def cache_performance_data(self, url: str, data: Dict, ttl: int = 1800)
```

**Cache Levels**:

- **Level 1**: In-memory (current session)
- **Level 2**: Local file system (24-48 hours)
- **Level 3**: Database storage (7-30 days)

### Processing Optimization

**Parallel Processing**:

```python
async def process_multiple_leads(self, businesses: List[Dict]) -> List[Dict]:
    """Process multiple leads with controlled parallelism"""

    # Batch processing with rate limiting
    # Error handling and retry logic
    # Progress tracking and reporting
```

**Resource Management**:

- Maximum 5 concurrent lead processing
- 2-second delays between API calls
- Automatic retry with exponential backoff
- Memory management for large datasets

---

## Monitoring & Analytics

### Processing Statistics

**Real-Time Metrics**:

```python
self.stats = {
    'businesses_discovered': 0,
    'websites_analyzed': 0,
    'intelligence_gathered': 0,
    'profiles_enriched': 0,
    'qualified_leads': 0,
    'processing_time': 0,
    'duplicates_skipped': 0,
    'validation_failures': 0,
    'data_conflicts_resolved': 0,
    'cached_prospects_skipped': 0
}
```

**Performance Monitoring**:

- Average processing time per lead
- API call efficiency and success rates
- Cache hit ratios and effectiveness
- Quality metrics and validation success

### Error Handling & Logging

**Structured Logging**:

```python
logger.info(f"🎯 Lead Generation Complete!")
logger.info(f"   📊 Statistics:")
logger.info(f"      • Businesses Discovered: {self.stats['businesses_discovered']}")
logger.info(f"      • Qualified Leads: {len(comprehensive_leads)}")
logger.info(f"      • Processing Time: {self.stats['processing_time']:.1f} seconds")
```

**Error Recovery**:

- Graceful degradation for API failures
- Fallback mechanisms for data sources
- Transaction rollback for failed validations
- Comprehensive error reporting and tracking

---

## Integration & Export

### Export Capabilities

**Multiple Format Support**:

```python
def export_comprehensive_results(self, leads: List[Dict], filename: str = None) -> str:
    """Export comprehensive results with metadata"""

    # JSON format for API integration
    # CSV format for spreadsheet analysis
    # PDF format for client presentation
    # Markdown format for documentation
```

**Integration APIs**:

- REST API endpoints for external systems
- Webhook support for real-time updates
- Batch export for CRM integration
- Custom format adapters

### Extensibility Framework

**Plugin Architecture**:

```python
class PluginManager:
    """Extensible plugin system for custom integrations"""

    def register_qualification_strategy(self, strategy: QualificationStrategy)
    def register_data_source(self, connector: DataConnector)
    def register_export_format(self, exporter: DataExporter)
```

**Custom Extensions**:

- Industry-specific qualification strategies
- Additional data source connectors
- Custom report formats and templates
- Specialized analysis engines

This architecture provides a robust, scalable foundation for the Growth Efficiency Optimization methodology while maintaining flexibility for future enhancements and market expansion.

### 2.6. Módulo `src/reports` - Geração de Relatórios

Responsável por formatar e apresentar os leads qualificados e insights gerados em diferentes formatos.

- `json_reporter.py`: Módulo para gerar relatórios em formato JSON.
- `markdown_reporter.py`: Módulo para gerar relatórios em formato Markdown.

### 2.7. Módulo `src/utils` - Funções Utilitárias

Contém funções de suporte e utilitários que podem ser utilizadas por vários módulos. (Manter `data_enrichment.py` se ainda for relevante, caso contrário, remover esta seção ou o arquivo).

## 3. Fluxo de Dados (Exemplo de Prospecção e Qualificação de Leads)

1.  **Inicialização:** O `main.py` inicia a aplicação, carrega as configurações via `config_manager.py` e configura o `logger.py`.
2.  **Coleta de Dados:** O `engine.py` utiliza os `connectors` (ex: `google_ads_connector.py`, `web_scraper_connector.py`) para coletar dados brutos de potenciais leads.
3.  **Processamento e Qualificação:** O `engine.py` aplica uma ou mais `strategies` (ex: `tech_stack_qualification.py`, `ad_spend_qualification.py`) aos dados coletados para qualificar os leads com base em critérios definidos.
4.  **Modelagem de Dados:** Os dados qualificados são estruturados utilizando o modelo `lead.py`.
5.  **Geração de Relatórios:** O `engine.py` utiliza os `reports` (ex: `json_reporter.py`, `markdown_reporter.py`) para formatar e salvar os leads qualificados no diretório `output/`.

## 4. Tecnologias Chave

- **Python:** Linguagem de programação principal.
- **APIs Externas:** Integração com APIs como Google Ads, Meta Business, etc.
- **Estrutura Modular:** Organização do código em módulos e pacotes para facilitar a manutenção e escalabilidade.
- **CLI:** Interface de linha de comando para interação com o usuário.

## 5. Escalabilidade e Extensibilidade

A arquitetura modular do Arco-Find permite:

- **Adição de Novos Conectores:** Facilmente integrar novas fontes de dados (outras APIs, bancos de dados).
- **Desenvolvimento de Novas Estratégias:** Adicionar novos algoritmos e lógicas de qualificação sem impactar o core do sistema.
- **Customização de Relatórios:** Adaptar os formatos de saída para diferentes necessidades de apresentação.
- **Processamento Distribuído:** A estrutura do pipeline permite a futura implementação de processamento em paralelo ou distribuído para lidar com grandes volumes de dados.

Esta arquitetura visa garantir que o Arco-Find seja robusto, eficiente e adaptável às crescentes necessidades de prospecção e qualificação de leads.
