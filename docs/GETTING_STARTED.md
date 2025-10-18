# Getting Started with RLVR MiniGrid Pipeline

Quick guide to get up and running with the RLVR implementation.

## Installation (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test installation:**
   ```bash
   python test_installation.py
   ```

   This will verify that all packages are installed correctly and CUDA is working.

3. **Run quickstart (optional):**
   ```bash
   python quickstart.py
   ```

   Interactive script that demonstrates the system and optionally runs a short training demo.

## Quick Training (15-30 minutes)

### Option 1: Train RLVR Agent Only

```bash
python train_rlvr.py --mode rlvr --env MiniGrid-Empty-8x8-v0 --timesteps 100000 --n-envs 4
```

Results saved to: `./rlvr_results/rlvr_MiniGrid-Empty-8x8-v0_*/`

### Option 2: Compare RLVR vs Baseline

```bash
python train_rlvr.py --mode compare --env MiniGrid-Empty-8x8-v0 --timesteps 100000 --n-envs 4
```

This trains both RLVR and baseline agents for direct comparison.

### Option 3: Different Environment

Try a more challenging environment:

```bash
python train_rlvr.py --mode rlvr --env MiniGrid-DoorKey-5x5-v0 --timesteps 150000
```

## View Training Progress

```bash
tensorboard --logdir ./rlvr_results
```

Open browser to `http://localhost:6006`

## Demonstrate Trained Agent

After training, demonstrate your agent:

```bash
# Find your model path (example):
# ./rlvr_results/rlvr_MiniGrid-Empty-8x8-v0_20250118_123456/best_model/best_model.zip

# Demo with visualization
python demo_rlvr.py --model <path_to_model> --mode demo --episodes 5

# Show detailed verification
python demo_rlvr.py --model <path_to_model> --mode verify

# Save video
python demo_rlvr.py --model <path_to_model> --save-video --video-path my_agent.gif
```

## Analyze Results

```bash
# Generate summary report
python analyze_results.py --mode summary --results-dir ./rlvr_results

# Plot training curves
python analyze_results.py --mode plot --rlvr-dir ./rlvr_results/rlvr_* --baseline-dir ./rlvr_results/baseline_*

# Compare performance
python analyze_results.py --mode compare --rlvr-dir ./rlvr_results/rlvr_* --baseline-dir ./rlvr_results/baseline_*
```

## Recommended Workflow for Survey Paper

1. **Test installation:**
   ```bash
   python test_installation.py
   ```

2. **Run quick demo:**
   ```bash
   python quickstart.py
   ```

3. **Train comparison:**
   ```bash
   python train_rlvr.py --mode compare --env MiniGrid-Empty-8x8-v0 --timesteps 100000
   ```

4. **Analyze results:**
   ```bash
   python analyze_results.py --mode compare --rlvr-dir ./rlvr_results/rlvr_* --baseline-dir ./rlvr_results/baseline_*
   ```

5. **Create demo video:**
   ```bash
   python demo_rlvr.py --model ./rlvr_results/rlvr_*/best_model/best_model.zip --save-video
   ```

6. **Document findings:**
   - Training curves from TensorBoard
   - Comparison plots from analysis
   - Demo video
   - Verification logs

## Troubleshooting

### "CUDA out of memory"
```bash
# Reduce parallel environments
python train_rlvr.py --mode rlvr --n-envs 2 --timesteps 100000
```

### "Import error: No module named X"
```bash
pip install --upgrade -r requirements.txt
```

### Training too slow
- Ensure GPU is being used (look for "Using device: cuda" in output)
- Reduce environment complexity (use Empty-8x8 instead of DoorKey)
- Reduce timesteps for initial testing

### Can't find trained model
```bash
# List all experiments
ls ./rlvr_results/

# Find best model in experiment directory
ls ./rlvr_results/rlvr_*/best_model/
```

## Understanding the Code

### Key Files

1. **rlvr_verifier.py** - Core RLVR logic
   - `extract_symbolic_state()` - Converts visual obs to symbols
   - `verify_task_completion()` - Applies verification rules

2. **rlvr_env_wrapper.py** - Environment integration
   - `RLVRMiniGridWrapper` - Replaces env reward with verified reward
   - `make_rlvr_env()` - Factory function

3. **train_rlvr.py** - Training script
   - `MinigridCNN` - Custom CNN for visual observations
   - `train_rlvr_agent()` - PPO training loop

4. **demo_rlvr.py** - Demonstration
   - `demonstrate_agent()` - Run and visualize agent
   - `visualize_verification_process()` - Detailed verification logs

### Key Concepts

**Visual Observations:**
- Agent sees 7×7×3 RGB image (partial view of grid)
- CNN processes image to features
- Policy maps features to actions

**Symbolic State:**
```python
{
    'agent_pos': (3, 4),      # Agent location
    'agent_dir': 0,           # Facing direction
    'goal_pos': (6, 6),       # Goal location
    'carrying': None,         # What agent carries
}
```

**Verification:**
```python
# Rule: Goal reached?
if agent_pos == goal_pos:
    reward = 1.0  # Verified success
else:
    reward = -0.001 * distance  # Shaping
```

## Next Steps

1. **Extend verification rules** - Add temporal logic, complex goals
2. **Try harder environments** - DoorKey, FourRooms, custom mazes
3. **Experiment with hyperparameters** - Learning rate, network size
4. **Add more analysis** - Statistical significance tests
5. **Document for paper** - Figures, tables, explanations

## Resources

- **MiniGrid docs:** https://minigrid.farama.org/
- **Stable Baselines3 docs:** https://stable-baselines3.readthedocs.io/
- **PPO paper:** https://arxiv.org/abs/1707.06347

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Run `test_installation.py` to diagnose problems
3. Review code comments in source files

Good luck with your survey paper! 🚀
