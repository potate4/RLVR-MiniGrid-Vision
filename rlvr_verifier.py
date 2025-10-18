"""
RLVR Verifier Module

This module implements an independent reward verifier that checks symbolic state
rather than using the environment's built-in reward signal directly.
This is the core component that makes this an RLVR (Reinforcement Learning
with Verifiable Rewards) system.
"""

import numpy as np
from typing import Dict, Any, Tuple
from enum import IntEnum


class ObjectType(IntEnum):
    """MiniGrid object types (subset)"""
    UNSEEN = 0
    EMPTY = 1
    WALL = 2
    DOOR = 4
    KEY = 5
    GOAL = 8


class RLVRVerifier:
    """
    Independent reward verifier for MiniGrid environments.

    Key RLVR Principle: The verifier operates on symbolic state representation
    and applies verifiable logic rules to determine rewards, decoupled from
    the environment's internal reward mechanism.
    """

    def __init__(self, task_type: str = "reach_goal"):
        """
        Initialize the RLVR verifier.

        Args:
            task_type: Type of task to verify ('reach_goal', 'pick_key', 'open_door')
        """
        self.task_type = task_type
        self.verification_history = []
        self.symbolic_states = []

    def extract_symbolic_state(self, obs: Dict[str, Any], env) -> Dict[str, Any]:
        """
        Extract symbolic representation from visual observation.

        This converts the raw observation into a symbolic state that can be
        verified using logical rules.

        Args:
            obs: Visual observation from environment
            env: MiniGrid environment instance

        Returns:
            Dictionary containing symbolic state information
        """
        symbolic_state = {
            'agent_pos': tuple(env.unwrapped.agent_pos),
            'agent_dir': int(env.unwrapped.agent_dir),
            'carrying': None,
            'grid_state': {},
        }

        # Check what agent is carrying
        if env.unwrapped.carrying is not None:
            symbolic_state['carrying'] = {
                'type': env.unwrapped.carrying.type,
                'color': env.unwrapped.carrying.color,
            }

        # Extract goal position if exists
        grid = env.unwrapped.grid
        for i in range(grid.width):
            for j in range(grid.height):
                cell = grid.get(i, j)
                if cell is not None:
                    if cell.type == 'goal':
                        symbolic_state['goal_pos'] = (i, j)
                    elif cell.type == 'key':
                        symbolic_state['key_pos'] = (i, j)
                    elif cell.type == 'door':
                        if (i, j) not in symbolic_state.get('doors', {}):
                            if 'doors' not in symbolic_state:
                                symbolic_state['doors'] = {}
                            symbolic_state['doors'][(i, j)] = {
                                'is_open': cell.is_open,
                                'is_locked': cell.is_locked,
                                'color': cell.color
                            }

        return symbolic_state

    def verify_task_completion(self, symbolic_state: Dict[str, Any],
                               prev_symbolic_state: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Verify task completion using symbolic logic rules.

        This is the core RLVR component: independent verification based on
        formal rules rather than environment-provided rewards.

        Args:
            symbolic_state: Current symbolic state
            prev_symbolic_state: Previous symbolic state (for transition-based rewards)

        Returns:
            Tuple of (reward, verification_info)
        """
        reward = 0.0
        verification_info = {
            'verified': False,
            'rule_applied': None,
            'explanation': '',
        }

        if self.task_type == "reach_goal":
            # Rule: Agent successfully completes task if positioned at goal location
            if 'goal_pos' in symbolic_state:
                goal_pos = symbolic_state['goal_pos']
                agent_pos = symbolic_state['agent_pos']

                if agent_pos == goal_pos:
                    reward = 1.0
                    verification_info['verified'] = True
                    verification_info['rule_applied'] = 'REACH_GOAL'
                    verification_info['explanation'] = f"Agent reached goal at {goal_pos}"
                else:
                    # Small negative reward for distance (optional shaping)
                    distance = abs(agent_pos[0] - goal_pos[0]) + abs(agent_pos[1] - goal_pos[1])
                    reward = -0.001 * distance
                    verification_info['explanation'] = f"Agent at {agent_pos}, goal at {goal_pos}"

        elif self.task_type == "pick_key":
            # Rule: Agent successfully completes task if carrying a key
            if symbolic_state['carrying'] is not None:
                if symbolic_state['carrying']['type'] == 'key':
                    reward = 1.0
                    verification_info['verified'] = True
                    verification_info['rule_applied'] = 'PICK_KEY'
                    verification_info['explanation'] = "Agent successfully picked up key"

        elif self.task_type == "open_door":
            # Rule: Agent successfully completes task if door is open
            if 'doors' in symbolic_state:
                for door_pos, door_info in symbolic_state['doors'].items():
                    if door_info['is_open'] and prev_symbolic_state is not None:
                        # Check if door was just opened
                        if 'doors' in prev_symbolic_state:
                            prev_door_info = prev_symbolic_state['doors'].get(door_pos)
                            if prev_door_info and not prev_door_info['is_open']:
                                reward = 1.0
                                verification_info['verified'] = True
                                verification_info['rule_applied'] = 'OPEN_DOOR'
                                verification_info['explanation'] = f"Agent opened door at {door_pos}"

        self.verification_history.append(verification_info)
        return reward, verification_info

    def get_verification_stats(self) -> Dict[str, Any]:
        """
        Get statistics about verification history.

        Returns:
            Dictionary with verification statistics
        """
        total_verifications = len(self.verification_history)
        successful_verifications = sum(1 for v in self.verification_history if v['verified'])

        rules_applied = {}
        for v in self.verification_history:
            if v['rule_applied']:
                rules_applied[v['rule_applied']] = rules_applied.get(v['rule_applied'], 0) + 1

        return {
            'total_verifications': total_verifications,
            'successful_verifications': successful_verifications,
            'success_rate': successful_verifications / total_verifications if total_verifications > 0 else 0,
            'rules_applied': rules_applied,
        }

    def reset(self):
        """Reset verifier state for new episode."""
        self.symbolic_states = []
