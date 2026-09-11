from typing import Dict, Any, List

class UserSessionService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.is_logged_in = False
        self.user = None
        self.connected_services = []
        self.onboarding_complete = False
        self.autonomy_profile = "NONE"
        
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
        
    def get_session_state(self) -> Dict[str, Any]:
        return {
            "is_logged_in": self.is_logged_in,
            "user": self.user,
            "connected_services": self.connected_services,
            "onboarding_complete": self.onboarding_complete,
            "autonomy_profile": self.autonomy_profile
        }
