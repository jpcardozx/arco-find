# Implementation Plan

- [x] 1. Extend core data models with marketing data support

  - Extend /arco/models/prospect.py to add MarketingData dataclass and marketing_data field
  - Add MarketingLeak class extending existing Leak in /arco/models/qualified_prospect.py
  - Update model serialization methods (to_dict/from_dict) to handle new marketing fields
  - _Requirements: 1.1, 1.2_

- [x] 2. Create marketing benchmarks configuration system

  - Create /arco/config/marketing_benchmarks.yml with industry-specific CPC, conversion rates, and web vitals thresholds
  - Add industry-specific qualification criteria to existing /arco/config/production.yml
  - Implement benchmark loading logic in LeakEngine following existing config patterns
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Implement Google Analytics integration

  - [x] 3.1 Create GoogleAnalyticsIntegration class in /arco/integrations/google_analytics.py

    - Implement APIClientInterface following existing integration patterns
    - Add credentials handling and client initialization
    - _Requirements: 1.1, 2.1_

  - [x] 3.2 Implement web vitals data collection methods

    - Code get_web_vitals() method to collect LCP, FID, CLS, TTFB metrics
    - Code get_conversion_metrics() method for bounce rate, session duration, conversion rate
    - Add proper error handling and timeout management
    - _Requirements: 1.1, 1.3_

  - [x] 3.3 Add traffic source analysis functionality

    - Implement get_traffic_sources() method to analyze organic vs paid traffic
    - Add data validation and confidence scoring
    - Write unit tests for GA integration methods
    - _Requirements: 1.1, 1.3_

- [x] 4. Implement Google Ads integration

  - [x] 4.1 Create GoogleAdsIntegration class in /arco/integrations/google_ads.py

    - Implement APIClientInterface with proper authentication
    - Add rate limiting and exponential backoff following existing patterns
    - _Requirements: 2.1, 2.4_

  - [x] 4.2 Implement campaign metrics collection

    - Code get_campaign_metrics() method for CPC, CTR, conversion rate, ROAS data
    - Add monthly spend calculation and cost analysis
    - Implement proper error handling for API failures
    - _Requirements: 2.1, 2.2_

  - [x] 4.3 Add keyword performance analysis

    - Implement get_keyword_performance() method for keyword-level insights
    - Add search term analysis and negative keyword identification
    - Write unit tests for Ads integration methods
    - _Requirements: 2.1, 2.2_

- [ ] 5. Implement priority scoring engine for lead prioritization

  - [x] 5.1 Create PriorityEngine class in /arco/engines/priority_engine.py

    - Implement PriorityScore dataclass with scoring components
    - Code score_batch() method for rapid prospect scoring
    - Add get_top_percentage() method to identify top 10% leads
    - _Requirements: 7.1, 7.2_

  - [x] 5.2 Implement priority scoring algorithms

    - Code \_calculate_priority_score() method with weighted scoring
    - Add company size scoring based on employee count and revenue
    - Implement technology maturity scoring based on stack analysis
    - Add growth indicators scoring from web traffic and funding data
    - _Requirements: 7.1, 7.3_

  - [x] 5.3 Add decision maker identification

    - Code \_identify_decision_makers() method using LinkedIn/Apollo data
    - Add contact accessibility scoring based on available contact info
    - Implement role-based targeting (CTO, CMO, CEO) for different industries
    - _Requirements: 7.3_

  - [x] 5.4 Create scoring configuration system

    - Add priority_scoring section to /arco/config/production.yml
    - Define industry-specific scoring weights and thresholds
    - Implement confidence level calculation for incomplete data
    - _Requirements: 7.4_

- [ ] 6. Enhance existing LeakEngine with marketing leak detection

  - [x] 6.1 Add marketing data enrichment to existing analyze() method

    - Extend existing LeakEngine.**init**() to initialize GA and Ads clients
    - Add \_enrich_marketing_data() method following existing enrichment patterns
    - Integrate marketing data collection into existing prospect processing flow
    - _Requirements: 1.1, 2.1, 5.1_

  - [ ] 6.2 Implement performance impact leak detection

    - Code \_analyze_performance_impact() method to detect web vitals affecting conversions
    - Calculate conversion loss based on LCP delays using industry benchmarks
    - Generate MarketingLeak objects with specific recommendations
    - _Requirements: 5.1, 5.3_

  - [ ] 6.3 Implement ad efficiency leak detection

    - Code \_analyze_ad_efficiency() method comparing CPC/conversion rates to industry benchmarks
    - Calculate monthly waste for high CPC + low conversion scenarios
    - Add specific recommendations for campaign optimization
    - _Requirements: 2.2, 2.3, 5.2_

  - [ ] 6.4 Integrate marketing leaks into existing leak analysis flow
    - Modify existing analyze() method to include marketing leaks in results
    - Update qualification scoring to consider marketing efficiency
    - Maintain compatibility with existing LeakResult and QualifiedProspect models
    - _Requirements: 5.4, 6.1_

- [ ] 7. Implement personalized outreach generation

  - [x] 7.1 Create OutreachEngine class in /arco/engines/outreach_engine.py

    - Implement OutreachContent dataclass with messaging components
    - Code generate_outreach() method for personalized content creation
    - Add industry-specific messaging templates and value propositions
    - _Requirements: 8.1, 8.2_

  - [x] 7.2 Implement decision-maker context analysis

    - Code \_get_decision_maker_context() method for role-specific insights
    - Add \_get_technical_talking_points() method based on leak analysis
    - Implement pain point extraction from marketing inefficiencies
    - _Requirements: 8.3, 8.4_

  - [ ] 7.3 Create outreach templates and messaging logic
    - Add outreach_templates section to /arco/config/production.yml
    - Implement subject line generation based on prospect context
    - Code value proposition generation with specific ROI calculations
    - _Requirements: 8.2, 8.3_

- [ ] 8. Fix existing technology detection with robust fallbacks

  - [ ] 8.1 Fix Wappalyzer coroutine issue in existing code

    - Debug and fix "coroutine was never awaited" error in current Wappalyzer integration
    - Add proper async/await handling and timeout management
    - _Requirements: 4.1, 4.3_

  - [ ] 8.2 Implement HTTP header analysis fallback

    - Code \_analyze_http_headers() method to detect technologies from HTTP headers
    - Add User-Agent, Server, and custom header analysis
    - Integrate as first fallback when Wappalyzer fails
    - _Requirements: 4.1, 4.2_

  - [ ] 8.3 Implement DNS record analysis fallback

    - Code \_analyze_dns_records() method to detect hosting and email technologies
    - Add MX, TXT, and CNAME record analysis for technology detection
    - Integrate as second fallback option
    - _Requirements: 4.1, 4.2_

  - [ ] 8.4 Add industry-based technology assignment
    - Code \_get_industry_technologies() method using marketing benchmarks config
    - Assign common technologies when all detection methods fail
    - Add confidence scoring for each detection method
    - _Requirements: 4.4, 3.4_

- [ ] 9. Implement industry-specific qualification criteria

  - [ ] 9.1 Create industry-specific criteria loading system

    - Code \_load_industry_criteria() method in LeakEngine
    - Add criteria selection based on prospect industry
    - Integrate with existing qualification logic
    - _Requirements: 3.1, 3.4_

  - [ ] 9.2 Update qualification scoring with industry benchmarks

    - Modify \_calculate_qualification_score() to use industry-specific thresholds
    - Add technology requirement validation for each industry
    - Update priority tier assignment logic
    - _Requirements: 3.2, 3.3_

  - [ ] 9.3 Add industry-specific ROI calculations
    - Code industry-specific ROI calculation methods
    - Replace generic savings formulas with industry-benchmarked calculations
    - Update annual savings projections based on real data
    - _Requirements: 3.2, 3.3_

- [ ] 10. Enhance CRM integration with marketing insights

  - [ ] 8.1 Extend existing CRM integration to include marketing data

    - Modify existing CRMIntegrationInterface to handle marketing fields
    - Update HubSpotIntegration and MockCRMIntegration classes
    - _Requirements: 6.1, 6.2_

  - [ ] 8.2 Add marketing-specific CRM fields

    - Code marketing performance fields for CRM records
    - Add marketing waste calculations and recommendations to CRM data
    - Include web performance metrics and technical recommendations
    - _Requirements: 6.2, 6.3_

  - [ ] 8.3 Update CRM data mapping for marketing insights
    - Modify existing CRM field mapping to include marketing leak data
    - Add data availability indicators when marketing data is missing
    - Write integration tests for enhanced CRM functionality
    - _Requirements: 6.4_

- [ ] 9. Add comprehensive error handling and fallbacks

  - [ ] 9.1 Implement API rate limiting and retry logic

    - Add exponential backoff for Google APIs following existing patterns
    - Implement request queuing and rate limit detection
    - Add proper logging for API failures and retries
    - _Requirements: 2.4, 1.3_

  - [ ] 9.2 Add graceful degradation for missing marketing data

    - Code fallback logic when marketing APIs are unavailable
    - Maintain existing functionality when marketing enrichment fails
    - Add data confidence indicators for partial data scenarios
    - _Requirements: 1.3, 6.4_

  - [ ] 9.3 Implement comprehensive logging and monitoring
    - Add detailed logging for marketing data collection processes
    - Implement performance monitoring for API response times
    - Add success/failure metrics tracking for each integration
    - _Requirements: 1.3, 2.4_

- [ ] 10. Create comprehensive test suite

  - [ ] 10.1 Write unit tests for marketing integrations

    - Create test files for GoogleAnalyticsIntegration and GoogleAdsIntegration
    - Test API response handling, error scenarios, and data parsing
    - Mock external API calls for reliable testing
    - _Requirements: 1.1, 2.1_

  - [ ] 10.2 Write integration tests for enhanced leak detection

    - Test end-to-end marketing leak detection flow
    - Verify industry-specific qualification criteria application
    - Test CRM integration with marketing data
    - _Requirements: 5.1, 3.1, 6.1_

  - [ ] 10.3 Add performance and load testing
    - Test concurrent marketing data collection
    - Verify API rate limiting and error handling under load
    - Test memory usage and processing time with marketing enrichment
    - _Requirements: 2.4, 1.3_
