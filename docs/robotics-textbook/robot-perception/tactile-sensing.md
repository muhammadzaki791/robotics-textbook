---
title: Tactile Sensing and Haptics
sidebar_position: 6
description: Understanding tactile sensors and haptic feedback systems for robotic manipulation and interaction.
---

# Tactile Sensing and Haptics

Tactile sensing provides information about contact and force, essential for manipulation and safe interaction.

## Tactile Sensor Technologies

**Resistive Sensors**: Measure contact through changes in electrical resistance.

**Capacitive Sensors**: Detect contact through changes in capacitance.

**Optical Sensors**: Use light to detect deformation of a sensing surface.

**Piezoelectric Sensors**: Generate electrical signals in response to applied force.

## Applications

**Grasp Stability**: Detecting whether an object is slipping during grasping.

**Surface Properties**: Identifying material properties through touch.

**Safe Interaction**: Ensuring compliant behavior during human-robot interaction.

**Assembly Tasks**: Providing feedback during precise assembly operations.

## Perception for Humanoid Locomotion

Humanoid robots face unique perception challenges for locomotion:

### Terrain Analysis

Robots must perceive terrain properties:
- **Traversability**: Is the ground safe to step on?
- **Slope**: How steep is the terrain?
- **Obstacles**: What obstacles need to be avoided or stepped over?
- **Footstep Planning**: Where are good places to place feet?

### Balance-Related Perception

**Center of Pressure**: For bipedal robots, knowing where ground reaction forces act.

**Support Polygon**: The area where feet contact the ground, affecting balance stability.

**Visual Feedback**: Using vision to maintain heading and avoid obstacles during walking.