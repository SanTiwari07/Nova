import os
import json
import time
import base64
import hashlib
import secrets
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional

SESSION_FILE = os.path.join(os.path.dirname(__file__), "swiggy_session.json")
DEFAULT_REDIRECT_URI = os.environ.get(
    "SWIGGY_REDIRECT_URI", "http://localhost:8000/api/auth/swiggy/callback"
)
CLIENT_ID = os.environ.get("SWIGGY_CLIENT_ID", "swiggy-mcp")
AUTHORIZE_ENDPOINT = "https://mcp.swiggy.com/auth/authorize"
TOKEN_ENDPOINT = "https://mcp.swiggy.com/auth/token"
SCOPES = "mcp:tools"

class SwiggyOAuthManager:
    """
    Manages OAuth 2.1 + PKCE authentication for Swiggy Instamart MCP.
    Strictly follows RFC 7636 and official Swiggy MCP documentation.
    """

    def __init__(self, session_path: str = SESSION_FILE):
        self.session_path = session_path
        self._session_cache: Dict[str, Any] = {}
        # Stores transient {state: {"verifier": ..., "redirect_uri": ..., "created_at": ...}}
        self._pending_states: Dict[str, Dict[str, Any]] = {}
        self._load_session()

    def _load_session(self):
        if os.path.exists(self.session_path):
            try:
                with open(self.session_path, "r", encoding="utf-8") as f:
                    self._session_cache = json.load(f)
            except Exception as e:
                print(f"[Swiggy OAuth] Failed to load session from {self.session_path}: {e}")
                self._session_cache = {}

    def _save_session(self):
        try:
            with open(self.session_path, "w", encoding="utf-8") as f:
                json.dump(self._session_cache, f, indent=2)
        except Exception as e:
            print(f"[Swiggy OAuth] Failed to save session to {self.session_path}: {e}")

    @staticmethod
    def _generate_code_verifier() -> str:
        """Generate high-entropy cryptographic random string for PKCE verifier (RFC 7636)."""
        token_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(token_bytes).decode("utf-8").rstrip("=")

    @staticmethod
    def _generate_code_challenge(verifier: str) -> str:
        """Generate SHA256 code challenge from verifier (RFC 7636 S256)."""
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    def start_auth_flow(self, redirect_uri: Optional[str] = None) -> Dict[str, str]:
        """
        Initiates the PKCE OAuth authorization flow.
        Returns the authorization URL and state.
        """
        chosen_redirect = redirect_uri or DEFAULT_REDIRECT_URI
        verifier = self._generate_code_verifier()
        challenge = self._generate_code_challenge(verifier)
        state = secrets.token_hex(16)

        # Store pending state with timestamp (TTL 15 minutes)
        self._pending_states[state] = {
            "verifier": verifier,
            "redirect_uri": chosen_redirect,
            "created_at": time.time()
        }
        self._cleanup_pending_states()

        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": chosen_redirect,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
            "scope": SCOPES,
        }

        auth_url = f"{AUTHORIZE_ENDPOINT}?{urllib.parse.urlencode(params)}"
        print(f"[Swiggy OAuth] Initiated authorization flow. State: {state}")
        return {
            "auth_url": auth_url,
            "state": state,
            "code_challenge": challenge,
            "redirect_uri": chosen_redirect
        }

    def _cleanup_pending_states(self):
        """Clean up state tokens older than 15 minutes."""
        now = time.time()
        expired = [s for s, data in self._pending_states.items() if now - data.get("created_at", 0) > 900]
        for s in expired:
            self._pending_states.pop(s, None)

    def exchange_code(self, code: str, state: str) -> Dict[str, Any]:
        """
        Exchanges the authorization code for an OAuth access token using PKCE verifier.
        """
        pending = self._pending_states.pop(state, None)
        if not pending:
            # Check if there is an active session or fallback state for tolerance
            print(f"[Swiggy OAuth] Warning: State {state} not found in pending cache.")
            verifier = None
            redirect_uri = DEFAULT_REDIRECT_URI
        else:
            verifier = pending.get("verifier")
            redirect_uri = pending.get("redirect_uri", DEFAULT_REDIRECT_URI)

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": CLIENT_ID
        }
        if verifier:
            payload["code_verifier"] = verifier

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Household-Autopilot/1.0"
        }

        req = urllib.request.Request(TOKEN_ENDPOINT, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = resp.read().decode("utf-8")
                token_resp = json.loads(resp_data)
                
                access_token = token_resp.get("access_token")
                expires_in = token_resp.get("expires_in", 432000) # Default 5 days
                token_type = token_resp.get("token_type", "Bearer")
                scope = token_resp.get("scope", SCOPES)

                self._session_cache = {
                    "access_token": access_token,
                    "token_type": token_type,
                    "scope": scope,
                    "expires_at": time.time() + expires_in,
                    "created_at": time.time(),
                    "active_address_id": self._session_cache.get("active_address_id"),
                    "active_address": self._session_cache.get("active_address")
                }
                self._save_session()
                print(f"[Swiggy OAuth] Successfully exchanged token! Expires in {expires_in}s")
                return self._session_cache
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"[Swiggy OAuth] Token exchange failed HTTP {e.code}: {err_body}")
            raise RuntimeError(f"Swiggy token exchange failed HTTP {e.code}: {err_body}")
        except Exception as e:
            print(f"[Swiggy OAuth] Token exchange error: {e}")
            raise

    def is_authenticated(self) -> bool:
        """Check if an active, unexpired Swiggy OAuth access token is stored."""
        env_token = os.environ.get("SWIGGY_ACCESS_TOKEN") or os.environ.get("SWIGGY_BEARER_TOKEN")
        if env_token:
            return True

        token = self._session_cache.get("access_token")
        expires_at = self._session_cache.get("expires_at", 0)
        return bool(token and expires_at > time.time() + 60)

    def get_access_token(self) -> Optional[str]:
        """Return valid access token if authenticated, else None."""
        env_token = os.environ.get("SWIGGY_ACCESS_TOKEN") or os.environ.get("SWIGGY_BEARER_TOKEN")
        if env_token:
            return env_token

        if self.is_authenticated():
            return self._session_cache.get("access_token")
        return None

    def get_session(self) -> Dict[str, Any]:
        """Get sanitized session status."""
        return {
            "authenticated": self.is_authenticated(),
            "expires_at": self._session_cache.get("expires_at"),
            "scope": self._session_cache.get("scope"),
            "active_address_id": self._session_cache.get("active_address_id"),
            "active_address": self._session_cache.get("active_address"),
            "created_at": self._session_cache.get("created_at")
        }

    def set_active_address(self, address: Dict[str, Any]):
        """Set the active delivery address dictionary and address ID."""
        addr_id = address.get("id") or address.get("addressId")
        self._session_cache["active_address_id"] = str(addr_id) if addr_id else None
        self._session_cache["active_address"] = address
        self._save_session()
        print(f"[Swiggy OAuth] Set active address: {addr_id} ({address.get('addressLine') or address.get('label')})")

    def get_active_address(self) -> Optional[Dict[str, Any]]:
        """Return the user's currently selected delivery address."""
        return self._session_cache.get("active_address")

    def get_active_address_id(self) -> Optional[str]:
        """Return the active delivery address ID."""
        return self._session_cache.get("active_address_id")

    def clear_session(self):
        """Disconnect and clear saved Swiggy session."""
        self._session_cache = {}
        if os.path.exists(self.session_path):
            try:
                os.remove(self.session_path)
            except Exception as e:
                print(f"[Swiggy OAuth] Error deleting session file: {e}")
        print("[Swiggy OAuth] Cleared Swiggy session.")

# Singleton instance
oauth_manager = SwiggyOAuthManager()

if __name__ == "__main__":
    import sys
    import webbrowser

    if len(sys.argv) > 1 and sys.argv[1] == "login":
        print("=" * 60)
        print("Swiggy Instamart OAuth 2.1 + PKCE CLI Login")
        print("=" * 60)
        
        flow = oauth_manager.start_auth_flow("http://localhost:8000/api/auth/swiggy/callback")
        auth_url = flow["auth_url"]
        print(f"\nOpening official Swiggy login page in browser:\n{auth_url}\n")
        webbrowser.open(auth_url)
        print("Complete phone + OTP verification on the Swiggy login page.")
        print("When redirected to http://localhost:8000/api/auth/swiggy/callback, your token will be saved.")
    else:
        print("Usage: python -m backend.commerce.swiggy_oauth login")
