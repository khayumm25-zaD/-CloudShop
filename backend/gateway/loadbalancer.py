"""Service discovery and load balancing."""

from typing import List, Dict, Optional
import random
from datetime import datetime, timedelta
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class ServiceInstance:
    """Represents a service instance."""

    def __init__(self, url: str, service_name: str):
        self.url = url
        self.service_name = service_name
        self.healthy = True
        self.last_health_check = None
        self.response_time = 0


class ServiceDiscovery:
    """Service discovery and registration."""

    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.service_cache = {}

    def register_service(self, service_name: str, instances: List[str]):
        """Register service instances."""
        self.services[service_name] = [
            ServiceInstance(url, service_name) for url in instances
        ]
        logger.info(f"Registered service: {service_name} with {len(instances)} instances")

    def get_service_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get healthy service instance using round-robin."""
        if service_name not in self.services:
            logger.warning(f"Service {service_name} not found")
            return None

        healthy_instances = [
            instance for instance in self.services[service_name]
            if instance.healthy
        ]

        if not healthy_instances:
            logger.error(f"No healthy instances for service: {service_name}")
            return None

        # Round-robin selection
        return random.choice(healthy_instances)

    def mark_unhealthy(self, service_name: str, url: str):
        """Mark service instance as unhealthy."""
        if service_name in self.services:
            for instance in self.services[service_name]:
                if instance.url == url:
                    instance.healthy = False
                    logger.warning(f"Marked instance unhealthy: {url}")

    def mark_healthy(self, service_name: str, url: str):
        """Mark service instance as healthy."""
        if service_name in self.services:
            for instance in self.services[service_name]:
                if instance.url == url:
                    instance.healthy = True
                    logger.info(f"Marked instance healthy: {url}")


class LoadBalancer:
    """Load balancer for distributing requests."""

    def __init__(self):
        self.discovery = ServiceDiscovery()
        self.strategy = "round-robin"  # round-robin, least-connections, weighted

    def get_next_server(self, service_name: str) -> Optional[str]:
        """Get next server based on load balancing strategy."""
        instance = self.discovery.get_service_instance(service_name)
        return instance.url if instance else None

    def set_strategy(self, strategy: str):
        """Set load balancing strategy."""
        if strategy in ["round-robin", "least-connections", "weighted"]:
            self.strategy = strategy
            logger.info(f"Load balancer strategy set to: {strategy}")
        else:
            logger.warning(f"Unknown load balancing strategy: {strategy}")
