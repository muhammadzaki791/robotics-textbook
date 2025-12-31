---
title: Kinematics - The Study of Motion
sidebar_position: 3
description: Understanding forward and inverse kinematics for robotic motion analysis.
---

# Kinematics - The Study of Motion

Kinematics is the study of motion without considering the forces that cause it. In robotics, we use kinematics to understand the relationship between joint positions and the position and orientation of the robot's end-effector (or other parts of the robot).

## Forward Kinematics

Forward kinematics answers the question: "Given the joint angles, where is the end-effector?"

For a simple 2D robot arm with two joints, if we know:
- Joint angle θ₁ (angle of first joint from x-axis)
- Joint angle θ₂ (relative angle of second joint)
- Link lengths L₁ and L₂

We can calculate the end-effector position (x, y) using trigonometry:

```
x = L₁ * cos(θ₁) + L₂ * cos(θ₁ + θ₂)
y = L₁ * sin(θ₁) + L₂ * sin(θ₁ + θ₂)
```

For more complex robots, including humanoid robots with many joints, forward kinematics involves multiplying a series of transformation matrices, one for each joint.

**Application to Humanoid Robots**: Forward kinematics is essential for humanoid robots to understand where their hands, feet, and other body parts are located in space based on their joint angles.

## Inverse Kinematics

Inverse kinematics answers the opposite question: "Where should the joints be to place the end-effector at a desired position and orientation?"

This is much more challenging than forward kinematics. For the same 2-joint arm, if we want the end-effector at position (x, y), we need to solve:

```
θ₂ = ± arccos((x² + y² - L₁² - L₂²) / (2 * L₁ * L₂))
θ₁ = arctan(y/x) - arctan((L₂ * sin(θ₂)) / (L₁ + L₂ * cos(θ₂)))
```

Notice that there can be multiple solutions (the ± indicates two possible configurations), and sometimes no solution exists if the desired position is outside the robot's reach.

For humanoid robots, inverse kinematics is crucial for tasks like:
- Reaching for objects
- Walking with specific foot placements
- Maintaining balance while moving arms

## Jacobian Matrix

The Jacobian matrix relates joint velocities to end-effector velocities. It's essential for understanding how small changes in joint angles affect the end-effector position.

For a robot with n joints, the Jacobian is a 6×n matrix (6 because we have 3 linear and 3 angular velocities) that maps joint space velocities to Cartesian space velocities:

```
[ẋ]   [J₁₁  J₁₂  ...  J₁n] [θ̇₁]
[ẏ]   [J₂₁  J₂₂  ...  J₂n] [θ̇₂]
[ż] = [J₃₁  J₃₂  ...  J₃n] [...]
[ωₓ]  [J₄₁  J₄₂  ...  J₄n] [θ̇ₙ]
[ωᵧ]
[ωz]
```

The Jacobian is crucial for:
- Velocity control of robot arms
- Understanding singularities (configurations where the robot loses degrees of freedom)
- Force control applications

## Practical Examples

### Example 1: 2-Link Robot Arm
Consider a simple 2-link robot arm with link lengths L₁ = 5 units and L₂ = 3 units. If joint angles are θ₁ = 30° and θ₂ = 45°, what is the position of the end-effector?

**Solution:**
First, convert angles to radians: θ₁ = π/6, θ₂ = π/4
Then calculate:
x = 5 * cos(π/6) + 3 * cos(π/6 + π/4) = 5 * 0.866 + 3 * cos(5π/12) ≈ 4.33 + 0.776 = 5.106
y = 5 * sin(π/6) + 3 * sin(π/6 + π/4) = 5 * 0.5 + 3 * sin(5π/12) ≈ 2.5 + 2.898 = 5.398

### Example 2: Inverse Kinematics for Reach
If you want the same 2-link arm to reach point (4, 3), what are the required joint angles?

**Solution:**
Using the inverse kinematics formulas with x=4, y=3, L₁=5, L₂=3:
r² = x² + y² = 16 + 9 = 25
θ₂ = ± arccos((25 - 25 - 9) / (2*5*3)) = ± arccos(-9/30) = ± arccos(-0.3) ≈ ±1.876 radians (≈ ±107.4°)

## Exercises

1. **Forward Kinematics Practice**: For a 2-link robot arm with L₁ = 4 units and L₂ = 2 units, calculate the end-effector position when θ₁ = 60° and θ₂ = 30°.

2. **Workspace Analysis**: For a 2-link arm with L₁ = 6 and L₂ = 4, what is the maximum distance the end-effector can reach from the base? What is the minimum distance?

3. **Inverse Kinematics Challenge**: Can the same arm from Exercise 1 reach the point (8, 1)? Justify your answer mathematically.

4. **Jacobian Application**: If a 2-link robot arm has joint velocities θ̇₁ = 0.1 rad/s and θ̇₂ = 0.2 rad/s, and the Jacobian at the current configuration is:
   ```
   [0.8  -0.6]
   [0.6   0.8]
   ```
   What are the resulting end-effector velocities?

5. **Humanoid Application**: How would you apply inverse kinematics to position both feet of a humanoid robot for stable bipedal walking? What constraints would you need to consider?