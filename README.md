# Capstone Vision Project

## Overview

Capstone Vision Project is a capstone AI / computer vision project built around the Tap Strap SDK. The repository contains wearable sensor data collection workflows, BLE device integration code, and visualization utilities for gesture and motion understanding experiments.

Related repository: [dla8156/CapstoneDesign](https://github.com/dla8156/CapstoneDesign)

## Tech Stack

- Python
- Tap Strap SDK
- BLE communication with `bleak`
- Tkinter
- Pygame
- Pandas
- Matplotlib

## Architecture

Wearable input device -> Sensor stream capture -> Processing and labeling -> Visualization / downstream model input

## Usage

```bash
pip install -r requirements.txt
python train.py
python inference.py
```

## Results

The project provides a working base for collecting synchronized left-hand and right-hand motion signals, saving labeled samples, and visualizing sensor traces for capstone experimentation.
