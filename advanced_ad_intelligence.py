"""
Advanced Ad Intelligence Analysis - Real Vulnerabilities Detection
Based on Google Ads Transparency Center rich data
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

class AdIntelligenceAnalyzer:
    """Advanced analysis of advertising patterns to identify real business vulnerabilities"""
    
    def analyze_ad_vulnerabilities(self, transparency_data: Dict) -> Dict:
        """
        Perform sophisticated analysis of ad data to identify real business vulnerabilities
        Returns detailed vulnerability assessment with specific improvement opportunities
        """
        ad_creatives = transparency_data.get('ad_creatives', [])
        
        if not ad_creatives:
            return {
                'vulnerability_score': 10,  # Maximum vulnerability 
                'primary_issues': ['NO_ADVERTISING'],
                'revenue_impact': 'CRITICAL',
                'analysis': 'No advertising presence detected - missing major lead generation channel'
            }
        
        vulnerabilities = []
        opportunity_score = 0
        
        # 1. TEMPORAL PATTERN ANALYSIS
        temporal_analysis = self._analyze_temporal_patterns(ad_creatives)
        vulnerabilities.extend(temporal_analysis['issues'])
        opportunity_score += temporal_analysis['score']
        
        # 2. CREATIVE QUALITY ANALYSIS  
        creative_analysis = self._analyze_creative_quality(ad_creatives)
        vulnerabilities.extend(creative_analysis['issues'])
        opportunity_score += creative_analysis['score']
        
        # 3. ADVERTISER MANAGEMENT ANALYSIS
        management_analysis = self._analyze_advertiser_management(ad_creatives)
        vulnerabilities.extend(management_analysis['issues'])
        opportunity_score += management_analysis['score']
        
        # 4. CAMPAIGN SOPHISTICATION ANALYSIS
        sophistication_analysis = self._analyze_campaign_sophistication(ad_creatives)
        vulnerabilities.extend(sophistication_analysis['issues'])
        opportunity_score += sophistication_analysis['score']
        
        # 5. COMPETITIVE GAPS ANALYSIS
        competitive_analysis = self._analyze_competitive_gaps(ad_creatives)
        vulnerabilities.extend(competitive_analysis['issues'])
        opportunity_score += competitive_analysis['score']
        
        return {
            'vulnerability_score': min(opportunity_score, 10),
            'primary_issues': vulnerabilities[:3],  # Top 3 issues
            'revenue_impact': self._calculate_revenue_impact(opportunity_score),
            'detailed_analysis': {
                'temporal': temporal_analysis,
                'creative': creative_analysis, 
                'management': management_analysis,
                'sophistication': sophistication_analysis,
                'competitive': competitive_analysis
            }
        }
    
    def _analyze_temporal_patterns(self, ads: List[Dict]) -> Dict:
        """Analyze timing patterns for gaps and inefficiencies"""
        issues = []
        score = 0
        
        # Parse dates and calculate gaps
        active_periods = []
        for ad in ads:
            try:
                start = datetime.fromisoformat(ad.get('first_shown_datetime', '').replace('Z', '+00:00'))
                end = datetime.fromisoformat(ad.get('last_shown_datetime', '').replace('Z', '+00:00'))
                days_shown = ad.get('total_days_shown', 0)
                active_periods.append((start, end, days_shown))
            except:
                continue
        
        if not active_periods:
            return {'issues': ['TEMPORAL_DATA_MISSING'], 'score': 2}
        
        # Sort by start date
        active_periods.sort(key=lambda x: x[0])
        
        # 1. Detect campaign gaps
        gaps = []
        for i in range(1, len(active_periods)):
            prev_end = active_periods[i-1][1]
            current_start = active_periods[i][0]
            gap_days = (current_start - prev_end).days
            if gap_days > 7:  # Gap > 1 week
                gaps.append(gap_days)
        
        if gaps:
            avg_gap = statistics.mean(gaps)
            if avg_gap > 30:
                issues.append(f'LONG_CAMPAIGN_GAPS_{int(avg_gap)}d')
                score += 3
            elif avg_gap > 14:
                issues.append(f'MEDIUM_CAMPAIGN_GAPS_{int(avg_gap)}d')
                score += 2
        
        # 2. Detect inconsistent spend patterns
        days_shown_list = [period[2] for period in active_periods]
        if len(days_shown_list) > 1:
            std_dev = statistics.stdev(days_shown_list)
            mean_days = statistics.mean(days_shown_list)
            
            if std_dev > mean_days * 0.5:  # High variance
                issues.append('INCONSISTENT_SPEND_PATTERNS')
                score += 2
        
        # 3. Recent activity check
        most_recent = max(active_periods, key=lambda x: x[1])[1]
        days_since_last = (datetime.now(most_recent.tzinfo) - most_recent).days
        
        if days_since_last > 30:
            issues.append(f'STALE_CAMPAIGNS_{days_since_last}d')
            score += 3
        elif days_since_last > 14:
            issues.append(f'RECENT_GAP_{days_since_last}d') 
            score += 1
        
        return {
            'issues': issues,
            'score': score,
            'details': {
                'campaign_gaps': gaps,
                'days_since_last_active': days_since_last,
                'consistency_variance': std_dev / mean_days if len(days_shown_list) > 1 else 0
            }
        }
    
    def _analyze_creative_quality(self, ads: List[Dict]) -> Dict:
        """Analyze creative assets for quality and optimization opportunities"""
        issues = []
        score = 0
        
        formats = [ad.get('format') for ad in ads]
        images = [ad.get('image', {}) for ad in ads if ad.get('image')]
        
        # 1. Format diversity analysis
        unique_formats = set(f for f in formats if f)
        if len(unique_formats) == 1:
            if 'text' in unique_formats:
                issues.append('ONLY_TEXT_ADS_NO_VISUAL')
                score += 3
            else:
                issues.append('LIMITED_FORMAT_DIVERSITY')
                score += 1
        
        # 2. Image dimension analysis  
        if images:
            dimensions = []
            for img in images:
                try:
                    w, h = img.get('width', 0), img.get('height', 0)
                    if w and h:
                        dimensions.append((w, h))
                except:
                    continue
            
            if dimensions:
                # Check for mobile optimization
                mobile_optimized = sum(1 for w, h in dimensions if w <= 400 or h <= 400)
                mobile_ratio = mobile_optimized / len(dimensions)
                
                if mobile_ratio < 0.3:
                    issues.append('POOR_MOBILE_CREATIVE_OPTIMIZATION')
                    score += 2
                
                # Check dimension diversity (indicates testing)
                unique_dimensions = len(set(dimensions))
                if unique_dimensions < len(dimensions) * 0.5:
                    issues.append('LIMITED_CREATIVE_TESTING')
                    score += 2
        
        # 3. Creative freshness
        if len(ads) < 5:
            issues.append('LOW_CREATIVE_VOLUME')
            score += 2
        elif len(ads) < 10:
            issues.append('MODERATE_CREATIVE_VOLUME')
            score += 1
        
        return {
            'issues': issues,
            'score': score,
            'details': {
                'format_diversity': list(unique_formats),
                'total_creatives': len(ads),
                'mobile_optimization_ratio': mobile_ratio if images else 0
            }
        }
    
    def _analyze_advertiser_management(self, ads: List[Dict]) -> Dict:
        """Analyze advertiser management structure for optimization opportunities"""
        issues = []
        score = 0
        
        advertisers = {}
        for ad in ads:
            advertiser = ad.get('advertiser', {})
            adv_id = advertiser.get('id')
            adv_name = advertiser.get('name')
            
            if adv_id:
                if adv_id not in advertisers:
                    advertisers[adv_id] = {'name': adv_name, 'ads': []}
                advertisers[adv_id]['ads'].append(ad)
        
        # 1. Management structure analysis
        if len(advertisers) > 1:
            # Multiple advertisers = potential agency management or fragmentation
            ad_distribution = [len(adv['ads']) for adv in advertisers.values()]
            
            if max(ad_distribution) < len(ads) * 0.7:  # No dominant advertiser
                issues.append('FRAGMENTED_ADVERTISER_MANAGEMENT')
                score += 2
            else:
                issues.append('MULTI_ADVERTISER_SETUP')
                score += 1
        
        # 2. Advertiser naming analysis (indicates professionalism)
        advertiser_names = [adv['name'] for adv in advertisers.values()]
        
        suspicious_patterns = ['llc', 'inc', 'corp', 'ltd']
        professional_count = sum(1 for name in advertiser_names 
                               if any(pattern in name.lower() for pattern in suspicious_patterns))
        
        if professional_count < len(advertiser_names) * 0.5:
            issues.append('UNPROFESSIONAL_ADVERTISER_NAMES')
            score += 1
        
        return {
            'issues': issues,
            'score': score,
            'details': {
                'total_advertisers': len(advertisers),
                'advertiser_names': advertiser_names,
                'ad_distribution': ad_distribution if len(advertisers) > 1 else [len(ads)]
            }
        }
    
    def _analyze_campaign_sophistication(self, ads: List[Dict]) -> Dict:
        """Analyze campaign sophistication and strategic gaps"""
        issues = []
        score = 0
        
        # 1. Campaign duration analysis
        durations = [ad.get('total_days_shown', 0) for ad in ads]
        
        if durations:
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            if avg_duration < 30:
                issues.append('SHORT_CAMPAIGN_DURATIONS')
                score += 2
            elif avg_duration < 60:
                issues.append('MODERATE_CAMPAIGN_DURATIONS')
                score += 1
            
            if max_duration < 90:
                issues.append('NO_LONG_TERM_CAMPAIGNS')
                score += 2
        
        # 2. Campaign overlap analysis (indicates strategic planning)
        overlapping_campaigns = 0
        for i, ad1 in enumerate(ads):
            for ad2 in ads[i+1:]:
                try:
                    start1 = datetime.fromisoformat(ad1.get('first_shown_datetime', '').replace('Z', '+00:00'))
                    end1 = datetime.fromisoformat(ad1.get('last_shown_datetime', '').replace('Z', '+00:00'))
                    start2 = datetime.fromisoformat(ad2.get('first_shown_datetime', '').replace('Z', '+00:00'))
                    end2 = datetime.fromisoformat(ad2.get('last_shown_datetime', '').replace('Z', '+00:00'))
                    
                    if start1 <= end2 and start2 <= end1:  # Overlap exists
                        overlapping_campaigns += 1
                except:
                    continue
        
        total_possible_overlaps = len(ads) * (len(ads) - 1) // 2
        overlap_ratio = overlapping_campaigns / total_possible_overlaps if total_possible_overlaps > 0 else 0
        
        if overlap_ratio < 0.2:
            issues.append('SEQUENTIAL_ONLY_CAMPAIGNS')
            score += 2
        elif overlap_ratio < 0.4:
            issues.append('LIMITED_CAMPAIGN_OVERLAP')
            score += 1
        
        return {
            'issues': issues,
            'score': score,
            'details': {
                'average_duration': avg_duration if durations else 0,
                'max_duration': max_duration if durations else 0,
                'overlap_ratio': overlap_ratio
            }
        }
    
    def _analyze_competitive_gaps(self, ads: List[Dict]) -> Dict:
        """Analyze gaps vs competitive best practices"""
        issues = []
        score = 0
        
        # 1. Video adoption
        video_ads = sum(1 for ad in ads if ad.get('format') == 'video')
        video_ratio = video_ads / len(ads) if ads else 0
        
        if video_ratio == 0:
            issues.append('NO_VIDEO_ADVERTISING')
            score += 3
        elif video_ratio < 0.3:
            issues.append('LOW_VIDEO_ADOPTION')
            score += 2
        
        # 2. Recency competitive gap
        now = datetime.now()
        recent_ads = 0
        
        for ad in ads:
            try:
                last_shown = datetime.fromisoformat(ad.get('last_shown_datetime', '').replace('Z', '+00:00'))
                if (now - last_shown.replace(tzinfo=None)).days <= 30:
                    recent_ads += 1
            except:
                continue
        
        recent_ratio = recent_ads / len(ads) if ads else 0
        
        if recent_ratio < 0.3:
            issues.append('OUTDATED_CAMPAIGN_PORTFOLIO')
            score += 2
        elif recent_ratio < 0.5:
            issues.append('MIXED_CAMPAIGN_FRESHNESS')
            score += 1
        
        return {
            'issues': issues,
            'score': score,
            'details': {
                'video_adoption_ratio': video_ratio,
                'recent_campaign_ratio': recent_ratio
            }
        }
    
    def _calculate_revenue_impact(self, vulnerability_score: int) -> str:
        """Calculate estimated revenue impact based on vulnerability score"""
        if vulnerability_score >= 8:
            return 'CRITICAL'  # 25-40% revenue opportunity
        elif vulnerability_score >= 6:
            return 'HIGH'      # 15-25% revenue opportunity  
        elif vulnerability_score >= 4:
            return 'MEDIUM'    # 8-15% revenue opportunity
        elif vulnerability_score >= 2:
            return 'LOW'       # 3-8% revenue opportunity
        else:
            return 'MINIMAL'   # <3% revenue opportunity

# Example usage:
"""
analyzer = AdIntelligenceAnalyzer()
vulnerability_report = analyzer.analyze_ad_vulnerabilities(transparency_data)

print(f"Vulnerability Score: {vulnerability_report['vulnerability_score']}/10")
print(f"Revenue Impact: {vulnerability_report['revenue_impact']}")
print(f"Primary Issues: {vulnerability_report['primary_issues']}")
"""
