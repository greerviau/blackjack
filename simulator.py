#!/usr/bin/env python3
"""
Blackjack strategy simulator.

Run simulations for multiple strategies and compare their performance.
"""

import argparse
import math
import os
import random
import statistics
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List

from core import Blackjack
from strategies import ComposableStrategy
from strategies.presets import create_strategy, get_strategy_names


@dataclass
class SimulationResult:
    """Results from a single strategy simulation."""

    name: str
    rounds_played: int
    starting_bankroll: float
    final_bankroll: float
    total_wagered: float
    total_won: float
    profit: float
    roi_percent: float
    max_bankroll: float
    min_bankroll: float
    busted: bool
    win_rate: float
    push_rate: float
    loss_rate: float
    surrender_rate: float
    max_drawdown: float
    hands_won: int
    hands_lost: int
    hands_pushed: int
    hands_surrendered: int


@dataclass
class AggregateResult:
    """Aggregate results from multiple games of the same strategy."""

    name: str
    num_games: int
    avg_rounds_per_game: float
    total_rounds: int
    avg_roi: float
    std_roi: float
    min_roi: float
    max_roi: float
    median_roi: float
    avg_house_edge: float
    ev_per_hand: float  # Expected value per hand in dollars
    risk_of_ruin: float  # Percentage of games that went bust
    avg_final_bankroll: float
    success_rate: float
    avg_win_rate: float
    avg_push_rate: float
    avg_loss_rate: float
    avg_surrender_rate: float
    avg_max_drawdown: float
    roi_std_error: float  # Standard error of mean ROI
    roi_confidence_95: tuple  # (lower, upper) 95% CI


def run_strategy_games(
    strategy_name: str,
    num_games: int,
    max_rounds: int,
    starting_bankroll: float,
    n_decks: int,
    table_min: int,
    table_max: int,
    h17: bool,
    das: bool,
    late_surrender: bool,
    max_splits: int,
    seed: float,
) -> List[SimulationResult]:
    """Run multiple games for a single strategy. Used by parallel executor."""
    random.seed(seed)
    results = []

    for _ in range(num_games):
        strategy = create_strategy(
            strategy_name, starting_bankroll, n_decks, table_min, table_max, h17
        )
        result = run_simulation(
            name=strategy_name,
            strategy=strategy,
            max_rounds=max_rounds,
            starting_bankroll=starting_bankroll,
            n_decks=n_decks,
            table_min=table_min,
            table_max=table_max,
            h17=h17,
            das=das,
            late_surrender=late_surrender,
            max_splits=max_splits,
        )
        results.append(result)

    return results


def run_simulation(
    name: str,
    strategy: ComposableStrategy,
    max_rounds: int,
    starting_bankroll: float,
    n_decks: int,
    table_min: int,
    table_max: int,
    h17: bool,
    das: bool,
    late_surrender: bool,
    max_splits: int,
) -> SimulationResult:
    """Run a single simulation with the given strategy."""
    game = Blackjack(
        strategy,
        n_decks=n_decks,
        table_min=table_min,
        table_max=table_max,
        h17=h17,
        das=das,
        late_surrender=late_surrender,
        max_splits=max_splits,
    )

    results = game.play(max_rounds=max_rounds)

    final_bankroll = results["final_bankroll"]
    rounds_played = results["rounds_played"]
    total_wagered = results["total_wagered"]
    total_won = results["total_won"]
    profit = results["profit"]
    roi_percent = (profit / starting_bankroll) * 100

    busted = final_bankroll <= 0

    hands_won = results["hands_won"]
    hands_lost = results["hands_lost"]
    hands_pushed = results["hands_pushed"]
    hands_surrendered = results["hands_surrendered"]
    total_hands = hands_won + hands_lost + hands_pushed + hands_surrendered

    if total_hands > 0:
        push_rate = (hands_pushed / total_hands) * 100
        loss_rate = (hands_lost / total_hands) * 100
        surrender_rate = (hands_surrendered / total_hands) * 100
    else:
        push_rate = 0
        loss_rate = 0
        surrender_rate = 0

    return SimulationResult(
        name=name,
        rounds_played=rounds_played,
        starting_bankroll=starting_bankroll,
        final_bankroll=final_bankroll,
        total_wagered=total_wagered,
        total_won=total_won,
        profit=profit,
        roi_percent=roi_percent,
        max_bankroll=results["max_bankroll"],
        min_bankroll=results["min_bankroll"],
        busted=busted,
        win_rate=results["win_rate"],
        push_rate=push_rate,
        loss_rate=loss_rate,
        surrender_rate=surrender_rate,
        max_drawdown=results["max_drawdown"],
        hands_won=hands_won,
        hands_lost=hands_lost,
        hands_pushed=hands_pushed,
        hands_surrendered=hands_surrendered,
    )


def aggregate_results(results: List[SimulationResult]) -> AggregateResult:
    """Aggregate multiple game results into summary statistics."""
    name = results[0].name
    num_games = len(results)

    rounds = [r.rounds_played for r in results]
    total_rounds = sum(rounds)
    rois = [r.roi_percent for r in results]
    final_bankrolls = [r.final_bankroll for r in results]
    busts = sum(1 for r in results if r.busted)
    profitable = sum(1 for r in results if r.profit > 0)
    win_rates = [r.win_rate for r in results]
    push_rates = [r.push_rate for r in results]
    loss_rates = [r.loss_rate for r in results]
    surrender_rates = [r.surrender_rate for r in results]
    drawdowns = [r.max_drawdown for r in results]

    # Calculate house edge from total wagered and profit/loss
    # House Edge = -Profit / Total Wagered × 100
    # Positive = house advantage, Negative = player advantage
    total_wagered = sum(r.total_wagered for r in results)
    total_profit = sum(r.profit for r in results)
    if total_wagered > 0:
        avg_house_edge = (-total_profit / total_wagered) * 100
    else:
        avg_house_edge = 0

    # Calculate EV per hand (expected value in dollars)
    if total_rounds > 0:
        ev_per_hand = total_profit / total_rounds
    else:
        ev_per_hand = 0

    # Calculate confidence intervals
    avg_roi = statistics.mean(rois)
    std_roi = statistics.stdev(rois) if num_games > 1 else 0

    # Standard error of the mean
    roi_sem = std_roi / math.sqrt(num_games) if num_games > 0 else 0

    # 95% confidence interval (±1.96 * SEM for normal distribution)
    margin = 1.96 * roi_sem
    roi_ci_lower = avg_roi - margin
    roi_ci_upper = avg_roi + margin

    return AggregateResult(
        name=name,
        num_games=num_games,
        avg_rounds_per_game=statistics.mean(rounds),
        total_rounds=total_rounds,
        avg_roi=avg_roi,
        std_roi=std_roi,
        min_roi=min(rois),
        max_roi=max(rois),
        median_roi=statistics.median(rois),
        avg_house_edge=avg_house_edge,
        ev_per_hand=ev_per_hand,
        risk_of_ruin=(busts / num_games) * 100,
        avg_final_bankroll=statistics.mean(final_bankrolls),
        success_rate=(profitable / num_games) * 100,
        avg_win_rate=statistics.mean(win_rates),
        avg_push_rate=statistics.mean(push_rates),
        avg_loss_rate=statistics.mean(loss_rates),
        avg_surrender_rate=statistics.mean(surrender_rates),
        avg_max_drawdown=statistics.mean(drawdowns),
        roi_std_error=roi_sem,
        roi_confidence_95=(roi_ci_lower, roi_ci_upper),
    )


def print_aggregate_results(
    agg_results: List[AggregateResult],
    hands_per_hour: int = 70,
    show_surrender: bool = False,
):
    """Print aggregate results from multiple simulations."""
    # Calculate dynamic width based on longest strategy name
    name_width = max(len(r.name) for r in agg_results) + 2
    total_width = name_width + 105
    if show_surrender:
        total_width += 10

    print("\n")
    print("=" * total_width)
    print("  SIMULATION RESULTS")
    print("=" * total_width)

    # Build header
    header_parts = [
        f"{'Strategy':<{name_width}}",
        f"{'Rounds':>10}",
        f"{'$/Hour':>10}",
        f"{'House Edge':>13}",
        f"{'Win':>8}",
        f"{'Push':>8}",
        f"{'Loss':>8}",
    ]
    if show_surrender:
        header_parts.append(f"{'Surr':>10}")
    header_parts.extend(
        [
            f"{'Profit%':>10}",
            f"{'RoR':>8}",
            f"{'Drawdown':>10}",
        ]
    )

    print("  " + "".join(header_parts))
    print("-" * total_width)

    # Sort by EV per hand (descending - best EV first)
    sorted_results = sorted(agg_results, key=lambda x: x.ev_per_hand, reverse=True)

    # Print each result
    for result in sorted_results:
        rounds_str = f"{result.total_rounds:,}"
        dollars_per_hour = result.ev_per_hand * hands_per_hour
        dph_str = f"{dollars_per_hour:>+.2f}"
        edge_str = f"{result.avg_house_edge:>+.2f}%"

        row_parts = [
            f"  {result.name:<{name_width}}",
            f"{rounds_str:>10}",
            f"{dph_str:>10}",
            f"{edge_str:>13}",
            f"{result.avg_win_rate:>7.1f}%",
            f"{result.avg_push_rate:>7.1f}%",
            f"{result.avg_loss_rate:>7.1f}%",
        ]
        if show_surrender:
            row_parts.append(f"{result.avg_surrender_rate:>9.1f}%")
        row_parts.extend(
            [
                f"{result.success_rate:>9.1f}%",
                f"{result.risk_of_ruin:>7.1f}%",
                f"{result.avg_max_drawdown:>9.1f}%",
            ]
        )

        print("".join(row_parts))

    print("-" * total_width)

    # Rankings
    print("\n  RANKINGS")
    print("  " + "-" * 50)

    by_ev = sorted(agg_results, key=lambda x: x.ev_per_hand, reverse=True)
    by_edge = sorted(agg_results, key=lambda x: x.avg_house_edge)
    by_vol = sorted(agg_results, key=lambda x: x.std_roi)
    by_success = sorted(agg_results, key=lambda x: x.success_rate, reverse=True)
    by_dd = sorted(agg_results, key=lambda x: x.avg_max_drawdown)
    by_ror = sorted(agg_results, key=lambda x: x.risk_of_ruin)

    print(
        f"  Best $/Hour:      {by_ev[0].name} ({by_ev[0].ev_per_hand * hands_per_hour:>+.2f})"
    )
    print(
        f"  Worst $/Hour:     {by_ev[-1].name} ({by_ev[-1].ev_per_hand * hands_per_hour:>+.2f})"
    )
    print(
        f"\n  Lowest Edge:      {by_edge[0].name} ({by_edge[0].avg_house_edge:>+.2f}%)"
    )
    print(
        f"  Highest Edge:     {by_edge[-1].name} ({by_edge[-1].avg_house_edge:>+.2f}%)"
    )
    print(f"\n  Lowest Variance:  {by_vol[0].name} (std: {by_vol[0].std_roi:.2f}%)")
    print(f"  Highest Variance: {by_vol[-1].name} (std: {by_vol[-1].std_roi:.2f}%)")
    print(
        f"\n  Best Profit%:     {by_success[0].name} ({by_success[0].success_rate:.1f}%)"
    )
    print(
        f"  Worst Profit%:    {by_success[-1].name} ({by_success[-1].success_rate:.1f}%)"
    )
    print(f"\n  Lowest Drawdown:  {by_dd[0].name} ({by_dd[0].avg_max_drawdown:.1f}%)")
    print(f"  Highest Drawdown: {by_dd[-1].name} ({by_dd[-1].avg_max_drawdown:.1f}%)")
    print(f"\n  Lowest RoR:       {by_ror[0].name} ({by_ror[0].risk_of_ruin:.1f}%)")
    print(f"  Highest RoR:      {by_ror[-1].name} ({by_ror[-1].risk_of_ruin:.1f}%)")

    print()


def main():
    """Main simulator entry point."""
    parser = argparse.ArgumentParser(
        description="Blackjack Strategy Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all strategies with defaults
  python simulator.py

  # Run specific strategies by index
  python simulator.py --strategies 0 2 5

  # Run with custom bankroll and hands
  python simulator.py --bankroll 5000 --hands 500 --games 100

  # List available strategies
  python simulator.py --list
        """,
    )

    parser.add_argument(
        "--strategies",
        type=int,
        nargs="+",
        help="Run specific strategies by index (see --list)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all available strategies"
    )
    parser.add_argument(
        "--rounds",
        "-r",
        type=int,
        default=500,
        help="Number of rounds per game (default: 500)",
    )
    parser.add_argument(
        "--games",
        "-g",
        type=int,
        default=1000,
        help="Number of games to play per strategy (default: 1000)",
    )
    parser.add_argument(
        "--bankroll",
        "-b",
        type=int,
        default=1000,
        help="Starting bankroll for all strategies (default: 1000)",
    )
    parser.add_argument(
        "--table-min",
        type=int,
        default=10,
        help="Table minimum (default: 10)",
    )
    parser.add_argument(
        "--table-max",
        type=int,
        default=300,
        help="Table maximum (default: 300)",
    )
    parser.add_argument(
        "--decks",
        "-d",
        type=int,
        default=8,
        help="Number of decks in the shoe (default: 8)",
    )
    parser.add_argument(
        "--splits",
        "-s",
        type=int,
        default=3,
        help="Max number of splits",
    )
    parser.add_argument("--s17", action="store_true", help="Dealer stays on a soft s17")
    parser.add_argument(
        "--no-das", action="store_true", help="Disallow double after splits"
    )
    parser.add_argument("--surrender", action="store_true", help="Allow late surrender")
    parser.add_argument(
        "--exit", action="store_true", help="Include exit strategies in presets"
    )
    parser.add_argument(
        "--seed",
        type=float,
        default=None,
        help="Random seed for reproducibility (optional)",
    )
    parser.add_argument(
        "--hands-per-hour",
        type=int,
        default=70,
        help="Hands per hour for $/hour calculation (default: 70)",
    )

    args = parser.parse_args()

    rounds = args.rounds
    games = args.games
    starting_bankroll = args.bankroll
    table_max = args.table_max
    table_min = args.table_min
    decks = args.decks
    seed = args.seed
    h17 = not args.s17
    das = not args.no_das
    late_surrender = args.surrender
    max_splits = args.splits
    hands_per_hour = args.hands_per_hour

    if not seed:
        seed = random.random()

    # List strategies
    include_exit = args.exit
    all_strategy_names = get_strategy_names(include_exit=include_exit)

    if args.list:
        print()
        print("=" * 40)
        print("  AVAILABLE STRATEGIES")
        print("=" * 40)
        for i, name in enumerate(all_strategy_names):
            print(f"    {i}: {name}")
        print()
        return

    # Determine which strategies to run
    if args.strategies:
        strategies_to_run = []
        for idx in args.strategies:
            if 0 <= idx < len(all_strategy_names):
                strategies_to_run.append(all_strategy_names[idx])
            else:
                print(
                    f"Warning: Strategy index {idx} out of range (0-{len(all_strategy_names) - 1})"
                )
        if not strategies_to_run:
            print("Error: No valid strategies selected")
            return
    else:
        strategies_to_run = all_strategy_names

    # Run simulations
    print()
    print("=" * 50)
    print("  BLACKJACK STRATEGY SIMULATOR")
    print("=" * 50)
    print()
    print("  Configuration:")
    print(f"    Strategies:      {len(strategies_to_run)}")
    print(f"    Bankroll:        ${starting_bankroll:,}")
    print(f"    Rounds/Game:     {rounds:,}")
    print(f"    Games/Strategy:  {games:,}")
    if seed is not None:
        print(f"    Random Seed:     {seed}")
    print()
    print("  Table Rules:")
    print(f"    Bet Range:       ${table_min} - ${table_max}")
    print(f"    Decks:           {decks}")
    print(f"    Dealer H17:      {'Yes' if h17 else 'No'}")
    print(f"    DAS:             {'Yes' if das else 'No'}")
    print(f"    Late Surrender:  {'Yes' if late_surrender else 'No'}")
    print(f"    Max Splits:      {max_splits}")
    print()

    # Run simulations in parallel
    all_results = {}
    status = {name: "pending" for name in strategies_to_run}
    spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    stop_spinner = threading.Event()

    def render_status(frame_idx: int = 0):
        """Render the current status of all strategies."""
        lines = ["  Running Strategies:", "  " + "-" * 40]
        for name in strategies_to_run:
            state = status[name]
            if state == "done":
                lines.append(f"    ✓ {name}")
            elif state == "running":
                lines.append(
                    f"    {spinner_frames[frame_idx % len(spinner_frames)]} {name}"
                )
            else:
                lines.append(f"      {name}")
        return lines

    def spinner_thread():
        """Animate the spinner while strategies are running."""
        frame = 0
        while not stop_spinner.is_set():
            lines = render_status(frame)
            # Move cursor up and rewrite
            sys.stdout.write(f"\033[{len(lines)}A")
            sys.stdout.write("\033[J")
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stdout.flush()
            frame += 1
            time.sleep(0.1)

    # Print initial status
    for line in render_status():
        print(line)

    num_workers = min(len(strategies_to_run), os.cpu_count() or 4)

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(
                run_strategy_games,
                name,
                games,
                rounds,
                starting_bankroll,
                decks,
                table_min,
                table_max,
                h17,
                das,
                late_surrender,
                max_splits,
                seed,
            ): name
            for name in strategies_to_run
        }

        # Mark submitted strategies as running
        for name in strategies_to_run:
            status[name] = "running"

        # Start spinner animation
        spinner = threading.Thread(target=spinner_thread, daemon=True)
        spinner.start()

        for future in as_completed(futures):
            name = futures[future]
            all_results[name] = future.result()
            status[name] = "done"

        # Stop spinner and render final state
        stop_spinner.set()
        spinner.join(timeout=0.2)

    # Final render
    lines = render_status()
    sys.stdout.write(f"\033[{len(lines)}A")
    sys.stdout.write("\033[J")
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()

    # Print aggregate results
    agg_results = [aggregate_results(results) for results in all_results.values()]
    print_aggregate_results(agg_results, hands_per_hour, late_surrender)


if __name__ == "__main__":
    main()
