"""
Tests for the ImageResolver pipeline.

Test plan (per spec):

  TEST 1: Exact barcode match
    → real Open Food Facts image

  TEST 2: No barcode but exact brand/name/quantity match
    → real image if confidence >= threshold

  TEST 3: Wrong quantity (Maggi 70g vs Maggi 280g)
    → NO automatic match

  TEST 4: No Open Food Facts match
    → imageUrl = null, imageStatus = "unavailable"

  TEST 5: Swiggy provides an image
    → Swiggy image wins; Open Food Facts NOT called

  TEST 6: Open Food Facts API unavailable
    → commerce product intact, imageStatus = "unavailable"

  TEST 7: Same product searched twice
    → cache hit on second call; no extra OFF API request

  TEST 8: Confidence scoring
    → validate the numeric scores for each scenario

Run with:
    cd backend
    python -m pytest images/tests/test_image_resolver.py -v
"""

import asyncio
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Make sure backend/ is on the path when running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from images.image_resolver import ImageResolver
from images.image_cache import ImageCache
from images.open_food_facts import OpenFoodFactsResolver


# ── Helpers ───────────────────────────────────────────────────────────────────

def run(coro):
    """Run an async coroutine in a test — compatible with Python 3.10+."""
    return asyncio.run(coro)


def make_product(
    id="spin_test_001",
    name="Maggi 2-Minute Masala Noodles",
    brand="Maggi",
    quantity="70",
    unit="g",
    pack_size="70 g",
    image_url=None,
    barcode=None,
    **kwargs,
):
    p = {
        "id": id,
        "variantId": id,
        "productId": "prod_maggi",
        "name": name,
        "brand": brand,
        "quantity": quantity,
        "unit": unit,
        "pack_size": pack_size,
        "imageUrl": image_url,
        "image": image_url,
        "retailer": "swiggy_instamart",
    }
    if barcode:
        p["barcode"] = barcode
    p.update(kwargs)
    return p


# ── Test Cases ────────────────────────────────────────────────────────────────


class TestImageResolverTest1BarcodeMatch(unittest.TestCase):
    """TEST 1: Exact barcode match → real OFF image, confidence 1.00"""

    def test_barcode_returns_real_image(self):
        resolver = ImageResolver(cache=ImageCache())
        product = make_product(barcode="8901764100055")

        fake_image = "https://images.openfoodfacts.org/images/products/890/176/410/0055/front_en.jpg"

        with patch.object(
            OpenFoodFactsResolver,
            "lookup_by_barcode",
            return_value=(fake_image, 1.0, "8901764100055"),
        ):
            result = run(resolver.resolve(product))

        self.assertEqual(result["imageUrl"], fake_image)
        self.assertEqual(result["imageSource"], "open_food_facts")
        self.assertAlmostEqual(result["imageConfidence"], 1.0)
        self.assertEqual(result["imageStatus"], "found")

    def test_barcode_confidence_is_1(self):
        resolver = ImageResolver(cache=ImageCache())
        product = make_product(barcode="1234567890123")
        fake_image = "https://images.openfoodfacts.org/test.jpg"

        with patch.object(
            OpenFoodFactsResolver,
            "lookup_by_barcode",
            return_value=(fake_image, 1.0, "1234567890123"),
        ):
            result = run(resolver.resolve(product))

        self.assertEqual(result["imageConfidence"], 1.0)


class TestImageResolverTest2IdentityMatch(unittest.TestCase):
    """TEST 2: Brand + name + quantity exact match → real image"""

    def test_identity_match_returns_image(self):
        resolver = ImageResolver()
        product = make_product(quantity="1", unit="L", pack_size="1 L",
                               name="Amul Taaza Homogenised Toned Milk", brand="Amul")

        fake_image = "https://images.openfoodfacts.org/amul_taaza_1l.jpg"

        with patch.object(
            OpenFoodFactsResolver,
            "lookup_by_barcode",
            return_value=(None, 0.0, None),
        ):
            with patch.object(
                OpenFoodFactsResolver,
                "lookup_by_identity",
                return_value=(fake_image, 0.90, "Amul Taaza Homogenised Toned Milk 1 L"),
            ):
                result = run(resolver.resolve(product))

        self.assertEqual(result["imageUrl"], fake_image)
        self.assertEqual(result["imageSource"], "open_food_facts")
        self.assertGreaterEqual(result["imageConfidence"], 0.90)


class TestImageResolverTest3WrongQuantity(unittest.TestCase):
    """TEST 3: Wrong pack size (70g vs 280g) → NO automatic match"""

    def test_maggi_70g_does_not_match_280g(self):
        """
        The OFF search returns a Maggi 280g result.
        Confidence scoring must reject this due to quantity mismatch.
        """
        off = OpenFoodFactsResolver()

        candidate_280g = {
            "product_name": "Maggi 2-Minute Masala Noodles",
            "brands": "Maggi",
            "quantity": "280 g",
        }

        score, reason = off._score_candidate(
            candidate_280g,
            name="Maggi 2-Minute Masala Noodles",
            brand="Maggi",
            quantity="70",
            unit="g",
        )

        # Must be 0.0 due to hard quantity mismatch rejection
        self.assertEqual(score, 0.0, f"Expected 0.0 (qty mismatch) but got {score}. Reason: {reason}")
        self.assertIn("mismatch", reason.lower())

    def test_different_pack_sizes_rejected(self):
        """Fortune Sunflower Oil 1L vs 5L — must reject."""
        off = OpenFoodFactsResolver()

        candidate_5l = {
            "product_name": "Fortune Sunflower Oil",
            "brands": "Fortune",
            "quantity": "5 L",
        }

        score, reason = off._score_candidate(
            candidate_5l,
            name="Fortune Sunflower Oil",
            brand="Fortune",
            quantity="1",
            unit="L",
        )

        self.assertEqual(score, 0.0, f"Expected 0.0 (qty mismatch) but got {score}. Reason: {reason}")

    def test_amul_taaza_500ml_does_not_match_1l(self):
        """Amul Taaza Milk 500ml vs 1L — must reject."""
        off = OpenFoodFactsResolver()

        candidate_1l = {
            "product_name": "Amul Taaza Toned Milk",
            "brands": "Amul",
            "quantity": "1 L",
        }

        score, reason = off._score_candidate(
            candidate_1l,
            name="Amul Taaza Toned Milk",
            brand="Amul",
            quantity="500",
            unit="ml",
        )

        self.assertEqual(score, 0.0, f"Expected 0.0 (500ml vs 1L mismatch) but got {score}. Reason: {reason}")


class TestImageResolverTest4NoMatch(unittest.TestCase):
    """TEST 4: No Open Food Facts match → imageUrl=null, imageStatus=unavailable"""

    def test_no_match_returns_unavailable(self):
        resolver = ImageResolver(cache=ImageCache())
        product = make_product(name="Some Unknown Obscure Product XYZ-9999", brand="NoSuchBrand")

        with patch.object(OpenFoodFactsResolver, "lookup_by_barcode", return_value=(None, 0.0, None)):
            with patch.object(OpenFoodFactsResolver, "lookup_by_identity", return_value=(None, 0.0, None)):
                result = run(resolver.resolve(product))

        self.assertIsNone(result["imageUrl"])
        self.assertEqual(result["imageStatus"], "unavailable")

    def test_low_confidence_returns_unavailable(self):
        """Even if OFF returns something, if confidence < threshold, must return unavailable."""
        resolver = ImageResolver(cache=ImageCache())
        product = make_product()

        with patch.object(OpenFoodFactsResolver, "lookup_by_barcode", return_value=(None, 0.0, None)):
            with patch.object(
                OpenFoodFactsResolver,
                "lookup_by_identity",
                # Confidence below threshold (0.70 < 0.90)
                return_value=("https://images.openfoodfacts.org/wrong.jpg", 0.70, "some key"),
            ):
                result = run(resolver.resolve(product))

        self.assertIsNone(result["imageUrl"])
        self.assertEqual(result["imageStatus"], "unavailable")


class TestImageResolverTest5SwiggyImagePriority(unittest.TestCase):
    """TEST 5: Swiggy provides image → Swiggy wins; OFF must NOT be called"""

    def test_swiggy_image_takes_priority(self):
        resolver = ImageResolver(cache=ImageCache())
        swiggy_url = "https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,w_500/abcdef123"
        product = make_product(image_url=swiggy_url)

        # If OFF is called, the test fails
        with patch.object(
            OpenFoodFactsResolver,
            "lookup_by_barcode",
            side_effect=AssertionError("OFF lookup_by_barcode called when Swiggy URL available"),
        ):
            with patch.object(
                OpenFoodFactsResolver,
                "lookup_by_identity",
                side_effect=AssertionError("OFF lookup_by_identity called when Swiggy URL available"),
            ):
                result = run(resolver.resolve(product))

        self.assertEqual(result["imageUrl"], swiggy_url)
        self.assertEqual(result["imageSource"], "swiggy")
        self.assertEqual(result["imageConfidence"], 1.0)
        self.assertEqual(result["imageStatus"], "found")


class TestImageResolverTest6OFFUnavailable(unittest.TestCase):
    """TEST 6: Open Food Facts API unavailable → commerce data works, image unavailable"""

    def test_off_failure_gives_unavailable_image(self):
        """When OFF fails, the product should still have all commerce data, just no image."""
        resolver = ImageResolver(cache=ImageCache())
        product = make_product(barcode="8901764100055")

        # Simulate network failure
        with patch.object(
            OpenFoodFactsResolver,
            "lookup_by_barcode",
            return_value=(None, 0.0, None),
        ):
            with patch.object(
                OpenFoodFactsResolver,
                "lookup_by_identity",
                return_value=(None, 0.0, None),
            ):
                result = run(resolver.resolve(product))

        # Image is unavailable — but result dict still returned cleanly
        self.assertIsNone(result["imageUrl"])
        self.assertEqual(result["imageStatus"], "unavailable")


class TestImageResolverTest7CacheHit(unittest.TestCase):
    """TEST 7: Same product searched twice → cache hit; no extra OFF call"""

    def test_second_call_uses_cache(self):
        resolver = ImageResolver()
        product = make_product(id="cache_test_spin", barcode="0987654321098")
        fake_image = "https://images.openfoodfacts.org/cached.jpg"

        call_count = {"barcode": 0, "identity": 0}

        def mock_barcode(barcode):
            call_count["barcode"] += 1
            return (fake_image, 1.0, barcode)

        def mock_identity(name, brand=None, quantity=None, unit=None):
            call_count["identity"] += 1
            return (None, 0.0, None)

        with patch.object(OpenFoodFactsResolver, "lookup_by_barcode", side_effect=mock_barcode):
            with patch.object(OpenFoodFactsResolver, "lookup_by_identity", side_effect=mock_identity):
                result1 = run(resolver.resolve(product))
                result2 = run(resolver.resolve(product))  # Must hit cache

        # OFF should have been called exactly once
        self.assertEqual(call_count["barcode"], 1, "Expected exactly 1 OFF barcode call (cache hit on second)")
        self.assertEqual(result1["imageUrl"], result2["imageUrl"])
        self.assertEqual(result1["imageStatus"], "found")
        self.assertEqual(result2["imageStatus"], "found")


class TestImageResolverTest8ConfidenceScoring(unittest.TestCase):
    """TEST 8: Verify confidence score values for each scenario"""

    def setUp(self):
        self.off = OpenFoodFactsResolver()

    def test_exact_brand_name_quantity_score(self):
        """Brand + name + quantity match should score at or above threshold."""
        candidate = {
            "product_name": "Maggi 2-Minute Masala Noodles",
            "brands": "Maggi",
            "quantity": "70 g",
        }
        score, reason = self.off._score_candidate(
            candidate,
            name="Maggi 2-Minute Masala Noodles",
            brand="Maggi",
            quantity="70",
            unit="g",
        )
        self.assertGreaterEqual(score, 0.90, f"Expected >= 0.90 but got {score}. Reason: {reason}")

    def test_name_only_score_low(self):
        """Name only (no brand, no quantity) should have low score."""
        candidate = {
            "product_name": "Maggi Masala Noodles",
            "brands": "",
            "quantity": "",
        }
        score, reason = self.off._score_candidate(
            candidate,
            name="Maggi Masala Noodles",
            brand=None,
            quantity=None,
            unit=None,
        )
        # No brand, no quantity — score should be < threshold
        self.assertLess(score, 0.90, f"Expected < 0.90 for name-only match but got {score}. Reason: {reason}")

    def test_quantity_unit_normalization_kg_to_g(self):
        """1 kg should match 1000 g."""
        off = OpenFoodFactsResolver()
        val_kg, unit_kg = off._parse_quantity("1 kg")
        val_g, unit_g = off._parse_quantity("1000 g")
        self.assertEqual(val_kg, 1000.0)
        self.assertEqual(val_g, 1000.0)
        self.assertEqual(unit_kg, unit_g)

    def test_quantity_unit_normalization_l_to_ml(self):
        """1 L should match 1000 ml."""
        off = OpenFoodFactsResolver()
        val_l, unit_l = off._parse_quantity("1 L")
        val_ml, unit_ml = off._parse_quantity("1000 ml")
        self.assertEqual(val_l, 1000.0)
        self.assertEqual(val_ml, 1000.0)
        self.assertEqual(unit_l, unit_ml)


class TestImageCacheBasic(unittest.TestCase):
    """Basic cache behavior tests."""

    def test_cache_miss(self):
        cache = ImageCache()
        self.assertIsNone(cache.get("nonexistent:key"))

    def test_cache_set_and_get(self):
        cache = ImageCache()
        cache.set("test:key", "https://example.com/img.jpg", "open_food_facts", 1.0, "1234567890")
        record = cache.get("test:key")
        self.assertIsNotNone(record)
        self.assertEqual(record["imageUrl"], "https://example.com/img.jpg")
        self.assertEqual(record["source"], "open_food_facts")

    def test_null_image_cached(self):
        """Unavailable result should also be cached to prevent repeated lookups."""
        cache = ImageCache()
        cache.set("test:unavail", None, "unavailable", 0.0, None)
        record = cache.get("test:unavail")
        self.assertIsNotNone(record)
        self.assertIsNone(record["imageUrl"])
        self.assertEqual(record["source"], "unavailable")

    def test_cache_stats(self):
        cache = ImageCache()
        cache.set("k1", "https://ex.com/a.jpg", "swiggy", 1.0)
        cache.set("k2", None, "unavailable", 0.0)
        stats = cache.stats()
        self.assertEqual(stats["valid_entries"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
