---
title: Coordinate Systems and Representations
sidebar_position: 2
description: Understanding mathematical representations for robot position and orientation in 3D space.
---

# Coordinate Systems and Representations

Before we can describe how robots move, we need a way to describe where things are in space. In robotics, we use coordinate systems to specify positions and orientations of objects.

## Cartesian Coordinate Systems

The most common coordinate system in robotics is the 3D Cartesian coordinate system, which uses three perpendicular axes (x, y, z) to specify positions in space. Each point in space can be represented as a set of three coordinates (x, y, z).

For example, if we have a robot arm in a room, we might define the origin (0, 0, 0) at the base of the robot, with the x-axis pointing forward, the y-axis pointing left, and the z-axis pointing up.

## Representing Orientation

While position tells us where something is, orientation tells us which direction it's pointing. Representing orientation in 3D space is more complex than position. We have several options:

**Euler Angles**: Three sequential rotations around different axes (commonly roll, pitch, yaw). While intuitive, Euler angles suffer from "gimbal lock" where certain orientations become impossible to represent uniquely.

**Rotation Matrices**: 3x3 matrices that transform vectors from one coordinate system to another. These are mathematically robust but require 9 numbers to represent 3 degrees of freedom.

**Quaternions**: Four numbers that represent rotation without the problems of Euler angles. These are commonly used in robotics and computer graphics.

For humanoid robots, orientation representation is particularly important because they need to maintain balance and coordinate complex movements of multiple body parts.

## Homogeneous Transformations

To represent both position and orientation together, we use homogeneous transformations. These are 4x4 matrices that can represent both rotation and translation in a single mathematical operation.

```
    [ R₁₁  R₁₂  R₁₃  x ]
T = [ R₂₁  R₂₂  R₂₃  y ]
    [ R₃₁  R₃₂  R₃₃  z ]
    [  0    0    0   1 ]
```

Where R represents the 3x3 rotation matrix and (x, y, z) represents the translation.