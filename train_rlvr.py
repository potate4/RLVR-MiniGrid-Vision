"""
RLVR Training Script

Train a PPO agent on MiniGrid with RLVR verification.
Compares RLVR-based training vs baseline (environment rewards).
"""

import os
import argparse
from datetime import datetime
import torch
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecMonitor, VecVideoRecorder
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback, BaseCallback
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch.nn as nn
import gymnasium as gym

from rlvr_env_wrapper import make_rlvr_env


class MinigridCNN(BaseFeaturesExtractor):
    """
    Custom CNN for MiniGrid visual observations.

    Lightweight architecture suitable for RTX 4060.
    """

    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 128):
        super().__init__(observation_space, features_dim)

        n_input_channels = observation_space.shape[0]

        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute shape by doing one forward pass
        with torch.no_grad():
            n_flatten = self.cnn(
                torch.as_tensor(observation_space.sample()[None]).float()
            ).shape[1]

        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        # MiniGrid observations are (H, W, C), need to transpose to (C, H, W)
        observations = observations.permute(0, 3, 1, 2)
        return self.linear(self.cnn(observations))


class RLVRLoggingCallback(BaseCallback):
    """
    Custom callback to log RLVR-specific metrics.
    """

    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_rlvr_rewards = []
        self.episode_env_rewards = []

    def _on_step(self) -> bool:
        # Log RLVR verification info if available
        for idx, done in enumerate(self.locals['dones']):
            if done:
                info = self.locals['infos'][idx]
                if 'episode' in info:
                    self.logger.record('rollout/ep_rew_mean', info['episode']['r'])
                    self.logger.record('rollout/ep_len_mean', info['episode']['l'])

        return True


def train_rlvr_agent(
    env_name: str = "MiniGrid-Empty-8x8-v0",
    use_rlvr: bool = True,
    total_timesteps: int = 100000,
    n_envs: int = 4,
    save_dir: str = "./rlvr_results",
    seed: int = 42,
):
    """
    Train PPO agent with or without RLVR.

    Args:
        env_name: MiniGrid environment name
        use_rlvr: Whether to use RLVR verifier
        total_timesteps: Total training timesteps
        n_envs: Number of parallel environments
        save_dir: Directory to save results
        seed: Random seed
    """
    # Create save directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_name = f"{'rlvr' if use_rlvr else 'baseline'}_{env_name}_{timestamp}"
    exp_dir = os.path.join(save_dir, exp_name)
    os.makedirs(exp_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Training {'RLVR' if use_rlvr else 'Baseline'} Agent")
    print(f"Environment: {env_name}")
    print(f"Total timesteps: {total_timesteps}")
    print(f"Parallel envs: {n_envs}")
    print(f"Save directory: {exp_dir}")
    print(f"{'='*60}\n")

    # Create vectorized environment
    env = make_vec_env(
        lambda: make_rlvr_env(
            env_name=env_name,
            task_type="reach_goal",
            use_rlvr=use_rlvr,
        ),
        n_envs=n_envs,
        seed=seed,
    )

    # Wrap with monitor
    env = VecMonitor(env)

    # Create evaluation environment
    eval_env = make_vec_env(
        lambda: make_rlvr_env(
            env_name=env_name,
            task_type="reach_goal",
            use_rlvr=use_rlvr,
        ),
        n_envs=1,
        seed=seed + 1000,
    )
    eval_env = VecMonitor(eval_env)

    # Configure PPO for efficiency on RTX 4060
    policy_kwargs = dict(
        features_extractor_class=MinigridCNN,
        features_extractor_kwargs=dict(features_dim=128),
        net_arch=[dict(pi=[64], vf=[64])],  # Smaller network for faster training
    )

    # Initialize PPO
    model = PPO(
        policy="CnnPolicy",
        env=env,
        policy_kwargs=policy_kwargs,
        learning_rate=3e-4,
        n_steps=128,  # Reduced for faster updates
        batch_size=64,
        n_epochs=4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        tensorboard_log=os.path.join(exp_dir, "tensorboard"),
        verbose=1,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )

    print(f"Using device: {model.device}\n")

    # Setup callbacks
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=os.path.join(exp_dir, "best_model"),
        log_path=os.path.join(exp_dir, "eval"),
        eval_freq=max(5000 // n_envs, 1),
        n_eval_episodes=5,
        deterministic=True,
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=max(10000 // n_envs, 1),
        save_path=os.path.join(exp_dir, "checkpoints"),
        name_prefix="rlvr_model",
    )

    rlvr_callback = RLVRLoggingCallback()

    # Train the model
    print("Starting training...\n")
    model.learn(
        total_timesteps=total_timesteps,
        callback=[eval_callback, checkpoint_callback, rlvr_callback],
        progress_bar=True,
    )

    # Save final model
    final_model_path = os.path.join(exp_dir, "final_model")
    model.save(final_model_path)
    print(f"\nFinal model saved to: {final_model_path}")

    # Cleanup
    env.close()
    eval_env.close()

    return model, exp_dir


def compare_rlvr_vs_baseline(
    env_name: str = "MiniGrid-Empty-8x8-v0",
    total_timesteps: int = 100000,
    n_envs: int = 4,
    seed: int = 42,
):
    """
    Train both RLVR and baseline agents for comparison.
    """
    print("\n" + "="*60)
    print("RLVR vs Baseline Comparison")
    print("="*60 + "\n")

    # Train RLVR agent
    print(">>> Training RLVR Agent...\n")
    rlvr_model, rlvr_dir = train_rlvr_agent(
        env_name=env_name,
        use_rlvr=True,
        total_timesteps=total_timesteps,
        n_envs=n_envs,
        seed=seed,
    )

    print("\n" + "="*60 + "\n")

    # Train baseline agent
    print(">>> Training Baseline Agent...\n")
    baseline_model, baseline_dir = train_rlvr_agent(
        env_name=env_name,
        use_rlvr=False,
        total_timesteps=total_timesteps,
        n_envs=n_envs,
        seed=seed + 100,
    )

    print("\n" + "="*60)
    print("Training Complete!")
    print(f"RLVR results: {rlvr_dir}")
    print(f"Baseline results: {baseline_dir}")
    print("="*60 + "\n")

    return rlvr_model, baseline_model, rlvr_dir, baseline_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RLVR agent on MiniGrid")
    parser.add_argument(
        "--env",
        type=str,
        default="MiniGrid-Empty-8x8-v0",
        help="MiniGrid environment name",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["rlvr", "baseline", "compare"],
        default="rlvr",
        help="Training mode",
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=100000,
        help="Total training timesteps",
    )
    parser.add_argument(
        "--n-envs",
        type=int,
        default=4,
        help="Number of parallel environments",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )

    args = parser.parse_args()

    # Set random seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    if args.mode == "compare":
        compare_rlvr_vs_baseline(
            env_name=args.env,
            total_timesteps=args.timesteps,
            n_envs=args.n_envs,
            seed=args.seed,
        )
    else:
        train_rlvr_agent(
            env_name=args.env,
            use_rlvr=(args.mode == "rlvr"),
            total_timesteps=args.timesteps,
            n_envs=args.n_envs,
            seed=args.seed,
        )
