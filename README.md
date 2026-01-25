# 🚀 Starship Falcon

A beautiful ASCII rocket launch animation for your terminal, written in Python.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## ✨ Features

- 🎨 **Colorful ASCII Art** - Beautifully designed rocket with vibrant ANSI colors
- 🔥 **Animated Flames** - Dynamic exhaust flames that flicker realistically
- ⭐ **Twinkling Stars** - Random star field with twinkling effect
- 🔄 **Continuous Loop** - Watch the rocket launch over and over
- 💻 **Cross-Platform** - Works on Windows, Linux, and macOS
- 📦 **Zero Dependencies** - Uses only Python standard library

## 🖥️ Preview

```
  🚀 STARSHIP FALCON - LAUNCH SEQUENCE 🌟
  ──────────────────────────────────────────────────
  │                    *                           │
  │         .                          *           │
  │                        ^                       │
  │    *                  /|\                 .    │
  │                      /███\                     │
  │         .            ███                       │
  │                     [===]                  *   │
  │                    / ||| \                     │
  │                   /  |||  \                    │
  │              *      \|||/              .       │
  │                    \|||||/                     │
  ──────────────────────────────────────────────────
  Frame: 0042 │ Altitude:  25 units │ Press Ctrl+C to exit
```

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- A terminal that supports ANSI escape codes (most modern terminals do)

### Installation

```bash
# Clone the repository
git clone https://github.com/parthchaudhari90/starship-falcon-game.git

# Navigate to the directory
cd starship-falcon-game

# Run the game
python starship_falcon.py
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `Ctrl+C` | Exit the animation |

## 🛠️ How It Works

The animation uses:
- **ANSI escape codes** for colors and cursor control
- **Double buffering** for smooth rendering
- **Signal handling** for graceful exit
- **Frame-based animation** for consistent movement

## 📁 Project Structure

```
starship-falcon-game/
├── starship_falcon.py   # Main game file
├── requirements.txt     # Dependencies (none required!)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🎨 Customization

You can easily customize the animation by modifying these constants in `starship_falcon.py`:

```python
WIDTH = 80          # Terminal width
HEIGHT = 30         # Terminal height
FRAME_DELAY = 0.05  # Animation speed (seconds per frame)
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests

---

<p align="center">
  Made with ❤️ and Python
  <br>
  ⭐ Star this repo if you found it cool!
</p>

