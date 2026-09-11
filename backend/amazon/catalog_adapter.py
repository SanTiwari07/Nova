from catalog.product_repository import ProductRepository
from typing import Dict, Any, List


class MockAmazonCatalogAdapter:
    """
    Wraps the existing ProductRepository and tags results as AMAZON_MOCK.
    In a real integration, replace with AmazonCreatorsAdapter.
    """

    def __init__(self):
        self.repo = ProductRepository()
        self.source = "AMAZON_MOCK"

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        results = self.repo.search(query, skip=0, limit=limit)
        return [self._tag(p) for p in results]

    def get_by_id(self, product_id: str) -> Dict[str, Any]:
        p = self.repo.get_by_id(product_id)
        return self._tag(p) if p else None

    def get_all(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        results = self.repo.get_all(skip=skip, limit=limit)
        return [self._tag(p) for p in results]

    def _tag(self, product: Dict[str, Any]) -> Dict[str, Any]:
        if product:
            product["source"] = self.source
            product["retailer"] = "Amazon"
            product["prime_eligible"] = True
            product["delivery_estimate"] = "Tomorrow"
        return product


class AmazonCreatorsAdapter:
    """
    Skeleton for real Amazon Creators API integration.
    Requires: AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG
    set as environment variables. Never commit credentials.
    """

    def __init__(self):
        import os
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        self.marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.in")
        self.source = "AMAZON_LIVE"
        self._available = bool(self.access_key and self.secret_key and self.associate_tag)

    def is_available(self) -> bool:
        return self._available

    def search(self, query: str, limit: int = 20):
        if not self._available:
            raise RuntimeError("Amazon Creators API credentials not configured. Set AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG.")
        # TODO: Implement SearchItems call via paapi5-python-sdk or requests
        raise NotImplementedError("Amazon Creators API integration not yet implemented.")
