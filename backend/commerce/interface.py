from abc import ABC, abstractmethod
from typing import Dict, Any, List

class CommerceInterface(ABC):
    @abstractmethod
    async def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    async def check_availability(self, product_id: str) -> bool:
        pass
        
    @abstractmethod
    async def create_cart(self) -> str:
        pass
        
    @abstractmethod
    async def checkout(self, cart_id: str) -> Dict[str, Any]:
        pass
