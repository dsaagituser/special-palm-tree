# Video Analysis and Template Generation System

A powerful Python tool that analyzes video structure and generates reusable templates. Given an input video, it automatically identifies the number of images and videos needed, their durations, and alignment, allowing you to recreate the same editing style with your own content.

## Features

- **Automatic Video Analysis**: Analyzes input videos to detect segments (static images vs. video clips)
- **Motion Detection**: Uses computer vision to distinguish between static and dynamic content
- **Template Generation**: Creates JSON templates that describe video structure and timing
- **Content Replacement**: Apply templates to your own images and videos
- **Flexible CLI**: Easy-to-use command-line interface for all operations
- **Preserves Timing**: Maintains exact durations and transitions from the original video

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dsaagituser/special-palm-tree.git
cd special-palm-tree
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Analyze a Video

Analyze an input video to create a template:

```bash
python src/cli.py analyze reference_video.mp4 -o template.json
```

This will output:
- Total video duration
- Number of segments detected
- Number of images needed
- Number of videos needed

### 2. View Template Information

Inspect the generated template:

```bash
python src/cli.py info template.json
```

This shows detailed information about each segment, including:
- Segment type (image or video)
- Duration
- Time range
- Frame count

### 3. Apply Template to Your Content

Replace the original content with your own images and videos:

```bash
python src/cli.py apply template.json -o output.mp4 \
  -a 0:my_image_1.jpg 1:my_video_1.mp4 2:my_image_2.jpg
```

Or use a JSON file to specify assets:

```bash
python src/cli.py apply template.json -o output.mp4 -f assets.json
```

Example `assets.json`:
```json
{
  "0": "path/to/my_image_1.jpg",
  "1": "path/to/my_video_1.mp4",
  "2": "path/to/my_image_2.jpg",
  "3": "path/to/my_video_2.mp4"
}
```

## Usage

### Command Line Interface

The CLI provides three main commands:

#### analyze
Analyze a video and generate a template:
```bash
python src/cli.py analyze INPUT_VIDEO -o OUTPUT_TEMPLATE [OPTIONS]

Options:
  -t, --threshold FLOAT    Motion detection threshold (default: 25.0)
  -v, --verbose           Show detailed segment information
```

#### info
Display information about a template:
```bash
python src/cli.py info TEMPLATE_FILE
```

#### apply
Apply a template to user assets:
```bash
python src/cli.py apply TEMPLATE_FILE -o OUTPUT_VIDEO [OPTIONS]

Options:
  -a, --assets ASSETS...   Assets in format segment_id:path
  -f, --assets-file FILE   JSON file containing assets mapping
```

### Python API

You can also use the system programmatically:

```python
from src.video_analyzer import (
    VideoAnalyzer,
    VideoCompositor,
    VideoTemplate
)

# Analyze a video
analyzer = VideoAnalyzer(motion_threshold=25.0)
template = analyzer.analyze_video("input.mp4")
template.to_json("template.json")

# Apply template to new content
template = VideoTemplate.from_json("template.json")
compositor = VideoCompositor(template)
assets = {
    0: "my_image_1.jpg",
    1: "my_video_1.mp4",
    2: "my_image_2.jpg"
}
compositor.compose_video(assets, "output.mp4")
```

## How It Works

### 1. Video Analysis

The system uses computer vision (OpenCV) to analyze the input video:

- **Frame Sampling**: Samples frames at regular intervals for efficient processing
- **Motion Detection**: Compares consecutive frames to detect motion
- **Segmentation**: Groups frames with similar motion characteristics
- **Classification**: Identifies segments as either static images or video clips

### 2. Template Structure

Templates are JSON files that describe the video structure:

```json
{
  "total_duration": 30.5,
  "fps": 30.0,
  "width": 1920,
  "height": 1080,
  "num_images": 3,
  "num_videos": 2,
  "segments": [
    {
      "segment_id": 0,
      "start_time": 0.0,
      "end_time": 5.0,
      "duration": 5.0,
      "segment_type": "image",
      "frame_count": 150
    },
    {
      "segment_id": 1,
      "start_time": 5.0,
      "end_time": 15.0,
      "duration": 10.0,
      "segment_type": "video",
      "frame_count": 300
    }
  ]
}
```

### 3. Template Application

When applying a template:

- **Images**: Each image is displayed for the specified duration
- **Videos**: Videos are resampled to match the required duration
- **Resolution**: All content is resized to match the template dimensions
- **Timing**: Exact timing from the original video is preserved

## Configuration

### Motion Threshold

The motion threshold determines how the system distinguishes between static and dynamic content:

- **Lower values** (e.g., 10-20): More sensitive, may classify small movements as video
- **Default value** (25): Balanced sensitivity for most use cases
- **Higher values** (e.g., 30-50): Less sensitive, requires more motion to classify as video

Adjust based on your content:
```bash
python src/cli.py analyze input.mp4 -o template.json -t 20.0
```

## Examples

See the `examples/` directory for detailed usage examples:

```bash
python examples/example_usage.py
```

## Testing

Run the test suite:

```bash
python tests/test_video_analyzer.py
```

## Use Cases

- **Video Editing Automation**: Quickly recreate the same video structure with different content
- **Template-Based Production**: Create video templates for consistent branding
- **Content Personalization**: Generate personalized videos from a master template
- **Batch Processing**: Apply the same editing style to multiple sets of content
- **Educational Content**: Create consistent lesson formats with different materials

## Requirements

- Python 3.7+
- OpenCV (opencv-python)
- NumPy

## Project Structure

```
special-palm-tree/
├── src/
│   ├── video_analyzer.py    # Core video analysis and composition logic
│   └── cli.py                # Command-line interface
├── tests/
│   └── test_video_analyzer.py  # Unit tests
├── examples/
│   └── example_usage.py      # Usage examples
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

## License

This project is open source and available for use and modification.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Troubleshooting

### "Cannot open video file"
- Ensure the video file path is correct
- Check that the video format is supported by OpenCV
- Verify the video file is not corrupted

### "Cannot read image/video"
- Verify asset file paths are correct
- Ensure image/video formats are supported
- Check file permissions

### Output video quality issues
- Ensure input assets match or exceed template resolution
- Use high-quality source materials
- Consider adjusting video codec settings in the code

## Future Enhancements

Potential improvements for future versions:
- Support for audio tracks
- Transition effects between segments
- Advanced motion detection algorithms
- GPU acceleration for faster processing
- Support for multiple video formats and codecs
- Web interface for easier use