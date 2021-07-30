import sys
from typing import Dict
from .App import App as BaseApp

class AppManager:
    def __init__(self) -> None:
        """Manage some application"""
        self.applications: Dict[str, BaseApp] = {}
        self.default_app: BaseApp = None


    def get(self, host: str) -> BaseApp:
        """Get App by host. Return default if not found"""
        return self.applications.get(host, self.default_app)


    def create_app(self, host: str, app_module: str = None, is_default: bool = False):
        """Create New App. Replace if host exist"""
        app = self.applications.get(host)
        if app:
            self.deleteApp(host)

        if app_module is None: app_module = host
        mod = __import__(app_module)
        mod_config = getattr(mod, "config", {})
        self.applications[host] = BaseApp(mod, mod_config)

        if is_default or self.default_app is None:
            self.default_app = self.applications[host]


    def delete_app(self, host: str):
        """Close then delete host"""
        app = self.applications.get(host)
        app.close()
        
        del self.applications[host]
        delattr(sys.modules[host])
        for k in sys.modules.keys():
            if k.startswith(host+".") and sys.modules[k] != None:
                del sys.modules[k]


    def close(self):
        """Close all applicatios"""
        for host in self.applications:
            self.applications[host].close()