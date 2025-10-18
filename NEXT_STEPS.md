# Next Steps - Fix Environment Issue

## What Happened

You got an error: `Environment 'MiniGrid-Empty-8x8' doesn't exist`

This is because different versions of MiniGrid may have different environment names.

## How to Fix (3 Simple Steps)

### Step 1: Check What Environments Are Available

Run this command:
```bash
python check_envs.py
```

This will show you:
- All available MiniGrid environments on your system
- Which recommended environments are available
- A test to make sure environments work

### Step 2: Use an Available Environment

After running `check_envs.py`, you'll see a list like:
```
✓ MiniGrid-Empty-6x6-v0
✓ MiniGrid-Empty-8x8-v0
✓ MiniGrid-FourRooms-v0
```

Pick one and use it in your training command:

```bash
# Example with Empty-8x8
python train_rlvr.py --mode rlvr --env MiniGrid-Empty-8x8-v0 --timesteps 100000

# Or try Empty-6x6 (smaller, faster)
python train_rlvr.py --mode rlvr --env MiniGrid-Empty-6x6-v0 --timesteps 100000

# Or try FourRooms (more challenging)
python train_rlvr.py --mode rlvr --env MiniGrid-FourRooms-v0 --timesteps 150000
```

### Step 3: Monitor Training

Once training starts, you should see:
```
============================================================
Training RLVR Agent
Environment: MiniGrid-Empty-8x8-v0
Total timesteps: 100000
Parallel envs: 4
Save directory: ./rlvr_results\rlvr_MiniGrid-Empty-8x8-v0_TIMESTAMP
============================================================

Using device: cuda
```

Training will show a progress bar and take 10-30 minutes depending on the environment.

## Alternative: Run Quickstart

If you want an interactive diagnosis and demo:

```bash
python quickstart.py
```

This will:
1. Check your system
2. Test the environment
3. Show the verifier in action
4. Optionally run a quick training demo

## What I Fixed

The code has been updated to:
1. ✅ Import `minigrid` module to register environments
2. ✅ Show helpful error messages with available environments
3. ✅ Suggest similar environments if one is not found
4. ✅ Added `check_envs.py` to diagnose environment issues

## TL;DR - Quick Commands

```bash
# 1. Check what's available
python check_envs.py

# 2. Pick an environment from the output and train
python train_rlvr.py --mode rlvr --env <ENVIRONMENT_NAME> --timesteps 100000

# OR just run the interactive quickstart
python quickstart.py
```

## If You're Still Stuck

See `TROUBLESHOOTING.md` for more detailed help.

Ready to go! 🚀
