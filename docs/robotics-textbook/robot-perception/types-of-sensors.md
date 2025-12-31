---
title: Types of Sensors in Robotics
sidebar_position: 2
description: Understanding exteroceptive and proprioceptive sensors used in robotic systems.
---

# Types of Sensors in Robotics

Robotic sensors can be broadly categorized into two types: exteroceptive and proprioceptive.

## Exteroceptive Sensors

Exteroceptive sensors perceive the external environment. These sensors provide information about the robot's surroundings, objects in the environment, and other agents.

### Vision Systems (Cameras)

Cameras are among the most important sensors for humanoid robots, providing rich visual information about the environment. There are several types of vision systems:

**RGB Cameras**: Standard cameras that capture color images. These provide detailed visual information but lack depth information.

**Stereo Cameras**: Two cameras positioned to mimic human eyes, allowing depth estimation through triangulation. Stereo vision enables robots to perceive 3D structure from 2D images.

**RGB-D Cameras**: Combine color information with depth data, providing both visual appearance and 3D structure. The Microsoft Kinect and Intel RealSense are examples of RGB-D sensors.

**Event Cameras**: A newer technology that captures changes in brightness rather than full frames, offering high temporal resolution and low latency for dynamic scenes.

**Applications in Robotics**:
- Object recognition and classification
- Scene understanding
- Navigation and obstacle detection
- Human detection and gesture recognition
- Visual servoing (controlling robot motion based on visual feedback)

### LiDAR (Light Detection and Ranging)

LiDAR sensors emit laser pulses and measure the time it takes for the light to return after reflecting off objects. This provides accurate 3D distance measurements.

**Advantages**:
- High accuracy in distance measurement
- Works in various lighting conditions
- Provides 3D spatial information directly

**Disadvantages**:
- Expensive compared to cameras
- Can be affected by reflective surfaces
- Limited resolution compared to cameras

**Types**:
- **2D LiDAR**: Provides 2D range measurements, commonly used for navigation
- **3D LiDAR**: Provides full 3D point clouds, more suitable for complex scene understanding

### Range Sensors

Other range sensors include:

**Ultrasonic Sensors**: Use sound waves to measure distance. Inexpensive but limited accuracy and range.

**Infrared Sensors**: Measure distance using infrared light. Useful for short-range detection.

**Time-of-Flight (ToF) Sensors**: Measure distance based on the time it takes for light to travel to an object and back.

## Proprioceptive Sensors

Proprioceptive sensors measure the robot's internal state—its configuration and motion.

### Inertial Measurement Units (IMUs)

IMUs typically combine accelerometers, gyroscopes, and sometimes magnetometers:

**Accelerometers**: Measure linear acceleration along three axes. Used for detecting gravity (for orientation relative to ground) and linear motion.

**Gyroscopes**: Measure angular velocity around three axes. Used for detecting rotation and maintaining orientation.

**Magnetometers**: Measure magnetic field, providing absolute orientation relative to magnetic north.

For humanoid robots, IMUs are crucial for balance control and motion estimation.

### Joint Sensors

**Encoders**: Measure joint angles with high precision. Can be absolute (knowing position immediately) or incremental (requiring homing procedure).

**Force/Torque Sensors**: Measure forces and torques at joints or end-effectors. Essential for safe interaction and manipulation.

**Tactile Sensors**: Measure contact forces across surfaces, providing detailed touch information.

### Proprioceptive Applications in Humanoid Robots

- **Balance Control**: IMUs and joint encoders provide information about the robot's pose and motion
- **Safe Interaction**: Force/torque sensors enable compliant behavior
- **Gait Analysis**: Joint sensors monitor walking patterns
- **Self-Monitoring**: Sensors detect mechanical issues or unusual loading