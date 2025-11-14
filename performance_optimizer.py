"""
Performance Optimizer & Profiler
Advanced performance monitoring and optimization for 60 FPS YouTube content creation.

Already at 60 FPS, but this module ensures:
- Consistent frame times (no stuttering)
- Efficient memory usage
- Optimized OpenGL rendering
- Automatic performance tuning
- Bottleneck detection

This is CRITICAL for:
- Smooth animation preview
- Real-time multi-character scenes
- HD rendering performance
- Export speed optimization
"""

import time
import psutil
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

from OpenGL.GL import *


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

class PerformanceLevel(Enum):
    """Performance level presets."""
    LOW = "low"              # Below 30 FPS
    MEDIUM = "medium"        # 30-45 FPS
    HIGH = "high"            # 45-60 FPS
    EXCELLENT = "excellent"  # Solid 60 FPS
    MAXIMUM = "maximum"      # Above 60 FPS


@dataclass
class FrameStats:
    """Statistics for a single frame."""
    frame_number: int
    frame_time: float          # Total frame time (ms)
    render_time: float         # Rendering time (ms)
    update_time: float         # Update logic time (ms)
    fps: float                 # Calculated FPS
    memory_mb: float           # Memory usage (MB)
    gpu_memory_mb: float = 0.0 # GPU memory (if available)


@dataclass
class PerformanceReport:
    """
    Complete performance analysis report.
    """
    # Average metrics
    avg_fps: float
    avg_frame_time: float
    min_fps: float
    max_fps: float

    # Frame time analysis
    frame_time_std: float      # Standard deviation (consistency)
    dropped_frames: int        # Frames that took too long

    # Memory
    avg_memory_mb: float
    peak_memory_mb: float

    # Bottlenecks
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Performance level
    performance_level: PerformanceLevel = PerformanceLevel.HIGH


# ============================================================================
# PERFORMANCE PROFILER
# ============================================================================

class PerformanceProfiler:
    """
    Real-time performance monitoring and profiling.
    Tracks FPS, frame times, memory, and identifies bottlenecks.
    """

    def __init__(self, target_fps: int = 60, history_size: int = 300):
        """
        Initialize performance profiler.

        Args:
            target_fps: Target frame rate (default 60)
            history_size: Number of frames to keep in history
        """
        self.target_fps = target_fps
        self.target_frame_time = 1000.0 / target_fps  # ms

        # Frame history
        self.frame_stats: deque[FrameStats] = deque(maxlen=history_size)

        # Current frame tracking
        self.current_frame = 0
        self.frame_start_time = 0.0
        self.render_start_time = 0.0
        self.update_start_time = 0.0

        # Timing accumulators
        self.total_render_time = 0.0
        self.total_update_time = 0.0

        # System info
        self.process = psutil.Process()

        # Performance level
        self.current_performance_level = PerformanceLevel.EXCELLENT

        print(f"[OK] Performance profiler initialized (target: {target_fps} FPS)")

    # ========================================================================
    # FRAME TIMING
    # ========================================================================

    def begin_frame(self):
        """Mark the start of a frame."""
        self.frame_start_time = time.perf_counter()
        self.current_frame += 1

    def begin_update(self):
        """Mark the start of update phase."""
        self.update_start_time = time.perf_counter()

    def end_update(self):
        """Mark the end of update phase."""
        if self.update_start_time > 0:
            update_time = (time.perf_counter() - self.update_start_time) * 1000.0
            self.total_update_time += update_time

    def begin_render(self):
        """Mark the start of render phase."""
        self.render_start_time = time.perf_counter()

    def end_render(self):
        """Mark the end of render phase."""
        if self.render_start_time > 0:
            render_time = (time.perf_counter() - self.render_start_time) * 1000.0
            self.total_render_time += render_time

    def end_frame(self):
        """Mark the end of a frame and record stats."""
        if self.frame_start_time <= 0:
            return

        # Calculate frame time
        frame_time = (time.perf_counter() - self.frame_start_time) * 1000.0
        fps = 1000.0 / frame_time if frame_time > 0 else 0.0

        # Get memory usage
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB

        # Create frame stats
        stats = FrameStats(
            frame_number=self.current_frame,
            frame_time=frame_time,
            render_time=self.total_render_time,
            update_time=self.total_update_time,
            fps=fps,
            memory_mb=memory_mb
        )

        # Add to history
        self.frame_stats.append(stats)

        # Reset accumulators
        self.total_render_time = 0.0
        self.total_update_time = 0.0
        self.frame_start_time = 0.0

        # Update performance level
        self._update_performance_level(fps)

    def _update_performance_level(self, current_fps: float):
        """Update current performance level based on FPS."""
        if current_fps >= self.target_fps:
            self.current_performance_level = PerformanceLevel.EXCELLENT
        elif current_fps >= 45:
            self.current_performance_level = PerformanceLevel.HIGH
        elif current_fps >= 30:
            self.current_performance_level = PerformanceLevel.MEDIUM
        else:
            self.current_performance_level = PerformanceLevel.LOW

    # ========================================================================
    # ANALYSIS
    # ========================================================================

    def generate_report(self) -> PerformanceReport:
        """
        Generate comprehensive performance report.

        Returns:
            Performance analysis with recommendations
        """
        if not self.frame_stats:
            return PerformanceReport(
                avg_fps=0.0,
                avg_frame_time=0.0,
                min_fps=0.0,
                max_fps=0.0,
                frame_time_std=0.0,
                dropped_frames=0,
                avg_memory_mb=0.0,
                peak_memory_mb=0.0,
                performance_level=PerformanceLevel.LOW
            )

        # Calculate statistics
        fps_values = [stat.fps for stat in self.frame_stats]
        frame_times = [stat.frame_time for stat in self.frame_stats]
        memory_values = [stat.memory_mb for stat in self.frame_stats]

        avg_fps = np.mean(fps_values)
        min_fps = np.min(fps_values)
        max_fps = np.max(fps_values)
        avg_frame_time = np.mean(frame_times)
        frame_time_std = np.std(frame_times)

        avg_memory = np.mean(memory_values)
        peak_memory = np.max(memory_values)

        # Count dropped frames (frames that took too long)
        dropped_frames = sum(1 for ft in frame_times if ft > self.target_frame_time * 1.5)

        # Analyze bottlenecks
        bottlenecks = self._identify_bottlenecks()
        recommendations = self._generate_recommendations(avg_fps, frame_time_std, bottlenecks)

        # Determine performance level
        if avg_fps >= 60:
            perf_level = PerformanceLevel.EXCELLENT
        elif avg_fps >= 45:
            perf_level = PerformanceLevel.HIGH
        elif avg_fps >= 30:
            perf_level = PerformanceLevel.MEDIUM
        else:
            perf_level = PerformanceLevel.LOW

        return PerformanceReport(
            avg_fps=avg_fps,
            avg_frame_time=avg_frame_time,
            min_fps=min_fps,
            max_fps=max_fps,
            frame_time_std=frame_time_std,
            dropped_frames=dropped_frames,
            avg_memory_mb=avg_memory,
            peak_memory_mb=peak_memory,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            performance_level=perf_level
        )

    def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        if not self.frame_stats:
            return bottlenecks

        # Calculate average times
        avg_render_time = np.mean([stat.render_time for stat in self.frame_stats])
        avg_update_time = np.mean([stat.update_time for stat in self.frame_stats])

        # Check if rendering is the bottleneck
        if avg_render_time > self.target_frame_time * 0.6:
            bottlenecks.append("Rendering (consider reducing quality or resolution)")

        # Check if update logic is slow
        if avg_update_time > self.target_frame_time * 0.3:
            bottlenecks.append("Update logic (optimize skeleton/animation updates)")

        # Check for inconsistent frame times
        frame_times = [stat.frame_time for stat in self.frame_stats]
        if np.std(frame_times) > 5.0:
            bottlenecks.append("Inconsistent frame times (stuttering detected)")

        # Check memory usage
        peak_memory = max(stat.memory_mb for stat in self.frame_stats)
        if peak_memory > 1000:  # 1GB
            bottlenecks.append("High memory usage (consider optimization)")

        return bottlenecks

    def _generate_recommendations(
        self,
        avg_fps: float,
        frame_time_std: float,
        bottlenecks: List[str]
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # FPS-based recommendations
        if avg_fps < 30:
            recommendations.append("Performance is LOW - consider:")
            recommendations.append("  • Switch to Vector rendering mode")
            recommendations.append("  • Reduce number of characters in scene")
            recommendations.append("  • Close other applications")
        elif avg_fps < 45:
            recommendations.append("Performance is MEDIUM - consider:")
            recommendations.append("  • Use Vector mode for editing, HD for export only")
            recommendations.append("  • Limit active animations")
        elif avg_fps < 60:
            recommendations.append("Performance is GOOD - minor optimizations possible:")
            recommendations.append("  • Enable GPU acceleration if available")

        # Consistency recommendations
        if frame_time_std > 5.0:
            recommendations.append("Frame time inconsistency detected:")
            recommendations.append("  • Close background applications")
            recommendations.append("  • Disable Windows visual effects")

        # Memory recommendations
        if any("memory" in b.lower() for b in bottlenecks):
            recommendations.append("High memory usage detected:")
            recommendations.append("  • Clear unused animations")
            recommendations.append("  • Restart application periodically")

        # If performance is excellent
        if avg_fps >= 60 and not bottlenecks:
            recommendations.append("Performance is EXCELLENT!")
            recommendations.append("  • You can enable HD rendering for preview")
            recommendations.append("  • Add more characters if needed")

        return recommendations

    def get_current_fps(self) -> float:
        """Get current FPS (average of last 10 frames)."""
        if not self.frame_stats:
            return 0.0

        recent_frames = list(self.frame_stats)[-10:]
        return np.mean([stat.fps for stat in recent_frames])

    def get_current_frame_time(self) -> float:
        """Get current frame time in ms."""
        if not self.frame_stats:
            return 0.0

        return self.frame_stats[-1].frame_time

    def get_performance_level(self) -> PerformanceLevel:
        """Get current performance level."""
        return self.current_performance_level

    def print_report(self):
        """Print formatted performance report."""
        report = self.generate_report()

        print("\n" + "=" * 60)
        print("PERFORMANCE REPORT")
        print("=" * 60)

        print(f"\n📊 FPS Metrics:")
        print(f"  Average FPS: {report.avg_fps:.1f}")
        print(f"  Min FPS: {report.min_fps:.1f}")
        print(f"  Max FPS: {report.max_fps:.1f}")
        print(f"  Frame Time: {report.avg_frame_time:.2f} ms (target: {self.target_frame_time:.2f} ms)")
        print(f"  Consistency: {report.frame_time_std:.2f} ms std dev")
        print(f"  Dropped Frames: {report.dropped_frames}")

        print(f"\n💾 Memory:")
        print(f"  Average: {report.avg_memory_mb:.1f} MB")
        print(f"  Peak: {report.peak_memory_mb:.1f} MB")

        print(f"\n⚡ Performance Level: {report.performance_level.value.upper()}")

        if report.bottlenecks:
            print(f"\n[WARNING] Bottlenecks:")
            for bottleneck in report.bottlenecks:
                print(f"  • {bottleneck}")

        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  {rec}")

        print("=" * 60)


# ============================================================================
# AUTOMATIC OPTIMIZER
# ============================================================================

class AutoOptimizer:
    """
    Automatic performance optimization.
    Adjusts quality settings based on current performance.
    """

    def __init__(self, profiler: PerformanceProfiler):
        """
        Initialize auto optimizer.

        Args:
            profiler: Performance profiler to monitor
        """
        self.profiler = profiler
        self.optimization_callbacks: Dict[str, Callable] = {}

        # Optimization state
        self.current_quality_level = "high"
        self.auto_adjust_enabled = False

        print("[OK] Auto optimizer initialized")

    def enable_auto_adjust(self):
        """Enable automatic quality adjustment."""
        self.auto_adjust_enabled = True
        print("[OK] Auto quality adjustment enabled")

    def disable_auto_adjust(self):
        """Disable automatic quality adjustment."""
        self.auto_adjust_enabled = False
        print("[OK] Auto quality adjustment disabled")

    def register_optimization(self, name: str, callback: Callable):
        """
        Register optimization callback.

        Args:
            name: Optimization name
            callback: Function to call when optimization is triggered
        """
        self.optimization_callbacks[name] = callback

    def update(self):
        """Update optimizer (call every frame)."""
        if not self.auto_adjust_enabled:
            return

        # Get current performance level
        perf_level = self.profiler.get_performance_level()

        # Adjust quality based on performance
        if perf_level == PerformanceLevel.LOW:
            self._optimize_for_low_performance()
        elif perf_level == PerformanceLevel.MEDIUM:
            self._optimize_for_medium_performance()

    def _optimize_for_low_performance(self):
        """Apply optimizations for low performance."""
        if self.current_quality_level != "low":
            print("⚡ Auto-optimizing for LOW performance...")

            # Trigger callbacks
            if "reduce_quality" in self.optimization_callbacks:
                self.optimization_callbacks["reduce_quality"]()

            if "disable_effects" in self.optimization_callbacks:
                self.optimization_callbacks["disable_effects"]()

            self.current_quality_level = "low"

    def _optimize_for_medium_performance(self):
        """Apply optimizations for medium performance."""
        if self.current_quality_level == "high":
            print("⚡ Auto-optimizing for MEDIUM performance...")

            # Trigger callbacks
            if "reduce_quality" in self.optimization_callbacks:
                self.optimization_callbacks["reduce_quality"]()

            self.current_quality_level = "medium"


# ============================================================================
# OPENGL OPTIMIZER
# ============================================================================

class OpenGLOptimizer:
    """
    OpenGL-specific optimizations.
    Reduces draw calls and improves GPU performance.
    """

    @staticmethod
    def enable_optimizations():
        """Enable OpenGL performance optimizations."""
        # Enable VSync for consistent frame pacing
        try:
            import pygame
            pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
        except:
            pass

        # Optimize OpenGL state
        glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_FASTEST)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)

        # Enable culling for better performance
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        print("[OK] OpenGL optimizations enabled")

    @staticmethod
    def get_gpu_info() -> Dict[str, str]:
        """Get GPU information."""
        info = {}

        try:
            info["vendor"] = glGetString(GL_VENDOR).decode('utf-8')
            info["renderer"] = glGetString(GL_RENDERER).decode('utf-8')
            info["version"] = glGetString(GL_VERSION).decode('utf-8')
        except:
            info["error"] = "Unable to query GPU info"

        return info


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_profiler(target_fps: int = 60) -> PerformanceProfiler:
    """
    Create performance profiler.

    Args:
        target_fps: Target frame rate

    Returns:
        Configured profiler
    """
    return PerformanceProfiler(target_fps)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PERFORMANCE OPTIMIZER TEST")
    print("=" * 60)

    # Create profiler
    profiler = create_profiler(60)

    # Simulate some frames
    print("\nSimulating 100 frames...")

    for i in range(100):
        profiler.begin_frame()

        profiler.begin_update()
        time.sleep(0.001)  # 1ms update
        profiler.end_update()

        profiler.begin_render()
        time.sleep(0.010)  # 10ms render
        profiler.end_render()

        profiler.end_frame()

    # Generate report
    profiler.print_report()

    # Test GPU info
    print("\n" + "=" * 60)
    print("GPU INFORMATION")
    print("=" * 60)

    gpu_info = OpenGLOptimizer.get_gpu_info()
    for key, value in gpu_info.items():
        print(f"  {key.capitalize()}: {value}")

    print("\n[OK] Performance system ready for optimization!")
