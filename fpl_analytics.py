"""
FPL Analytics Module
Performs data aggregation, crunching, ownership calculations, and trend analysis for mini-leagues.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from fpl_api import FPLApiClient

POSITION_MAP = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}

class FPLMiniLeagueAnalyzer:
    def __init__(self, api_client: Optional[FPLApiClient] = None):
        self.api = api_client or FPLApiClient()
        self.bootstrap = self.api.get_bootstrap_static()
        self._build_lookups()

    def _build_lookups(self):
        """Build quick lookups for players and teams."""
        self.elements = {el["id"]: el for el in self.bootstrap.get("elements", [])}
        self.teams = {t["id"]: t for t in self.bootstrap.get("teams", [])}
        self.events = {ev["id"]: ev for ev in self.bootstrap.get("events", [])}
        self.element_types = {et["id"]: et for et in self.bootstrap.get("element_types", [])}

    def get_player_info(self, element_id: int) -> Dict[str, Any]:
        el = self.elements.get(element_id, {})
        team = self.teams.get(el.get("team", 0), {})
        pos_id = el.get("element_type", 1)
        return {
            "id": element_id,
            "web_name": el.get("web_name", f"Player_{element_id}"),
            "full_name": f"{el.get('first_name', '')} {el.get('second_name', '')}".strip(),
            "team_short": team.get("short_name", "---"),
            "team_name": team.get("name", "---"),
            "position": POSITION_MAP.get(pos_id, "UNK"),
            "now_cost": el.get("now_cost", 0) / 10.0,
            "total_points": el.get("total_points", 0),
            "selected_by_percent": float(el.get("selected_by_percent", 0.0))
        }

    def fetch_full_league_data(
        self, 
        league_id: int, 
        gameweek: Optional[int] = None, 
        max_entries: Optional[int] = None,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        Fetch and compile complete mini-league data including standings, 
        manager picks for the gameweek, and manager histories.
        """
        if gameweek is None:
            gameweek = self.api.get_current_gameweek()

        league_data = self.api.get_all_league_standings(league_id)
        league_info = league_data.get("league", {})
        standings_results = league_data.get("standings", {}).get("results", [])

        if max_entries:
            standings_results = standings_results[:max_entries]

        total_managers = len(standings_results)
        if total_managers == 0:
            return {
                "league_info": league_info,
                "gameweek": gameweek,
                "managers": [],
                "standings_df": pd.DataFrame(),
                "ownership_df": pd.DataFrame(),
                "captaincy_df": pd.DataFrame(),
                "chips_df": pd.DataFrame(),
                "history_df": pd.DataFrame()
            }

        # Multi-threaded fetching for manager picks and histories
        manager_picks_map = {}
        manager_history_map = {}

        def fetch_manager_details(result):
            entry_id = result["entry"]
            picks = {}
            history = {}
            try:
                picks = self.api.get_manager_picks(entry_id, gameweek)
            except Exception:
                pass
            try:
                history = self.api.get_manager_history(entry_id)
            except Exception:
                pass
            return entry_id, picks, history

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(fetch_manager_details, r) for r in standings_results]
            completed = 0
            for future in futures:
                entry_id, picks, history = future.result()
                manager_picks_map[entry_id] = picks
                manager_history_map[entry_id] = history
                completed += 1
                if progress_callback:
                    progress_callback(completed, total_managers)

        # Process Standings & Details
        standings_rows = []
        ownership_counter = {}  # element_id: {owned: int, starting: int, captain: int, vc: int, benched: int}
        chips_rows = []
        history_rows = []

        for item in standings_results:
            entry_id = item["entry"]
            picks_data = manager_picks_map.get(entry_id, {})
            history_data = manager_history_map.get(entry_id, {})

            picks = picks_data.get("picks", [])
            entry_history = picks_data.get("entry_history", {})
            active_chip = picks_data.get("active_chip", None)

            # Determine rank movement
            rank = item.get("rank", 0)
            last_rank = item.get("last_rank", rank)
            if last_rank == 0 or rank == last_rank:
                movement = "➖ 0"
            elif rank < last_rank:
                movement = f"🔼 +{last_rank - rank}"
            else:
                movement = f"🔽 -{rank - last_rank}"

            # Captain & Vice Captain
            captain_name = "-"
            vc_name = "-"
            captain_multiplier = 2
            squad_elements = []

            for p in picks:
                elem_id = p.get("element")
                is_cap = p.get("is_captain", False)
                is_vc = p.get("is_vice_captain", False)
                pos = p.get("position", 1)  # 1-11 starting, 12-15 bench
                multiplier = p.get("multiplier", 1)

                p_info = self.get_player_info(elem_id)
                squad_elements.append({
                    **p_info,
                    "is_captain": is_cap,
                    "is_vice_captain": is_vc,
                    "position_slot": pos,
                    "multiplier": multiplier,
                    "is_starting": pos <= 11
                })

                if is_cap:
                    captain_name = f"{p_info['web_name']} ({p_info['team_short']})"
                    captain_multiplier = multiplier
                if is_vc:
                    vc_name = f"{p_info['web_name']} ({p_info['team_short']})"

                # Ownership metrics aggregation
                if elem_id not in ownership_counter:
                    ownership_counter[elem_id] = {
                        "info": p_info,
                        "owned_count": 0,
                        "starting_count": 0,
                        "benched_count": 0,
                        "captain_count": 0,
                        "vc_count": 0,
                        "triple_captain_count": 0
                    }
                
                ownership_counter[elem_id]["owned_count"] += 1
                if pos <= 11:
                    ownership_counter[elem_id]["starting_count"] += 1
                else:
                    ownership_counter[elem_id]["benched_count"] += 1
                
                if is_cap:
                    ownership_counter[elem_id]["captain_count"] += 1
                    if multiplier == 3:
                        ownership_counter[elem_id]["triple_captain_count"] += 1
                if is_vc:
                    ownership_counter[elem_id]["vc_count"] += 1

            # Chips used by this manager
            manager_chips = history_data.get("chips", [])
            chips_used_dict = {c["name"]: c["event"] for c in manager_chips}

            # Season performance history
            for gw_stat in history_data.get("current", []):
                history_rows.append({
                    "entry_id": entry_id,
                    "manager_name": item.get("player_name"),
                    "team_name": item.get("entry_name"),
                    "gameweek": gw_stat.get("event"),
                    "gw_points": gw_stat.get("points"),
                    "total_points": gw_stat.get("total_points"),
                    "overall_rank": gw_stat.get("overall_rank"),
                    "gw_rank": gw_stat.get("rank"),
                    "transfers": gw_stat.get("event_transfers"),
                    "transfer_cost": gw_stat.get("event_transfers_cost"),
                    "bench_points": gw_stat.get("points_on_bench"),
                    "team_value": gw_stat.get("value", 0) / 10.0,
                    "bank": gw_stat.get("bank", 0) / 10.0
                })

            chips_rows.append({
                "Rank": rank,
                "Team Name": item.get("entry_name"),
                "Manager": item.get("player_name"),
                "Active GW Chip": active_chip.upper() if active_chip else "-",
                "Wildcard 1": f"GW{chips_used_dict['wildcard']}" if 'wildcard' in chips_used_dict and chips_used_dict['wildcard'] <= 19 else "-",
                "Wildcard 2": f"GW{chips_used_dict['wildcard']}" if 'wildcard' in chips_used_dict and chips_used_dict['wildcard'] > 19 else "-",
                "Free Hit": f"GW{chips_used_dict['freehit']}" if 'freehit' in chips_used_dict else "-",
                "Triple Captain": f"GW{chips_used_dict['3xc']}" if '3xc' in chips_used_dict else "-",
                "Bench Boost": f"GW{chips_used_dict['bboost']}" if 'bboost' in chips_used_dict else "-",
                "Total Chips Used": len(manager_chips)
            })

            standings_rows.append({
                "Rank": rank,
                "Move": movement,
                "Team Name": item.get("entry_name"),
                "Manager": item.get("player_name"),
                "GW Points": item.get("event_total", entry_history.get("points", 0)),
                "Total Points": item.get("total", entry_history.get("total_points", 0)),
                "Overall Rank": entry_history.get("overall_rank", "-"),
                "Captain": captain_name,
                "Vice Captain": vc_name,
                "Active Chip": active_chip.upper() if active_chip else "-",
                "Transfers": entry_history.get("event_transfers", 0),
                "Transfer Cost": entry_history.get("event_transfers_cost", 0),
                "Bench Points": entry_history.get("points_on_bench", 0),
                "Team Value (£m)": entry_history.get("value", 0) / 10.0,
                "Bank (£m)": entry_history.get("bank", 0) / 10.0,
                "entry_id": entry_id,
                "squad": squad_elements
            })

        # Build DataFrames
        standings_df = pd.DataFrame(standings_rows)
        chips_df = pd.DataFrame(chips_rows)
        history_df = pd.DataFrame(history_rows)

        # Build Ownership DataFrame
        ownership_rows = []
        for elem_id, data in ownership_counter.items():
            info = data["info"]
            owned = data["owned_count"]
            starts = data["starting_count"]
            caps = data["captain_count"]
            tc = data["triple_captain_count"]
            
            # Effective Ownership (EO): (starts + captains + tc_extra) / total_managers * 100
            effective_owners = starts + caps + tc
            eo_pct = round((effective_owners / total_managers) * 100, 1)
            own_pct = round((owned / total_managers) * 100, 1)
            cap_pct = round((caps / total_managers) * 100, 1)

            ownership_rows.append({
                "Player": info["web_name"],
                "Team": info["team_short"],
                "Pos": info["position"],
                "Cost (£m)": info["now_cost"],
                "League Own %": own_pct,
                "Effective Own % (EO)": eo_pct,
                "Starting Count": starts,
                "Bench Count": data["benched_count"],
                "Captain Count": caps,
                "Triple Captain": tc,
                "FPL Overall Own %": info["selected_by_percent"],
                "Total Pts": info["total_points"]
            })

        ownership_df = pd.DataFrame(ownership_rows)
        if not ownership_df.empty:
            ownership_df = ownership_df.sort_values(by=["Effective Own % (EO)", "League Own %"], ascending=[False, False]).reset_index(drop=True)

        # Build Captaincy Summary DataFrame
        if not standings_df.empty:
            cap_counts = standings_df["Captain"].value_counts().reset_index()
            cap_counts.columns = ["Captain", "Count"]
            cap_counts["% of League"] = (cap_counts["Count"] / total_managers * 100).round(1)
            captaincy_df = cap_counts
        else:
            captaincy_df = pd.DataFrame()

        return {
            "league_info": league_info,
            "gameweek": gameweek,
            "total_managers": total_managers,
            "standings_df": standings_df,
            "ownership_df": ownership_df,
            "captaincy_df": captaincy_df,
            "chips_df": chips_df,
            "history_df": history_df,
            "raw_standings": standings_rows
        }
