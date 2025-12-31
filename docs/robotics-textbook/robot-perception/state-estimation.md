---
title: State Estimation
sidebar_position: 3
description: Understanding Kalman filters, particle filters, and other techniques for estimating robot state from sensor measurements.
---

# State Estimation

State estimation is the process of determining the robot's state (position, orientation, velocity, etc.) from sensor measurements. Since sensors are noisy and sometimes fail, robots must estimate their state rather than rely on raw sensor readings.

## The State Estimation Problem

The state estimation problem can be formulated as:
- Given a sequence of control inputs and sensor measurements
- Estimate the robot's state (position, orientation, velocity, etc.)
- Account for uncertainty in both motion and sensing

## Kalman Filters

Kalman filters provide optimal state estimation for linear systems with Gaussian noise. They work by:

1. **Prediction Step**: Predict the state based on motion model and control inputs
2. **Update Step**: Correct the prediction using sensor measurements

The Kalman filter maintains a state estimate and its uncertainty (represented as a covariance matrix). It optimally combines predictions and measurements based on their respective uncertainties.

**Mathematical Formulation**:

State prediction: `x̂ₖ|ₖ₋₁ = Fₖx̂ₖ₋₁|ₖ₋₁ + Bₖuₖ`

Covariance prediction: `Pₖ|ₖ₋₁ = FₖPₖ₋₁|ₖ₋₁Fₖᵀ + Qₖ`

Kalman gain: `Kₖ = Pₖ|ₖ₋₁Hₖᵀ(HₖPₖ|ₖ₋₁Hₖᵀ + Rₖ)⁻¹`

State update: `x̂ₖ|ₖ = x̂ₖ|ₖ₋₁ + Kₖ(zₖ - Hₖx̂ₖ|ₖ₋₁)`

Covariance update: `Pₖ|ₖ = (I - KₖHₖ)Pₖ|ₖ₋₁`

Where:
- `x̂` is the state estimate
- `P` is the covariance matrix
- `F` is the state transition model
- `B` is the control-input model
- `u` is the control vector
- `H` is the observation model
- `z` is the measurement
- `Q` is the process noise covariance
- `R` is the observation noise covariance

## Extended Kalman Filter (EKF)

For nonlinear systems, the Extended Kalman Filter linearizes the system around the current estimate. This is useful for robot systems that involve rotations and complex kinematics.

## Particle Filters

Particle filters represent the state distribution as a set of random samples (particles). They're particularly useful for multimodal distributions and highly nonlinear systems.

**Algorithm**:
1. Initialize particles randomly according to prior belief
2. For each control input:
   - Predict particle motion based on motion model
   - Add noise to represent uncertainty
3. For each measurement:
   - Weight particles based on how well they match the measurement
   - Resample particles based on their weights

Particle filters are especially useful for:
- Global localization (finding position in a map)
- Tracking multiple hypotheses
- Non-Gaussian noise models

## Applications in Humanoid Robotics

State estimation is crucial for humanoid robots:

**Balance Control**: Accurate estimation of center of mass and base orientation is essential for maintaining balance.

**Localization**: Determining the robot's position in the environment for navigation.

**SLAM (Simultaneous Localization and Mapping)**: Building a map while localizing in it—essential for autonomous navigation.

**Motion Capture**: Estimating full-body pose for imitation learning or motion analysis.