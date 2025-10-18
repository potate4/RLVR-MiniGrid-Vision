"""
Results Analysis Script

Analyze and visualize training results from RLVR experiments.
"""

import os
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from tensorboard.backend.event_processing import event_accumulator


def load_tensorboard_data(logdir):
    """Load data from TensorBoard logs."""
    ea = event_accumulator.EventAccumulator(logdir)
    ea.Reload()

    data = {}

    # Get available tags
    tags = ea.Tags()

    # Load scalar data
    for tag in tags['scalars']:
        try:
            events = ea.Scalars(tag)
            steps = [e.step for e in events]
            values = [e.value for e in events]
            data[tag] = {'steps': steps, 'values': values}
        except:
            pass

    return data


def plot_training_curves(rlvr_dir, baseline_dir=None, save_path='training_curves.png'):
    """
    Plot training curves comparing RLVR vs baseline.

    Args:
        rlvr_dir: Directory containing RLVR results
        baseline_dir: Directory containing baseline results (optional)
        save_path: Path to save plot
    """
    print("\n" + "="*70)
    print("PLOTTING TRAINING CURVES")
    print("="*70 + "\n")

    # Check if directories exist
    if not os.path.exists(rlvr_dir):
        print(f"❌ RLVR directory not found: {rlvr_dir}")
        print("\nMake sure you've run training first:")
        print("  python train_rlvr.py --mode rlvr --timesteps 100000")
        return

    if baseline_dir and not os.path.exists(baseline_dir):
        print(f"⚠️  Baseline directory not found: {baseline_dir}")
        print("   Plotting RLVR only...\n")
        baseline_dir = None

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('RLVR vs Baseline Training Comparison', fontsize=16, fontweight='bold')

    # Find tensorboard directories
    rlvr_tb_dir = None
    baseline_tb_dir = None

    print(f"Searching for TensorBoard logs in: {rlvr_dir}")
    for root, dirs, files in os.walk(rlvr_dir):
        for file in files:
            if 'events.out.tfevents' in file:
                rlvr_tb_dir = root
                print(f"✓ Found RLVR TensorBoard logs: {rlvr_tb_dir}")
                break
        if rlvr_tb_dir:
            break

    if baseline_dir:
        print(f"Searching for TensorBoard logs in: {baseline_dir}")
        for root, dirs, files in os.walk(baseline_dir):
            for file in files:
                if 'events.out.tfevents' in file:
                    baseline_tb_dir = root
                    print(f"✓ Found baseline TensorBoard logs: {baseline_tb_dir}")
                    break
            if baseline_tb_dir:
                break

    if not rlvr_tb_dir:
        print(f"\n❌ No TensorBoard logs found in {rlvr_dir}")
        print("\nPossible reasons:")
        print("1. Training hasn't been run yet")
        print("2. Training is still in progress")
        print("3. Directory path is incorrect")
        print("\nTo generate logs, run:")
        print("  python train_rlvr.py --mode rlvr --timesteps 100000")
        return

    data_plotted = False

    if rlvr_tb_dir:
        print(f"\nLoading RLVR data from {rlvr_tb_dir}...")
        try:
            rlvr_data = load_tensorboard_data(rlvr_tb_dir)
            print(f"  Available metrics: {list(rlvr_data.keys())}")
        except Exception as e:
            print(f"  ❌ Error loading data: {e}")
            rlvr_data = {}

        # Plot episode reward
        if 'rollout/ep_rew_mean' in rlvr_data:
            steps = rlvr_data['rollout/ep_rew_mean']['steps']
            values = rlvr_data['rollout/ep_rew_mean']['values']
            axes[0, 0].plot(steps, values, label='RLVR', linewidth=2, color='blue')
            data_plotted = True
            print(f"  ✓ Plotted episode reward ({len(steps)} points)")

        # Plot episode length
        if 'rollout/ep_len_mean' in rlvr_data:
            steps = rlvr_data['rollout/ep_len_mean']['steps']
            values = rlvr_data['rollout/ep_len_mean']['values']
            axes[0, 1].plot(steps, values, label='RLVR', linewidth=2, color='blue')
            data_plotted = True
            print(f"  ✓ Plotted episode length ({len(steps)} points)")

        # Plot loss
        if 'train/loss' in rlvr_data:
            steps = rlvr_data['train/loss']['steps']
            values = rlvr_data['train/loss']['values']
            axes[1, 0].plot(steps, values, label='RLVR', linewidth=2, color='blue')
            data_plotted = True
            print(f"  ✓ Plotted training loss ({len(steps)} points)")

        # Plot learning rate
        if 'train/learning_rate' in rlvr_data:
            steps = rlvr_data['train/learning_rate']['steps']
            values = rlvr_data['train/learning_rate']['values']
            axes[1, 1].plot(steps, values, label='RLVR', linewidth=2, color='blue')
            print(f"  ✓ Plotted learning rate ({len(steps)} points)")

    if baseline_tb_dir:
        print(f"\nLoading baseline data from {baseline_tb_dir}...")
        try:
            baseline_data = load_tensorboard_data(baseline_tb_dir)
            print(f"  Available metrics: {list(baseline_data.keys())}")
        except Exception as e:
            print(f"  ❌ Error loading data: {e}")
            baseline_data = {}

        # Plot episode reward
        if 'rollout/ep_rew_mean' in baseline_data:
            steps = baseline_data['rollout/ep_rew_mean']['steps']
            values = baseline_data['rollout/ep_rew_mean']['values']
            axes[0, 0].plot(steps, values, label='Baseline', linewidth=2, color='orange', linestyle='--')
            data_plotted = True
            print(f"  ✓ Plotted episode reward ({len(steps)} points)")

        # Plot episode length
        if 'rollout/ep_len_mean' in baseline_data:
            steps = baseline_data['rollout/ep_len_mean']['steps']
            values = baseline_data['rollout/ep_len_mean']['values']
            axes[0, 1].plot(steps, values, label='Baseline', linewidth=2, color='orange', linestyle='--')
            data_plotted = True
            print(f"  ✓ Plotted episode length ({len(steps)} points)")

        # Plot loss
        if 'train/loss' in baseline_data:
            steps = baseline_data['train/loss']['steps']
            values = baseline_data['train/loss']['values']
            axes[1, 0].plot(steps, values, label='Baseline', linewidth=2, color='orange', linestyle='--')
            data_plotted = True
            print(f"  ✓ Plotted training loss ({len(steps)} points)")

        # Plot learning rate
        if 'train/learning_rate' in baseline_data:
            steps = baseline_data['train/learning_rate']['steps']
            values = baseline_data['train/learning_rate']['values']
            axes[1, 1].plot(steps, values, label='Baseline', linewidth=2, color='orange', linestyle='--')
            print(f"  ✓ Plotted learning rate ({len(steps)} points)")

    # Formatting
    axes[0, 0].set_xlabel('Training Steps')
    axes[0, 0].set_ylabel('Mean Episode Reward')
    axes[0, 0].set_title('Episode Reward')
    if axes[0, 0].get_lines():
        axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].set_xlabel('Training Steps')
    axes[0, 1].set_ylabel('Mean Episode Length')
    axes[0, 1].set_title('Episode Length')
    if axes[0, 1].get_lines():
        axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].set_xlabel('Training Steps')
    axes[1, 0].set_ylabel('Loss')
    axes[1, 0].set_title('Training Loss')
    if axes[1, 0].get_lines():
        axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].set_xlabel('Training Steps')
    axes[1, 1].set_ylabel('Learning Rate')
    axes[1, 1].set_title('Learning Rate Schedule')
    if axes[1, 1].get_lines():
        axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')

    print("\n" + "="*70)
    if data_plotted:
        print(f"✓ Plot saved to {save_path}")
        print("\nYou can now:")
        print("  1. View the plot image")
        print("  2. Use it in your survey paper")
        print("  3. Compare RLVR vs baseline visually")
    else:
        print(f"⚠️  Plot saved to {save_path} but contains no data")
        print("\nNo training data was found to plot.")
        print("Make sure you've completed training first:")
        print("  python train_rlvr.py --mode compare --timesteps 100000")
    print("="*70 + "\n")

    plt.close()


def generate_summary_report(results_dir, output_file='summary_report.txt'):
    """
    Generate a text summary report of all experiments.

    Args:
        results_dir: Directory containing experiment results
        output_file: Path to save summary report
    """
    report = []
    report.append("="*70)
    report.append("RLVR EXPERIMENTS SUMMARY REPORT")
    report.append("="*70)
    report.append("")

    # Find all experiment directories
    experiments = []
    for item in os.listdir(results_dir):
        item_path = os.path.join(results_dir, item)
        if os.path.isdir(item_path):
            experiments.append((item, item_path))

    if not experiments:
        report.append("No experiments found in directory.")
    else:
        report.append(f"Found {len(experiments)} experiments:\n")

        for exp_name, exp_path in sorted(experiments):
            report.append("-"*70)
            report.append(f"Experiment: {exp_name}")
            report.append("-"*70)

            # Check for best model
            best_model_path = os.path.join(exp_path, "best_model")
            if os.path.exists(best_model_path):
                report.append("✓ Best model saved")

            # Check for checkpoints
            checkpoints_path = os.path.join(exp_path, "checkpoints")
            if os.path.exists(checkpoints_path):
                checkpoints = [f for f in os.listdir(checkpoints_path) if f.endswith('.zip')]
                report.append(f"✓ {len(checkpoints)} checkpoints saved")

            # Check for tensorboard logs
            tb_path = os.path.join(exp_path, "tensorboard")
            if os.path.exists(tb_path):
                report.append("✓ TensorBoard logs available")

                # Try to load final metrics
                try:
                    for root, dirs, files in os.walk(tb_path):
                        if any('events.out.tfevents' in f for f in files):
                            data = load_tensorboard_data(root)
                            if 'rollout/ep_rew_mean' in data:
                                final_reward = data['rollout/ep_rew_mean']['values'][-1]
                                report.append(f"  Final Episode Reward: {final_reward:.3f}")
                            if 'rollout/ep_len_mean' in data:
                                final_length = data['rollout/ep_len_mean']['values'][-1]
                                report.append(f"  Final Episode Length: {final_length:.1f}")
                            break
                except Exception as e:
                    report.append(f"  (Could not load metrics: {e})")

            report.append("")

    report.append("="*70)
    report.append("END OF REPORT")
    report.append("="*70)

    # Write report
    report_text = "\n".join(report)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print(f"\nReport saved to {output_file}")


def compare_final_performance(rlvr_dir, baseline_dir):
    """
    Compare final performance metrics between RLVR and baseline.

    Args:
        rlvr_dir: RLVR experiment directory
        baseline_dir: Baseline experiment directory
    """
    print("\n" + "="*70)
    print("FINAL PERFORMANCE COMPARISON")
    print("="*70 + "\n")

    metrics = {}

    for name, exp_dir in [('RLVR', rlvr_dir), ('Baseline', baseline_dir)]:
        print(f"Loading {name} results...")
        tb_dir = None
        for root, dirs, files in os.walk(exp_dir):
            if any('events.out.tfevents' in f for f in files):
                tb_dir = root
                break

        if tb_dir:
            data = load_tensorboard_data(tb_dir)

            metrics[name] = {}
            if 'rollout/ep_rew_mean' in data:
                rewards = data['rollout/ep_rew_mean']['values']
                metrics[name]['final_reward'] = rewards[-1]
                metrics[name]['max_reward'] = max(rewards)
                metrics[name]['mean_reward'] = np.mean(rewards[-10:])  # Last 10 points

            if 'rollout/ep_len_mean' in data:
                lengths = data['rollout/ep_len_mean']['values']
                metrics[name]['final_length'] = lengths[-1]
                metrics[name]['min_length'] = min(lengths)
                metrics[name]['mean_length'] = np.mean(lengths[-10:])

    # Print comparison
    print("\nMetric Comparison:")
    print("-"*70)
    print(f"{'Metric':<30} {'RLVR':<15} {'Baseline':<15} {'Difference':<15}")
    print("-"*70)

    if 'RLVR' in metrics and 'Baseline' in metrics:
        for metric in ['final_reward', 'max_reward', 'mean_reward', 'final_length', 'min_length', 'mean_length']:
            if metric in metrics['RLVR'] and metric in metrics['Baseline']:
                rlvr_val = metrics['RLVR'][metric]
                baseline_val = metrics['Baseline'][metric]
                diff = rlvr_val - baseline_val
                diff_pct = (diff / baseline_val * 100) if baseline_val != 0 else 0

                print(f"{metric:<30} {rlvr_val:>10.3f}     {baseline_val:>10.3f}     {diff:>+10.3f} ({diff_pct:>+6.1f}%)")

    print("-"*70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze RLVR experiment results")
    parser.add_argument(
        "--results-dir",
        type=str,
        default="./rlvr_results",
        help="Directory containing experiment results",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["summary", "plot", "compare"],
        default="summary",
        help="Analysis mode",
    )
    parser.add_argument(
        "--rlvr-dir",
        type=str,
        help="RLVR experiment directory (for plot/compare modes)",
    )
    parser.add_argument(
        "--baseline-dir",
        type=str,
        help="Baseline experiment directory (for plot/compare modes)",
    )

    args = parser.parse_args()

    if args.mode == "summary":
        generate_summary_report(args.results_dir)

    elif args.mode == "plot":
        if not args.rlvr_dir:
            print("Error: --rlvr-dir required for plot mode")
        else:
            plot_training_curves(args.rlvr_dir, args.baseline_dir)

    elif args.mode == "compare":
        if not args.rlvr_dir or not args.baseline_dir:
            print("Error: Both --rlvr-dir and --baseline-dir required for compare mode")
        else:
            compare_final_performance(args.rlvr_dir, args.baseline_dir)
            plot_training_curves(args.rlvr_dir, args.baseline_dir)
