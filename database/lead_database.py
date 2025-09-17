#!/usr/bin/env python3
"""
🗄️ LEAD DATABASE - Componente 2  
PostgreSQL simples para lead tracking

FOCO: Database básico mas efetivo para operação
- Não complexo, só funcional
- Track status: new/contacted/qualified/closed
- Query rápida para KPIs
- Integra com batch processor
"""

import asyncio
import asyncpg
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import os

@dataclass
class Lead:
    """Lead básico para tracking"""
    domain: str
    monthly_saas_waste: int
    estimated_revenue: int
    leak_score: int
    priority: str
    immediate_action: str
    status: str = 'new'  # new/contacted/qualified/closed
    contact_email: Optional[str] = None
    last_contact: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LeadDatabase:
    """
    Simple PostgreSQL database for lead management
    
    Foco: Funcionalidade básica mas robusta
    - Lead tracking
    - Status management  
    - KPI queries
    - Batch import from processor
    """
    
    def __init__(self, connection_string: str = None):
        # Default local PostgreSQL
        self.connection_string = connection_string or "postgresql://postgres:password@localhost:5432/arco_leads"
        self.pool = None
        
        print("🗄️ LEAD DATABASE INITIALIZED")
        print("=" * 40)
        print(f"📊 Target: Simple but effective lead tracking")
        print(f"🔗 Connection: {self.connection_string.split('@')[1] if '@' in self.connection_string else 'Local'}")

    async def initialize(self):
        """Initialize database connection and create tables"""
        
        try:
            self.pool = await asyncpg.create_pool(self.connection_string)
            await self._create_tables()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("💡 Make sure PostgreSQL is running and database exists")
            raise

    async def _create_tables(self):
        """Create simple but effective table structure"""
        
        async with self.pool.acquire() as conn:
            # Main leads table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    domain VARCHAR(255) PRIMARY KEY,
                    monthly_saas_waste INTEGER NOT NULL DEFAULT 0,
                    estimated_revenue INTEGER NOT NULL DEFAULT 0,
                    leak_score INTEGER NOT NULL DEFAULT 0,
                    priority VARCHAR(20) NOT NULL DEFAULT 'low',
                    immediate_action TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'new',
                    contact_email VARCHAR(255),
                    last_contact TIMESTAMP,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Index for fast queries
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
                CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads(priority);
                CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(leak_score DESC);
                CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);
            """)
            
            # Contact log table (simple tracking)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS contact_log (
                    id SERIAL PRIMARY KEY,
                    domain VARCHAR(255) REFERENCES leads(domain),
                    contact_type VARCHAR(50) NOT NULL,
                    message TEXT,
                    response TEXT,
                    contacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    async def insert_leads_batch(self, leads_data: List[Dict[str, Any]]) -> int:
        """Insert batch of leads from processor"""
        
        if not leads_data:
            return 0
        
        async with self.pool.acquire() as conn:
            # Prepare data for insertion
            lead_records = []
            
            for lead_data in leads_data:
                if lead_data.get('success', False):  # Only successful analyses
                    lead_records.append((
                        lead_data['domain'],
                        lead_data.get('monthly_saas_waste', 0),
                        lead_data.get('estimated_revenue', 0),
                        lead_data.get('leak_score', 0),
                        lead_data.get('priority', 'low'),
                        lead_data.get('immediate_action', ''),
                        'new',  # Default status
                        None,   # contact_email
                        None,   # last_contact
                        None,   # notes
                        datetime.now(),  # created_at
                        datetime.now()   # updated_at
                    ))
            
            if not lead_records:
                return 0
            
            # Batch insert with conflict handling
            inserted = await conn.executemany("""
                INSERT INTO leads (
                    domain, monthly_saas_waste, estimated_revenue, leak_score,
                    priority, immediate_action, status, contact_email, last_contact,
                    notes, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (domain) DO UPDATE SET
                    monthly_saas_waste = EXCLUDED.monthly_saas_waste,
                    estimated_revenue = EXCLUDED.estimated_revenue,
                    leak_score = EXCLUDED.leak_score,
                    priority = EXCLUDED.priority,
                    immediate_action = EXCLUDED.immediate_action,
                    updated_at = CURRENT_TIMESTAMP
            """, lead_records)
            
            print(f"📊 Inserted/updated {len(lead_records)} leads")
            return len(lead_records)

    async def get_qualified_leads(self, min_score: int = 75) -> List[Lead]:
        """Get leads with score >= threshold for outreach"""
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM leads 
                WHERE leak_score >= $1 
                AND status IN ('new', 'contacted')
                ORDER BY leak_score DESC, estimated_revenue DESC
            """, min_score)
            
            leads = []
            for row in rows:
                leads.append(Lead(
                    domain=row['domain'],
                    monthly_saas_waste=row['monthly_saas_waste'],
                    estimated_revenue=row['estimated_revenue'],
                    leak_score=row['leak_score'],
                    priority=row['priority'],
                    immediate_action=row['immediate_action'],
                    status=row['status'],
                    contact_email=row['contact_email'],
                    last_contact=row['last_contact'],
                    notes=row['notes'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            
            return leads

    async def update_lead_status(self, domain: str, status: str, notes: str = None) -> bool:
        """Update lead status"""
        
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE leads 
                SET status = $1, notes = $2, updated_at = CURRENT_TIMESTAMP
                WHERE domain = $3
            """, status, notes, domain)
            
            return result != "UPDATE 0"

    async def add_contact_log(self, domain: str, contact_type: str, message: str, response: str = None):
        """Log contact attempt"""
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO contact_log (domain, contact_type, message, response)
                VALUES ($1, $2, $3, $4)
            """, domain, contact_type, message, response)
            
            # Update last_contact in leads table
            await conn.execute("""
                UPDATE leads 
                SET last_contact = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE domain = $1
            """, domain)

    async def get_kpi_summary(self) -> Dict[str, Any]:
        """Get KPI summary for dashboard"""
        
        async with self.pool.acquire() as conn:
            # Total leads by status
            status_counts = await conn.fetch("""
                SELECT status, COUNT(*) as count
                FROM leads 
                GROUP BY status
            """)
            
            # Priority distribution
            priority_counts = await conn.fetch("""
                SELECT priority, COUNT(*) as count
                FROM leads
                GROUP BY priority
            """)
            
            # Revenue potential
            revenue_summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_leads,
                    SUM(monthly_saas_waste) as total_waste,
                    SUM(estimated_revenue) as total_revenue,
                    AVG(leak_score) as avg_score,
                    COUNT(*) FILTER (WHERE leak_score >= 75) as qualified_leads
                FROM leads
            """)
            
            # Recent activity (last 7 days)
            recent_activity = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as new_leads_7d,
                    COUNT(*) FILTER (WHERE status = 'contacted') as contacted_7d
                FROM leads 
                WHERE created_at >= $1
            """, datetime.now() - timedelta(days=7))
            
            return {
                'status_distribution': {row['status']: row['count'] for row in status_counts},
                'priority_distribution': {row['priority']: row['count'] for row in priority_counts},
                'revenue_summary': dict(revenue_summary),
                'recent_activity': dict(recent_activity),
                'last_updated': datetime.now().isoformat()
            }

    async def get_top_opportunities(self, limit: int = 10) -> List[Lead]:
        """Get top opportunities by score and revenue"""
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM leads 
                WHERE status IN ('new', 'contacted')
                ORDER BY 
                    (leak_score * 0.7 + (estimated_revenue / 1000) * 0.3) DESC,
                    leak_score DESC
                LIMIT $1
            """, limit)
            
            leads = []
            for row in rows:
                leads.append(Lead(
                    domain=row['domain'],
                    monthly_saas_waste=row['monthly_saas_waste'],
                    estimated_revenue=row['estimated_revenue'],
                    leak_score=row['leak_score'],
                    priority=row['priority'],
                    immediate_action=row['immediate_action'],
                    status=row['status'],
                    contact_email=row['contact_email'],
                    last_contact=row['last_contact'],
                    notes=row['notes'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            
            return leads

    async def search_leads(self, query: str, status: str = None) -> List[Lead]:
        """Search leads by domain or action"""
        
        async with self.pool.acquire() as conn:
            sql = """
                SELECT * FROM leads 
                WHERE (domain ILIKE $1 OR immediate_action ILIKE $1)
            """
            params = [f"%{query}%"]
            
            if status:
                sql += " AND status = $2"
                params.append(status)
                
            sql += " ORDER BY leak_score DESC LIMIT 50"
            
            rows = await conn.fetch(sql, *params)
            
            leads = []
            for row in rows:
                leads.append(Lead(
                    domain=row['domain'],
                    monthly_saas_waste=row['monthly_saas_waste'],
                    estimated_revenue=row['estimated_revenue'],
                    leak_score=row['leak_score'],
                    priority=row['priority'],
                    immediate_action=row['immediate_action'],
                    status=row['status'],
                    contact_email=row['contact_email'],
                    last_contact=row['last_contact'],
                    notes=row['notes'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            
            return leads

    async def close(self):
        """Close database connection"""
        if self.pool:
            await self.pool.close()

# Demo & Testing
async def demo_lead_database():
    """Demo do lead database"""
    
    print("\n🗄️ LEAD DATABASE DEMO")
    print("=" * 40)
    
    # Note: This demo requires PostgreSQL running
    print("📋 This demo requires PostgreSQL running locally")
    print("🔗 Connection: postgresql://postgres:password@localhost:5432/arco_leads")
    print("💡 Create database first: CREATE DATABASE arco_leads;")
    
    try:
        db = LeadDatabase()
        await db.initialize()
        
        # Sample lead data (from batch processor)
        sample_leads = [
            {
                'domain': 'glossier.com',
                'monthly_saas_waste': 2174,
                'estimated_revenue': 175134,
                'leak_score': 64,
                'priority': 'medium',
                'immediate_action': 'Replace Optimizely with Google Optimize (save $1950/month)',
                'success': True
            },
            {
                'domain': 'sephora.com',
                'monthly_saas_waste': 3250,
                'estimated_revenue': 425000,
                'leak_score': 78,
                'priority': 'high',
                'immediate_action': 'SaaS audit recommended - $3250/month detected',
                'success': True
            }
        ]
        
        # Insert sample leads
        inserted = await db.insert_leads_batch(sample_leads)
        print(f"✅ Inserted {inserted} sample leads")
        
        # Get qualified leads  
        qualified = await db.get_qualified_leads(min_score=60)
        print(f"📊 Qualified leads (score ≥60): {len(qualified)}")
        
        for lead in qualified[:3]:
            print(f"  • {lead.domain}: {lead.leak_score}/100 - ${lead.monthly_saas_waste}/mo waste")
        
        # Get KPIs
        kpis = await db.get_kpi_summary()
        print(f"\n📈 KPI SUMMARY:")
        print(f"  • Total leads: {kpis['revenue_summary']['total_leads']}")
        print(f"  • Total waste: ${kpis['revenue_summary']['total_waste']:,}/month")
        print(f"  • Avg score: {kpis['revenue_summary']['avg_score']:.1f}/100")
        print(f"  • Qualified leads: {kpis['revenue_summary']['qualified_leads']}")
        
        # Update status demo
        if qualified:
            domain = qualified[0].domain
            await db.update_lead_status(domain, 'contacted', 'Initial outreach sent')
            await db.add_contact_log(domain, 'email', 'Initial savings opportunity email', None)
            print(f"✅ Updated {domain} status to 'contacted'")
        
        await db.close()
        print(f"\n✅ Lead database demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure PostgreSQL is running and create database 'arco_leads'")

if __name__ == "__main__":
    asyncio.run(demo_lead_database())
