---
title: Control Systems in Robotics
sidebar_position: 5
description: Understanding feedback control, PID controllers, and advanced control strategies for robotic systems.
---

# Control Systems in Robotics

Control systems determine how robots respond to commands and disturbances. In robotics, we typically want to make a robot follow a desired trajectory or maintain a desired state.

## Open-Loop vs. Closed-Loop Control

**Open-loop control** sends commands to the robot without checking if the desired result is achieved. For example, commanding a joint to move to a specific angle without verifying it actually gets there.

**Closed-loop control** (feedback control) measures the actual state of the system and adjusts commands based on the difference between desired and actual states. This is much more robust to disturbances and model inaccuracies.

## Proportional-Integral-Derivative (PID) Control

PID control is the most common control strategy in robotics. It calculates control actions based on three terms:

```
u(t) = Kp * e(t) + Ki * ∫e(t)dt + Kd * de(t)/dt
```

Where:
- e(t) is the error (desired value - actual value)
- Kp is the proportional gain
- Ki is the integral gain
- Kd is the derivative gain

**Proportional term (Kp)**: Reacts to current error. Higher Kp makes the system respond faster but can cause oscillations.

**Integral term (Ki)**: Reacts to accumulated past error. Helps eliminate steady-state error but can cause instability if too high.

**Derivative term (Kd)**: Reacts to rate of change of error. Provides damping to reduce oscillations.

## PID Tuning for Robotics

Tuning PID parameters for robotic systems requires understanding the system dynamics:

- For position control of robot joints, start with high proportional gain for responsiveness
- Add derivative gain to dampen oscillations
- Use integral gain sparingly to eliminate small steady-state errors

For humanoid robots, different joints may require different PID parameters based on their mechanical properties and role in the system.

## Advanced Control Concepts

**Feedforward Control**: In addition to feedback control, we can add feedforward terms that anticipate the required control based on desired motion. For example, when a robot arm is moving fast, we might need to apply additional torque to overcome Coriolis forces.

**Computed Torque Control**: Uses the robot's dynamic model to calculate the required torques, then adds feedback control to handle model errors and disturbances.

**Impedance Control**: Instead of controlling position precisely, impedance control makes the robot behave like a spring-damper system, allowing controlled interaction with the environment.

## Control Architectures

Robotic systems often use hierarchical control:

**High-level (Task Space)**: Plan desired movements in Cartesian space (where should the hand go?)

**Mid-level (Inverse Kinematics)**: Convert task-space commands to joint-space commands

**Low-level (Joint Control)**: Execute joint commands using PID or other controllers

This hierarchy allows for more intuitive programming while maintaining precise control.

## Control in Humanoid Robotics

Humanoid robots present unique control challenges:

### Balance Control

Maintaining balance requires:
- Real-time center of mass tracking
- Zero Moment Point (ZMP) control
- Whole-body control strategies that coordinate multiple joints
- Fast reaction to disturbances

### Walking Control

Humanoid walking involves:
- Gait planning (where to place feet)
- Dynamic balance during single and double support phases
- Adaptive control for different terrains
- Energy-efficient motion patterns

### Multi-Task Control

Humanoid robots often need to perform multiple tasks simultaneously:
- Maintain balance while moving arms
- Walk while carrying objects
- Interact with environment while maintaining stability

This requires advanced control techniques like operational space control or quadratic programming-based controllers that can prioritize different tasks.

## Practical Examples

### Example 1: PID Control for Robot Joint
Consider a robot arm joint that needs to move to a desired angle of 45°. The current angle is 30°, and the PID parameters are Kp=2, Ki=0.1, Kd=0.5. The error is currently 15° and increasing at 5°/s. What is the control output?

**Solution:**
- Proportional term: 2 × 15° = 30
- Derivative term: 0.5 × 5°/s = 2.5
- Assuming no accumulated error yet, integral term ≈ 0
- Total control output = 30 + 0 + 2.5 = 32.5 (units depend on system)

### Example 2: Balance Control for Humanoid Robot
A humanoid robot is standing on one foot. To maintain balance, it must keep its center of mass (CoM) directly over the support foot. If the CoM is detected to be 2cm forward of the support point, how should the robot adjust its posture?

**Solution:**
The robot could:
1. Lean back slightly by adjusting hip and ankle joints
2. Use feedback from IMU sensors to measure tilt
3. Apply PID control to minimize the CoM offset error
4. Coordinate multiple joints (ankle, hip, knee) for stable balance

## Exercises

1. **PID Tuning**: For a robot joint that tends to oscillate around the target position, which PID parameter should be increased to reduce oscillations? Explain your reasoning.

2. **Control Architecture**: Design a control architecture for a humanoid robot that needs to walk forward while avoiding obstacles detected by its cameras. What are the different control levels and how do they interact?

3. **Balance Challenge**: A humanoid robot is standing on a moving platform. How would you modify the balance control system to handle this disturbance? What additional sensors would be helpful?

4. **Multi-Task Control**: How would you prioritize tasks when a humanoid robot needs to maintain balance, move its arm to pick up an object, and avoid an obstacle simultaneously? Design a priority scheme.

5. **ZMP Control**: Explain the concept of Zero Moment Point (ZMP) in humanoid robotics. Why is it important for stable walking, and how would you implement a simple ZMP controller?