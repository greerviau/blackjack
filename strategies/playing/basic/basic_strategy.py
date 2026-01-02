"""
Basic Strategy - Optimal play based on mathematical expectation.

Uses pre-computed optimal decision tables for hard hands, soft hands, and pairs.
"""

import csv
import os

from ..base import PlayingStrategy


class BasicPlayingStrategy(PlayingStrategy):
    """Optimal basic strategy from CSV tables."""

    def __init__(self, h17: bool):
        # Load tables from the same directory as this file
        base_path = os.path.dirname(__file__)
        if h17:
            self.hard_table = self._load_table(os.path.join(base_path, "hard_h17.csv"))
            self.soft_table = self._load_table(os.path.join(base_path, "soft_h17.csv"))
        else:
            self.hard_table = self._load_table(os.path.join(base_path, "hard_s17.csv"))
            self.soft_table = self._load_table(os.path.join(base_path, "soft_s17.csv"))
        self.pairs_table = self._load_table(os.path.join(base_path, "pairs.csv"))

    def _load_table(self, filepath: str) -> dict:
        """Load strategy table from CSV."""
        table = {}
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            dealer_cards = [int(x) for x in header[1:]]

            for row in reader:
                player_total = int(row[0])
                actions = row[1:]
                table[player_total] = {}
                for dealer_card, action in zip(dealer_cards, actions):
                    table[player_total][dealer_card] = action

        return table

    def _lookup_action(self, table: dict, key: int, dealer_upcard: int) -> str | None:
        """Look up action code from a strategy table."""
        return table.get(key, {}).get(dealer_upcard)

    def decide_action(
        self,
        hand,
        dealer_upcard_value: int,
        valid_actions: list,
    ) -> str:
        """Use basic strategy tables."""
        action_code = None

        if hand.is_pair:
            action_code = self._lookup_action(
                self.pairs_table,
                hand.cards[0].value,
                dealer_upcard_value,
            )
        elif hand.is_soft:
            action_code = self._lookup_action(
                self.soft_table,
                hand.value,
                dealer_upcard_value,
            )
        else:
            action_code = self._lookup_action(
                self.hard_table,
                hand.value,
                dealer_upcard_value,
            )

        return self._translate_action(action_code, valid_actions)

    def _translate_action(self, action_code: str | None, valid_actions: list) -> str:
        """Translate action code to actual action."""
        if not action_code:
            return "stand"

        actions = {
            "H": "hit",
            "S": "stand",
            "Dh": "double" if "double" in valid_actions else "hit",
            "Ds": "double" if "double" in valid_actions else "stand",
            "P": "split" if "split" in valid_actions else "hit",
            "Xh": "surrender" if "surrender" in valid_actions else "hit",
            "Xs": "surrender" if "surrender" in valid_actions else "stand",
            "Xp": "surrender" if "surrender" in valid_actions else "split",
        }
        return actions.get(action_code, "stand")
