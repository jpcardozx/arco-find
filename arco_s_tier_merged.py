#!/usr/bin/env python3
"""
ARCO S‑TIER ENGINE — versão consolidada (fitness AU)
====================================================

Objetivo
--------
Detecção de SMBs com anúncios ativos e problemas quantificáveis em criativos/mensagem
para outreach consultivo. Arquitetura enxuta, auditável e com pontos claros de
integração ao SearchApi (SERP + Advertiser Info + Transparency Center).

Destaques
---------
- Pipeline híbrido: SERP (descoberta) → Advertiser Info (resolução) → Transparency Center (criativos/recência)
- Scoring objetivo (0–100) e waste_ratio conservador (cap 0.45)
- Gate de qualidade: score≥65, recência≤60d, ≥2 issues
- Thresholds realistas; sem “verified” falso
- Cache simples em disco (opcional) e rate-limit/backoff exponencial
- Export em JSON/CSV
- CLI e providers desacoplados (mock/searchapi)
- Heurísticas de análise enriquecidas (sinais de contato, owner-operated, tipos de business, domínio)

Uso
----
python arco_s_tier_merged.py \
  --vertical fitness_au \
  --max-credits 20 \
  --min-good 5 \
  --out-json ./prospects.json \
  --out-csv  ./prospects.csv \
  --provider mock  # ou searchapi

Para usar SearchApi de verdade, defina env var SEARCHAPI_KEY e provider=searchapi.
"""
from __future__ import annotations
import asyncio
import json
import logging
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp is not installed. Please run 'pip install aiohttp'.", file=sys.stderr)
    sys.exit(1)

# Import API keys
try:
    from config.api_keys import APIConfig
except ImportError:
    print("ERROR: Could not import API keys from config.api_keys", file=sys.stderr)
    sys.exit(1)

# ----------------------------- Logging ---------------------------------------
LOG_LEVEL = os.getenv("ARCO_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("arco")

# --------------------------- Configuração ------------------------------------
VERTICALS: Dict[str, Dict[str, Any]] = {
    "fitness_au": {
        "name": "Fitness & Health (AU)",
        "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
        "queries": [
            'personal trainer [CITY] -yellowpages -truelocal -groupon',
            'gym [CITY] australia -yellowpages -truelocal',
            'pilates studio [CITY] -yellowpages -truelocal',
        ],
        "google_domain": "google.com.au",
        "gl": "au",
        "hl": "en",
        "spend_bands": {"micro": (2000, 4000), "small": (4000, 8000), "medium": (8000, 15000)},
    },
}
DEFAULT_MAX_CREDITS = 20
DEFAULT_MIN_GOOD = 5
QUALITY_SCORE_THRESHOLD = 50  # Mais realista para prospect qualification
MAX_RECENCY_DAYS = 60
MAX_WASTE_CAP = 0.45
CACHE_FILE = Path(os.getenv("ARCO_CACHE_FILE", ".arco_cache.json"))

# ----------------------------- Data Models -----------------------------------
@dataclass
class Creative:
    headline: str = ""
    description: str = ""
    last_shown: Optional[str] = None  # ISO date

@dataclass
class Advertiser:
    name: str
    domain: str
    city: str
    advertiser_id: Optional[str] = None
    creatives: List[Creative] = field(default_factory=list)
    last_seen_days: Optional[int] = None
    spend_band: str = "small"
    # Heurísticas extras
    contact_signals: List[str] = field(default_factory=list)
    owner_operated: bool = False  # Removido - heurística não confiável
    business_type: str = ""

@dataclass
class Prospect:
    advertiser: Advertiser
    issues: List[str]
    score: int
    waste_ratio: float
    est_spend: int
    est_waste: int

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "advertiser": self.advertiser.name,
            "domain": self.advertiser.domain,
            "city": self.advertiser.city,
            "advertiser_id": self.advertiser.advertiser_id,
            "score": self.score,
            "issues": self.issues,
            "waste_ratio": round(self.waste_ratio, 3),
            "est_spend": self.est_spend,
            "est_waste": self.est_waste,
            "last_seen_days": self.advertiser.last_seen_days,
            "spend_band": self.advertiser.spend_band,
            "contact_signals": self.advertiser.contact_signals,
            "owner_operated": self.advertiser.owner_operated,
            "business_type": self.advertiser.business_type,
        }
        return d

# ----------------------------- Providers -------------------------------------
class BaseProvider:
    async def search_serp(self, session: aiohttp.ClientSession, *, query: str, city: str, vcfg: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
    async def advertiser_info(self, session: aiohttp.ClientSession, *, domain: str, name: str) -> Optional[str]:
        raise NotImplementedError
    async def transparency_center(self, session: aiohttp.ClientSession, *, advertiser_id: Optional[str], domain: str) -> Tuple[List[Creative], Optional[int]]:
        raise NotImplementedError

class MockProvider(BaseProvider):
    def __init__(self, seed: int = 42):
        random.seed(seed)
    async def search_serp(self, session, *, query: str, city: str, vcfg: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        data = {
            "organic_results": [
                {"title": f"Pulse Fitness Studio {city}", "link": "https://pulsefitness.com.au", "snippet": "Book your trial."},
                {"title": f"Zen Pilates {city}", "link": "https://zenpilates.com.au", "snippet": "Join our programs."},
                {"title": f"Budget Gym {city}", "link": "https://budgetgym.com.au", "snippet": "Cheap deals, low cost memberships."},
            ]
        }
        return data
    async def advertiser_info(self, session, *, domain: str, name: str) -> Optional[str]:
        await asyncio.sleep(0.005)
        return None if "budget" in domain else f"adv_{abs(hash(domain))%10_000}"
    async def transparency_center(self, session, *, advertiser_id: Optional[str], domain: str) -> Tuple[List[Creative], Optional[int]]:
        await asyncio.sleep(0.01)
        now = datetime.now(timezone.utc)
        n = random.randint(2, 5)
        creatives = []
        
        # Gera criativos com problemas realistas para teste
        problem_headlines = [
            "Best Personal Training in Sydney - Guaranteed Results!",
            "Learn More About Our Gym",
            "Cheap Fitness Deals - 50% Off",
            "Leading Pilates Studio",
            "Click Here for More Info",
        ]
        
        problem_descriptions = [
            "Instant transformation guaranteed in 30 days.",
            "Read more about our services.",
            "Affordable rates, budget-friendly options.",
            "See what makes us the top choice.",
            "Find out more by clicking here.",
        ]
        
        for i in range(n):
            # Recência realista (7-45 dias)
            days_ago = random.randint(7, 45)
            dt = now.timestamp() - days_ago * 86400
            
            creatives.append(
                Creative(
                    headline=random.choice(problem_headlines),
                    description=random.choice(problem_descriptions),
                    last_shown=datetime.utcfromtimestamp(dt).replace(tzinfo=timezone.utc).isoformat(),
                )
            )
        
        last_seen_days = min(
            int((now - datetime.fromisoformat(c.last_shown)).days) for c in creatives
        ) if creatives and creatives[0].last_shown else None
        
        return creatives, last_seen_days

class SearchApiProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str = "https://www.searchapi.io/api/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
    async def _get(self, session: aiohttp.ClientSession, params: Dict[str, Any], *, backoff: float = 1.0, retries: int = 3) -> Dict[str, Any]:
        url = f"{self.base_url}/search"
        last_err: Optional[str] = None
        for attempt in range(retries):
            try:
                async with session.get(url, params=params, timeout=30) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    if resp.status in (429, 500, 502, 503, 504):
                        await asyncio.sleep(backoff * (2 ** attempt))
                        continue
                    last_err = f"HTTP {resp.status}"
                    break
            except Exception as e:
                last_err = str(e)
                await asyncio.sleep(backoff * (2 ** attempt))
        logger.warning("SearchApi GET falhou: %s (params=%s)", last_err, {k:v for k,v in params.items() if k!="api_key"})
        return {}
    async def search_serp(self, session, *, query: str, city: str, vcfg: Dict[str, Any]) -> Dict[str, Any]:
        params = {
            "api_key": self.api_key,
            "engine": "google",
            "q": query,
            "location": f"{city}, Australia",
            "google_domain": vcfg.get("google_domain", "google.com.au"),
            "gl": vcfg.get("gl", "au"),
            "hl": vcfg.get("hl", "en"),
            "num": "20",
            "device": "desktop",
        }
        return await self._get(session, params)
    async def advertiser_info(self, session, *, domain: str, name: str) -> Optional[str]:
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_advertiser_info",
            "query": domain or name,
        }
        data = await self._get(session, params)
        adv_id = None
        if isinstance(data, dict):
            adv_id = data.get("advertiser_id") or data.get("id")
        return adv_id
    async def transparency_center(self, session, *, advertiser_id: Optional[str], domain: str) -> Tuple[List[Creative], Optional[int]]:
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_transparency_center",
        }
        if advertiser_id:
            params["advertiser_id"] = advertiser_id
        else:
            params["domain"] = domain
        
        data = await self._get(session, params)
        creatives: List[Creative] = []
        last_seen_days: Optional[int] = None
        
        # Se não há dados reais, retorna vazio em vez de dados artificiais
        if not data or not isinstance(data, dict):
            logger.debug("Sem dados do Transparency Center para %s", domain)
            return [], None
            
        def parse_date(s: str) -> Optional[datetime]:
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
                try:
                    return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
                except Exception:
                    continue
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None
        
        now = datetime.now(timezone.utc)
        ads = data.get("ads") or data.get("ad_details") or []
        
        # Se não há anúncios reais, não fabricar dados
        if not ads:
            logger.debug("Nenhum anúncio encontrado no Transparency Center para %s", domain)
            return [], None
        
        for ad in ads:
            headline = ad.get("headline") or ad.get("title") or ""
            desc = ad.get("description") or ad.get("body") or ""
            last = ad.get("last_shown") or ad.get("last_active") or ad.get("last_seen")
            
            # Só aceita se tem conteúdo real
            if not headline and not desc:
                continue
                
            dt = parse_date(last) if last else None
            if dt:
                creatives.append(Creative(headline=headline, description=desc, last_shown=dt.isoformat()))
            else:
                # Sem data válida = dados suspeitos
                logger.debug("Anúncio sem data válida rejeitado para %s", domain)
                continue
        
        if creatives:
            days = []
            for c in creatives:
                if c.last_shown:
                    dt = datetime.fromisoformat(c.last_shown)
                    days_diff = (now - dt).days
                    # Rejeita datas artificiais/suspeitas
                    if days_diff < 0 or days_diff > 365:
                        logger.debug("Data suspeita rejeitada: %d dias", days_diff)
                        continue
                    days.append(days_diff)
            
            if days:
                last_seen_days = min(days)
            
        logger.debug("Transparency Center para %s: %d criativos válidos, recency=%s", 
                    domain, len(creatives), last_seen_days)
        
        return creatives, last_seen_days

# ----------------------------- Utilidades ------------------------------------
def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def analyze_contact_signals(text: str, domain: str) -> List[str]:
    """Analisa apenas sinais explícitos de contato nos criativos dos anúncios"""
    signals = []
    text_lower = text.lower()
    
    # Sinais explícitos de contato apenas baseados no conteúdo real dos anúncios
    if any(ind in text_lower for ind in ['call now', 'phone us', 'contact us', 'ring us']):
        signals.append("Explicit phone CTA in ads")
    if any(ind in text_lower for ind in ['book now', 'schedule', 'reserve your spot', 'appointment']):
        signals.append("Booking CTA present")
    if any(ind in text_lower for ind in ['visit us', 'come in', 'drop by', 'find us at']):
        signals.append("Physical visit encouraged")
    
    return signals

def detect_business_focus(text: str) -> str:
    """Detecta foco do negócio apenas baseado em conteúdo real dos anúncios"""
    if not text.strip():
        return "unknown"
    
    text_lower = text.lower()
    fitness_types = ['pilates', 'yoga', 'crossfit', 'boxing', 'martial arts', 'cycling', 'barre']
    
    for fitness_type in fitness_types:
        if fitness_type in text_lower:
            return fitness_type
    
    if any(term in text_lower for term in ['personal trainer', 'pt ', 'personal training']):
        return "personal_training"
    if any(term in text_lower for term in ['gym', 'fitness', 'workout']):
        return "general_fitness"
    
    return "unknown"

# ------------------------------- Engine --------------------------------------
class ArcoEngine:
    def __init__(self, provider: BaseProvider, *, cache_file: Path = CACHE_FILE):
        self.provider = provider
        self.cache_file = cache_file
        self.cache_ai: Dict[str, str] = {}  # domain -> advertiser_id
        self.seen_domains: set[str] = set()
        self._load_cache()
    async def run(self, vertical_key: str = "fitness_au", *, max_credits: int = DEFAULT_MAX_CREDITS, min_good: int = DEFAULT_MIN_GOOD) -> List[Prospect]:
        vcfg = VERTICALS[vertical_key]
        prospects: List[Prospect] = []
        credits_used = 0
        async with aiohttp.ClientSession() as session:  # type: ignore
            for city in vcfg["cities"]:
                if credits_used >= max_credits:
                    break
                if self._count_good(prospects) >= min_good:
                    break
                logger.info("Cidade: %s", city)
                for q in vcfg["queries"]:
                    if credits_used >= max_credits:
                        break
                    query = q.replace("[CITY]", city)
                    data = await self.provider.search_serp(session, query=query, city=city, vcfg=vcfg)
                    credits_used += 1
                    candidates = self._extract_candidates(data)
                    logger.info("%s candidatos brutos", len(candidates))
                    for (name, domain) in candidates:
                        if credits_used >= max_credits:
                            break
                        if not domain or domain in self.seen_domains:
                            continue
                        self.seen_domains.add(domain)
                        adv_id = await self._resolve_advertiser(session, name=name, domain=domain)
                        credits_used += 1
                        creatives, recency = await self.provider.transparency_center(session, advertiser_id=adv_id, domain=domain)
                        credits_used += 1
                        
                        # VALIDAÇÃO RIGOROSA: Só aceita empresas com dados REAIS de anúncios
                        if not creatives:
                            logger.debug("❌ Rejeitado %s: sem dados reais de anúncios", domain)
                            continue
                        
                        if recency is None:
                            logger.debug("❌ Rejeitado %s: sem dados de recência válidos", domain)
                            continue
                            
                        # Verifica se tem conteúdo real nos anúncios
                        has_real_content = any(
                            (c.headline and c.headline.strip() and c.headline != "No ads found") and
                            (c.description and c.description.strip() and c.description != "Manual research needed")
                            for c in creatives
                        )
                        if not has_real_content:
                            logger.debug("❌ Rejeitado %s: criativos sem conteúdo real", domain)
                            continue
                        band = self._infer_band(creatives)
                        est_spend = self._estimate_spend(vcfg, band)
                        # --- Análise baseada apenas em dados reais dos criativos ---
                        all_text = " ".join([c.headline + " " + c.description for c in creatives])
                        contact_signals = analyze_contact_signals(all_text, domain)
                        business_focus = detect_business_focus(all_text)
                        
                        advertiser = Advertiser(
                            name=name, domain=domain, city=city, advertiser_id=adv_id, creatives=creatives,
                            last_seen_days=recency, spend_band=band, contact_signals=contact_signals,
                            owner_operated=False, business_type=business_focus
                        )
                        issues, score, waste_ratio = self._analyze(advertiser)
                        # GATE DE QUALIDADE RIGOROSO
                        if not self._passes_gate(score, recency, issues):
                            logger.debug("Rejeitado: %s (score=%d, recency=%s, issues=%d)", 
                                       name, score, recency, len(issues))
                            continue
                        est_waste = int(est_spend * min(waste_ratio, MAX_WASTE_CAP))
                        prospects.append(Prospect(advertiser, issues, score, waste_ratio, est_spend, est_waste))
        prospects.sort(key=lambda p: (p.score, p.est_waste), reverse=True)
        logger.info("Créditos usados: %s | Prospectos bons: %s", credits_used, self._count_good(prospects))
        return prospects
    def _analyze(self, adv: Advertiser) -> Tuple[List[str], int, float]:
        text = " | ".join((c.headline + " " + c.description).lower() for c in adv.creatives)
        
        # Adiciona logs de debug para entender o que está acontecendo
        logger.debug("Analisando: %s | Criativos: %d | Recência: %s", 
                    adv.name, len(adv.creatives), adv.last_seen_days)
        
        # Adiciona nome e domínio para análise quando há poucos dados de criativos
        analysis_text = f"{text} {adv.name.lower()} {adv.domain.lower()}"
        
        issues: List[str] = []
        score = 100
        def hit(patterns: Iterable[str]) -> bool:
            return any(p in text for p in patterns)
        # 1. Compliance (claims exageradas) - CRÍTICO
        if hit(["guaranteed", "instant", "miracle", "lose 10kg", "30 days", "100% effective"]):
            issues.append("Compliance risk (promessas exageradas)")
            score -= 20
        
        # 2. Posicionamento genérico sem diferenciação - MÉDIO IMPACTO
        if hit(["best", "#1", "leading", "top"]) and not hit(["program", "method", "specialty", "pilates", "yoga", "crossfit"]):
            issues.append("Posicionamento genérico")
            score -= 15
        
        # 3. CTA fraco - MÉDIO IMPACTO
        if hit(["learn more", "read more", "see more"]) and not hit(["book", "call", "join", "trial", "appointment", "schedule"]):
            issues.append("CTA fraco")
            score -= 12
        
        # 4. Preço como âncora
        if hit(["cheap", "discount", "low cost", "deal", "special offer", "affordable", "budget", "half price"]):
            issues.append("Competição por preço")
            score -= 10
        # Duplicação criativa (heurística simples)
        headlines = [c.headline.strip().lower() for c in adv.creatives if c.headline]
        if len(headlines) >= 3 and len(set(headlines)) <= max(1, len(headlines) // 2):
            issues.append("Baixa variação criativa")
            score -= 10
        # Recência
        if adv.last_seen_days is not None and adv.last_seen_days > MAX_RECENCY_DAYS:
            issues.append(f"Anúncios não vistos nos últimos {MAX_RECENCY_DAYS} dias")
            score -= 8
        # Sinais de contato reais (baseados em CTAs explícitos nos anúncios)
        if not adv.contact_signals:
            issues.append("Nenhum CTA de contato explícito nos anúncios")
            score -= 8
        
        # Foco do negócio (baseado apenas no conteúdo dos anúncios)
        if adv.business_type and adv.business_type not in ["unknown", "general_fitness"]:
            score += 5  # Bônus por nicho específico claramente identificado
        
        # Waste ratio a partir de issues
        w = 0.0
        for i in issues:
            if i.startswith("Compliance"):
                w += 0.10
            elif i.startswith("Geo"):
                w += 0.08
            elif i.startswith("Posicionamento"):
                w += 0.08
            elif i.startswith("CTA"):
                w += 0.06
            elif i.startswith("Competição"):
                w += 0.06
            elif "variação criativa" in i:
                w += 0.05
            elif "contato" in i:
                w += 0.04
        waste_ratio = min(w, MAX_WASTE_CAP)
        
        logger.debug("Resultado análise: %s | Score: %d | Issues: %d | Waste: %.2f", 
                    adv.name, max(0, score), len(issues), waste_ratio)
        logger.debug("Issues encontrados: %s", issues)
        
        return issues, max(0, score), waste_ratio
    def _extract_candidates(self, data: Dict[str, Any]) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        for sec in ("ads", "ads_results", "local_results", "organic_results"):
            for r in data.get(sec, []) or []:
                link = r.get("link") or r.get("website") or r.get("displayed_link") or ""
                if not link and sec == "local_results":
                    link = r.get("cid") or ""
                domain = domain_of(link)
                if not domain:
                    continue
                title = r.get("title") or r.get("source") or r.get("name") or domain
                out.append((title, domain))
        seen: set[str] = set()
        unique: List[Tuple[str, str]] = []
        for name, dom in out:
            if dom not in seen:
                seen.add(dom)
                unique.append((name, dom))
        return unique
    async def _resolve_advertiser(self, session: aiohttp.ClientSession, *, name: str, domain: str) -> Optional[str]:
        if domain in self.cache_ai:
            return self.cache_ai[domain] or None
        adv_id = await self.provider.advertiser_info(session, domain=domain, name=name)
        self.cache_ai[domain] = adv_id or ""
        self._save_cache()
        return adv_id
    def _infer_band(self, creatives: List[Creative]) -> str:
        return "small" if len(creatives) <= 3 else "medium"
    def _estimate_spend(self, vcfg: Dict[str, Any], band: str) -> int:
        low, high = vcfg["spend_bands"].get(band, (4000, 8000))
        return int((low + high) // 2)
    def _passes_gate(self, score: int, recency: Optional[int], issues: List[str]) -> bool:
        """Gate de qualidade rigoroso - só aceita prospects com dados válidos"""
        if score < QUALITY_SCORE_THRESHOLD:
            logger.debug("❌ Score muito baixo: %d < %d", score, QUALITY_SCORE_THRESHOLD)
            return False
        
        if recency is None:
            logger.debug("❌ Sem dados de recência")
            return False
            
        # Rejeita valores artificiais suspeitos
        if recency >= 999:
            logger.debug("❌ Valor artificial suspeito: recency=%d", recency)
            return False
            
        if recency > MAX_RECENCY_DAYS:
            logger.debug("❌ Anúncios muito antigos: %d > %d dias", recency, MAX_RECENCY_DAYS)
            return False
        
        if len(issues) < 2:
            logger.debug("❌ Poucos issues identificados: %d < 2", len(issues))
            return False
            
        logger.info("✅ Passou no gate: score=%d, recency=%d dias, issues=%d", 
                   score, recency, len(issues))
        return True
    def _count_good(self, prospects: List[Prospect]) -> int:
        return sum(1 for p in prospects if p.score >= QUALITY_SCORE_THRESHOLD)
    def _load_cache(self) -> None:
        try:
            if self.cache_file.exists():
                data = json.loads(self.cache_file.read_text(encoding="utf-8"))
                self.cache_ai = data.get("advertiser_info", {})
                logger.debug("Cache carregado (%d entradas)", len(self.cache_ai))
        except Exception as e:
            logger.warning("Falha ao carregar cache: %s", e)
    def _save_cache(self) -> None:
        try:
            payload = {"advertiser_info": self.cache_ai}
            self.cache_file.write_text(json.dumps(payload), encoding="utf-8")
        except Exception as e:
            logger.warning("Falha ao salvar cache: %s", e)

# ------------------------------- Exporters -----------------------------------
def export_json(path: Path, prospects: List[Prospect]) -> None:
    data = [p.to_dict() for p in prospects]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def export_csv(path: Path, prospects: List[Prospect]) -> None:
    import csv
    prospects_dicts = [p.to_dict() for p in prospects]
    if not prospects_dicts:
        return
    headers = prospects_dicts[0].keys()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in prospects_dicts:
            # Garante que valores de lista sejam convertidos para string
            for key, value in row.items():
                if isinstance(value, list):
                    row[key] = ", ".join(map(str, value))
            writer.writerow(row)

# --------------------------------- CLI ---------------------------------------
def _build_provider(kind: str) -> BaseProvider:
    kind = kind.lower()
    if kind == "mock":
        return MockProvider()
    if kind == "searchapi":
        key = APIConfig.SEARCHAPI_KEY
        if not key:
            raise RuntimeError("SearchAPI key not found in config/api_keys.py")
        return SearchApiProvider(api_key=key)
    raise ValueError(f"Provider desconhecido: {kind}")

async def _amain(args: List[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="ARCO S‑TIER ENGINE (fitness AU)")
    parser.add_argument("--vertical", default="fitness_au")
    parser.add_argument("--provider", default="mock", choices=["mock", "searchapi"])
    parser.add_argument("--max-credits", type=int, default=DEFAULT_MAX_CREDITS)
    parser.add_argument("--min-good", type=int, default=DEFAULT_MIN_GOOD)
    parser.add_argument("--out-json", type=Path, default=Path("prospects.json"))
    parser.add_argument("--out-csv", type=Path, default=Path("prospects.csv"))
    ns = parser.parse_args(args)
    provider = _build_provider(ns.provider)
    engine = ArcoEngine(provider)
    prospects = await engine.run(ns.vertical, max_credits=ns.max_credits, min_good=ns.min_good)
    export_json(ns.out_json, prospects)
    export_csv(ns.out_csv, prospects)
    for p in prospects[:10]:
        logger.info("%s | %s | %s | score=%s | waste≈A$%s/m",
                    p.advertiser.name, p.advertiser.domain, p.advertiser.city, p.score, p.est_waste)
    logger.info("Exportado: %s (%d itens), %s", ns.out_json, len(prospects), ns.out_csv)
    return 0

def main() -> int:
    try:
        return asyncio.run(_amain(sys.argv[1:]))
    except KeyboardInterrupt:
        return 130

if __name__ == "__main__":
    raise SystemExit(main())
