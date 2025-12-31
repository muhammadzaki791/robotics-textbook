---
title: Zero Moment Point (ZMP) Theory
sidebar_position: 3
description: Understanding the ZMP concept and its application in bipedal robot balance control.
---

# Zero Moment Point (ZMP) Theory

The Zero Moment Point is a fundamental concept in bipedal robotics that provides a simplified approach to balance control.

## Definition and Physics

The ZMP is the point on the ground where the net moment (torque) of the inertial and gravitational forces acting on the robot is zero. In simpler terms, it's the point where all the forces acting on the robot appear to be applied.

Mathematically, for a robot with center of mass at (x_com, y_com, z_com):
```
x_zmp = x_com - (z_com - z_support) * ẍ_com / g
y_zmp = y_com - (z_com - z_support) * ÿ_com / g
```

Where g is gravitational acceleration and z_support is the height of the support surface.

## ZMP Stability Criterion

For stable locomotion, the ZMP must remain within the support polygon (the area under the feet). This provides a clear stability criterion that can be used in control design.

## ZMP-Based Walking Pattern Generation

The ZMP approach allows for the generation of stable walking patterns:

1. **Desired ZMP Trajectory**: Define a ZMP trajectory that stays within the support polygon
2. **CoM Trajectory**: Integrate the ZMP equations to find the required CoM motion
3. **Joint Trajectory**: Use inverse kinematics to find joint angles that achieve the CoM motion

## Advantages and Limitations

**Advantages**:
- Provides clear stability criterion
- Well-established mathematical framework
- Computationally efficient

**Limitations**:
- Assumes relatively slow, quasi-static motion
- Simplifies complex whole-body dynamics
- May not capture all aspects of dynamic locomotion