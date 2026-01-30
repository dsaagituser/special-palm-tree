#!/usr/bin/env python3
"""
Command-line interface for video analysis and template generation
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from video_analyzer import (
    analyze_and_generate_template,
    apply_template,
    VideoTemplate
)


def cmd_analyze(args):
    """Analyze a video and generate a template"""
    try:
        template = analyze_and_generate_template(
            args.input,
            args.output,
            motion_threshold=args.threshold
        )
        
        # Print segment details if verbose
        if args.verbose:
            print("\nSegment Details:")
            print("-" * 80)
            for seg in template.segments:
                print(f"Segment {seg.segment_id}:")
                print(f"  Type: {seg.segment_type}")
                print(f"  Duration: {seg.duration:.2f}s")
                print(f"  Time: {seg.start_time:.2f}s - {seg.end_time:.2f}s")
                print(f"  Frames: {seg.frame_count}")
                print()
        
        return 0
    except Exception as e:
        print(f"Error analyzing video: {e}", file=sys.stderr)
        return 1


def cmd_info(args):
    """Display information about a template"""
    try:
        template = VideoTemplate.from_json(args.template)
        
        print("Template Information")
        print("=" * 80)
        print(f"Duration: {template.total_duration:.2f} seconds")
        print(f"FPS: {template.fps}")
        print(f"Resolution: {template.width}x{template.height}")
        print(f"Total segments: {len(template.segments)}")
        print(f"Images needed: {template.num_images}")
        print(f"Videos needed: {template.num_videos}")
        print()
        
        print("Segments:")
        print("-" * 80)
        for seg in template.segments:
            print(f"Segment {seg.segment_id}: {seg.segment_type} "
                  f"({seg.duration:.2f}s, {seg.start_time:.2f}s-{seg.end_time:.2f}s)")
        
        return 0
    except Exception as e:
        print(f"Error reading template: {e}", file=sys.stderr)
        return 1


def cmd_apply(args):
    """Apply a template to user assets"""
    try:
        # Parse assets from command line or file
        assets = {}
        
        if args.assets_file and args.assets:
            print("Warning: Both --assets and --assets-file provided, using --assets-file")
        
        if args.assets_file:
            with open(args.assets_file, 'r') as f:
                assets_data = json.load(f)
                assets = {int(k): v for k, v in assets_data.items()}
        elif args.assets:
            # Parse from command line: segment_id:path format
            for asset_spec in args.assets:
                if ':' not in asset_spec:
                    print(f"Error: Invalid asset specification '{asset_spec}'. Expected format: segment_id:path", file=sys.stderr)
                    return 1
                seg_id, path = asset_spec.split(':', 1)
                try:
                    assets[int(seg_id)] = path
                except ValueError:
                    print(f"Error: Invalid segment ID in '{asset_spec}'. Segment ID must be an integer.", file=sys.stderr)
                    return 1
        else:
            print("Error: Must provide either --assets or --assets-file", file=sys.stderr)
            return 1
        
        success = apply_template(args.template, assets, args.output)
        return 0 if success else 1
        
    except Exception as e:
        print(f"Error applying template: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Video Analysis and Template Generation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a video and create a template
  %(prog)s analyze input.mp4 -o template.json
  
  # View template information
  %(prog)s info template.json
  
  # Apply template to new assets
  %(prog)s apply template.json -o output.mp4 -a 0:image1.jpg 1:video1.mp4
  
  # Apply template using assets file
  %(prog)s apply template.json -o output.mp4 -f assets.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a video and generate a template'
    )
    analyze_parser.add_argument(
        'input',
        help='Input video file path'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output template JSON file path'
    )
    analyze_parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=25.0,
        help='Motion detection threshold (default: 25.0)'
    )
    analyze_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed segment information'
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Display template information'
    )
    info_parser.add_argument(
        'template',
        help='Template JSON file path'
    )
    info_parser.set_defaults(func=cmd_info)
    
    # Apply command
    apply_parser = subparsers.add_parser(
        'apply',
        help='Apply template to user assets'
    )
    apply_parser.add_argument(
        'template',
        help='Template JSON file path'
    )
    apply_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output video file path'
    )
    
    # Create mutually exclusive group for assets
    assets_group = apply_parser.add_mutually_exclusive_group()
    assets_group.add_argument(
        '-a', '--assets',
        nargs='+',
        help='Assets in format segment_id:path (e.g., 0:image.jpg 1:video.mp4)'
    )
    assets_group.add_argument(
        '-f', '--assets-file',
        help='JSON file containing assets mapping'
    )
    apply_parser.set_defaults(func=cmd_apply)
    
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
