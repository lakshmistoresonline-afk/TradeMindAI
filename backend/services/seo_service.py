class SEOService:
    """
    Centralized SEO Metadata Service.
    """

    METADATA = {
        "home": {
            "title": "TradeMind AI — Evidence-Driven Signal Intelligence for Indian Equities",
            "description": "Discover institutional-grade NIFTY-200 market signals. Auditable evidence and historical transparency for professional investors."
        },
        "signals": {
            "title": "Live Equity Signals — TradeMind AI",
            "description": "Active momentum signals across NIFTY-200 universe. Full structural evidence and machine-learning thesis."
        },
        "performance": {
            "title": "Historical Signal Track Record — TradeMind AI",
            "description": "Transparent audit of observed historical signal outcomes. Win rate, profit factor, and forensic accountability."
        }
    }

    @staticmethod
    def get_metadata(page: str):
        return SEOService.METADATA.get(page, SEOService.METADATA["home"])
