---
title: Fundamentals of Bipedal Locomotion
sidebar_position: 2
description: Understanding the basic principles and challenges of bipedal walking for humanoid robots.
---

# Fundamentals of Bipedal Locomotion

## Why is Bipedal Walking Challenging?

Bipedal locomotion presents several unique challenges:

**Dynamic Instability**: Unlike wheeled robots that are statically stable, bipedal robots are dynamically stable—they must constantly move to avoid falling.

**Underactuation**: During the single-support phase (when only one foot is on the ground), the robot has fewer actuators in contact with the ground than degrees of freedom, making it underactuated.

**Impact Dynamics**: The transition between steps involves impacts that create impulsive forces and require careful control.

**Energy Efficiency**: Human walking is remarkably efficient, but replicating this efficiency in robots is challenging.

## Phases of Bipedal Gait

A complete walking cycle consists of several phases:

**Single Support**: One foot is in contact with the ground, the other is swinging forward. This is the majority of the gait cycle.

**Double Support**: Both feet are in contact with the ground, occurring briefly at the transition between steps.

**Pre-swing**: The trailing leg prepares to lift off.

**Initial Contact**: The swing foot makes contact with the ground.

**Loading Response**: Weight transfers to the newly contacted foot.

## Key Biomechanical Concepts

**Center of Mass (CoM)**: The point where the robot's mass is concentrated. Maintaining CoM stability is crucial for balance.

**Center of Pressure (CoP)**: The point where the ground reaction force acts. The CoP must remain within the support polygon (the area under the feet) for stability.

**Support Polygon**: The convex hull of all contact points with the ground. For bipedal robots, this changes as feet transition from single to double support.

**Step Width and Length**: Parameters that affect stability and efficiency of walking.

## Practical Examples

### Example 1: Balance Recovery
A humanoid robot walking on level ground suddenly encounters a small step. Its center of mass starts to fall outside the support polygon. The robot must quickly:
1. Adjust its foot placement for the next step
2. Shift its upper body to counterbalance
3. Use ankle, hip, and stepping strategies to recover balance
4. Continue walking with modified gait parameters

### Example 2: Walking on Uneven Terrain
When a humanoid robot walks on uneven ground:
- **Perception**: Vision and force sensors detect terrain variations
- **Planning**: Adjust step location and height based on terrain
- **Control**: Modify joint trajectories to accommodate terrain changes
- **Adaptation**: Learn from previous steps to improve future performance

## Exercises

1. **Stability Analysis**: For a bipedal robot with a 50cm step width, estimate the maximum lateral disturbance it can withstand without falling. What factors would influence this?

2. **Gait Parameter Design**: Design a walking gait for a humanoid robot that needs to walk efficiently but also be stable. What step length, step width, and walking speed would you choose? Justify your choices.

3. **Balance Strategy**: Compare ankle strategy, hip strategy, and stepping strategy for balance recovery. When would each be most appropriate?

4. **Underactuation Challenge**: Explain why bipedal robots are underactuated during the single support phase. How does this affect controller design?

5. **Energy Efficiency**: What are the main sources of energy loss in bipedal walking? How could they be minimized in a humanoid robot design?