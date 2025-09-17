#!/usr/bin/env python3
"""
Sistema de Análise Avançada de Leads
Análise profunda baseada em critérios de negócio sofisticados
"""

import pandas as pd
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedLeadAnalyzer:
    def __init__(self):
        self.segment_weights = {
            'moda_fashion': {'revenue_multiplier': 1.2, 'urgency': 'alta', 'seasonality': 'alta'},
            'alimentacao_saude': {'revenue_multiplier': 1.1, 'urgency': 'media', 'seasonality': 'baixa'},
            'tecnologia_eletronicos': {'revenue_multiplier': 1.3, 'urgency': 'alta', 'seasonality': 'media'},
            'casa_decoracao': {'revenue_multiplier': 1.0, 'urgency': 'media', 'seasonality': 'alta'},
            'pet_care': {'revenue_multiplier': 0.9, 'urgency': 'baixa', 'seasonality': 'baixa'},
            'joias_acessorios': {'revenue_multiplier': 1.1, 'urgency': 'media', 'seasonality': 'alta'},
            'esportes_fitness': {'revenue_multiplier': 1.0, 'urgency': 'media', 'seasonality': 'media'},
            'arte_cultura': {'revenue_multiplier': 0.8, 'urgency': 'baixa', 'seasonality': 'baixa'},
            'automotivo': {'revenue_multiplier': 1.2, 'urgency': 'alta', 'seasonality': 'media'},
            'impressao_grafica': {'revenue_multiplier': 1.1, 'urgency': 'media', 'seasonality': 'baixa'}
        }
        
        self.tech_stack_scores = {
            'shopify': {'performance_risk': 0.3, 'optimization_potential': 0.8},
            'vtex': {'performance_risk': 0.4, 'optimization_potential': 0.7},
            'woocommerce': {'performance_risk': 0.6, 'optimization_potential': 0.9},
            'magento': {'performance_risk': 0.5, 'optimization_potential': 0.8},
            'custom': {'performance_risk': 0.7, 'optimization_potential': 0.6}
        }
        
        self.brazil_priority_states = {
            'Sao Paulo': 1.0, 'State of Sao Paulo': 1.0,
            'Rio de Janeiro': 0.9, 'State of Rio de Janeiro': 0.9,
            'Minas Gerais': 0.8, 'State of Minas Gerais': 0.8,
            'Santa Catarina': 0.7, 'State of Santa Catarina': 0.7,
            'Rio Grande do Sul': 0.7,
            'Parana': 0.6, 'Goias': 0.6, 'Bahia': 0.6
        }

    def classify_segment(self, company_data: Dict) -> str:
        """Classifica o segmento específico da empresa"""
        keywords = str(company_data.get('Keywords', '')).lower()
        description = str(company_data.get('Short Description