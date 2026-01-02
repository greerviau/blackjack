# Blackjack Strategy Simulator

[![Tests](https://github.com/greerviau/blackjack/actions/workflows/tests.yml/badge.svg)](https://github.com/greerviau/blackjack/actions/workflows/tests.yml)

A blackjack simulator for testing and comparing different playing, counting, and betting strategies.

## Features

- **Composable Strategies**: Mix and match playing strategies, counting systems, and betting spreads
- **Card Counting**: Hi-Lo, Pseudo counting, win/loss streaks
- **Betting Systems**: Flat, Martingale, linear spreads, min-max spreads
- **Exit Strategies**: Double-up, Peak (trailing profit lock)
- **Realistic Rules**: H17/S17, DAS, late surrender, resplit aces, hit split aces
- **Detailed Statistics**: $/hour, house edge, RoR, drawdown, win/loss/push rates

## Quick Start

```bash
# Run all strategies
python simulator.py

# List available strategies
python simulator.py --list

# Run specific strategies
python simulator.py --strategies 0 3 5

# Custom settings
python simulator.py --bankroll 5000 --rounds 500 --games 1000
```

## Example Output

```
===========================================================================
  SIMULATION RESULTS
===========================================================================
  Strategy                Rounds    $/Hour   House Edge     Win    Push    Loss   Profit%     RoR  Drawdown
---------------------------------------------------------------------------
  Basic + Hi-Lo + MinMax  110,657   +51.62       -0.96%   41.3%    8.4%   50.3%     24.6%   70.2%     77.4%
  Basic + Hi-Lo + Linear  179,475   +24.09       -0.92%   42.4%    8.6%   49.0%     42.4%   42.2%     61.3%
  Basic + Flat            250,000    -3.03       +0.38%   43.5%    8.6%   47.9%     45.0%    0.0%     18.0%
```

## Available Strategies

| Strategy | Description |
|----------|-------------|
| Basic + Flat | Basic strategy with flat betting |
| Basic + Martingale | Double bet after each loss |
| Basic + Win Increase | Increase bet after wins (1-2-4) |
| Basic + Hi-Lo + Linear | Hi-Lo counting with linear bet spread |
| Basic + Hi-Lo + MinMax | Hi-Lo counting with min/max spread |
| Basic + Pseudo + Linear | Simplified counting (2-5 vs 10-A) |
| Basic + Pseudo + MinMax | Simplified counting with min/max spread |

### Exit Strategies

Add `--exit` to include exit strategy variants:

| Exit Strategy | Description |
|---------------|-------------|
| Double | Exit after doubling bankroll |
| Peak | Trailing stop-loss that locks in profits |

## CLI Options

```
Options:
  --strategies N [N ...]  Run specific strategies by index
  --list                  List all available strategies
  --rounds, -r N          Rounds per game (default: 500)
  --games, -g N           Games per strategy (default: 1000)
  --bankroll, -b N        Starting bankroll (default: 1000)
  --table-min N           Table minimum (default: 10)
  --table-max N           Table maximum (default: 300)
  --decks, -d N           Number of decks (default: 8)
  --s17                   Dealer stands on soft 17 (default: hits)
  --no-das                Disable double after split
  --surrender             Enable late surrender
  --exit                  Include exit strategies
  --hands-per-hour N      For $/hour calculation (default: 70)
  --seed N                Random seed for reproducibility
```

## Project Structure

```
blackjack/
├── core/
│   ├── cards.py          # Card and Deck classes
│   ├── hand.py           # Hand management
│   ├── player.py         # Player base class
│   └── game.py           # Game engine and rules
├── strategies/
│   ├── composable_strategy.py  # Main strategy composer
│   ├── playing/          # Playing strategies (basic strategy)
│   ├── counting/         # Counting systems (Hi-Lo, Pseudo, streaks)
│   ├── bet_spread.py     # Bet sizing based on count
│   ├── exit/             # Exit strategies (Double, Peak)
│   └── presets.py        # Pre-configured strategy combinations
├── tests/
│   └── test_game.py      # Game logic tests
├── simulator.py          # CLI simulator
└── play.py               # Interactive play mode
```

## Game Rules

Default rules (configurable):
- 8 decks
- Dealer hits soft 17
- Double after split allowed
- Up to 3 splits
- No surrender (enable with `--surrender`)
- 3:2 blackjack payout
- 75% penetration

## Custom Strategies

Strategies are composed of three components:

### 1. Counting System

Track cards to inform betting decisions. Create a new counter in `strategies/counting/`:

```python
from strategies.counting.base import CountingSystem

class MyCounter(CountingSystem):
    def count_card(self, card) -> None:
        # Update running_count based on card.value or card.rank
        if card.value <= 6:
            self.running_count += 1
        elif card.value >= 10:
            self.running_count -= 1
        self.cards_seen += 1

    def get_true_count(self) -> int:
        decks_remaining = (self.n_decks * 52 - self.cards_seen) / 52
        return int(self.running_count / max(decks_remaining, 0.5))
```

### 2. Bet Spread

Define how bet size changes with the count using `BetSpread`:

```python
from strategies.bet_spread import BetSpread

# Bet $10 at count 0, $25 at count 2, $50 at count 3+
spread = BetSpread(
    spread={2: 25, 3: 50},
    min_bet=10,
    max_bet=300
)
```

### 3. Exit Strategy

Define when to leave the table. Create in `strategies/exit/`:

```python
from strategies.exit.base import ExitStrategy

class MyExitStrategy(ExitStrategy):
    def __init__(self, starting_bankroll: float, target_pct: float = 0.5):
        super().__init__(starting_bankroll)
        self.target = starting_bankroll * (1 + target_pct)

    def should_exit(self, bankroll: float) -> bool:
        return bankroll >= self.target
```

### Composing a Strategy

Combine components into a `ComposableStrategy`:

```python
from strategies import ComposableStrategy
from strategies.counting import HiLoCounter
from strategies.bet_spread import BetSpread
from strategies.exit import DoubleExitStrategy
from strategies.playing import BasicStrategy

strategy = ComposableStrategy(
    bankroll=1000,
    playing_strategy=BasicStrategy(h17=True),
    counting_system=HiLoCounter(n_decks=8),
    bet_spread=BetSpread({1: 20, 2: 40, 3: 80}, min_bet=10, max_bet=300),
    exit_strategy=DoubleExitStrategy(starting_bankroll=1000),
)
```

### Adding to Presets

To include your strategy in the simulator, add it to `strategies/presets.py`:

```python
def create_strategy(name: str, bankroll: float, ...) -> ComposableStrategy:
    # Add your strategy configuration here
    if name == "My Custom Strategy":
        return ComposableStrategy(
            bankroll=bankroll,
            playing_strategy=BasicStrategy(h17=h17),
            counting_system=MyCounter(n_decks),
            bet_spread=BetSpread({2: 25, 3: 50}, table_min, table_max),
        )
```

### Testing Your Strategy

Run a quick test:

```python
from core import Blackjack

game = Blackjack(strategy, n_decks=8, table_min=10, table_max=300)
results = game.play(max_rounds=1000)

print(f"Profit: ${results['profit']:.2f}")
print(f"Win rate: {results['win_rate']:.1f}%")
```

Or add it to presets and use the simulator for statistical analysis across many games.

## Testing

```bash
python -m pytest
```

## Interactive Play

```bash
python play.py
```

## Understanding the Stats

| Stat | Description |
|------|-------------|
| $/Hour | Expected hourly profit/loss at 70 hands/hour |
| House Edge | Casino advantage (negative = player advantage) |
| Win/Push/Loss | Hand outcome percentages |
| Profit% | Percentage of sessions ending in profit |
| RoR | Risk of Ruin - percentage of sessions that went bust |
| Drawdown | Average maximum drawdown from peak bankroll |

## License

Educational use only. Gambling involves risk.
