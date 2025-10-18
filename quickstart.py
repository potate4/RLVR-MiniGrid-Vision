"""
Quick Start Script for RLVR Pipeline

This script provides an easy entry point to test the RLVR implementation.
It runs a short training session and demonstrates the verifier in action.
"""

import sys
import torch
import numpy as np
from stable_baselines3 import PPO
from rlvr_env_wrapper import make_rlvr_env
from rlvr_verifier import RLVRVerifier


def check_system():
    """Check system requirements."""
    print("\n" + "="*60)
    print("System Check")
    print("="*60)

    # Check Python version
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 8):
        print("⚠️  Warning: Python 3.8+ recommended")
    else:
        print("✓ Python version OK")

    # Check CUDA
    cuda_available = torch.cuda.is_available()
    print(f"\nCUDA Available: {cuda_available}")
    if cuda_available:
        print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
        print(f"✓ CUDA Version: {torch.version.cuda}")
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✓ GPU Memory: {gpu_memory:.1f} GB")
    else:
        print("⚠️  No CUDA GPU detected - training will use CPU (slower)")

    # Check RAM
    import psutil
    ram_gb = psutil.virtual_memory().total / 1e9
    print(f"\nSystem RAM: {ram_gb:.1f} GB")
    if ram_gb < 16:
        print("⚠️  Warning: 16GB+ RAM recommended")
    else:
        print("✓ RAM OK")

    print("="*60 + "\n")


def test_environment():
    """Test that the environment works correctly."""
    print("Testing RLVR Environment...")

    try:
        # Create environment
        env = make_rlvr_env(
            env_name="MiniGrid-Empty-8x8-v0",
            task_type="reach_goal",
            use_rlvr=True,
        )

        # Test reset
        obs, info = env.reset()
        print(f"✓ Environment reset successful")
        print(f"  Observation shape: {obs.shape}")

        # Test a few steps
        for i in range(5):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)

            if 'symbolic_state' in info:
                symbolic_state = info['symbolic_state']
                print(f"  Step {i+1}: Agent at {symbolic_state['agent_pos']}, Reward: {reward:.3f}")

        env.close()
        print("✓ Environment test successful\n")
        return True

    except Exception as e:
        print(f"✗ Environment test failed: {e}\n")
        return False


def quick_training_demo():
    """Run a quick training demo (5000 steps)."""
    print("="*60)
    print("Quick Training Demo (5000 steps)")
    print("="*60 + "\n")

    # Create environment
    print("Creating training environment...")
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.vec_env import VecMonitor

    env = make_vec_env(
        lambda: make_rlvr_env(
            env_name="MiniGrid-Empty-8x8-v0",
            task_type="reach_goal",
            use_rlvr=True,
        ),
        n_envs=2,
        seed=42,
    )
    env = VecMonitor(env)

    # Create PPO model
    print("Initializing PPO agent...")
    from train_rlvr import MinigridCNN

    policy_kwargs = dict(
        features_extractor_class=MinigridCNN,
        features_extractor_kwargs=dict(features_dim=128),
        net_arch=dict(pi=[64], vf=[64]),
    )

    model = PPO(
        policy="CnnPolicy",
        env=env,
        policy_kwargs=policy_kwargs,
        learning_rate=3e-4,
        n_steps=128,
        batch_size=64,
        verbose=1,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )

    print(f"Using device: {model.device}\n")

    # Train briefly
    print("Training for 5000 steps...")
    print("(This is just a quick test - full training takes 100k+ steps)\n")

    model.learn(total_timesteps=5000, progress_bar=True)

    print("\n✓ Quick training demo completed successfully!")

    # Test the trained model
    print("\nTesting trained model on 3 episodes...")

    test_env = make_rlvr_env(
        env_name="MiniGrid-Empty-8x8-v0",
        task_type="reach_goal",
        use_rlvr=True,
    )

    episode_rewards = []
    for episode in range(3):
        obs, info = test_env.reset()
        episode_reward = 0
        done = False
        steps = 0

        while not done and steps < 50:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = test_env.step(action)
            done = terminated or truncated
            episode_reward += reward
            steps += 1

        episode_rewards.append(episode_reward)
        print(f"  Episode {episode+1}: Reward = {episode_reward:.2f}, Steps = {steps}")

    print(f"\nMean Reward: {np.mean(episode_rewards):.2f}")
    print("\n✓ Model test completed!\n")

    env.close()
    test_env.close()


def demonstrate_verifier():
    """Demonstrate the RLVR verifier in isolation."""
    print("="*60)
    print("RLVR Verifier Demonstration")
    print("="*60 + "\n")

    print("The RLVR verifier applies formal logic rules to verify rewards.")
    print("Let's see it in action...\n")

    # Create simple environment
    env = make_rlvr_env(
        env_name="MiniGrid-Empty-8x8-v0",
        task_type="reach_goal",
        use_rlvr=True,
    )

    obs, info = env.reset()
    print("Initial State:")
    if 'symbolic_state' in info:
        symbolic_state = info['symbolic_state']
        print(f"  Agent Position: {symbolic_state['agent_pos']}")
        if 'goal_pos' in symbolic_state:
            print(f"  Goal Position: {symbolic_state['goal_pos']}")
    print()

    # Take a few steps
    print("Taking random actions and showing verification...\n")
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        if 'rlvr_verification' in info:
            verification = info['rlvr_verification']
            symbolic_state = info['symbolic_state']

            print(f"Step {i+1}:")
            print(f"  Action: {action}")
            print(f"  Agent Position: {symbolic_state['agent_pos']}")
            print(f"  Reward: {reward:.3f}")
            print(f"  Verified: {verification['verified']}")
            if verification['verified']:
                print(f"  ✓ {verification['explanation']}")
            print()

        if terminated or truncated:
            print("Episode ended!\n")
            break

    env.close()
    print("✓ Verifier demonstration complete\n")


def main():
    """Main quickstart function."""
    print("\n" + "="*60)
    print("RLVR MiniGrid Pipeline - Quick Start")
    print("="*60 + "\n")

    print("This script will:")
    print("1. Check your system requirements")
    print("2. Test the RLVR environment")
    print("3. Demonstrate the verifier")
    print("4. Run a quick training demo (optional)")
    print()

    # System check
    check_system()

    # Test environment
    if not test_environment():
        print("❌ Environment test failed. Please check your installation.")
        print("Try: pip install -r requirements.txt")
        return

    # Demonstrate verifier
    demonstrate_verifier()

    # Ask about training demo
    print("="*60)
    response = input("Run quick training demo? (5000 steps, ~2-3 minutes) [y/N]: ")
    if response.lower() in ['y', 'yes']:
        quick_training_demo()
    else:
        print("\nSkipping training demo.")

    # Final message
    print("\n" + "="*60)
    print("Quick Start Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Full training: python train_rlvr.py --mode rlvr --timesteps 100000")
    print("2. Compare RLVR vs baseline: python train_rlvr.py --mode compare")
    print("3. Read README.md for more details")
    print("\nGood luck with your survey paper! 🚀\n")


if __name__ == "__main__":
    main()
