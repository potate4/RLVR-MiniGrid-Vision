# Troubleshooting Guide

## Environment Not Found Error

If you see an error like:
```
gymnasium.error.NameNotFound: Environment `MiniGrid-Empty-8x8` doesn't exist.
```

**Solution:**

1. **Check available environments:**
   ```bash
   python check_envs.py
   ```

   This will show you all available MiniGrid environments on your system.

2. **The code has been updated** to automatically handle this. When you run the training script again, it will show you available environments and suggest the correct name.

3. **Common fixes:**
   - Make sure you have the latest version of minigrid: `pip install --upgrade minigrid`
   - The environment names might be slightly different (e.g., `MiniGrid-Empty-Random-8x8-v0` instead of `MiniGrid-Empty-8x8-v0`)

## Quick Fix Steps

### Step 1: Check Available Environments
```bash
python check_envs.py
```

This will output something like:
```
Available MiniGrid environments:
  ✓ MiniGrid-Empty-6x6-v0
  ✓ MiniGrid-Empty-8x8-v0
  ✓ MiniGrid-FourRooms-v0
  ...
```

### Step 2: Use a Working Environment Name

Once you know which environments are available, use one of them:

```bash
# Example: If MiniGrid-Empty-Random-8x8-v0 is available
python train_rlvr.py --mode rlvr --env MiniGrid-Empty-Random-8x8-v0 --timesteps 100000
```

Or try these common ones (in order of simplicity):
```bash
# Simplest (try first)
python train_rlvr.py --mode rlvr --env MiniGrid-Empty-6x6-v0 --timesteps 100000

# Medium difficulty
python train_rlvr.py --mode rlvr --env MiniGrid-FourRooms-v0 --timesteps 150000

# With key and door (harder)
python train_rlvr.py --mode rlvr --env MiniGrid-DoorKey-6x6-v0 --timesteps 200000
```

## Other Common Issues

### CUDA Out of Memory
**Error:** `RuntimeError: CUDA out of memory`

**Solution:**
```bash
# Reduce number of parallel environments
python train_rlvr.py --mode rlvr --n-envs 2 --timesteps 100000

# Or train on CPU (slower but works)
# Edit train_rlvr.py and change device to "cpu" or add a command line flag
```

### Import Errors
**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# Or install specific package
pip install gymnasium minigrid stable-baselines3 torch
```

### Training Too Slow
**Solutions:**
1. Use fewer parallel environments: `--n-envs 2`
2. Use simpler environment: `--env MiniGrid-Empty-6x6-v0`
3. Reduce training steps for testing: `--timesteps 50000`
4. Ensure GPU is being used (check for "Using device: cuda" in output)

### Can't Find Trained Model
After training, find your model:

```bash
# List all experiments
ls ./rlvr_results/

# Example output:
# rlvr_MiniGrid-Empty-8x8-v0_20251018_123456/
# baseline_MiniGrid-Empty-8x8-v0_20251018_124500/

# Model is in:
./rlvr_results/rlvr_MiniGrid-Empty-8x8-v0_TIMESTAMP/best_model/best_model.zip
```

Use this path for demonstration:
```bash
python demo_rlvr.py --model "./rlvr_results/rlvr_MiniGrid-Empty-8x8-v0_20251018_123456/best_model/best_model.zip" --mode demo
```

### Observation Space Issues
If you see errors about observation space, the environment might return observations in a different format.

**Solution:** The `VisualObservationWrapper` in `rlvr_env_wrapper.py` handles this. If issues persist, check the observation format:

```python
import gymnasium as gym
import minigrid

env = gym.make("MiniGrid-Empty-8x8-v0")
obs, info = env.reset()
print(f"Observation type: {type(obs)}")
print(f"Observation keys: {obs.keys() if isinstance(obs, dict) else 'N/A'}")
```

## Getting Help

1. **Run installation test:**
   ```bash
   python test_installation.py
   ```

2. **Check environment availability:**
   ```bash
   python check_envs.py
   ```

3. **Read the documentation:**
   - `README.md` - Full documentation
   - `GETTING_STARTED.md` - Quick start guide
   - This file - Troubleshooting

4. **Check code comments:** All Python files have detailed comments explaining functionality

## Environment-Specific Notes

### MiniGrid Version Differences
Different versions of MiniGrid might have:
- Different environment names
- Different observation formats
- Different action spaces

The code has been designed to handle most variations, but if you encounter issues:
1. Check your minigrid version: `pip show minigrid`
2. Check the [MiniGrid documentation](https://minigrid.farama.org/)
3. Run `check_envs.py` to see exactly what's available

## Still Having Issues?

If the above doesn't help:

1. **Check Python version:** Needs Python 3.8+
   ```bash
   python --version
   ```

2. **Check GPU drivers:** For CUDA support
   ```bash
   nvidia-smi
   ```

3. **Try the quickstart:**
   ```bash
   python quickstart.py
   ```
   This will interactively diagnose issues.

4. **Start simple:**
   ```bash
   # Just test environment creation
   python check_envs.py

   # Test full installation
   python test_installation.py

   # Try minimal training
   python train_rlvr.py --mode rlvr --timesteps 5000 --n-envs 1
   ```

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Environment not found | Run `python check_envs.py` and use an available environment |
| CUDA OOM | Add `--n-envs 2` to training command |
| Import errors | Run `pip install --upgrade -r requirements.txt` |
| Training slow | Use `--env MiniGrid-Empty-6x6-v0 --timesteps 50000` |
| Can't find model | Check `./rlvr_results/` directory |

Good luck! 🚀
