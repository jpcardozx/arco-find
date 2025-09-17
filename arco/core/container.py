"""
Dependency Injection Container for ARCO services.

This module provides a professional dependency injection container that manages
service dependencies and implements constructor injection patterns throughout
the application.
"""

from typing import Dict, Type, TypeVar, Callable, Any, Optional, get_type_hints, Union
import inspect
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceRegistrationError(Exception):
    """Raised when service registration fails."""
    pass


class ServiceResolutionError(Exception):
    """Raised when service resolution fails."""
    pass


class ServiceLifetime:
    """Service lifetime management options."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class ServiceDescriptor:
    """Describes how a service should be registered and resolved."""
    
    def __init__(self, 
                 service_type: Type[T],
                 implementation_type: Optional[Type[T]] = None,
                 factory: Optional[Callable[[], T]] = None,
                 instance: Optional[T] = None,
                 lifetime: str = ServiceLifetime.TRANSIENT):
        self.service_type = service_type
        self.implementation_type = implementation_type or service_type
        self.factory = factory
        self.instance = instance
        self.lifetime = lifetime
        
        # Allow self-registration when only service_type is provided
        if implementation_type is None and factory is None and instance is None:
            self.implementation_type = service_type
        elif not any([implementation_type, factory, instance]):
            raise ServiceRegistrationError(
                f"Service {service_type.__name__} must have implementation, factory, or instance"
            )


class ServiceContainer:
    """
    Professional dependency injection container with constructor injection support.
    
    Features:
    - Service registration with multiple lifetime options
    - Automatic constructor injection
    - Circular dependency detection
    - Service validation
    - Comprehensive error handling
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._resolution_stack: set = set()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_singleton(self, service_type: Type[T], implementation_type: Type[T] = None) -> 'ServiceContainer':
        """Register a service as singleton (one instance per container)."""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        self._logger.debug(f"Registered singleton service: {service_type.__name__}")
        return self
    
    def register_transient(self, service_type: Type[T], implementation_type: Type[T] = None) -> 'ServiceContainer':
        """Register a service as transient (new instance each time)."""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            lifetime=ServiceLifetime.TRANSIENT
        )
        self._services[service_type] = descriptor
        self._logger.debug(f"Registered transient service: {service_type.__name__}")
        return self
    
    def register_instance(self, service_type: Type[T], instance: T) -> 'ServiceContainer':
        """Register a specific instance for a service type."""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            instance=instance,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        self._singletons[service_type] = instance
        self._logger.debug(f"Registered instance for service: {service_type.__name__}")
        return self
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T], 
                        lifetime: str = ServiceLifetime.TRANSIENT) -> 'ServiceContainer':
        """Register a factory function for creating service instances."""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifetime=lifetime
        )
        self._services[service_type] = descriptor
        self._logger.debug(f"Registered factory for service: {service_type.__name__}")
        return self
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance with automatic dependency injection.
        
        Args:
            service_type: The type of service to resolve
            
        Returns:
            An instance of the requested service
            
        Raises:
            ServiceResolutionError: If the service cannot be resolved
        """
        try:
            return self._resolve_service(service_type)
        except Exception as e:
            self._logger.error(f"Failed to resolve service {service_type.__name__}: {e}")
            raise ServiceResolutionError(f"Cannot resolve service {service_type.__name__}: {e}")
    
    def _resolve_service(self, service_type: Type[T]) -> T:
        """Internal service resolution with circular dependency detection."""
        
        # Check for circular dependencies
        if service_type in self._resolution_stack:
            raise ServiceResolutionError(
                f"Circular dependency detected for service {service_type.__name__}"
            )
        
        # Check if service is registered
        if service_type not in self._services:
            raise ServiceResolutionError(f"Service {service_type.__name__} is not registered")
        
        descriptor = self._services[service_type]
        
        # Return existing singleton instance
        if descriptor.lifetime == ServiceLifetime.SINGLETON and service_type in self._singletons:
            return self._singletons[service_type]
        
        # Add to resolution stack for circular dependency detection
        self._resolution_stack.add(service_type)
        
        try:
            # Resolve using registered instance
            if descriptor.instance is not None:
                instance = descriptor.instance
            
            # Resolve using factory
            elif descriptor.factory is not None:
                instance = descriptor.factory()
            
            # Resolve using implementation type with constructor injection
            else:
                instance = self._create_instance_with_injection(descriptor.implementation_type)
            
            # Store singleton instance
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                self._singletons[service_type] = instance
            
            return instance
            
        finally:
            # Remove from resolution stack
            self._resolution_stack.discard(service_type)
    
    def _create_instance_with_injection(self, implementation_type: Type[T]) -> T:
        """Create instance with automatic constructor dependency injection."""
        
        # Get constructor signature
        constructor = implementation_type.__init__
        signature = inspect.signature(constructor)
        
        # Skip 'self' parameter
        parameters = list(signature.parameters.values())[1:]
        
        if not parameters:
            # No dependencies, create simple instance
            return implementation_type()
        
        # Resolve constructor dependencies
        dependencies = {}
        
        for param in parameters:
            # Skip *args and **kwargs parameters
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
                
            param_type = param.annotation
            
            # Skip parameters without type annotations
            if param_type == inspect.Parameter.empty:
                if param.default != inspect.Parameter.empty:
                    continue  # Use default value
                else:
                    raise ServiceResolutionError(
                        f"Parameter '{param.name}' in {implementation_type.__name__} "
                        f"has no type annotation and no default value"
                    )
            
            # Handle string type annotations (forward references)
            if isinstance(param_type, str):
                # For now, skip string annotations as they require complex resolution
                if param.default != inspect.Parameter.empty:
                    continue  # Use default value
                else:
                    raise ServiceResolutionError(
                        f"String type annotation '{param_type}' for parameter '{param.name}' "
                        f"in {implementation_type.__name__} is not supported"
                    )
            
            # Handle Optional types
            if hasattr(param_type, '__origin__') and param_type.__origin__ is Union:
                # Check if it's Optional (Union with None)
                args = param_type.__args__
                if len(args) == 2 and type(None) in args:
                    param_type = next(arg for arg in args if arg is not type(None))
                    try:
                        dependencies[param.name] = self._resolve_service(param_type)
                    except ServiceResolutionError:
                        if param.default != inspect.Parameter.empty:
                            continue  # Use default value
                        dependencies[param.name] = None
                    continue
            
            # Resolve required dependency
            try:
                dependencies[param.name] = self._resolve_service(param_type)
            except ServiceResolutionError:
                if param.default != inspect.Parameter.empty:
                    continue  # Use default value
                raise
        
        # Create instance with resolved dependencies
        return implementation_type(**dependencies)
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def get_registered_services(self) -> Dict[Type, ServiceDescriptor]:
        """Get all registered services for debugging/inspection."""
        return self._services.copy()
    
    def validate_registrations(self) -> None:
        """
        Validate all service registrations to detect potential issues early.
        
        Raises:
            ServiceRegistrationError: If validation fails
        """
        self._logger.info("Validating service registrations...")
        
        for service_type, descriptor in self._services.items():
            try:
                # Validate implementation type can be instantiated
                if descriptor.implementation_type and not descriptor.factory and not descriptor.instance:
                    self._validate_constructor(descriptor.implementation_type)
                
                self._logger.debug(f"Validated service: {service_type.__name__}")
                
            except Exception as e:
                raise ServiceRegistrationError(
                    f"Invalid registration for {service_type.__name__}: {e}"
                )
        
        self._logger.info(f"Successfully validated {len(self._services)} service registrations")
    
    def _validate_constructor(self, implementation_type: Type) -> None:
        """Validate that a type's constructor can be resolved."""
        constructor = implementation_type.__init__
        signature = inspect.signature(constructor)
        parameters = list(signature.parameters.values())[1:]  # Skip 'self'
        
        for param in parameters:
            # Skip *args and **kwargs parameters
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
                
            if param.annotation == inspect.Parameter.empty:
                if param.default == inspect.Parameter.empty:
                    raise ServiceRegistrationError(
                        f"Parameter '{param.name}' in {implementation_type.__name__} "
                        f"has no type annotation and no default value"
                    )
            else:
                param_type = param.annotation
                
                # Handle Optional types
                if hasattr(param_type, '__origin__'):
                    continue  # Skip complex generic types for now
                
                # Check if dependency is registered
                if not self.is_registered(param_type) and param.default == inspect.Parameter.empty:
                    raise ServiceRegistrationError(
                        f"Dependency {param_type.__name__} for {implementation_type.__name__} "
                        f"is not registered and has no default value"
                    )


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container instance."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def configure_container() -> ServiceContainer:
    """Configure and return a new service container."""
    global _container
    _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    _container = None