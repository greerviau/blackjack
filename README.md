# Blackjack Strategy Simulator

A comprehensive blackjack simulator with composable strategy architecture for testing different playing, counting, and betting strategies.

## Features

- **Composable Architecture**: Mix and match playing strategies, counting systems, and betting strategies
- **10 Predefined Strategies**: Ready-to-use configurations for comparison
- **JSON Configuration**: Define custom strategies without writing code
- **Full Card Counting**: Automatic card counting with count reset on shuffle
- **Progressive Betting**: Martingale, Paroli, Fibonacci, and more
- **Detailed Statistics**: ROI, house edge, bankroll tracking, and result export

## Quick Start

### Run All Strategies
```bash
python simulator.py --all
```

### Run Specific Strategies
```bash
# List available strategies
python simulator.py --list

# Run by index
python simulator.py --strategies 0 2 5
```

### Use Custom Configuration
```bash
python simulator.py --config my_strategies.json
```

## Project Structure

```
blackjack/
├── game.py                          # Core game engine
├── player.py                        # Player class
├── hand.py                          # Hand management
├── cards.py                         # Card and deck classes
├── strategy.py                      # Base strategy interface
├── simulator.py                     # Main simulator CLI
├── config_example.json              # Example configuration
│
├── strategies/
│   ├── components/                  # Composable strategy components
│   │   ├── playing_strategies.py   # How to play hands
│   │   ├── counting_systems.py     # Card counting systems
│   │   ├── betting_strategies.py   # Bet sizing strategies
│   │   └── composable_strategy.py  # Main composable strategy
│   └── [legacy strategies...]       # Old monolithic strategies
│
├── tests/
│   ├── test_components.py          # Component unit tests
│   ├── test_counting_integration.py # Integration tests
│   └── test_game.py                 # Game logic tests
│
├── analysis/
│   └── [analysis scripts...]        # Performance analysis tools
│
└── docs/
    ├── README.md                    # This file
    ├── COMPOSABLE_ARCHITECTURE.md   # Component architecture guide
    └── SIMULATOR_README.md          # Detailed simulator guide
```

## Available Components

### Playing Strategies
- **BasicPlayingStrategy**: Optimal basic strategy using lookup tables
- **SimplePlayingStrategy**: Hit until 17, then stand
- **RandomPlayingStrategy**: Random decisions (for testing)

### Counting Systems
- **NoCounter**: No card counting
- **HiLoCounter**: Hi-Lo counting (+1 for 2-6, -1 for 10-A)
- **HiOptICounter**: Hi-Opt I counting (more accurate)
- **KOCounter**: Knockout counting (unbalanced, simpler)

### Betting Strategies
- **FlatBetting**: Fixed bet amount
- **CountBasedBetting**: Bet based on true count (linear/aggressive/min-max spreads)
- **MartingaleBetting**: Double after loss
- **ParoliBetting**: Double after win
- **FibonacciBetting**: Fibonacci sequence
- **OscarGrindBetting**: Conservative progression
- **OneTwoThreeBetting**: 1-2-3 unit progression

## Example Usage

### Example 1: Basic Strategy with Flat Betting
```python
from strategies.components import ComposableStrategy, BasicPlayingStrategy, NoCounter, FlatBetting
from player import Player
from game import Blackjack

strategy = ComposableStrategy(
    playing_strategy=BasicPlayingStrategy(),
    counting_system=NoCounter(),
    betting_strategy=FlatBetting(min_bet=10),
    max_rounds=1000
)

player = Player(strategy=strategy, bankroll=1000)
game = Blackjack(player, n_decks=6, table_min=10, table_max=1000)
results = game.play()
```

### Example 2: Hi-Lo Card Counting
```python
from strategies.components import ComposableStrategy, BasicPlayingStrategy, HiLoCounter, CountBasedBetting

strategy = ComposableStrategy(
    playing_strategy=BasicPlayingStrategy(),
    counting_system=HiLoCounter(),
    betting_strategy=CountBasedBetting(min_bet=10, max_bet=500, spread_type="aggressive"),
    max_rounds=1000
)
```

### Example 3: JSON Configuration
Create `my_strategy.json`:
```json
{
  "strategies": [
    {
      "name": "My Counter",
      "playing_strategy": "basic",
      "counting_system": "hilo",
      "betting_strategy": {
        "type": "count_based",
        "min_bet": 10,
        "max_bet": 500,
        "spread_type": "aggressive"
      },
      "starting_bankroll": 5000,
      "max_rounds": 1000
    }
  ],
  "game_settings": {
    "n_decks": 6,
    "table_min": 10,
    "table_max": 1000,
    "blackjack_payout": 1.5,
    "penetration": 0.75
  }
}
```

Run it:
```bash
python simulator.py --config my_strategy.json
```

## Simulator Commands

| Command | Description |
|---------|-------------|
| `--all` | Run all 10 predefined strategies |
| `--strategies N [N ...]` | Run specific strategies by index |
| `--config FILE` | Load custom strategy configuration |
| `--list` | List all available strategies |
| `--verbose` | Show detailed output |
| `--output FILE` | Save results to JSON |

## Card Counting Features

The simulator includes full card counting integration:

- **Automatic Counting**: Cards are counted as they're dealt
- **Count Reset**: Count automatically resets when deck is reshuffled
- **True Count**: Running count adjusted for remaining decks
- **Bet Spreading**: Bet size adjusts based on count
- **Multiple Systems**: Hi-Lo, KO, Hi-Opt I

## Testing

Run all tests:
```bash
# Component unit tests
python tests/test_components.py

# Integration tests (counting & betting)
python tests/test_counting_integration.py

# Game logic tests
python tests/test_game.py
```

## Documentation

- **[COMPOSABLE_ARCHITECTURE.md](COMPOSABLE_ARCHITECTURE.md)**: Detailed guide to the composable strategy system
- **[SIMULATOR_README.md](SIMULATOR_README.md)**: Complete simulator documentation with examples
- **[config_example.json](config_example.json)**: Example configuration file

## Understanding Results

### Key Metrics

- **ROI (Return on Investment)**: Percentage profit/loss relative to starting bankroll
- **House Edge**: Effective house advantage based on total wagered vs. won
- **Rounds**: Number of hands played
- **Busted**: Whether the strategy went bankrupt

### Expected Results

- **Basic Strategy (Flat Betting)**: -1% to +1% ROI (near break-even)
- **Card Counting (Good Spread)**: +2% to +5% ROI with proper bankroll
- **Progressive Betting**: High variance, risky but can show short-term gains
- **Simple Strategy**: -5% to -10% ROI (much worse than basic strategy)

## Tips

### For Beginners
1. Start with: `python simulator.py --strategies 0 9`
2. Compare basic strategy vs. simple strategy to see the difference

### For Card Counters
1. Test different spreads: `python simulator.py --strategies 1 2 3`
2. Aggressive spreads (1-50+) perform better but require larger bankroll

### For System Testing
1. Test progressive systems: `python simulator.py --strategies 6 7 8`
2. Remember: Progressive systems don't change house edge, just variance

## Creating Custom Strategies

1. **Copy the example**: `cp config_example.json my_strategy.json`
2. **Edit the JSON**: Modify strategies, game settings, and parameters
3. **Run it**: `python simulator.py --config my_strategy.json`

Mix and match any combination of:
- Playing: basic, simple
- Counting: none, hilo, ko, hiopt1
- Betting: flat, count_based, martingale, paroli, fibonacci, oscar_grind, 123

## Advanced Usage

### Programmatic Simulation

```python
from simulator import run_simulation
from strategies.components import ComposableStrategy, BasicPlayingStrategy, HiLoCounter, CountBasedBetting

strategy = ComposableStrategy(
    playing_strategy=BasicPlayingStrategy(),
    counting_system=HiLoCounter(),
    betting_strategy=CountBasedBetting(min_bet=10, max_bet=500)
)

result = run_simulation(
    name="My Strategy",
    strategy=strategy,
    starting_bankroll=5000
)

print(f"ROI: {result.roi_percent:.2f}%")
print(f"Final Bankroll: ${result.final_bankroll:,.2f}")
```

### Extending Components

Create new playing strategies:
```python
from strategies.components import PlayingStrategy

class MyPlayingStrategy(PlayingStrategy):
    def decide_action(self, hand, dealer_upcard_value, valid_actions):
        # Your logic here
        return "hit" or "stand" or "double" or "split"
```

Create new counting systems:
```python
from strategies.components import CountingSystem

class MyCounter(CountingSystem):
    def count_card(self, card):
        # Update self.running_count
        pass
    
    def get_true_count(self):
        # Calculate and return true count
        return self.running_count / decks_remaining
```

## Performance Notes

- Simulations run 1000 hands by default
- Running all 10 strategies takes ~30-60 seconds
- Results vary due to randomness - run multiple times for statistical significance
- Use larger bankrolls for aggressive betting strategies to avoid early bust-outs

## License

This is an educational project for understanding blackjack strategy and simulation.

## Contributing

Feel free to:
- Add new playing strategies
- Implement additional counting systems
- Create new betting strategies
- Improve documentation
- Add more tests

## Disclaimer

This simulator is for educational purposes only. Card counting is legal but casinos may ask you to leave. Gambling involves risk - never bet more than you can afford to lose.
