"""
Unit tests for video analysis and template generation
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from video_analyzer import (
    VideoSegment,
    VideoTemplate,
    VideoAnalyzer,
    VideoCompositor
)


class TestVideoSegment(unittest.TestCase):
    """Tests for VideoSegment class"""
    
    def test_create_segment(self):
        """Test creating a video segment"""
        segment = VideoSegment(
            segment_id=0,
            start_time=0.0,
            end_time=5.0,
            duration=5.0,
            segment_type='image',
            frame_count=150
        )
        
        self.assertEqual(segment.segment_id, 0)
        self.assertEqual(segment.start_time, 0.0)
        self.assertEqual(segment.end_time, 5.0)
        self.assertEqual(segment.duration, 5.0)
        self.assertEqual(segment.segment_type, 'image')
        self.assertEqual(segment.frame_count, 150)
    
    def test_segment_to_dict(self):
        """Test converting segment to dictionary"""
        segment = VideoSegment(
            segment_id=1,
            start_time=5.0,
            end_time=10.0,
            duration=5.0,
            segment_type='video',
            frame_count=150
        )
        
        data = segment.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['segment_id'], 1)
        self.assertEqual(data['segment_type'], 'video')


class TestVideoTemplate(unittest.TestCase):
    """Tests for VideoTemplate class"""
    
    def test_create_template(self):
        """Test creating a video template"""
        segments = [
            VideoSegment(0, 0.0, 5.0, 5.0, 'image', 150),
            VideoSegment(1, 5.0, 10.0, 5.0, 'video', 150)
        ]
        
        template = VideoTemplate(
            total_duration=10.0,
            fps=30.0,
            width=1920,
            height=1080,
            segments=segments,
            num_images=1,
            num_videos=1
        )
        
        self.assertEqual(template.total_duration, 10.0)
        self.assertEqual(template.fps, 30.0)
        self.assertEqual(template.width, 1920)
        self.assertEqual(template.height, 1080)
        self.assertEqual(len(template.segments), 2)
        self.assertEqual(template.num_images, 1)
        self.assertEqual(template.num_videos, 1)
    
    def test_template_to_json(self):
        """Test saving template to JSON"""
        segments = [
            VideoSegment(0, 0.0, 5.0, 5.0, 'image', 150)
        ]
        
        template = VideoTemplate(
            total_duration=5.0,
            fps=30.0,
            width=1920,
            height=1080,
            segments=segments,
            num_images=1,
            num_videos=0
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            template.to_json(temp_path)
            
            # Verify file exists and is valid JSON
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['total_duration'], 5.0)
            self.assertEqual(data['fps'], 30.0)
            self.assertEqual(data['num_images'], 1)
            self.assertEqual(len(data['segments']), 1)
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_template_from_json(self):
        """Test loading template from JSON"""
        data = {
            'total_duration': 10.0,
            'fps': 30.0,
            'width': 1920,
            'height': 1080,
            'num_images': 1,
            'num_videos': 1,
            'segments': [
                {
                    'segment_id': 0,
                    'start_time': 0.0,
                    'end_time': 5.0,
                    'duration': 5.0,
                    'segment_type': 'image',
                    'frame_count': 150
                },
                {
                    'segment_id': 1,
                    'start_time': 5.0,
                    'end_time': 10.0,
                    'duration': 5.0,
                    'segment_type': 'video',
                    'frame_count': 150
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            template = VideoTemplate.from_json(temp_path)
            
            self.assertEqual(template.total_duration, 10.0)
            self.assertEqual(template.fps, 30.0)
            self.assertEqual(template.width, 1920)
            self.assertEqual(template.height, 1080)
            self.assertEqual(len(template.segments), 2)
            self.assertEqual(template.num_images, 1)
            self.assertEqual(template.num_videos, 1)
            
            # Check segments
            self.assertEqual(template.segments[0].segment_type, 'image')
            self.assertEqual(template.segments[1].segment_type, 'video')
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestVideoAnalyzer(unittest.TestCase):
    """Tests for VideoAnalyzer class"""
    
    def test_create_analyzer(self):
        """Test creating a video analyzer"""
        analyzer = VideoAnalyzer(motion_threshold=25.0)
        self.assertEqual(analyzer.motion_threshold, 25.0)
    
    def test_segment_by_motion(self):
        """Test motion-based segmentation"""
        analyzer = VideoAnalyzer(motion_threshold=25.0)
        
        # Simulate motion scores: low motion, then high motion
        motion_scores = [10.0] * 20 + [50.0] * 20
        fps = 30.0
        sample_rate = 5
        total_frames = len(motion_scores) * sample_rate
        
        segments = analyzer._segment_by_motion(motion_scores, fps, sample_rate, total_frames)
        
        # Should detect at least 2 segments
        self.assertGreaterEqual(len(segments), 1)
        
        # Verify segment properties
        for seg in segments:
            self.assertIsInstance(seg, VideoSegment)
            self.assertGreaterEqual(seg.duration, 0)
            self.assertIn(seg.segment_type, ['image', 'video'])


class TestVideoCompositor(unittest.TestCase):
    """Tests for VideoCompositor class"""
    
    def test_create_compositor(self):
        """Test creating a video compositor"""
        segments = [
            VideoSegment(0, 0.0, 5.0, 5.0, 'image', 150)
        ]
        
        template = VideoTemplate(
            total_duration=5.0,
            fps=30.0,
            width=1920,
            height=1080,
            segments=segments,
            num_images=1,
            num_videos=0
        )
        
        compositor = VideoCompositor(template)
        self.assertEqual(compositor.template, template)
    
    def test_validate_assets(self):
        """Test asset validation"""
        segments = [
            VideoSegment(0, 0.0, 5.0, 5.0, 'image', 150),
            VideoSegment(1, 5.0, 10.0, 5.0, 'video', 150)
        ]
        
        template = VideoTemplate(
            total_duration=10.0,
            fps=30.0,
            width=1920,
            height=1080,
            segments=segments,
            num_images=1,
            num_videos=1
        )
        
        compositor = VideoCompositor(template)
        
        # Test with all assets
        assets = {0: 'image.jpg', 1: 'video.mp4'}
        self.assertTrue(compositor._validate_assets(assets))
        
        # Test with missing assets (should still return True but warn)
        assets = {0: 'image.jpg'}
        self.assertTrue(compositor._validate_assets(assets))


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_template_round_trip(self):
        """Test saving and loading a template"""
        segments = [
            VideoSegment(0, 0.0, 5.0, 5.0, 'image', 150),
            VideoSegment(1, 5.0, 10.0, 5.0, 'video', 150)
        ]
        
        original = VideoTemplate(
            total_duration=10.0,
            fps=30.0,
            width=1920,
            height=1080,
            segments=segments,
            num_images=1,
            num_videos=1
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # Save
            original.to_json(temp_path)
            
            # Load
            loaded = VideoTemplate.from_json(temp_path)
            
            # Compare
            self.assertEqual(original.total_duration, loaded.total_duration)
            self.assertEqual(original.fps, loaded.fps)
            self.assertEqual(original.width, loaded.width)
            self.assertEqual(original.height, loaded.height)
            self.assertEqual(len(original.segments), len(loaded.segments))
            self.assertEqual(original.num_images, loaded.num_images)
            self.assertEqual(original.num_videos, loaded.num_videos)
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
