"""
Video Analysis and Template Generation System

This module provides functionality to analyze videos and generate templates
that can be used to apply the same editing style to different content.
"""

import cv2
import numpy as np
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class VideoSegment:
    """Represents a segment in the video"""
    segment_id: int
    start_time: float
    end_time: float
    duration: float
    segment_type: str  # 'image' or 'video'
    frame_count: int
    
    def to_dict(self):
        return asdict(self)


@dataclass
class VideoTemplate:
    """Template representing the structure of a video"""
    total_duration: float
    fps: float
    width: int
    height: int
    segments: List[VideoSegment]
    num_images: int
    num_videos: int
    
    def to_dict(self):
        return {
            'total_duration': self.total_duration,
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'segments': [seg.to_dict() for seg in self.segments],
            'num_images': self.num_images,
            'num_videos': self.num_videos
        }
    
    def to_json(self, filepath: str):
        """Save template to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_json(cls, filepath: str) -> 'VideoTemplate':
        """Load template from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        segments = [VideoSegment(**seg) for seg in data['segments']]
        data['segments'] = segments
        return cls(**data)


class VideoAnalyzer:
    """Analyzes videos to extract structure and timing information"""
    
    def __init__(self, motion_threshold: float = 25.0):
        """
        Initialize VideoAnalyzer
        
        Args:
            motion_threshold: Threshold for detecting motion between frames (mean pixel difference)
        """
        self.motion_threshold = motion_threshold
    
    def analyze_video(self, video_path: str, sample_rate: int = 5) -> VideoTemplate:
        """
        Analyze a video and generate a template
        
        Args:
            video_path: Path to the input video file
            sample_rate: Sample every Nth frame for analysis
            
        Returns:
            VideoTemplate containing the video structure
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            cap.release()
            raise ValueError(f"Invalid FPS ({fps}) in video file: {video_path}")
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_duration = frame_count / fps
        
        # Detect segments based on motion analysis
        segments = self._detect_segments(cap, fps, sample_rate)
        
        cap.release()
        
        # Count image vs video segments
        num_images = sum(1 for seg in segments if seg.segment_type == 'image')
        num_videos = sum(1 for seg in segments if seg.segment_type == 'video')
        
        return VideoTemplate(
            total_duration=total_duration,
            fps=fps,
            width=width,
            height=height,
            segments=segments,
            num_images=num_images,
            num_videos=num_videos
        )
    
    def _detect_segments(self, cap: cv2.VideoCapture, fps: float, sample_rate: int) -> List[VideoSegment]:
        """
        Detect segments in the video based on motion analysis
        
        Args:
            cap: OpenCV VideoCapture object
            fps: Frames per second
            sample_rate: Sample every Nth frame
            
        Returns:
            List of VideoSegment objects
        """
        segments = []
        prev_frame = None
        segment_start_frame = 0
        current_segment_motion = []
        frame_idx = 0
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample frames for efficiency
            if frame_idx % sample_rate == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(prev_frame, gray)
                    motion_score = np.mean(diff)
                    current_segment_motion.append(motion_score)
                
                prev_frame = gray
            
            frame_idx += 1
        
        # Analyze motion patterns to determine segment types
        if current_segment_motion:
            segments = self._segment_by_motion(current_segment_motion, fps, sample_rate, frame_idx)
        
        # If no segments detected, treat entire video as one segment
        if not segments:
            duration = frame_idx / fps if fps > 0 else 0
            segments.append(VideoSegment(
                segment_id=0,
                start_time=0.0,
                end_time=duration,
                duration=duration,
                segment_type='video',
                frame_count=frame_idx
            ))
        
        return segments
    
    def _segment_by_motion(self, motion_scores: List[float], fps: float, 
                          sample_rate: int, total_frames: int) -> List[VideoSegment]:
        """
        Create segments based on motion analysis
        
        Args:
            motion_scores: List of motion scores for sampled frames
            fps: Frames per second
            sample_rate: Sample rate used
            total_frames: Total number of frames
            
        Returns:
            List of VideoSegment objects
        """
        segments = []
        segment_id = 0
        
        # Simple segmentation: group consecutive frames with similar motion characteristics
        window_size = 10  # Analyze motion in windows
        i = 0
        
        while i < len(motion_scores):
            window_end = min(i + window_size, len(motion_scores))
            window_motion = motion_scores[i:window_end]
            avg_motion = np.mean(window_motion)
            
            # Determine segment type based on motion
            segment_type = 'image' if avg_motion < self.motion_threshold else 'video'
            
            # Find the extent of this segment type
            segment_start = i
            while i < len(motion_scores):
                if i + window_size < len(motion_scores):
                    next_window = motion_scores[i:i + window_size]
                    next_avg_motion = np.mean(next_window)
                    next_type = 'image' if next_avg_motion < self.motion_threshold else 'video'
                    
                    if next_type != segment_type:
                        break
                    i += 1
                else:
                    # Reached end of motion scores
                    i = len(motion_scores)
                    break
            
            # Calculate segment timing
            start_frame = segment_start * sample_rate
            end_frame = min(i * sample_rate, total_frames)
            start_time = start_frame / fps if fps > 0 else 0
            end_time = end_frame / fps if fps > 0 else 0
            duration = end_time - start_time
            frame_count = end_frame - start_frame
            
            segments.append(VideoSegment(
                segment_id=segment_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                segment_type=segment_type,
                frame_count=frame_count
            ))
            
            segment_id += 1
        
        return segments


class VideoCompositor:
    """Applies a template to user-provided images and videos"""
    
    def __init__(self, template: VideoTemplate):
        """
        Initialize VideoCompositor
        
        Args:
            template: VideoTemplate to apply
        """
        self.template = template
    
    def compose_video(self, assets: Dict[int, str], output_path: str) -> bool:
        """
        Create a new video by applying the template to user assets
        
        Args:
            assets: Dictionary mapping segment_id to file path
            output_path: Path for the output video file
            
        Returns:
            True if successful, False otherwise
        """
        # Validate assets
        if not self._validate_assets(assets):
            return False
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path,
            fourcc,
            self.template.fps,
            (self.template.width, self.template.height)
        )
        
        if not out.isOpened():
            raise ValueError(f"Cannot create output video: {output_path}")
        
        try:
            # Process each segment
            for segment in self.template.segments:
                asset_path = assets.get(segment.segment_id)
                if not asset_path:
                    print(f"Warning: No asset provided for segment {segment.segment_id}")
                    continue
                
                self._add_segment_to_video(out, asset_path, segment)
        finally:
            out.release()
        
        return True
    
    def _validate_assets(self, assets: Dict[int, str]) -> bool:
        """Validate that required assets are provided and accessible"""
        from pathlib import Path
        
        required_segments = {seg.segment_id for seg in self.template.segments}
        provided_segments = set(assets.keys())
        
        missing = required_segments - provided_segments
        if missing:
            print(f"Warning: Missing assets for segments: {missing}")
        
        # Check that provided asset files exist
        for seg_id, asset_path in assets.items():
            if not Path(asset_path).exists():
                print(f"Warning: Asset file does not exist: {asset_path} (segment {seg_id})")
        
        return True
    
    def _add_segment_to_video(self, out: cv2.VideoWriter, asset_path: str, 
                             segment: VideoSegment):
        """
        Add a segment to the output video
        
        Args:
            out: VideoWriter object
            asset_path: Path to the asset file
            segment: VideoSegment specification
        """
        if segment.segment_type == 'image':
            # Read image and repeat for duration
            img = cv2.imread(asset_path)
            if img is None:
                print(f"Warning: Cannot read image: {asset_path}")
                return
            
            # Resize to match template dimensions
            img = cv2.resize(img, (self.template.width, self.template.height))
            
            # Calculate number of frames
            num_frames = int(segment.duration * self.template.fps)
            
            # Write image frames
            for _ in range(num_frames):
                out.write(img)
        
        else:  # video segment
            # Read video and extract frames for the duration
            cap = cv2.VideoCapture(asset_path)
            if not cap.isOpened():
                print(f"Warning: Cannot open video: {asset_path}")
                return
            
            try:
                target_frames = int(segment.duration * self.template.fps)
                source_fps = cap.get(cv2.CAP_PROP_FPS)
                source_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Calculate frame sampling to match duration
                if source_fps > 0 and source_frame_count > 0:
                    frame_step = source_frame_count / target_frames if target_frames > 0 else 1
                else:
                    frame_step = 1
                
                frame_idx = 0
                written_frames = 0
                
                while written_frames < target_frames:
                    target_frame_idx = int(frame_idx * frame_step)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_idx)
                    
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Resize to match template dimensions
                    frame = cv2.resize(frame, (self.template.width, self.template.height))
                    out.write(frame)
                    
                    frame_idx += 1
                    written_frames += 1
            finally:
                cap.release()


def analyze_and_generate_template(video_path: str, output_template_path: str, 
                                  motion_threshold: float = 25.0) -> VideoTemplate:
    """
    Convenience function to analyze a video and save the template
    
    Args:
        video_path: Path to input video
        output_template_path: Path to save the template JSON
        motion_threshold: Threshold for motion detection
        
    Returns:
        VideoTemplate object
    """
    analyzer = VideoAnalyzer(motion_threshold=motion_threshold)
    template = analyzer.analyze_video(video_path)
    template.to_json(output_template_path)
    
    print(f"Video analysis complete!")
    print(f"Total duration: {template.total_duration:.2f} seconds")
    print(f"Segments detected: {len(template.segments)}")
    print(f"Images needed: {template.num_images}")
    print(f"Videos needed: {template.num_videos}")
    print(f"\nTemplate saved to: {output_template_path}")
    
    return template


def apply_template(template_path: str, assets: Dict[int, str], output_path: str) -> bool:
    """
    Convenience function to apply a template to user assets
    
    Args:
        template_path: Path to template JSON file
        assets: Dictionary mapping segment_id to asset file path
        output_path: Path for output video
        
    Returns:
        True if successful
    """
    template = VideoTemplate.from_json(template_path)
    compositor = VideoCompositor(template)
    
    print(f"Applying template to {len(assets)} assets...")
    success = compositor.compose_video(assets, output_path)
    
    if success:
        print(f"Video created successfully: {output_path}")
    else:
        print("Failed to create video")
    
    return success
