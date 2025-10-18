"""
Check available MiniGrid environments and test basic functionality.
"""

import gymnasium as gym
import minigrid

print("\n" + "="*70)
print("MiniGrid Environment Check")
print("="*70 + "\n")

# Get all MiniGrid environments
all_envs = [e for e in gym.envs.registry.keys() if 'MiniGrid' in e]
print(f"Total MiniGrid environments found: {len(all_envs)}\n")

# Show recommended environments for RLVR
print("Recommended environments for RLVR training:")
print("-"*70)

recommended = {
    "MiniGrid-Empty-8x8-v0": "Empty grid, simplest (fastest training)",
    "MiniGrid-Empty-6x6-v0": "Smaller empty grid (very fast)",
    "MiniGrid-Empty-16x16-v0": "Larger empty grid (harder)",
    "MiniGrid-FourRooms-v0": "Navigate through four rooms",
    "MiniGrid-DoorKey-5x5-v0": "Pick up key and open door",
    "MiniGrid-DoorKey-6x6-v0": "Larger key-door task",
    "MiniGrid-DoorKey-8x8-v0": "Even larger key-door task",
}

for env_name, description in recommended.items():
    if env_name in all_envs:
        print(f"✓ {env_name:<30} - {description}")
    else:
        print(f"✗ {env_name:<30} - NOT AVAILABLE")

print("\n" + "-"*70)
print("\nAll available MiniGrid environments:")
print("-"*70)
for env in sorted(all_envs):
    print(f"  {env}")

print("\n" + "="*70)
print("\nTesting environment creation...")
print("="*70 + "\n")

# Try to create a test environment
test_env_name = "MiniGrid-Empty-8x8-v0"

# Find first available empty environment
empty_envs = [e for e in all_envs if 'Empty' in e]
if empty_envs:
    test_env_name = sorted(empty_envs)[0]
    print(f"Testing with: {test_env_name}")

    try:
        env = gym.make(test_env_name)
        print(f"✓ Environment created successfully")

        obs, info = env.reset()
        print(f"✓ Environment reset successful")
        print(f"  Observation type: {type(obs)}")
        if isinstance(obs, dict):
            print(f"  Observation keys: {list(obs.keys())}")
            if 'image' in obs:
                print(f"  Image shape: {obs['image'].shape}")

        env.close()
        print("\n✅ Environment test PASSED")

    except Exception as e:
        print(f"\n❌ Environment test FAILED: {e}")
else:
    print("❌ No Empty environments found!")

print("\n" + "="*70 + "\n")
