# pygmu with uv Package Manager

This guide provides complete instructions for installing and running pygmu using the modern [uv](https://github.com/astral-sh/uv) package manager, which provides faster dependency resolution and virtual environment management compared to traditional pip/pipenv.

## Quick Start

### Prerequisites

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Or on macOS with Homebrew:
   ```bash
   brew install uv
   ```

2. **Install system dependencies for GUI support** (macOS):
   ```bash
   # Install Python with proper Tkinter support
   brew install python@3.13
   brew install python-tk@3.13
   ```

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rdpoor/pygmu.git  # or your fork
   cd pygmu
   ```

2. **Create virtual environment with GUI support**:
   ```bash
   # Use homebrew Python for proper Tkinter support
   uv venv --python /opt/homebrew/bin/python3.13 .venv
   
   # Activate the environment
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   uv pip install bokeh  # Additional dependency for utils
   ```

4. **Test the installation**:
   ```bash
   # Test basic audio generation
   python examples/sine_example.py
   
   # Test GUI player (requires working Tkinter)
   python examples/pygplayer_example.py
   ```

## Usage Examples

### Basic Audio Generation

```python
# Simple sine wave example
import os
import sys
script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, '..', 'pygmu')
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

# Generate a 440Hz sine wave for 2 seconds
sin_pe = pg.SinPE(frequency=440, frame_rate=48000, amplitude=0.5)
cropped = sin_pe.crop(pg.Extent(0, 48000 * 2))  # 2 seconds

# Render to file
pg.FtsTransport(cropped).play()  # Fast offline rendering
```

### Interactive GUI Player

```python
# Using the GUI player (requires working Tkinter)
src = pg.WavReaderPE("samples/music/your_file.wav")
src.pygplay('Window Title')  # Opens interactive player window
```

## Directory Structure

After installation, your pygmu directory should look like:

```
pygmu/
├── .venv/                  # Virtual environment
├── pygmu/                  # Core library
│   ├── pygmu.py           # Main module
│   ├── *.py               # Processing elements
├── examples/              # Example scripts
├── pieces/                # Complex compositions
├── samples/               # Audio samples
├── user_files/            # Generated output
│   └── renders/           # Rendered audio files
├── vault/                 # GUI assets (auto-generated)
│   └── images/            # Player icons
├── requirements.txt       # Dependencies
└── README_UV.md          # This file
```

## Troubleshooting

### Common Issues and Solutions

1. **Frame Rate Errors**:
   ```
   pyg_exceptions.FrameRateMismatch: frame rate must be specified
   ```
   **Solution**: Ensure all ArrayPE objects specify frame_rate:
   ```python
   # Wrong
   return pg.ArrayPE(audio_data)
   
   # Correct
   return pg.ArrayPE(audio_data, frame_rate=sample_rate)
   ```

2. **Tkinter/GUI Issues**:
   ```
   TclError: Can't find a usable init.tcl
   ```
   **Solution**: Use homebrew Python with proper Tkinter:
   ```bash
   brew install python@3.13 python-tk@3.13
   uv venv --python /opt/homebrew/bin/python3.13 .venv
   ```

3. **Performance Issues**:
   - Large delay counts (e.g., `delays(src, 0.7, 18, 0.76)`) can cause exponential complexity
   - Use fewer delays (4-6 instead of 18+)
   - Avoid large `reverse()` operations on long audio segments

4. **Missing Audio Files**:
   ```bash
   # Create necessary directories
   mkdir -p user_files/renders
   mkdir -p vault/images
   ```

### Environment Debugging

Check your environment setup:

```bash
# Verify Python and packages
source .venv/bin/activate
python -c "
import sys
print('Python:', sys.version)

import tkinter as tk
print('Tkinter version:', tk.TkVersion)

import pygmu as pg
print('PygPlayer available:', hasattr(pg, 'PygPlayer'))

import numpy, soundfile, bokeh
print('All packages imported successfully')
"
```

## Performance Tips

1. **Use FtsTransport for offline rendering**:
   ```python
   # Fast offline rendering (no real-time playback)
   pg.FtsTransport(your_pe).play()
   ```

2. **Optimize complex processing chains**:
   ```python
   # Instead of many delays
   delays(src, 0.7, 18, 0.76)  # Creates 17 delayed copies!
   
   # Use fewer delays
   delays(src, 0.7, 4, 0.76)   # More manageable
   ```

3. **Monitor processing complexity**:
   - Check the frame duration output: `file duration: 28.48`
   - Progress should advance steadily, not hang at low percentages

## Development Workflow

### Running Tests
```bash
source .venv/bin/activate
cd pygmu
python -m unittest discover -f -s tests
```

### Profiling Performance
```bash
python -m cProfile -o profile.txt examples/your_piece.py
```

### Adding New Dependencies
```bash
uv pip install package_name
uv pip freeze > requirements.txt
```

## Key Differences from Original Setup

1. **Package Manager**: Uses `uv` instead of `pipenv` for faster dependency management
2. **Python Version**: Explicitly uses Homebrew Python 3.13 with proper Tkinter support
3. **Environment**: Creates `.venv` directory instead of global pipenv environment
4. **Dependencies**: Includes `bokeh` which is required but missing from requirements.txt
5. **GUI Support**: Properly configured Tkinter with placeholder icons

## Additional Resources

- **Original README**: See `README.md` for core pygmu concepts and API documentation
- **Examples**: Explore `examples/` directory for usage patterns
- **API Documentation**: See `API.md` for complete function reference

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your environment matches the installation steps
3. Test with simple examples before complex pieces
4. Consider performance limitations with complex processing chains

The setup has been tested and debugged to work on macOS with Apple Silicon. Adjustments may be needed for other platforms.