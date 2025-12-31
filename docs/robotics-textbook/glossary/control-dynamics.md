---
title: Control and Dynamics
sidebar_position: 3
description: Control systems and dynamic behavior including PID control, stability, and dynamic modeling.
---

# Control and Dynamics

**Admittance Control**: A control strategy where the robot's motion is controlled in response to applied forces, making the robot behave like a mechanical system with specified mass, damping, and stiffness properties.

**Balance Control**: The process of maintaining a robot's center of mass within its support polygon to prevent falling. Critical for bipedal robots.

**Compliance**: The ability of a robot to yield or adapt to external forces, often implemented through control algorithms or mechanical design to ensure safe interaction.

**Control Lyapunov Function**: A mathematical function used in control theory to prove the stability of control systems, increasingly applied in learning-based robot control.

**Force Control**: A control strategy that regulates the forces applied by a robot during interaction with objects or the environment, important for safe and effective manipulation.

**Impedance Control**: A control strategy that makes a robot behave like a spring-damper system, allowing controlled interaction with the environment by specifying desired mechanical impedance.

**Variable Impedance Control**: The ability to change the mechanical impedance of a robot's joints or end-effector to adapt to different tasks and interaction requirements.

**PID Control**: Proportional-Integral-Derivative control, a feedback control mechanism widely used in robotics for precise control of position, speed, and other variables.

**Torque Control**: Control of the rotational force applied by robot joints, important for safe interaction and precise manipulation.

**Inverse Dynamics**: The calculation of the forces and torques required to achieve a desired motion, important for robot control.

**Model Predictive Control (MPC)**: An advanced control method that uses a model of the system to predict future behavior and optimize control actions over a finite time horizon.

**Operational Space Control**: A control framework that allows for the control of multiple tasks in their natural coordinate systems simultaneously, such as end-effector position and joint limit avoidance.

**Robust Control**: Control strategies designed to maintain performance in the presence of uncertainties, disturbances, and model inaccuracies.

**Zero Moment Point (ZMP)**: A point on the ground where the net moment of the inertial and gravitational forces acting on a robot is zero, used as a stability criterion in bipedal robotics.

**Capture Point**: A point on the ground where a robot can step to stop its current motion and maintain balance. Used in humanoid balance control.

**Centroidal Dynamics**: The study of a robot's motion based on its center of mass and centroidal momentum, providing a simplified model for balance and locomotion control.

**Series Elastic Actuator (SEA)**: An actuator design that includes a spring in series with the motor, providing inherent compliance and accurate force control.

**Adaptive Control**: A control method that adjusts its parameters in real-time based on changes in the system or environment to maintain performance.

**Backstepping Control**: A nonlinear control design technique that constructs a Lyapunov function and control law systematically for systems in strict-feedback form.

**Cartesian Space Control**: Control of a robot's end-effector position and orientation directly in Cartesian coordinates rather than joint space.

**Computed Torque Control**: A control method that uses the robot's dynamic model to compute the required torques, then adds feedback control to handle model errors.

**Coordinate Descent**: An optimization algorithm that successively minimizes along coordinate axes, used in inverse kinematics and trajectory optimization.

**Cross-Coupled Control**: A control strategy that coordinates multiple axes or joints to improve overall system performance and accuracy.

**Dynamic Balance**: The ability to maintain balance while in motion, requiring continuous adjustment of the center of mass and support base.

**Dynamic Movement Primitives (DMP)**: A method for generating and controlling movements based on dynamical systems theory, useful for learning and reproducing movements.

**Feedback Linearization**: A control technique that transforms a nonlinear system into an equivalent linear system through feedback and coordinate transformation.

**Feedforward Control**: A control component that anticipates required control actions based on desired motion, often used in conjunction with feedback control.

**Gain Scheduling**: A control technique where controller parameters are adjusted based on operating conditions or system states.

**Hybrid Zero Dynamics**: A control framework for underactuated systems that combines continuous dynamics with discrete events for stable periodic motions.

**Linear Quadratic Regulator (LQR)**: An optimal control technique that minimizes a quadratic cost function of state and control effort.

**Motion Primitives**: Basic movement patterns that can be combined to generate complex behaviors in robotics.

**Nonlinear Control**: Control methods specifically designed for systems with nonlinear dynamics that cannot be adequately handled by linear control techniques.

**Operational Space Formulation**: A mathematical framework for controlling robot tasks in the space where they are naturally defined, such as end-effector position.

**Passivity-Based Control**: A control approach that exploits the energy properties of physical systems to ensure stability.

**Point-to-Point Control**: A simple control strategy that moves the robot from one configuration to another without specifying the intermediate trajectory.

**Proportional-Derivative (PD) Control**: A simplified form of PID control without the integral term, often sufficient for many robotic applications.

**Riccati Equation**: A matrix equation that appears in optimal control problems, particularly in LQR and LQG control design.

**Sliding Mode Control**: A robust control technique that forces the system state to follow a predefined sliding surface despite uncertainties and disturbances.

**Stability Margin**: A measure of how close a control system is to instability, important for robust performance.

**Trajectory Tracking**: The control of a robot to follow a desired time-varying path with specified position, velocity, and acceleration.

**Virtual Model Control**: A control approach that creates virtual components to achieve desired dynamic behavior in robotic systems.