from typing import Dict, Any, List, Optional
import os

class UserSessionService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.is_logged_in = True
        self.user = {"email": "alex@household.local", "name": "Nova Household"}
        self.connected_services = [
            {"provider": "swiggy", "connected": True, "mode": "demo"},
            {"provider": "amazon", "connected": True, "mode": "demo"}
        ]
        self.onboarding_complete = True
        # Default to FULL_AUTOPILOT for hackathon demo autopilot guarantees, unless overridden
        self.autonomy_profile = os.environ.get("DEFAULT_AUTONOMY_PROFILE", "FULL_AUTOPILOT")
        
    def login(self, email: str):
        self.is_logged_in = True
        self.user = {"email": email, "name": "Nova User"}
        
    def logout(self):
        self.reset()
        
    def connect_service(self, provider: str):
        if not any(s["provider"] == provider for s in self.connected_services):
            self.connected_services.append({
                "provider": provider,
                "connected": True,
                "mode": "demo"
            })
            
    def set_autonomy_profile(self, profile: str):
        self.autonomy_profile = profile
        self.onboarding_complete = True

    def get_autonomy_profile(self) -> str:
        return self.autonomy_profile
        
    def get_session_state(self) -> Dict[str, Any]:
        return {
            "is_logged_in": self.is_logged_in,
            "user": self.user,
            "connected_services": self.connected_services,
            "onboarding_complete": self.onboarding_complete,
            "autonomy_profile": self.autonomy_profile
        }
