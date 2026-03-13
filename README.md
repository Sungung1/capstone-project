# Capstone Vision Project

## Overview

Capstone Vision Project is a wearable-input and sensor-data collection project built around the Tap Strap SDK. The repository contains data collection scripts, BLE device integration code, and capstone examples for recording gesture-related accelerometer and gyroscope signals.

## Tech Stack

- Python
- Tap Strap SDK
- BLE communication with `bleak`
- Tkinter
- Pygame
- Pandas
- Matplotlib

## Architecture

Tap Strap devices -> BLE sensor stream -> collection GUI -> word-labeled motion files -> visualization and downstream modeling

## Usage

```bash
pip install -r requirements.txt
python examples/capstone/script.py
python examples/capstone/graph.py
```

## Results

The project provides a working base for collecting synchronized left-hand and right-hand motion signals, saving labeled samples, and visualizing sensor traces for capstone experimentation.
