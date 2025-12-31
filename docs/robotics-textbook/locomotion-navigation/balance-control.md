---
title: Balance Control Strategies
sidebar_position: 5
description: Understanding feedback and feedforward control approaches for humanoid balance.
---

# Balance Control Strategies

## Feedback Control Approaches

**Inverted Pendulum Model**: Simplifies the robot to a point mass on a stick, useful for basic balance control.

**Linear Inverted Pendulum Mode (LIPM)**: Assumes constant CoM height, leading to linear dynamics that are easier to control.

**Capture Point**: A point on the ground where a robot can step to stop its motion and maintain balance.

## Feedforward Control

**Trajectory Generation**: Pre-compute stable walking patterns based on ZMP or centroidal dynamics.

**Preview Control**: Use knowledge of future steps to improve current control.

## Disturbance Recovery

**Ankle Strategy**: Use ankle torques to recover from small disturbances.

**Hip Strategy**: Use hip torques for larger disturbances.

**Stepping Strategy**: Take a recovery step when other strategies are insufficient.

## Whole-Body Balance Control

For humanoid robots, balance control must coordinate multiple body parts:
- **Ankle Control**: Fine adjustments through ankle torques
- **Hip Control**: Larger adjustments through hip movements
- **Arm Control**: Counter-movements to help maintain balance
- **Stepping**: Reactive or proactive step planning