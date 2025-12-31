---
title: Contact Mechanics and Force Control
sidebar_position: 5
description: Understanding contact mechanics, friction models, and force control strategies for manipulation.
---

# Contact Mechanics and Force Control

Understanding contact mechanics is crucial for stable grasping and safe manipulation.

## Contact Models

**Point Contact**: Simple model assuming contact occurs at a point with friction.

**Surface Contact**: More realistic model considering the contact area and pressure distribution.

**Soft Contact**: Models the deformation of soft fingers or soft objects during contact.

## Friction and Grasp Stability

The friction cone defines the range of forces that can be applied at a contact point without causing slip:

```
|tangent_forces| ≤ μ × normal_force
```

Where μ is the coefficient of friction.

For stable grasping, the object's weight and any external forces must be balanced by contact forces within the friction cones at all contact points.

## Force Control Strategies

**Impedance Control**: Make the robot behave like a spring-damper system, allowing controlled interaction with the environment.

```
F = K(x_desired - x_actual) + B(v_desired - v_actual)
```

Where K is stiffness, B is damping, and x and v are position and velocity.

**Admittance Control**: Control the robot's motion in response to applied forces:

```
ẍ = M⁻¹(F_applied - Bẋ - Kx)
```

Where M is the desired mass.

**Hybrid Force/Position Control**: Control some degrees of freedom in position and others in force, useful for constrained motions like inserting pegs into holes.

## Compliance and Safety

For humanoid robots interacting with humans, compliance is essential for safety:

**Variable Compliance**: Adjust the robot's stiffness based on the task and environment.

**Active Compliance**: Use feedback control to achieve desired compliance characteristics.

**Passive Compliance**: Design mechanical compliance into the robot's structure.