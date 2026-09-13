import io
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, Optional

try:
    from PIL import Image as _PILImage
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

# Only cache definitive outcomes - NOT transient network failures.
# Transient: timeout, connection error, HTTP 429/502/503/504 → NOT cached
# Permanent: 200 OK (valid/invalid), 404, HTML content, bad dimensions → cached
_VALIDATION_CACHE: Dict[str, Tuple[bool, str, Optional[Tuple[int, int]]]] = {}

# HTTP status codes that are transient - never cache these
_TRANSIENT_HTTP_CODES = {429, 502, 503, 504, 408}


def validate_image_url(url: Optional[str]) -> Tuple[bool, str, Optional[Tuple[int, int]]]:
    """
    Validates a candidate image URL:
      1. URL is an HTTP/HTTPS string
      2. URL is reachable and returns HTTP 200
      3. Content-Type is image/*
      4. Response is not HTML
      5. Image can be decoded by Pillow (if available)
      6. Image dimensions are reasonable (min 80x80, max aspect ratio 4:1)
      7. Rejects raw uncurated crowdsourced user phone photos (e.g. /1.400.jpg)

    CRITICAL: Transient failures (timeout, connection error, HTTP 429/502/503/504)
    are NEVER cached. Only definitive outcomes are cached. This prevents a single
    network hiccup from permanently marking a valid image as unavailable.
    """
    if not url or not isinstance(url, str):
        return False, "Empty or non-string URL", None

    url_str = url.strip()
    if not (url_str.startswith("http://") or url_str.startswith("https://")):
        return False, "Not an HTTP/HTTPS URL", None

    if url_str in _VALIDATION_CACHE:
        return _VALIDATION_CACHE[url_str]

    # Deterministic check: reject uncurated raw user upload #1 photos from Open Food Facts.
    # /data/.../1.400.jpg or /data/.../1.jpg = raw unmoderated first photo from a contributor.
    # Official catalog front images are named front_*.jpg or in selected_images.
    if "openfoodfacts-images" in url_str:
        if url_str.endswith("/1.400.jpg") or url_str.endswith("/1.jpg") or url_str.endswith("/2.400.jpg"):
            reason = "Rejected crowdsourced raw user photograph (uncropped / unmoderated)"
            print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: N/A\nContent-Type: N/A\nDimensions: N/A\nVALID: false\nREASON: {reason}")
            _VALIDATION_CACHE[url_str] = (False, reason, None)
            return False, reason, None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }

    req = urllib.request.Request(url_str, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=6.0) as resp:
            status_code = resp.status
            content_type = (resp.headers.get("Content-Type") or "").lower()

            if status_code != 200:
                reason = f"HTTP {status_code}"
                print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {status_code}\nContent-Type: {content_type}\nDimensions: N/A\nVALID: false\nREASON: {reason}")
                # Only cache definitive 4xx client errors, not transient server errors
                if status_code not in _TRANSIENT_HTTP_CODES:
                    _VALIDATION_CACHE[url_str] = (False, reason, None)
                return False, reason, None

            if "text/html" in content_type or "text/plain" in content_type:
                reason = f"Invalid Content-Type {content_type} (expected image/*)"
                print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {status_code}\nContent-Type: {content_type}\nDimensions: N/A\nVALID: false\nREASON: {reason}")
                _VALIDATION_CACHE[url_str] = (False, reason, None)
                return False, reason, None

            # Read image data up to 2MB to decode
            data = resp.read(2 * 1024 * 1024)
            if len(data) < 500:
                reason = f"Payload too small ({len(data)} bytes)"
                print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {status_code}\nContent-Type: {content_type}\nDimensions: N/A\nVALID: false\nREASON: {reason}")
                _VALIDATION_CACHE[url_str] = (False, reason, None)
                return False, reason, None

            if _HAS_PIL:
                try:
                    img = _PILImage.open(io.BytesIO(data))
                    width, height = img.size

                    if width < 80 or height < 80:
                        reason = f"Image dimensions too small ({width}x{height})"
                        print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {status_code}\nContent-Type: {content_type}\nDimensions: {width}x{height}\nVALID: false\nREASON: {reason}")
                        _VALIDATION_CACHE[url_str] = (False, reason, (width, height))
                        return False, reason, (width, height)

                    aspect = width / height
                    if aspect < 0.25 or aspect > 4.0:
                        reason = f"Extreme aspect ratio ({aspect:.2f})"
                        print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {status_code}\nContent-Type: {content_type}\nDimensions: {width}x{height}\nVALID: false\nREASON: {reason}")
                        _VALIDATION_CACHE[url_str] = (False, reason, (width, height))
                        return False, reason, (width, height)

                    print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: 200\nContent-Type: {content_type}\nDimensions: {width}x{height}\nVALID: true\nREASON: Verified valid catalog image")
                    res = (True, "Valid catalog image", (width, height))
                    _VALIDATION_CACHE[url_str] = res
                    return res

                except Exception as dec_err:
                    reason = f"Decode failed: {dec_err}"
                    print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {status_code}\nContent-Type: {content_type}\nDimensions: N/A\nVALID: false\nREASON: {reason}")
                    _VALIDATION_CACHE[url_str] = (False, reason, None)
                    return False, reason, None
            else:
                # Pillow not available: accept if content-type is image/* and payload is large enough
                if "image/" in content_type:
                    print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: 200\nContent-Type: {content_type}\nDimensions: N/A (Pillow unavailable)\nVALID: true\nREASON: Content-Type is image/* and payload is large enough")
                    res = (True, "Valid image (content-type only, Pillow unavailable)", None)
                    _VALIDATION_CACHE[url_str] = res
                    return res
                else:
                    reason = f"Non-image Content-Type: {content_type}"
                    _VALIDATION_CACHE[url_str] = (False, reason, None)
                    return False, reason, None

    except urllib.error.HTTPError as e:
        reason = f"HTTP {e.code}"
        print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {e.code}\nContent-Type: N/A\nDimensions: N/A\nVALID: false\nREASON: {reason}")
        # Do NOT cache transient HTTP errors
        if e.code not in _TRANSIENT_HTTP_CODES:
            _VALIDATION_CACHE[url_str] = (False, reason, None)
        return False, reason, None

    except Exception as e:
        # Timeout, connection reset, SSL handshake, DNS failure - all TRANSIENT.
        # NEVER cache these as permanent failures.
        reason = f"Connection error: {e}"
        print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: N/A\nContent-Type: N/A\nDimensions: N/A\nVALID: false\nREASON: {reason} [transient - not cached]")
        return False, reason, None


def clear_validation_cache():
    _VALIDATION_CACHE.clear()
