import io
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, Optional
from PIL import Image

_VALIDATION_CACHE: Dict[str, Tuple[bool, str, Optional[Tuple[int, int]]]] = {}

def validate_image_url(url: Optional[str]) -> Tuple[bool, str, Optional[Tuple[int, int]]]:
    """
    Validates a candidate image URL according to Phase 4 & Phase 7 requirements:
      1. URL exists and is valid HTTP/HTTPS
      2. URL is reachable
      3. HTTP response is successful (200)
      4. Content-Type is actually image/*
      5. Response is not HTML
      6. Image can be decoded
      7. Image dimensions and aspect ratio are reasonable
      8. Rejects raw uncurated crowdsourced user phone photos (e.g. /1.400.jpg, /1.jpg)
    """
    if not url or not isinstance(url, str):
        return False, "Empty or non-string URL", None

    url_str = url.strip()
    if not (url_str.startswith("http://") or url_str.startswith("https://")):
        return False, "Not an HTTP/HTTPS URL", None

    if url_str in _VALIDATION_CACHE:
        return _VALIDATION_CACHE[url_str]

    # Deterministic check: reject uncurated raw user upload #1 photos from Open Food Facts
    # In Open Food Facts, /data/.../1.400.jpg or /data/.../1.jpg is the raw unmoderated first photo
    # taken by a contributor from their phone (almost always handheld with fingers, background clutter).
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
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            status_code = resp.status
            content_type = (resp.headers.get("Content-Type") or "").lower()

            if status_code != 200:
                reason = f"HTTP {status_code}"
                print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {status_code}\nContent-Type: {content_type}\nDimensions: N/A\nVALID: false\nREASON: {reason}")
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

            try:
                img = Image.open(io.BytesIO(data))
                width, height = img.size
                
                # Check dimensions
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

    except urllib.error.HTTPError as e:
        reason = f"HTTP {e.code}"
        print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: {e.code}\nContent-Type: N/A\nDimensions: N/A\nVALID: false\nREASON: {reason}")
        _VALIDATION_CACHE[url_str] = (False, reason, None)
        return False, reason, None
    except Exception as e:
        reason = f"Connection error: {e}"
        print(f"IMAGE VALIDATION\nURL: {url_str}\nHTTP: N/A\nContent-Type: N/A\nDimensions: N/A\nVALID: false\nREASON: {reason}")
        _VALIDATION_CACHE[url_str] = (False, reason, None)
        return False, reason, None

def clear_validation_cache():
    _VALIDATION_CACHE.clear()
