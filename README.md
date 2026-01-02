# Blackjack Strategy Simulator

[![Tests](https://github.com/greer/blackjack/actions/workflows/tests.yml/badge.svg)](https://github.com/greer/blackjack/actions/workflows/tests.yml)

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
