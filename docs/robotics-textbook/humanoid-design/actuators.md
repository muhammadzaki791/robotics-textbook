---
title: Actuator Technologies
sidebar_position: 3
description: Understanding different actuator technologies for humanoid robots including servo motors, compliance systems, and power considerations.
---

# Actuator Technologies

## Servo Motors

**DC Servo Motors**: Most common in humanoid robots.

**Characteristics**:
- Precise position control
- Good torque-to-weight ratio
- Requires gearboxes for high torque
- Can be backdrivable (important for safety)

**Control**: Typically use PID controllers for position, velocity, or torque control.

## Brushless DC Motors

**Advantages**:
- Higher efficiency than brushed motors
- Longer lifespan
- Better performance at high speeds
- Lower electromagnetic interference

**Applications**: High-performance joints requiring precise control.

## Gearbox Selection

**Harmonic Drives**: High reduction ratio, compact, smooth operation.
- Advantages: High precision, compact, zero backlash
- Disadvantages: Expensive, can be fragile, limited lifetime

**Planetary Gearboxes**: Good balance of performance and cost.
- Advantages: Robust, good torque density, cost-effective
- Disadvantages: Lower reduction ratios, potential backlash

**Cycloidal Drives**: High torque density, backlash-free.
- Advantages: High torque, zero backlash, compact
- Disadvantages: Complex, expensive

## Torque Control and Compliance

**Rigid Control**: Traditional approach with high gear ratios for precise position control.

**Compliant Control**: Intentionally allowing some flexibility for safety and interaction.

**Series Elastic Actuators (SEA)**: Include springs in series with the motor for inherent compliance.
- Advantages: Safe interaction, accurate force control, shock absorption
- Disadvantages: Reduced precision, added complexity

**Variable Stiffness Actuators (VSA)**: Actuators with controllable compliance.
- Advantages: Adjustable safety and performance characteristics
- Disadvantages: Increased complexity and weight

## Pneumatic and Hydraulic Actuation

**Pneumatic Systems**:
- Advantages: Light weight, inherent compliance, high power-to-weight ratio
- Disadvantages: Compressibility effects, need for air supply, less precise control

**Hydraulic Systems**:
- Advantages: High power density, excellent force control
- Disadvantages: Heavy, complex plumbing, potential for leaks