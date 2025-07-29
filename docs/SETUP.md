# ARCO Setup Guide

## Requirements

- Python 3.8+
- SearchAPI account (Meta Ad Library access)
- Google Cloud account (PageSpeed API)

## Installation

### 1. Clone and Setup

```bash
git clone <repository>
cd arco-find
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\\Scripts\\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create `.env` file:

```env
SEARCHAPI_KEY=your_searchapi_key_here
PAGESPEED_KEY=your_google_api_key_here
```

### 4. Verify Setup

```bash
python -m arco.core.arco_engine --test
```

## API Keys Setup

### SearchAPI

1. Go to [SearchAPI.io](https://searchapi.io)
2. Create account
3. Get API key from dashboard
4. Add to `.env` file

### Google PageSpeed

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable PageSpeed Insights API
3. Create API key
4. Add to `.env` file

## Usage

### Basic Usage

```python
from arco.core.arco_engine import ARCOIntermediateLeadFinder

# Initialize
arco = ARCOIntermediateLeadFinder()

# Search for leads
results = await arco.search_intermediate_leads(
    vertical="legal",
    country="US",
    max_results=10
)
```

### Business Intelligence

```python
# Analyze market opportunities
analysis = await arco.analyze_business_opportunities(
    market="US",
    verticals=["legal", "dental"]
)
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify keys in `.env` file
2. **Rate Limiting**: Built-in backoff handles this automatically
3. **Memory Usage**: Bounded caches prevent memory leaks

### Debug Mode

```bash
export LOG_LEVEL=DEBUG
python -m arco.core.arco_engine
```
