---
title: Centroidal Dynamics
sidebar_position: 4
description: Understanding centroidal momentum and dynamics for whole-body control.
---

# Centroidal Dynamics

Centroidal dynamics provides a more complete model of bipedal locomotion by considering the motion of the center of mass and the centroidal momentum.

## Centroidal Momentum

The centroidal momentum consists of:
- **Linear Momentum**: h = m * v_com (mass times CoM velocity)
- **Angular Momentum**: L = I_com * ω_com (momentum about CoM)

## Centroidal Dynamics Equations

The centroidal dynamics can be expressed as:
```
ḣ = f_total  (rate of change of linear momentum equals total external force)
L̇ = τ_total  (rate of change of angular momentum equals total external torque)
```

## Applications in Control

Centroidal dynamics enables more sophisticated control approaches:
- **Model Predictive Control (MPC)**: Predict future states based on centroidal dynamics
- **Whole-body Control**: Coordinate upper and lower body motion
- **Push Recovery**: Handle external disturbances more effectively