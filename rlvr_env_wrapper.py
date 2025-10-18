"""
RLVR Environment Wrapper for MiniGrid

This wrapper integrates the RLVR verifier with MiniGrid environments,
replacing the environment's native reward signal with verified rewards.
"""

import gymnasium as gym
import minigrid  # Import to register MiniGrid environments
import numpy as np
from typing import Tuple, Dict, Any
from rlvr_verifier import RLVRVerifier


class RLVRMiniGridWrapper(gym.Wrapper):
    """
    Wrapper that applies RLVR verification to MiniGrid environments.

    Key Feature: Instead of using env.reward directly, this wrapper uses
    an independent verifier to compute rewards based on symbolic state.
    """

    def __init__(self, env: gym.Env, task_type: str = "reach_goal", use_rlvr: bool = True):
        """
        Initialize RLVR wrapper.

        Args:
            env: Base MiniGrid environment
            task_type: Type of task for verifier
            use_rlvr: If True, use RLVR verifier; if False, use env rewards (baseline)
        """
        super().__init__(env)
        self.verifier = RLVRVerifier(task_type=task_type)
        self.use_rlvr = use_rlvr
        self.prev_symbolic_state = None
        self.episode_count = 0
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_episode_reward = 0
        self.current_episode_length = 0

    def reset(self, **kwargs):
        """Reset environment and verifier."""
        obs, info = self.env.reset(**kwargs)

        # Reset verifier
        self.verifier.reset()

        # Extract initial symbolic state
        self.prev_symbolic_state = self.verifier.extract_symbolic_state(
            obs, self.env
        )

        # Reset episode tracking
        if self.current_episode_length > 0:
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)
            self.episode_count += 1

        self.current_episode_reward = 0
        self.current_episode_length = 0

        return obs, info

    def step(self, action):
        """
        Execute action and compute RLVR-verified reward.

        This is where RLVR magic happens: we replace the environment's reward
        with our independently verified reward.
        """
        obs, env_reward, terminated, truncated, info = self.env.step(action)

        # Extract symbolic state
        symbolic_state = self.verifier.extract_symbolic_state(obs, self.env)

        if self.use_rlvr:
            # Use RLVR verifier to compute reward (KEY RLVR COMPONENT)
            verified_reward, verification_info = self.verifier.verify_task_completion(
                symbolic_state, self.prev_symbolic_state
            )
            reward = verified_reward

            # Add verification info to info dict
            info['rlvr_verification'] = verification_info
            info['env_reward'] = env_reward  # Keep original for comparison
            info['reward_source'] = 'rlvr_verifier'
        else:
            # Baseline: use environment's native reward
            reward = env_reward
            info['reward_source'] = 'environment'

        # Update previous state
        self.prev_symbolic_state = symbolic_state

        # Track episode statistics
        self.current_episode_reward += reward
        self.current_episode_length += 1

        # Add symbolic state to info for debugging
        info['symbolic_state'] = symbolic_state

        return obs, reward, terminated, truncated, info

    def get_episode_stats(self) -> Dict[str, Any]:
        """Get statistics about episodes."""
        stats = {
            'episode_count': self.episode_count,
            'mean_episode_reward': np.mean(self.episode_rewards) if self.episode_rewards else 0,
            'mean_episode_length': np.mean(self.episode_lengths) if self.episode_lengths else 0,
            'verifier_stats': self.verifier.get_verification_stats(),
        }
        return stats


class VisualObservationWrapper(gym.ObservationWrapper):
    """
    Wrapper to ensure we're using visual observations (image-based).

    MiniGrid can return symbolic or visual observations. For vision-based RLVR,
    we want to use the visual observations and extract symbolic state from them.
    """

    def __init__(self, env):
        super().__init__(env)
        # Update observation space to just the image
        self.observation_space = env.observation_space['image']

    def observation(self, obs):
        """Return only the visual component."""
        # MiniGrid returns dict with 'image', 'direction', 'mission'
        # We want just the image for visual RL
        if isinstance(obs, dict):
            return obs['image']
        return obs


def make_rlvr_env(env_name: str = "MiniGrid-Empty-8x8-v0",
                  task_type: str = "reach_goal",
                  use_rlvr: bool = True,
                  render_mode: str = None):
    """
    Factory function to create RLVR-wrapped MiniGrid environment.

    Args:
        env_name: Name of MiniGrid environment
        task_type: Task type for verifier
        use_rlvr: Whether to use RLVR or baseline
        render_mode: Render mode for environment

    Returns:
        Wrapped environment ready for training
    """
    # Check if environment exists and provide helpful error message
    available_envs = [e for e in gym.envs.registry.keys() if 'MiniGrid' in e]
    if env_name not in available_envs:
        print(f"\nError: Environment '{env_name}' not found.")
        print(f"\nAvailable MiniGrid environments (showing first 10):")
        for env in sorted(available_envs)[:10]:
            print(f"  - {env}")
        print(f"\nTrying to find similar environment...")

        # Try to find a similar environment
        base_name = env_name.replace('-v0', '')
        similar = [e for e in available_envs if base_name.split('-')[-1] in e]
        if similar:
            suggested = similar[0]
            print(f"Suggestion: Try '{suggested}' instead")
            raise ValueError(f"Environment '{env_name}' not found. Try: {suggested}")
        else:
            raise ValueError(f"Environment '{env_name}' not found. Available: {sorted(available_envs)[:5]}")

    # Create base environment
    env = gym.make(env_name, render_mode=render_mode)

    # Apply visual observation wrapper
    env = VisualObservationWrapper(env)

    # Apply RLVR wrapper
    env = RLVRMiniGridWrapper(env, task_type=task_type, use_rlvr=use_rlvr)

    return env
