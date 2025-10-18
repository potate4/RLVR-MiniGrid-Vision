"""
RLVR Demo Script

Visualize trained RLVR agent and show verification in action.
"""

import argparse
import time
import numpy as np
from stable_baselines3 import PPO
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import imageio

from rlvr_env_wrapper import make_rlvr_env


def demonstrate_agent(
    model_path: str,
    env_name: str = "MiniGrid-Empty-8x8-v0",
    use_rlvr: bool = True,
    n_episodes: int = 5,
    render: bool = True,
    save_video: bool = False,
    video_path: str = "rlvr_demo.gif",
):
    """
    Demonstrate trained agent with visualization.

    Args:
        model_path: Path to trained model
        env_name: Environment name
        use_rlvr: Whether to use RLVR
        n_episodes: Number of episodes to run
        render: Whether to render environment
        save_video: Whether to save video
        video_path: Path to save video
    """
    # Load model
    print(f"Loading model from {model_path}...")
    model = PPO.load(model_path)

    # Create environment
    render_mode = "rgb_array" if (render or save_video) else None
    env = make_rlvr_env(
        env_name=env_name,
        task_type="reach_goal",
        use_rlvr=use_rlvr,
        render_mode=render_mode,
    )

    print(f"\nDemonstrating {'RLVR' if use_rlvr else 'Baseline'} Agent")
    print(f"Environment: {env_name}")
    print(f"Episodes: {n_episodes}\n")

    episode_rewards = []
    episode_lengths = []
    verification_counts = []
    frames = [] if save_video else None

    for episode in range(n_episodes):
        obs, info = env.reset()
        episode_reward = 0
        episode_length = 0
        verifications = 0
        done = False

        print(f"Episode {episode + 1}/{n_episodes}")

        while not done:
            # Get action from model
            action, _states = model.predict(obs, deterministic=True)

            # Take step
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            episode_reward += reward
            episode_length += 1

            # Check verification
            if use_rlvr and 'rlvr_verification' in info:
                verification_info = info['rlvr_verification']
                if verification_info['verified']:
                    verifications += 1
                    print(f"  ✓ Verified: {verification_info['explanation']}")

            # Capture frame for video
            if save_video:
                frame = env.render()
                frames.append(frame)

            # Display state info
            if 'symbolic_state' in info:
                symbolic_state = info['symbolic_state']
                if episode_length % 10 == 0:  # Print every 10 steps
                    print(f"  Step {episode_length}: Agent at {symbolic_state['agent_pos']}")

            if render and not save_video:
                env.render()
                time.sleep(0.1)

        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        verification_counts.append(verifications)

        print(f"  Reward: {episode_reward:.2f}, Length: {episode_length}, Verifications: {verifications}\n")

    # Print summary statistics
    print("\n" + "="*60)
    print("Summary Statistics")
    print("="*60)
    print(f"Mean Episode Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"Mean Episode Length: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    if use_rlvr:
        print(f"Mean Verifications per Episode: {np.mean(verification_counts):.2f}")
    print("="*60 + "\n")

    # Save video if requested
    if save_video and frames:
        print(f"Saving video to {video_path}...")
        imageio.mimsave(video_path, frames, fps=10)
        print(f"Video saved!\n")

    env.close()

    return {
        'episode_rewards': episode_rewards,
        'episode_lengths': episode_lengths,
        'verification_counts': verification_counts,
    }


def compare_rlvr_baseline_demo(
    rlvr_model_path: str,
    baseline_model_path: str,
    env_name: str = "MiniGrid-Empty-8x8-v0",
    n_episodes: int = 10,
):
    """
    Compare RLVR and baseline agents side-by-side.
    """
    print("\n" + "="*60)
    print("RLVR vs Baseline Demonstration")
    print("="*60 + "\n")

    # Demonstrate RLVR agent
    print(">>> RLVR Agent:\n")
    rlvr_stats = demonstrate_agent(
        model_path=rlvr_model_path,
        env_name=env_name,
        use_rlvr=True,
        n_episodes=n_episodes,
        render=False,
    )

    print("\n" + "="*60 + "\n")

    # Demonstrate baseline agent
    print(">>> Baseline Agent:\n")
    baseline_stats = demonstrate_agent(
        model_path=baseline_model_path,
        env_name=env_name,
        use_rlvr=False,
        n_episodes=n_episodes,
        render=False,
    )

    # Plot comparison
    plot_comparison(rlvr_stats, baseline_stats)


def plot_comparison(rlvr_stats, baseline_stats):
    """
    Plot comparison between RLVR and baseline agents.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Plot rewards
    axes[0].bar(['RLVR', 'Baseline'],
                [np.mean(rlvr_stats['episode_rewards']),
                 np.mean(baseline_stats['episode_rewards'])],
                yerr=[np.std(rlvr_stats['episode_rewards']),
                      np.std(baseline_stats['episode_rewards'])],
                capsize=5)
    axes[0].set_ylabel('Mean Episode Reward')
    axes[0].set_title('Reward Comparison')
    axes[0].grid(True, alpha=0.3)

    # Plot lengths
    axes[1].bar(['RLVR', 'Baseline'],
                [np.mean(rlvr_stats['episode_lengths']),
                 np.mean(baseline_stats['episode_lengths'])],
                yerr=[np.std(rlvr_stats['episode_lengths']),
                      np.std(baseline_stats['episode_lengths'])],
                capsize=5)
    axes[1].set_ylabel('Mean Episode Length')
    axes[1].set_title('Episode Length Comparison')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('rlvr_vs_baseline_comparison.png', dpi=150, bbox_inches='tight')
    print("\nComparison plot saved to: rlvr_vs_baseline_comparison.png")
    plt.show()


def visualize_verification_process(
    model_path: str,
    env_name: str = "MiniGrid-Empty-8x8-v0",
):
    """
    Detailed visualization of RLVR verification process.
    """
    print("\n" + "="*60)
    print("RLVR Verification Process Visualization")
    print("="*60 + "\n")

    # Load model
    model = PPO.load(model_path)

    # Create environment
    env = make_rlvr_env(
        env_name=env_name,
        task_type="reach_goal",
        use_rlvr=True,
        render_mode="rgb_array",
    )

    obs, info = env.reset()
    done = False
    step = 0

    print("Running episode with detailed verification logging...\n")

    while not done and step < 100:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        step += 1

        # Print detailed info
        if 'symbolic_state' in info:
            symbolic_state = info['symbolic_state']
            print(f"Step {step}:")
            print(f"  Agent Position: {symbolic_state['agent_pos']}")
            print(f"  Agent Direction: {symbolic_state['agent_dir']}")

            if 'goal_pos' in symbolic_state:
                print(f"  Goal Position: {symbolic_state['goal_pos']}")

            if 'rlvr_verification' in info:
                verification = info['rlvr_verification']
                print(f"  Reward: {reward:.3f}")
                print(f"  Verified: {verification['verified']}")
                print(f"  Rule Applied: {verification.get('rule_applied', 'None')}")
                print(f"  Explanation: {verification['explanation']}")

            print()

        if done:
            print(f"\nEpisode completed in {step} steps!")
            if 'rlvr_verification' in info and info['rlvr_verification']['verified']:
                print("✓ Task successfully verified!")

    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demonstrate RLVR agent")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to trained model",
    )
    parser.add_argument(
        "--env",
        type=str,
        default="MiniGrid-Empty-8x8-v0",
        help="MiniGrid environment name",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["demo", "verify", "compare"],
        default="demo",
        help="Demonstration mode",
    )
    parser.add_argument(
        "--baseline-model",
        type=str,
        help="Path to baseline model (for compare mode)",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=5,
        help="Number of episodes",
    )
    parser.add_argument(
        "--save-video",
        action="store_true",
        help="Save video of episodes",
    )
    parser.add_argument(
        "--video-path",
        type=str,
        default="rlvr_demo.gif",
        help="Path to save video",
    )

    args = parser.parse_args()

    if args.mode == "demo":
        demonstrate_agent(
            model_path=args.model,
            env_name=args.env,
            use_rlvr=True,
            n_episodes=args.episodes,
            render=True,
            save_video=args.save_video,
            video_path=args.video_path,
        )
    elif args.mode == "verify":
        visualize_verification_process(
            model_path=args.model,
            env_name=args.env,
        )
    elif args.mode == "compare":
        if not args.baseline_model:
            print("Error: --baseline-model required for compare mode")
        else:
            compare_rlvr_baseline_demo(
                rlvr_model_path=args.model,
                baseline_model_path=args.baseline_model,
                env_name=args.env,
                n_episodes=args.episodes,
            )
