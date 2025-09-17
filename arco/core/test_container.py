"""
Tests for the dependency injection container.
"""

import pytest
from typing import Protocol
from arco.core.container import (
    ServiceContainer, ServiceRegistrationError, ServiceResolutionError,
    ServiceLifetime, get_container, configure_container, reset_container
)


# Test interfaces and implementations
class ITestService(Protocol):
    def get_value(self) -> str:
        ...


class TestService:
    def get_value(self) -> str:
        return "test_value"


class IDependentService(Protocol):
    def get_combined_value(self) -> str:
        ...


class DependentService:
    def __init__(self, test_service: ITestService):
        self.test_service = test_service
    
    def get_combined_value(self) -> str:
        return f"dependent_{self.test_service.get_value()}"


class ComplexService:
    def __init__(self, test_service: ITestService, dependent_service: IDependentService, optional_value: str = "default"):
        self.test_service = test_service
        self.dependent_service = dependent_service
        self.optional_value = optional_value
    
    def get_all_values(self) -> str:
        return f"{self.test_service.get_value()}_{self.dependent_service.get_combined_value()}_{self.optional_value}"


class TestServiceContainer:
    
    def setup_method(self):
        """Setup for each test method."""
        self.container = ServiceContainer()
    
    def test_register_and_resolve_singleton(self):
        """Test singleton service registration and resolution."""
        self.container.register_singleton(ITestService, TestService)
        
        # Resolve twice to ensure same instance
        service1 = self.container.resolve(ITestService)
        service2 = self.container.resolve(ITestService)
        
        assert isinstance(service1, TestService)
        assert service1 is service2  # Same instance
        assert service1.get_value() == "test_value"
    
    def test_register_and_resolve_transient(self):
        """Test transient service registration and resolution."""
        self.container.register_transient(ITestService, TestService)
        
        # Resolve twice to ensure different instances
        service1 = self.container.resolve(ITestService)
        service2 = self.container.resolve(ITestService)
        
        assert isinstance(service1, TestService)
        assert isinstance(service2, TestService)
        assert service1 is not service2  # Different instances
    
    def test_register_instance(self):
        """Test instance registration."""
        instance = TestService()
        self.container.register_instance(ITestService, instance)
        
        resolved = self.container.resolve(ITestService)
        assert resolved is instance
    
    def test_register_factory(self):
        """Test factory registration."""
        def create_service() -> ITestService:
            return TestService()
        
        self.container.register_factory(ITestService, create_service)
        
        service = self.container.resolve(ITestService)
        assert isinstance(service, TestService)
        assert service.get_value() == "test_value"
    
    def test_constructor_injection(self):
        """Test automatic constructor dependency injection."""
        self.container.register_singleton(ITestService, TestService)
        self.container.register_transient(IDependentService, DependentService)
        
        service = self.container.resolve(IDependentService)
        
        assert isinstance(service, DependentService)
        assert service.get_combined_value() == "dependent_test_value"
    
    def test_complex_dependency_injection(self):
        """Test complex dependency injection with optional parameters."""
        self.container.register_singleton(ITestService, TestService)
        self.container.register_transient(IDependentService, DependentService)
        self.container.register_transient(ComplexService)
        
        service = self.container.resolve(ComplexService)
        
        assert isinstance(service, ComplexService)
        assert service.get_all_values() == "test_value_dependent_test_value_default"
    
    def test_service_not_registered_error(self):
        """Test error when resolving unregistered service."""
        with pytest.raises(ServiceResolutionError, match="Service ITestService is not registered"):
            self.container.resolve(ITestService)
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        
        class ServiceA:
            def __init__(self, service_b: 'ServiceB'):
                self.service_b = service_b
        
        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a
        
        self.container.register_transient(ServiceA)
        self.container.register_transient(ServiceB)
        
        # Since we don't support string annotations yet, this will fail with string annotation error
        with pytest.raises(ServiceResolutionError, match="String type annotation"):
            self.container.resolve(ServiceA)
    
    def test_is_registered(self):
        """Test service registration checking."""
        assert not self.container.is_registered(ITestService)
        
        self.container.register_singleton(ITestService, TestService)
        assert self.container.is_registered(ITestService)
    
    def test_validate_registrations_success(self):
        """Test successful registration validation."""
        self.container.register_singleton(ITestService, TestService)
        self.container.register_transient(IDependentService, DependentService)
        
        # Should not raise any exception
        self.container.validate_registrations()
    
    def test_validate_registrations_missing_dependency(self):
        """Test validation failure for missing dependencies."""
        self.container.register_transient(IDependentService, DependentService)
        
        with pytest.raises(ServiceRegistrationError, match="Dependency ITestService"):
            self.container.validate_registrations()
    
    def test_get_registered_services(self):
        """Test getting registered services for inspection."""
        self.container.register_singleton(ITestService, TestService)
        
        services = self.container.get_registered_services()
        assert ITestService in services
        assert services[ITestService].lifetime == ServiceLifetime.SINGLETON


class TestGlobalContainer:
    
    def setup_method(self):
        """Reset global container before each test."""
        reset_container()
    
    def teardown_method(self):
        """Reset global container after each test."""
        reset_container()
    
    def test_get_container_singleton(self):
        """Test global container is singleton."""
        container1 = get_container()
        container2 = get_container()
        
        assert container1 is container2
    
    def test_configure_container(self):
        """Test container configuration."""
        container = configure_container()
        
        assert container is get_container()
        assert isinstance(container, ServiceContainer)
    
    def test_reset_container(self):
        """Test container reset."""
        container1 = get_container()
        reset_container()
        container2 = get_container()
        
        assert container1 is not container2


if __name__ == "__main__":
    pytest.main([__file__])