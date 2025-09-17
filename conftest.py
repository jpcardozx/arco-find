"""
Configuração do pytest para o projeto ARCO.

Este arquivo contém configurações e fixtures para os testes do projeto ARCO.
"""

import os
import sys
import pytest
import logging
import asyncio
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao sys.path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

# Registrar marcadores
def pytest_configure(config):
    """Configurar pytest."""
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio coroutine")
    config.addinivalue_line("markers", "integration: mark a test that requires external services")
    config.addinivalue_line("markers", "slow: mark a test that takes a long time to run")
    config.addinivalue_line("markers", "unit: mark a unit test")
    config.addinivalue_line("markers", "functional: mark a functional test")

# Fixture para event loop
@pytest.fixture
def event_loop():
    """Criar uma instância do event loop padrão para cada teste."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Fixture para diretório temporário
@pytest.fixture
def temp_dir(tmp_path):
    """Criar um diretório temporário para testes."""
    return tmp_path

# Fixture para configuração de teste
@pytest.fixture
def test_config():
    """Fornecer configuração de teste."""
    return {
        "api_keys": {
            "test": "test_key"
        },
        "endpoints": {
            "test": "https://example.com/api"
        },
        "timeouts": {
            "default": 5,
            "long": 30
        }
    }

# Fixture para mock de cliente HTTP
@pytest.fixture
def mock_http_client(mocker):
    """Fornecer um mock de cliente HTTP."""
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    return mock_client

# Fixture para mock de banco de dados
@pytest.fixture
def mock_db(mocker):
    """Fornecer um mock de banco de dados."""
    mock_db = mocker.MagicMock()
    mock_db.query.return_value = []
    mock_db.insert.return_value = 1
    mock_db.update.return_value = True
    mock_db.delete.return_value = True
    return mock_db

# Fixture para mock de cache
@pytest.fixture
def mock_cache(mocker):
    """Fornecer um mock de cache."""
    mock_cache = mocker.MagicMock()
    mock_cache.get.return_value = None
    mock_cache.set.return_value = True
    return mock_cache

# Fixture para mock de logger
@pytest.fixture
def mock_logger(mocker):
    """Fornecer um mock de logger."""
    return mocker.patch("logging.getLogger")

# Fixture para mock de configuração
@pytest.fixture
def mock_config(mocker):
    """Fornecer um mock de configuração."""
    mock_config = mocker.MagicMock()
    mock_config.get.return_value = "test_value"
    return mock_config

# Fixture para mock de pipeline
@pytest.fixture
def mock_pipeline(mocker):
    """Fornecer um mock de pipeline."""
    mock_pipeline = mocker.MagicMock()
    mock_pipeline.run.return_value = {"status": "success"}
    return mock_pipeline

# Fixture para mock de engine
@pytest.fixture
def mock_engine(mocker):
    """Fornecer um mock de engine."""
    mock_engine = mocker.MagicMock()
    mock_engine.process.return_value = {"status": "success"}
    return mock_engine

# Fixture para mock de integração
@pytest.fixture
def mock_integration(mocker):
    """Fornecer um mock de integração."""
    mock_integration = mocker.MagicMock()
    mock_integration.fetch.return_value = {"status": "success"}
    return mock_integration

# Fixture para mock de modelo
@pytest.fixture
def mock_model(mocker):
    """Fornecer um mock de modelo."""
    mock_model = mocker.MagicMock()
    mock_model.validate.return_value = True
    mock_model.to_dict.return_value = {"id": 1, "name": "test"}
    return mock_model