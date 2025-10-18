"""
Installation Test Script

Quick test to verify all dependencies are installed correctly.
"""

import sys


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...\n")

    packages = [
        ('gymnasium', 'Gymnasium'),
        ('minigrid', 'MiniGrid'),
        ('torch', 'PyTorch'),
        ('numpy', 'NumPy'),
        ('stable_baselines3', 'Stable Baselines3'),
        ('matplotlib', 'Matplotlib'),
        ('PIL', 'Pillow'),
        ('imageio', 'ImageIO'),
    ]

    failed = []

    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError as e:
            print(f"✗ {display_name} - FAILED")
            failed.append(display_name)

    print()

    if failed:
        print(f"❌ {len(failed)} package(s) failed to import:")
        for pkg in failed:
            print(f"   - {pkg}")
        print("\nPlease install missing packages:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages imported successfully!")
        return True


def test_cuda():
    """Test CUDA availability."""
    print("\nTesting CUDA...\n")

    try:
        import torch

        if torch.cuda.is_available():
            print(f"✓ CUDA is available")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA Version: {torch.version.cuda}")

            # Test a simple CUDA operation
            x = torch.tensor([1.0, 2.0, 3.0]).cuda()
            y = x * 2
            print(f"  Simple CUDA operation: {y.cpu().numpy()}")
            print("\n✅ CUDA test passed!")
            return True
        else:
            print("⚠️  CUDA is not available")
            print("   Training will use CPU (slower)")
            print("   This is OK for testing, but GPU recommended for full training")
            return True

    except Exception as e:
        print(f"❌ CUDA test failed: {e}")
        return False


def test_minigrid():
    """Test MiniGrid environment creation."""
    print("\nTesting MiniGrid environment...\n")

    try:
        import gymnasium as gym

        # Create environment
        env = gym.make("MiniGrid-Empty-8x8-v0")
        print("✓ Environment created")

        # Reset environment
        obs, info = env.reset()
        print(f"✓ Environment reset successful")
        print(f"  Observation type: {type(obs)}")
        if isinstance(obs, dict):
            print(f"  Observation keys: {obs.keys()}")
            if 'image' in obs:
                print(f"  Image shape: {obs['image'].shape}")

        # Take a step
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"✓ Environment step successful")
        print(f"  Action: {action}, Reward: {reward}")

        env.close()
        print("\n✅ MiniGrid test passed!")
        return True

    except Exception as e:
        print(f"❌ MiniGrid test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rlvr_modules():
    """Test custom RLVR modules."""
    print("\nTesting RLVR modules...\n")

    try:
        # Test verifier import
        from rlvr_verifier import RLVRVerifier
        print("✓ RLVRVerifier imported")

        # Test environment wrapper import
        from rlvr_env_wrapper import make_rlvr_env
        print("✓ Environment wrapper imported")

        # Create RLVR environment
        env = make_rlvr_env(
            env_name="MiniGrid-Empty-8x8-v0",
            task_type="reach_goal",
            use_rlvr=True,
        )
        print("✓ RLVR environment created")

        # Test environment
        obs, info = env.reset()
        print("✓ RLVR environment reset successful")

        # Take a step and check verification
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print("✓ RLVR environment step successful")

        if 'rlvr_verification' in info:
            print("✓ RLVR verification info present")
            verification = info['rlvr_verification']
            print(f"  Verified: {verification['verified']}")
            print(f"  Explanation: {verification['explanation']}")

        if 'symbolic_state' in info:
            print("✓ Symbolic state extraction working")
            symbolic_state = info['symbolic_state']
            print(f"  Agent position: {symbolic_state['agent_pos']}")

        env.close()
        print("\n✅ RLVR modules test passed!")
        return True

    except Exception as e:
        print(f"❌ RLVR modules test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ppo():
    """Test PPO model creation."""
    print("\nTesting PPO model creation...\n")

    try:
        from stable_baselines3 import PPO
        from rlvr_env_wrapper import make_rlvr_env
        from train_rlvr import MinigridCNN

        # Create environment
        env = make_rlvr_env(
            env_name="MiniGrid-Empty-8x8-v0",
            task_type="reach_goal",
            use_rlvr=True,
        )

        # Create PPO model
        policy_kwargs = dict(
            features_extractor_class=MinigridCNN,
            features_extractor_kwargs=dict(features_dim=128),
        )

        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"

        model = PPO(
            policy="CnnPolicy",
            env=env,
            policy_kwargs=policy_kwargs,
            verbose=0,
            device=device,
        )
        print(f"✓ PPO model created on {device}")

        # Test prediction
        obs, info = env.reset()
        action, _states = model.predict(obs)
        print(f"✓ Model prediction successful (action: {action})")

        env.close()
        print("\n✅ PPO test passed!")
        return True

    except Exception as e:
        print(f"❌ PPO test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("RLVR INSTALLATION TEST")
    print("="*70 + "\n")

    print(f"Python version: {sys.version}\n")

    tests = [
        ("Package Imports", test_imports),
        ("CUDA", test_cuda),
        ("MiniGrid Environment", test_minigrid),
        ("RLVR Modules", test_rlvr_modules),
        ("PPO Model", test_ppo),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

        print("\n" + "-"*70 + "\n")

    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your installation is ready.")
        print("\nNext steps:")
        print("1. Run quickstart: python quickstart.py")
        print("2. Train an agent: python train_rlvr.py --mode rlvr")
        print("3. Read README.md for more details")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("   Try reinstalling dependencies: pip install -r requirements.txt")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
