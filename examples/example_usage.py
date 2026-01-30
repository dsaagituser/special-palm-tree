#!/usr/bin/env python3
"""
Example usage of the video analysis and template generation system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from video_analyzer import (
    VideoAnalyzer,
    VideoCompositor,
    VideoTemplate
)


def example_analyze_video():
    """Example: Analyze a video and generate a template"""
    print("Example 1: Analyzing a video")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = VideoAnalyzer(motion_threshold=25.0)
    
    # Analyze video (you need to provide an actual video file)
    video_path = "example_input.mp4"
    
    print(f"Analyzing video: {video_path}")
    print("Note: You need to provide an actual video file for this to work")
    
    try:
        template = analyzer.analyze_video(video_path)
        
        print(f"\nAnalysis Results:")
        print(f"  Total duration: {template.total_duration:.2f} seconds")
        print(f"  FPS: {template.fps}")
        print(f"  Resolution: {template.width}x{template.height}")
        print(f"  Total segments: {len(template.segments)}")
        print(f"  Images needed: {template.num_images}")
        print(f"  Videos needed: {template.num_videos}")
        
        print("\nSegment breakdown:")
        for i, seg in enumerate(template.segments):
            print(f"  Segment {seg.segment_id}: {seg.segment_type} "
                  f"({seg.duration:.2f}s)")
        
        # Save template
        template.to_json("example_template.json")
        print("\nTemplate saved to: example_template.json")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to provide a valid video file")
    
    print()


def example_apply_template():
    """Example: Apply a template to new content"""
    print("Example 2: Applying a template to new content")
    print("=" * 80)
    
    try:
        # Load template
        template = VideoTemplate.from_json("example_template.json")
        
        print(f"Loaded template:")
        print(f"  Needs {template.num_images} images")
        print(f"  Needs {template.num_videos} videos")
        
        # Create assets mapping
        # In a real scenario, users would provide their own images and videos
        assets = {}
        for seg in template.segments:
            if seg.segment_type == 'image':
                assets[seg.segment_id] = f"user_image_{seg.segment_id}.jpg"
            else:
                assets[seg.segment_id] = f"user_video_{seg.segment_id}.mp4"
        
        print("\nAsset mapping:")
        for seg_id, path in assets.items():
            print(f"  Segment {seg_id}: {path}")
        
        # Apply template
        compositor = VideoCompositor(template)
        output_path = "example_output.mp4"
        
        print(f"\nCreating video: {output_path}")
        print("Note: You need to provide actual asset files for this to work")
        
        success = compositor.compose_video(assets, output_path)
        
        if success:
            print(f"Success! Video created: {output_path}")
        else:
            print("Failed to create video")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the template file exists and asset files are available")
    
    print()


def example_workflow():
    """Example: Complete workflow"""
    print("Example 3: Complete Workflow")
    print("=" * 80)
    print("""
Complete workflow for using the video analysis system:

1. Analyze a reference video:
   python src/cli.py analyze reference.mp4 -o template.json
   
2. View the template to see what assets are needed:
   python src/cli.py info template.json
   
   This will show you:
   - How many images are needed
   - How many videos are needed
   - Duration of each segment
   
3. Prepare your assets:
   - Collect images for each image segment
   - Collect videos for each video segment
   
4. Create an assets mapping file (assets.json):
   {
     "0": "my_image_1.jpg",
     "1": "my_video_1.mp4",
     "2": "my_image_2.jpg",
     "3": "my_video_2.mp4"
   }
   
5. Apply the template to your assets:
   python src/cli.py apply template.json -o output.mp4 -f assets.json
   
   Or use command line:
   python src/cli.py apply template.json -o output.mp4 \\
     -a 0:my_image_1.jpg 1:my_video_1.mp4 2:my_image_2.jpg 3:my_video_2.mp4

6. Your output video will have the same structure and timing as the reference,
   but with your content!
""")


def main():
    print("\n" + "=" * 80)
    print("Video Analysis and Template Generation - Examples")
    print("=" * 80 + "\n")
    
    example_workflow()
    
    print("\nTo run the actual examples (with video files):")
    print("  example_analyze_video()")
    print("  example_apply_template()")
    print()


if __name__ == '__main__':
    main()
