"""
Progress Tracker for ARCO.

This module contains the implementation of the progress tracking system,
which monitors the progress of lead enrichment, analysis, and outreach.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from pathlib import Path
import threading
import uuid

from arco.utils.logger import get_logger

logger = get_logger(__name__)

class ProgressStage:
    """Enum-like class for progress stages."""
    
    IMPORTED = "imported"
    ENRICHED_BASIC = "enriched_basic"
    ENRICHED_ADVANCED = "enriched_advanced"
    ANALYZED = "analyzed"
    QUALIFIED = "qualified"
    REGISTERED_CRM = "registered_crm"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    MEETING = "meeting"
    OPPORTUNITY = "opportunity"
    CLIENT = "client"
    
    @classmethod
    def get_all_stages(cls) -> List[str]:
        """Get all stages in order."""
        return [
            cls.IMPORTED,
            cls.ENRICHED_BASIC,
            cls.ENRICHED_ADVANCED,
            cls.ANALYZED,
            cls.QUALIFIED,
            cls.REGISTERED_CRM,
            cls.CONTACTED,
            cls.ENGAGED,
            cls.MEETING,
            cls.OPPORTUNITY,
            cls.CLIENT
        ]
    
    @classmethod
    def get_stage_index(cls, stage: str) -> int:
        """Get the index of a stage."""
        stages = cls.get_all_stages()
        if stage in stages:
            return stages.index(stage)
        return -1
    
    @classmethod
    def get_next_stage(cls, stage: str) -> Optional[str]:
        """Get the next stage after the given stage."""
        stages = cls.get_all_stages()
        idx = cls.get_stage_index(stage)
        if idx >= 0 and idx < len(stages) - 1:
            return stages[idx + 1]
        return None
    
    @classmethod
    def get_previous_stage(cls, stage: str) -> Optional[str]:
        """Get the previous stage before the given stage."""
        stages = cls.get_all_stages()
        idx = cls.get_stage_index(stage)
        if idx > 0:
            return stages[idx - 1]
        return None


class LeadProgress:
    """Class to track the progress of a lead."""
    
    def __init__(self, lead_id: str, domain: str, company_name: str = None):
        """
        Initialize the lead progress.
        
        Args:
            lead_id: Unique identifier for the lead
            domain: Domain of the lead
            company_name: Company name of the lead
        """
        self.lead_id = lead_id
        self.domain = domain
        self.company_name = company_name or domain
        self.current_stage = ProgressStage.IMPORTED
        self.stage_history = {
            ProgressStage.IMPORTED: {
                "timestamp": datetime.now().isoformat(),
                "duration": 0
            }
        }
        self.metadata = {}
        self.errors = []
    
    def update_stage(self, stage: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Update the stage of the lead.
        
        Args:
            stage: New stage
            metadata: Additional metadata for the stage
            
        Returns:
            True if the stage was updated, False otherwise
        """
        if stage not in ProgressStage.get_all_stages():
            logger.warning(f"Invalid stage: {stage}")
            return False
        
        # Calculate duration in previous stage
        if self.current_stage in self.stage_history:
            prev_timestamp = datetime.fromisoformat(self.stage_history[self.current_stage]["timestamp"])
            duration = (datetime.now() - prev_timestamp).total_seconds()
            self.stage_history[self.current_stage]["duration"] = duration
        
        # Update current stage
        self.current_stage = stage
        
        # Add to stage history
        self.stage_history[stage] = {
            "timestamp": datetime.now().isoformat(),
            "duration": 0
        }
        
        # Update metadata
        if metadata:
            if stage not in self.metadata:
                self.metadata[stage] = {}
            self.metadata[stage].update(metadata)
        
        logger.info(f"Lead {self.lead_id} ({self.domain}) updated to stage: {stage}")
        return True
    
    def add_error(self, stage: str, error_message: str, error_details: Dict[str, Any] = None) -> None:
        """
        Add an error to the lead.
        
        Args:
            stage: Stage where the error occurred
            error_message: Error message
            error_details: Additional error details
        """
        error = {
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "message": error_message,
            "details": error_details or {}
        }
        self.errors.append(error)
        logger.error(f"Lead {self.lead_id} ({self.domain}) error in stage {stage}: {error_message}")
    
    def get_stage_duration(self, stage: str) -> float:
        """
        Get the duration spent in a stage.
        
        Args:
            stage: Stage to get duration for
            
        Returns:
            Duration in seconds
        """
        if stage not in self.stage_history:
            return 0
        
        if stage == self.current_stage:
            # Calculate current duration
            timestamp = datetime.fromisoformat(self.stage_history[stage]["timestamp"])
            return (datetime.now() - timestamp).total_seconds()
        
        return self.stage_history[stage]["duration"]
    
    def get_total_duration(self) -> float:
        """
        Get the total duration since the lead was imported.
        
        Returns:
            Total duration in seconds
        """
        if ProgressStage.IMPORTED not in self.stage_history:
            return 0
        
        timestamp = datetime.fromisoformat(self.stage_history[ProgressStage.IMPORTED]["timestamp"])
        return (datetime.now() - timestamp).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "lead_id": self.lead_id,
            "domain": self.domain,
            "company_name": self.company_name,
            "current_stage": self.current_stage,
            "stage_history": self.stage_history,
            "metadata": self.metadata,
            "errors": self.errors,
            "total_duration": self.get_total_duration()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeadProgress':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            LeadProgress object
        """
        lead = cls(
            lead_id=data.get("lead_id", str(uuid.uuid4())),
            domain=data.get("domain", ""),
            company_name=data.get("company_name")
        )
        lead.current_stage = data.get("current_stage", ProgressStage.IMPORTED)
        lead.stage_history = data.get("stage_history", {})
        lead.metadata = data.get("metadata", {})
        lead.errors = data.get("errors", [])
        return lead


class ProgressTracker:
    """Class to track the progress of multiple leads."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProgressTracker, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the progress tracker.
        
        Args:
            storage_dir: Directory to store progress data
        """
        if self._initialized:
            return
        
        self.storage_dir = storage_dir or os.path.join("data", "progress")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.leads = {}
        self.last_save_time = 0
        self.auto_save_interval = 60  # seconds
        
        # Load existing progress data
        self._load_progress()
        
        self._initialized = True
    
    def _get_progress_file_path(self) -> str:
        """
        Get the path to the progress file.
        
        Returns:
            Path to the progress file
        """
        return os.path.join(self.storage_dir, "lead_progress.json")
    
    def _load_progress(self) -> None:
        """Load progress data from file."""
        file_path = self._get_progress_file_path()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for lead_data in data.get("leads", []):
                        lead = LeadProgress.from_dict(lead_data)
                        self.leads[lead.lead_id] = lead
                logger.info(f"Loaded progress data for {len(self.leads)} leads")
            except Exception as e:
                logger.error(f"Error loading progress data: {e}")
    
    def _save_progress(self) -> None:
        """Save progress data to file."""
        file_path = self._get_progress_file_path()
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "leads": [lead.to_dict() for lead in self.leads.values()]
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.last_save_time = time.time()
            logger.info(f"Saved progress data for {len(self.leads)} leads")
        except Exception as e:
            logger.error(f"Error saving progress data: {e}")
    
    def _auto_save(self) -> None:
        """Auto-save progress data if interval has elapsed."""
        if time.time() - self.last_save_time > self.auto_save_interval:
            self._save_progress()
    
    def add_lead(self, domain: str, company_name: str = None, lead_id: str = None) -> str:
        """
        Add a new lead to track.
        
        Args:
            domain: Domain of the lead
            company_name: Company name of the lead
            lead_id: Optional lead ID, generated if not provided
            
        Returns:
            Lead ID
        """
        lead_id = lead_id or str(uuid.uuid4())
        
        # Check if lead already exists
        for existing_lead in self.leads.values():
            if existing_lead.domain == domain:
                return existing_lead.lead_id
        
        # Create new lead
        lead = LeadProgress(lead_id, domain, company_name)
        self.leads[lead_id] = lead
        
        # Auto-save
        self._auto_save()
        
        return lead_id
    
    def update_stage(self, lead_id: str, stage: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Update the stage of a lead.
        
        Args:
            lead_id: Lead ID
            stage: New stage
            metadata: Additional metadata for the stage
            
        Returns:
            True if the stage was updated, False otherwise
        """
        if lead_id not in self.leads:
            logger.warning(f"Lead not found: {lead_id}")
            return False
        
        result = self.leads[lead_id].update_stage(stage, metadata)
        
        # Auto-save
        self._auto_save()
        
        return result
    
    def add_error(self, lead_id: str, stage: str, error_message: str, error_details: Dict[str, Any] = None) -> bool:
        """
        Add an error to a lead.
        
        Args:
            lead_id: Lead ID
            stage: Stage where the error occurred
            error_message: Error message
            error_details: Additional error details
            
        Returns:
            True if the error was added, False otherwise
        """
        if lead_id not in self.leads:
            logger.warning(f"Lead not found: {lead_id}")
            return False
        
        self.leads[lead_id].add_error(stage, error_message, error_details)
        
        # Auto-save
        self._auto_save()
        
        return True
    
    def get_lead(self, lead_id: str) -> Optional[LeadProgress]:
        """
        Get a lead by ID.
        
        Args:
            lead_id: Lead ID
            
        Returns:
            LeadProgress object or None if not found
        """
        return self.leads.get(lead_id)
    
    def get_lead_by_domain(self, domain: str) -> Optional[LeadProgress]:
        """
        Get a lead by domain.
        
        Args:
            domain: Domain
            
        Returns:
            LeadProgress object or None if not found
        """
        for lead in self.leads.values():
            if lead.domain == domain:
                return lead
        return None
    
    def get_leads_by_stage(self, stage: str) -> List[LeadProgress]:
        """
        Get all leads in a specific stage.
        
        Args:
            stage: Stage
            
        Returns:
            List of LeadProgress objects
        """
        return [lead for lead in self.leads.values() if lead.current_stage == stage]
    
    def get_stage_counts(self) -> Dict[str, int]:
        """
        Get counts of leads in each stage.
        
        Returns:
            Dictionary with stage counts
        """
        counts = {stage: 0 for stage in ProgressStage.get_all_stages()}
        for lead in self.leads.values():
            counts[lead.current_stage] = counts.get(lead.current_stage, 0) + 1
        return counts
    
    def get_average_durations(self) -> Dict[str, float]:
        """
        Get average durations in each stage.
        
        Returns:
            Dictionary with average durations
        """
        durations = {stage: [] for stage in ProgressStage.get_all_stages()}
        for lead in self.leads.values():
            for stage in lead.stage_history:
                if stage != lead.current_stage:  # Only include completed stages
                    durations[stage].append(lead.stage_history[stage]["duration"])
        
        # Calculate averages
        averages = {}
        for stage, values in durations.items():
            if values:
                averages[stage] = sum(values) / len(values)
            else:
                averages[stage] = 0
        
        return averages
    
    def get_conversion_rates(self) -> Dict[str, float]:
        """
        Get conversion rates between stages.
        
        Returns:
            Dictionary with conversion rates
        """
        stages = ProgressStage.get_all_stages()
        counts = self.get_stage_counts()
        
        rates = {}
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]
            
            current_count = counts.get(current_stage, 0)
            next_count = counts.get(next_stage, 0)
            
            if current_count > 0:
                rates[f"{current_stage}_to_{next_stage}"] = next_count / current_count
            else:
                rates[f"{current_stage}_to_{next_stage}"] = 0
        
        return rates
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of progress tracking.
        
        Returns:
            Dictionary with summary information
        """
        return {
            "total_leads": len(self.leads),
            "stage_counts": self.get_stage_counts(),
            "average_durations": self.get_average_durations(),
            "conversion_rates": self.get_conversion_rates(),
            "timestamp": datetime.now().isoformat()
        }
    
    def save(self) -> None:
        """Save progress data to file."""
        self._save_progress()
    
    def clear(self) -> None:
        """Clear all progress data."""
        self.leads = {}
        self._save_progress()
        logger.info("Cleared all progress data")


# Global instance
tracker = ProgressTracker()