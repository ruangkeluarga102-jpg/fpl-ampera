"""
FPL API Client Module
Provides methods to fetch official Fantasy Premier League data.
"""

import requests
from typing import Dict, Any, List, Optional
import time

BASE_URL = "https://fantasy.premierleague.com/api"

class FPLApiClient:
    def __init__(self, timeout: int = 15):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.timeout = timeout
        self._bootstrap_cache: Optional[Dict[str, Any]] = None

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_bootstrap_static(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch general FPL metadata (elements, teams, events/gameweeks)."""
        if self._bootstrap_cache is None or force_refresh:
            self._bootstrap_cache = self._get("bootstrap-static/")
        return self._bootstrap_cache

    def get_current_gameweek(self) -> int:
        """Find the current or latest active gameweek."""
        data = self.get_bootstrap_static()
        for event in data.get("events", []):
            if event.get("is_current"):
                return event.get("id")
            if event.get("is_next"):
                # If current hasn't started, previous is the latest played
                return max(1, event.get("id") - 1)
        # Fallback to last event or 1
        events = data.get("events", [])
        return events[-1]["id"] if events else 1

    def get_classic_league(self, league_id: int, page: int = 1) -> Dict[str, Any]:
        """Fetch standings for a classic mini-league."""
        return self._get(f"leagues-classic/{league_id}/standings/", params={"page_standings": page})

    def get_all_league_standings(self, league_id: int, max_pages: int = 10) -> Dict[str, Any]:
        """Fetch complete standings across multiple pages for a mini-league."""
        first_page = self.get_classic_league(league_id, page=1)
        league_info = first_page.get("league", {})
        standings_data = first_page.get("standings", {})
        results = list(standings_data.get("results", []))
        has_next = standings_data.get("has_next", False)
        
        # If standings results is empty (e.g. pre-season before GW1 points are computed), check new_entries
        if not results:
            new_entries = first_page.get("new_entries", {}).get("results", [])
            for idx, entry in enumerate(new_entries, 1):
                results.append({
                    "entry": entry.get("entry"),
                    "entry_name": entry.get("entry_name"),
                    "player_name": f"{entry.get('player_first_name', '')} {entry.get('player_last_name', '')}".strip(),
                    "rank": idx,
                    "last_rank": idx,
                    "total": 0,
                    "event_total": 0,
                    "rank_sort": idx
                })
            has_next = first_page.get("new_entries", {}).get("has_next", False)

        current_page = 1
        while has_next and current_page < max_pages:
            current_page += 1
            time.sleep(0.1)  # Respectful delay
            page_data = self.get_classic_league(league_id, page=current_page)
            page_standings = page_data.get("standings", {})
            page_results = page_standings.get("results", [])
            if page_results:
                results.extend(page_results)
                has_next = page_standings.get("has_next", False)
            else:
                page_new = page_data.get("new_entries", {}).get("results", [])
                if page_new:
                    for idx, entry in enumerate(page_new, len(results) + 1):
                        results.append({
                            "entry": entry.get("entry"),
                            "entry_name": entry.get("entry_name"),
                            "player_name": f"{entry.get('player_first_name', '')} {entry.get('player_last_name', '')}".strip(),
                            "rank": idx,
                            "last_rank": idx,
                            "total": 0,
                            "event_total": 0,
                            "rank_sort": idx
                        })
                    has_next = page_data.get("new_entries", {}).get("has_next", False)
                else:
                    has_next = False

        return {
            "league": league_info,
            "standings": {
                "has_next": has_next,
                "page": current_page,
                "results": results
            }
        }

    def get_manager_entry(self, entry_id: int) -> Dict[str, Any]:
        """Fetch manager team profile info."""
        return self._get(f"entry/{entry_id}/")

    def get_manager_picks(self, entry_id: int, event: int) -> Dict[str, Any]:
        """Fetch manager squad picks, captain, chips for a specific gameweek."""
        return self._get(f"entry/{entry_id}/event/{event}/picks/")

    def get_manager_history(self, entry_id: int) -> Dict[str, Any]:
        """Fetch manager season history (GW points, overall rank, chips used)."""
        return self._get(f"entry/{entry_id}/history/")

    def get_manager_transfers(self, entry_id: int) -> List[Dict[str, Any]]:
        """Fetch all transfers made by a manager throughout the season."""
        return self._get(f"entry/{entry_id}/transfers/")

    def get_live_event(self, event: int) -> Dict[str, Any]:
        """Fetch live stats and points for all players in a gameweek."""
        return self._get(f"event/{event}/live/")
