"""
Enhanced CSV Prospect Adapter for ARCO.

This adapter processes Apollo CSV exports and other prospect data sources,
integrating with the existing ARCO architecture and error handling system.
Features:
- Batch processing with configurable batch sizes
- Rate limiting to prevent API overload
- Integration with existing error handling system
- Real-time progress tracking and reporting
- Robust CSV parsing with field mapping
- Duplicate detection and handling
"""

import csv
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator, Tuple
from datetime import datetime
import re
import time
import uuid
from dataclasses import dataclass, field

from arco.models.prospect import Prospect, Technology, Contact
from arco.core.error_handler import ProcessingErrorHandler, with_error_handling, RetryConfig
from arco.utils.progress_tracker import ProgressTracker, ProgressStage
from arco.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing."""
    batch_size: int = 50
    rate_limit_delay: float = 0.1  # seconds between batches
    max_concurrent_batches: int = 3
    enable_progress_tracking: bool = True
    enable_duplicate_detection: bool = True
    save_intermediate_results: bool = True


@dataclass
class ProcessingStats:
    """Statistics for CSV processing."""
    total_rows: int = 0
    successful_parses: int = 0
    failed_parses: int = 0
    duplicates_found: int = 0
    processing_time: float = 0.0
    batches_processed: int = 0
    errors: List[str] = field(default_factory=list)
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_rows == 0:
            return 0.0
        return (self.successful_parses / self.total_rows) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "total_rows": self.total_rows,
            "successful_parses": self.successful_parses,
            "failed_parses": self.failed_parses,
            "duplicates_found": self.duplicates_found,
            "processing_time": self.processing_time,
            "batches_processed": self.batches_processed,
            "success_rate": self.get_success_rate(),
            "errors": self.errors
        }


class EnhancedCSVProspectAdapter:
    """
    Enhanced CSV adapter for processing Apollo exports and other prospect data.
    
    Features:
    - Batch processing with configurable batch sizes
    - Rate limiting to prevent system overload
    - Integration with existing error handling system
    - Real-time progress tracking and reporting
    - Robust CSV parsing with field mapping
    - Duplicate detection and handling
    - Async processing for better performance
    """
    
    def __init__(self, 
                 csv_path: str, 
                 config: Optional[BatchProcessingConfig] = None,
                 error_handler: Optional[ProcessingErrorHandler] = None):
        """
        Initialize the enhanced CSV adapter.
        
        Args:
            csv_path: Path to the CSV file
            config: Batch processing configuration
            error_handler: Optional error handler for robust processing
        """
        self.csv_path = Path(csv_path)
        self.config = config or BatchProcessingConfig()
        self.error_handler = error_handler or ProcessingErrorHandler()
        self.progress_tracker = ProgressTracker()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Processing state
        self.stats = ProcessingStats()
        self.processed_domains = set()  # For duplicate detection
        self.session_id = str(uuid.uuid4())[:8]
        
        # Apollo CSV field mappings
        self.apollo_field_mapping = {
            'company_name': ['Company', 'Company Name', 'Company Name for Emails'],
            'domain': ['Website'],
            'industry': ['Industry'],
            'employee_count': ['# Employees', 'Number of Employees'],
            'country': ['Company Country'],
            'city': ['Company City'],
            'state': ['Company State'],
            'phone': ['Company Phone'],
            'linkedin': ['Company Linkedin Url'],
            'technologies': ['Technologies'],
            'funding': ['Total Funding', 'Latest Funding Amount'],
            'revenue': ['Annual Revenue'],
            'description': ['Short Description'],
            'founded_year': ['Founded Year']
        }
        
        self._logger.info(f"🚀 Enhanced CSV Adapter initialized - Session: {self.session_id}")
        self._logger.info(f"📊 Config: batch_size={self.config.batch_size}, "
                         f"rate_limit={self.config.rate_limit_delay}s, "
                         f"max_concurrent={self.config.max_concurrent_batches}")
    
    async def load_prospects_async(self) -> Tuple[List[Prospect], ProcessingStats]:
        """
        Load all prospects from CSV file with async batch processing.
        
        Returns:
            Tuple of (prospects list, processing statistics)
        """
        start_time = time.time()
        self._logger.info(f"🔍 Starting async prospect loading from {self.csv_path}")
        
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        prospects = []
        
        try:
            # Count total rows first for progress tracking
            total_rows = await self._count_csv_rows()
            self.stats.total_rows = total_rows
            
            self._logger.info(f"📊 Processing {total_rows} rows in batches of {self.config.batch_size}")
            
            # Process CSV in batches
            async for batch_prospects, batch_stats in self._process_csv_in_batches():
                prospects.extend(batch_prospects)
                self._update_stats(batch_stats)
                
                # Rate limiting between batches
                if self.config.rate_limit_delay > 0:
                    await asyncio.sleep(self.config.rate_limit_delay)
            
            # Final statistics
            self.stats.processing_time = time.time() - start_time
            
            self._logger.info(f"✅ Async processing complete - Session: {self.session_id}")
            self._log_final_stats()
            
            return prospects, self.stats
            
        except Exception as e:
            self.stats.processing_time = time.time() - start_time
            self.stats.errors.append(f"Critical error: {str(e)}")
            self._logger.error(f"❌ Failed to load CSV: {e}")
            raise
    
    def load_prospects(self, batch_size: Optional[int] = None) -> List[Prospect]:
        """
        Synchronous wrapper for async prospect loading.
        
        Args:
            batch_size: Override default batch size
            
        Returns:
            List of Prospect objects
        """
        if batch_size:
            self.config.batch_size = batch_size
        
        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            prospects, stats = loop.run_until_complete(self.load_prospects_async())
            return prospects
        finally:
            loop.close()
    
    async def _count_csv_rows(self) -> int:
        """Count total rows in CSV for progress tracking."""
        try:
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as file:
                return sum(1 for _ in csv.DictReader(file))
        except Exception as e:
            self._logger.warning(f"Could not count CSV rows: {e}")
            return 0
    
    async def _process_csv_in_batches(self) -> AsyncIterator[Tuple[List[Prospect], Dict[str, int]]]:
        """Process CSV file in batches with error handling."""
        
        with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.DictReader(file)
            
            batch = []
            batch_stats = {"successful": 0, "failed": 0, "duplicates": 0}
            row_count = 0
            
            for row in reader:
                row_count += 1
                
                try:
                    # Parse prospect with error handling
                    prospect = await self._parse_prospect_row_async(row)
                    
                    if prospect:
                        # Check for duplicates
                        if self.config.enable_duplicate_detection:
                            if prospect.domain in self.processed_domains:
                                batch_stats["duplicates"] += 1
                                self._logger.debug(f"Duplicate found: {prospect.domain}")
                                continue
                            else:
                                self.processed_domains.add(prospect.domain)
                        
                        batch.append(prospect)
                        batch_stats["successful"] += 1
                        
                        # Update progress tracking
                        if self.config.enable_progress_tracking:
                            await self._update_progress_tracking(prospect, row_count)
                    
                except Exception as e:
                    batch_stats["failed"] += 1
                    error_msg = f"Row {row_count}: {str(e)}"
                    self.stats.errors.append(error_msg)
                    self._logger.warning(f"Failed to parse row {row_count}: {e}")
                
                # Yield batch when full
                if len(batch) >= self.config.batch_size:
                    self._logger.debug(f"📦 Processing batch {self.stats.batches_processed + 1} "
                                     f"({len(batch)} prospects)")
                    yield batch, batch_stats
                    
                    # Reset for next batch
                    batch = []
                    batch_stats = {"successful": 0, "failed": 0, "duplicates": 0}
                    self.stats.batches_processed += 1
            
            # Yield remaining prospects
            if batch:
                self._logger.debug(f"📦 Processing final batch ({len(batch)} prospects)")
                yield batch, batch_stats
                self.stats.batches_processed += 1
    
    @with_error_handling("parse_prospect_row", "csv_adapter")
    async def _parse_prospect_row_async(self, row: Dict[str, str]) -> Optional[Prospect]:
        """
        Parse a single CSV row into a Prospect object with async error handling.
        
        Args:
            row: CSV row as dictionary
            
        Returns:
            Prospect object or None if parsing fails
        """
        try:
            # Extract basic company information
            company_name = self._get_field_value(row, 'company_name')
            domain = self._get_field_value(row, 'domain')
            
            if not company_name and not domain:
                return None
            
            # Clean domain
            if domain:
                domain = self._clean_domain(domain)
            
            # Create prospect (adapting to existing model structure)
            prospect = Prospect(
                domain=domain or f"{company_name.replace(' ', '').lower()}.com" if company_name else "unknown.com",
                company_name=company_name,
                website=f"https://{domain}" if domain else None,
                description=self._get_field_value(row, 'description'),
                industry=self._get_field_value(row, 'industry'),
                employee_count=self._parse_int(self._get_field_value(row, 'employee_count')),
                revenue=self._parse_revenue(self._get_field_value(row, 'revenue')),
                country=self._get_field_value(row, 'country'),
                city=self._get_field_value(row, 'city')
            )
            
            # Parse technologies
            technologies_str = self._get_field_value(row, 'technologies')
            if technologies_str:
                prospect.technologies = self._parse_technologies(technologies_str)
            
            return prospect
            
        except Exception as e:
            self._logger.warning(f"Failed to parse prospect row: {e}")
            raise  # Re-raise for error handler
    
    async def _update_progress_tracking(self, prospect: Prospect, row_number: int):
        """Update progress tracking for processed prospect."""
        try:
            # Add lead to progress tracker
            lead_id = self.progress_tracker.add_lead(
                domain=prospect.domain,
                company_name=prospect.company_name
            )
            
            # Update stage to imported
            self.progress_tracker.update_stage(
                lead_id=lead_id,
                stage=ProgressStage.IMPORTED,
                metadata={
                    "source": "apollo_csv",
                    "csv_file": str(self.csv_path.name),
                    "row_number": row_number,
                    "session_id": self.session_id,
                    "industry": prospect.industry,
                    "employee_count": prospect.employee_count,
                    "country": prospect.country
                }
            )
            
        except Exception as e:
            self._logger.warning(f"Failed to update progress tracking: {e}")
    
    def _update_stats(self, batch_stats: Dict[str, int]):
        """Update processing statistics."""
        self.stats.successful_parses += batch_stats["successful"]
        self.stats.failed_parses += batch_stats["failed"]
        self.stats.duplicates_found += batch_stats["duplicates"]
    
    def _log_final_stats(self):
        """Log final processing statistics."""
        stats_dict = self.stats.to_dict()
        
        self._logger.info(f"📊 Processing Statistics - Session: {self.session_id}")
        self._logger.info(f"   Total rows: {stats_dict['total_rows']}")
        self._logger.info(f"   Successful: {stats_dict['successful_parses']}")
        self._logger.info(f"   Failed: {stats_dict['failed_parses']}")
        self._logger.info(f"   Duplicates: {stats_dict['duplicates_found']}")
        self._logger.info(f"   Success rate: {stats_dict['success_rate']:.1f}%")
        self._logger.info(f"   Processing time: {stats_dict['processing_time']:.2f}s")
        self._logger.info(f"   Batches processed: {stats_dict['batches_processed']}")
        
        if self.stats.errors:
            self._logger.warning(f"   Errors encountered: {len(self.stats.errors)}")
            for error in self.stats.errors[:5]:  # Show first 5 errors
                self._logger.warning(f"     - {error}")
            if len(self.stats.errors) > 5:
                self._logger.warning(f"     ... and {len(self.stats.errors) - 5} more errors")
    
    def get_processing_report(self) -> Dict[str, Any]:
        """Get comprehensive processing report."""
        return {
            "session_id": self.session_id,
            "csv_file": str(self.csv_path),
            "config": {
                "batch_size": self.config.batch_size,
                "rate_limit_delay": self.config.rate_limit_delay,
                "max_concurrent_batches": self.config.max_concurrent_batches,
                "enable_progress_tracking": self.config.enable_progress_tracking,
                "enable_duplicate_detection": self.config.enable_duplicate_detection
            },
            "statistics": self.stats.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    

    
    def _get_field_value(self, row: Dict[str, str], field_type: str) -> Optional[str]:
        """Get field value using field mapping."""
        possible_fields = self.apollo_field_mapping.get(field_type, [])
        
        for field in possible_fields:
            if field in row and row[field] and row[field].strip():
                return row[field].strip()
        
        return None
    
    def _clean_domain(self, domain: str) -> str:
        """Clean and normalize domain."""
        if not domain:
            return ""
        
        # Remove protocol
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^www\.', '', domain)
        
        # Remove trailing slash and paths
        domain = domain.split('/')[0]
        
        # Remove port numbers
        domain = domain.split(':')[0]
        
        return domain.lower().strip()
    
    def _parse_int(self, value: Optional[str]) -> int:
        """Parse integer value safely."""
        if not value:
            return 0
        
        try:
            # Remove non-numeric characters except digits
            cleaned = re.sub(r'[^\d]', '', str(value))
            return int(cleaned) if cleaned else 0
        except (ValueError, TypeError):
            return 0
    
    def _parse_revenue(self, value: Optional[str]) -> Optional[int]:
        """Parse revenue value safely."""
        if not value or value.lower() in ['', 'unknown', 'n/a', 'null']:
            return None
        
        try:
            # Handle revenue ranges like "$1M - $5M"
            value = str(value).upper()
            
            # Extract numbers and multipliers
            if 'M' in value:
                numbers = re.findall(r'(\d+(?:\.\d+)?)', value)
                if numbers:
                    return int(float(numbers[0]) * 1_000_000)
            elif 'K' in value:
                numbers = re.findall(r'(\d+(?:\.\d+)?)', value)
                if numbers:
                    return int(float(numbers[0]) * 1_000)
            else:
                # Try to parse as direct number
                cleaned = re.sub(r'[^\d]', '', value)
                return int(cleaned) if cleaned else None
                
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _parse_funding(self, value: Optional[str]) -> Optional[int]:
        """Parse funding value safely."""
        return self._parse_revenue(value)  # Same logic as revenue
    
    def _parse_technologies(self, technologies_str: str) -> List[Technology]:
        """Parse technologies string into Technology objects."""
        if not technologies_str:
            return []
        
        technologies = []
        
        # Split by comma and clean
        tech_names = [tech.strip() for tech in technologies_str.split(',') if tech.strip()]
        
        for tech_name in tech_names:
            # Categorize technology
            category = self._categorize_technology(tech_name)
            
            technology = Technology(
                name=tech_name,
                category=category,
                detection_confidence=0.8  # High confidence from Apollo data
            )
            technologies.append(technology)
        
        return technologies
    
    def _categorize_technology(self, tech_name: str) -> str:
        """Categorize technology based on name."""
        tech_lower = tech_name.lower()
        
        # Analytics
        if any(keyword in tech_lower for keyword in ['analytics', 'tracking', 'tag manager', 'pixel']):
            return 'Analytics'
        
        # E-commerce
        elif any(keyword in tech_lower for keyword in ['shopify', 'woocommerce', 'magento', 'commerce']):
            return 'E-commerce'
        
        # Email/Marketing
        elif any(keyword in tech_lower for keyword in ['klaviyo', 'mailchimp', 'email', 'marketing']):
            return 'Email Marketing'
        
        # Payment
        elif any(keyword in tech_lower for keyword in ['paypal', 'stripe', 'payment', 'afterpay']):
            return 'Payment'
        
        # Cloud/Hosting
        elif any(keyword in tech_lower for keyword in ['aws', 'cloudflare', 'hosting', 'cdn']):
            return 'Infrastructure'
        
        # Social
        elif any(keyword in tech_lower for keyword in ['facebook', 'twitter', 'social', 'instagram']):
            return 'Social Media'
        
        # Development
        elif any(keyword in tech_lower for keyword in ['jquery', 'react', 'angular', 'node', 'python']):
            return 'Development'
        
        else:
            return 'Other'


async def load_all_apollo_csvs_async(directory: str = "arco", 
                                   config: Optional[BatchProcessingConfig] = None) -> Tuple[List[Prospect], Dict[str, Any]]:
    """
    Load prospects from all Apollo CSV files in the directory with enhanced async processing.
    
    Args:
        directory: Directory containing Apollo CSV files
        config: Batch processing configuration
        
    Returns:
        Tuple of (combined list of all prospects, comprehensive processing report)
    """
    logger.info(f"🔍 Loading all Apollo CSVs from {directory} with enhanced processing")
    
    directory_path = Path(directory)
    csv_files = list(directory_path.glob("apollo-*.csv"))
    
    if not csv_files:
        logger.warning(f"No Apollo CSV files found in {directory}")
        return [], {"error": "No CSV files found", "files_processed": 0}
    
    all_prospects = []
    processing_reports = []
    total_stats = ProcessingStats()
    
    # Use default config if none provided
    if config is None:
        config = BatchProcessingConfig()
    
    logger.info(f"📊 Found {len(csv_files)} Apollo CSV files to process")
    
    for i, csv_file in enumerate(csv_files, 1):
        logger.info(f"📄 Processing file {i}/{len(csv_files)}: {csv_file.name}")
        
        try:
            # Create enhanced adapter for each file
            adapter = EnhancedCSVProspectAdapter(str(csv_file), config)
            
            # Process file asynchronously
            prospects, stats = await adapter.load_prospects_async()
            
            # Collect results
            all_prospects.extend(prospects)
            processing_reports.append(adapter.get_processing_report())
            
            # Aggregate statistics
            total_stats.total_rows += stats.total_rows
            total_stats.successful_parses += stats.successful_parses
            total_stats.failed_parses += stats.failed_parses
            total_stats.duplicates_found += stats.duplicates_found
            total_stats.processing_time += stats.processing_time
            total_stats.batches_processed += stats.batches_processed
            total_stats.errors.extend(stats.errors)
            
            logger.info(f"✅ Loaded {len(prospects)} prospects from {csv_file.name} "
                       f"(Success rate: {stats.get_success_rate():.1f}%)")
            
        except Exception as e:
            error_msg = f"Failed to load {csv_file.name}: {str(e)}"
            total_stats.errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            continue
    
    # Remove duplicates based on domain (global deduplication)
    logger.info("🔄 Performing global deduplication...")
    unique_prospects = {}
    duplicates_removed = 0
    
    for prospect in all_prospects:
        key = prospect.domain or prospect.company_name
        if key not in unique_prospects:
            unique_prospects[key] = prospect
        else:
            duplicates_removed += 1
    
    final_prospects = list(unique_prospects.values())
    
    # Create comprehensive report
    comprehensive_report = {
        "session_summary": {
            "files_found": len(csv_files),
            "files_processed": len(processing_reports),
            "total_prospects_loaded": len(all_prospects),
            "unique_prospects_after_deduplication": len(final_prospects),
            "global_duplicates_removed": duplicates_removed,
            "total_processing_time": total_stats.processing_time,
            "overall_success_rate": total_stats.get_success_rate()
        },
        "aggregated_statistics": total_stats.to_dict(),
        "file_reports": processing_reports,
        "config_used": {
            "batch_size": config.batch_size,
            "rate_limit_delay": config.rate_limit_delay,
            "max_concurrent_batches": config.max_concurrent_batches,
            "enable_progress_tracking": config.enable_progress_tracking,
            "enable_duplicate_detection": config.enable_duplicate_detection
        },
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"🎯 Enhanced processing complete:")
    logger.info(f"   Files processed: {len(processing_reports)}/{len(csv_files)}")
    logger.info(f"   Total prospects loaded: {len(all_prospects)}")
    logger.info(f"   Unique prospects: {len(final_prospects)}")
    logger.info(f"   Global duplicates removed: {duplicates_removed}")
    logger.info(f"   Overall success rate: {total_stats.get_success_rate():.1f}%")
    logger.info(f"   Total processing time: {total_stats.processing_time:.2f}s")
    
    return final_prospects, comprehensive_report


def load_all_apollo_csvs(directory: str = "arco", 
                        config: Optional[BatchProcessingConfig] = None) -> List[Prospect]:
    """
    Synchronous wrapper for enhanced Apollo CSV loading.
    
    Args:
        directory: Directory containing Apollo CSV files
        config: Batch processing configuration
        
    Returns:
        Combined list of all prospects
    """
    # Run async method in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        prospects, report = loop.run_until_complete(
            load_all_apollo_csvs_async(directory, config)
        )
        return prospects
    finally:
        loop.close()


# Backward compatibility alias
CSVProspectAdapter = EnhancedCSVProspectAdapter