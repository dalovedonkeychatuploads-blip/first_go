"""
Flame Effect Module
GPU-accelerated flame rendering using GLSL shaders.
Optimized for 60 FPS on RTX 3060M with full parameter control.

Features:
- Procedural noise-based flame animation
- Multiple flame presets (realistic, magic, plasma, energy)
- Real-time parameter adjustment via sliders
- Particle embers and sparks
- Additive blending for authentic glow
"""

import time
import random
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


# ============================================================================
# FLAME PARAMETERS
# ============================================================================

class FlamePreset(Enum):
    """Predefined flame styles for quick selection."""
    REALISTIC_FIRE = "realistic_fire"
    MAGIC_FIRE = "magic_fire"
    PLASMA = "plasma"
    ENERGY = "energy"
    COLD_FIRE = "cold_fire"  # Blue/white flames


@dataclass
class FlameParameters:
    """
    Complete set of parameters controlling flame appearance and behavior.
    All values are GPU-optimized and exposed for UI slider control.
    """
    # Color gradient (bottom to top)
    color_bottom: Tuple[float, float, float, float] = (1.0, 0.3, 0.0, 1.0)  # Orange base
    color_middle: Tuple[float, float, float, float] = (1.0, 0.6, 0.0, 1.0)  # Yellow-orange
    color_top: Tuple[float, float, float, float] = (1.0, 1.0, 0.3, 0.8)     # Bright yellow tip

    # Intensity and visibility
    intensity: float = 1.0          # Master brightness multiplier (0.0 - 2.0)
    opacity: float = 0.85           # Overall transparency (0.0 - 1.0)

    # Animation and motion
    speed: float = 1.0              # Animation speed multiplier (0.1 - 5.0)
    turbulence: float = 1.0         # Chaos/noise intensity (0.0 - 2.0)
    flicker_intensity: float = 0.3  # Random flicker strength (0.0 - 1.0)

    # Shape and size
    height: float = 1.0             # Vertical scale (0.1 - 3.0)
    width: float = 0.5              # Horizontal scale (0.1 - 2.0)
    taper: float = 0.7              # How much flame narrows at top (0.0 - 1.0)

    # Advanced parameters
    noise_scale: float = 2.0        # Frequency of noise pattern (0.5 - 5.0)
    distortion: float = 0.5         # Waviness/distortion amount (0.0 - 2.0)
    glow_radius: float = 1.2        # Additive glow spread (0.5 - 3.0)

    # Embers/particles
    ember_count: int = 20           # Number of floating embers (0 - 100)
    ember_speed: float = 1.0        # Ember rise speed (0.1 - 3.0)
    ember_size: float = 0.03        # Ember particle size (0.01 - 0.1)

    def __post_init__(self):
        """Validate and clamp parameters to safe ranges."""
        self.intensity = max(0.0, min(2.0, self.intensity))
        self.opacity = max(0.0, min(1.0, self.opacity))
        self.speed = max(0.1, min(5.0, self.speed))
        self.turbulence = max(0.0, min(2.0, self.turbulence))
        self.flicker_intensity = max(0.0, min(1.0, self.flicker_intensity))
        self.height = max(0.1, min(3.0, self.height))
        self.width = max(0.1, min(2.0, self.width))
        self.taper = max(0.0, min(1.0, self.taper))
        self.ember_count = max(0, min(100, self.ember_count))


# ============================================================================
# SHADER SOURCE CODE (GLSL)
# ============================================================================

FLAME_VERTEX_SHADER = """
#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;

out vec2 fragTexCoord;
out vec3 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

void main()
{
    fragTexCoord = texCoord;
    fragPosition = position;
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
}
"""

FLAME_FRAGMENT_SHADER = """
#version 330 core

in vec2 fragTexCoord;
in vec3 fragPosition;

out vec4 fragColor;

// Flame parameters (uniforms from CPU)
uniform float uTime;
uniform vec3 uColorBottom;
uniform vec3 uColorMiddle;
uniform vec3 uColorTop;
uniform float uIntensity;
uniform float uOpacity;
uniform float uSpeed;
uniform float uTurbulence;
uniform float uFlickerIntensity;
uniform float uNoiseScale;
uniform float uDistortion;

// Simplex noise function (optimized for GPU)
// Based on Stefan Gustavson's implementation
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }

float snoise(vec2 v)
{
    const vec4 C = vec4(0.211324865405187,  // (3.0-sqrt(3.0))/6.0
                        0.366025403784439,  // 0.5*(sqrt(3.0)-1.0)
                       -0.577350269189626,  // -1.0 + 2.0 * C.x
                        0.024390243902439); // 1.0 / 41.0

    vec2 i  = floor(v + dot(v, C.yy) );
    vec2 x0 = v -   i + dot(i, C.xx);

    vec2 i1;
    i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;

    i = mod289(i);
    vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
        + i.x + vec3(0.0, i1.x, 1.0 ));

    vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
    m = m*m ;
    m = m*m ;

    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;

    m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );

    vec3 g;
    g.x  = a0.x  * x0.x  + h.x  * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
}

// Multi-octave noise (fractal Brownian motion)
float fbm(vec2 p, int octaves)
{
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;

    for (int i = 0; i < octaves; i++)
    {
        value += amplitude * snoise(p * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }

    return value;
}

void main()
{
    vec2 uv = fragTexCoord;

    // Animated time with speed multiplier
    float animTime = uTime * uSpeed;

    // Create multi-layered noise for organic flame motion
    vec2 noiseCoord = uv * uNoiseScale;

    // Layer 1: Main flame shape (slow, large features)
    float noise1 = fbm(noiseCoord + vec2(0.0, animTime * 0.5), 4);

    // Layer 2: Detail turbulence (faster, smaller features)
    float noise2 = fbm(noiseCoord * 2.0 + vec2(animTime * 1.0, animTime * 0.8), 3);

    // Layer 3: Fine detail (rapid flickering)
    float noise3 = snoise(noiseCoord * 4.0 + vec2(animTime * 2.0, animTime * 1.5));

    // Combine noise layers with turbulence weighting
    float combinedNoise = noise1 * 0.5 + noise2 * 0.3 * uTurbulence + noise3 * 0.2 * uTurbulence;

    // Apply vertical gradient (flame rises upward)
    float verticalGradient = 1.0 - uv.y;

    // Horizontal centering (flame is narrower at top)
    float horizontalFalloff = 1.0 - abs(uv.x - 0.5) * 2.0;
    horizontalFalloff = pow(horizontalFalloff, 1.0 + uv.y * 2.0);  // Taper toward top

    // Distort flame shape with noise
    float distortedY = uv.y + combinedNoise * uDistortion * 0.1;
    float flameMask = verticalGradient * horizontalFalloff;

    // Add noise-based variation to flame shape
    flameMask *= (0.7 + combinedNoise * 0.3);

    // Clamp to valid range
    flameMask = clamp(flameMask, 0.0, 1.0);

    // Color gradient based on height
    vec3 flameColor;
    if (uv.y < 0.3)
    {
        // Bottom third: bottom to middle color
        float t = uv.y / 0.3;
        flameColor = mix(uColorBottom, uColorMiddle, t);
    }
    else
    {
        // Top two-thirds: middle to top color
        float t = (uv.y - 0.3) / 0.7;
        flameColor = mix(uColorMiddle, uColorTop, t);
    }

    // Add noise variation to color
    flameColor += vec3(noise3 * 0.1);

    // Random flicker effect
    float flicker = 1.0 + sin(animTime * 10.0 + noise1 * 5.0) * uFlickerIntensity * 0.1;
    flameColor *= flicker;

    // Apply intensity
    flameColor *= uIntensity;

    // Calculate alpha (transparency)
    float alpha = flameMask * uOpacity;

    // Apply soft edge falloff for smooth blending
    alpha *= smoothstep(0.0, 0.2, flameMask);

    // Output final color with alpha
    fragColor = vec4(flameColor, alpha);

    // Ensure no negative values or NaN
    fragColor = clamp(fragColor, 0.0, 1.0);
}
"""


# ============================================================================
# EMBER PARTICLE CLASS
# ============================================================================

@dataclass
class Ember:
    """Single ember particle rising from the flame."""
    position: np.ndarray  # [x, y, z]
    velocity: np.ndarray  # [vx, vy, vz]
    lifetime: float       # Remaining life (0.0 - 1.0)
    size: float          # Particle size
    color: np.ndarray    # [r, g, b, a]


# ============================================================================
# MAIN FLAME EFFECT CLASS
# ============================================================================

class FlameEffect:
    """
    GPU-accelerated flame effect with GLSL shaders.
    Renders procedural fire with real-time parameter control.
    """

    def __init__(self, parameters: Optional[FlameParameters] = None):
        """
        Initialize flame effect with optional custom parameters.

        Args:
            parameters: FlameParameters instance or None for defaults
        """
        self.parameters = parameters if parameters is not None else FlameParameters()

        # Shader program (compiled on first render)
        self.shader_program = None
        self.shader_compiled = False

        # Uniform locations (cached for performance)
        self.uniform_locations = {}

        # Flame geometry (quad with texture coordinates)
        self.vao = None
        self.vbo = None
        self.vertices = None

        # Ember particles
        self.embers: List[Ember] = []

        # Animation state
        self.start_time = time.time()
        self.last_spawn_time = 0.0

        # Error state
        self.shader_error = None

        print("✓ Flame effect initialized (shaders will compile on first render)")

    # ========================================================================
    # SHADER COMPILATION
    # ========================================================================

    def _compile_shaders(self):
        """
        Compile GLSL shaders and link shader program.
        This is done once on first render for performance.
        """
        if self.shader_compiled:
            return True

        try:
            print("Compiling flame shaders...")

            # Compile vertex shader
            vertex_shader = compileShader(FLAME_VERTEX_SHADER, GL_VERTEX_SHADER)

            # Compile fragment shader
            fragment_shader = compileShader(FLAME_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)

            # Link shader program
            self.shader_program = compileProgram(vertex_shader, fragment_shader)

            # Cache uniform locations for performance
            self._cache_uniform_locations()

            self.shader_compiled = True
            print("✓ Flame shaders compiled successfully")
            return True

        except Exception as e:
            self.shader_error = str(e)
            print(f"❌ Shader compilation failed: {e}")
            return False

    def _cache_uniform_locations(self):
        """Cache all uniform locations to avoid repeated glGetUniformLocation calls."""
        if self.shader_program is None:
            return

        uniform_names = [
            'uTime', 'uColorBottom', 'uColorMiddle', 'uColorTop',
            'uIntensity', 'uOpacity', 'uSpeed', 'uTurbulence',
            'uFlickerIntensity', 'uNoiseScale', 'uDistortion',
            'modelMatrix', 'viewMatrix', 'projectionMatrix'
        ]

        for name in uniform_names:
            location = glGetUniformLocation(self.shader_program, name)
            if location != -1:
                self.uniform_locations[name] = location
            else:
                print(f"Warning: Uniform '{name}' not found in shader")

    # ========================================================================
    # GEOMETRY SETUP
    # ========================================================================

    def _create_flame_geometry(self):
        """
        Create quad geometry for flame rendering.
        Flame is rendered on a textured quad with procedural shader.
        """
        if self.vao is not None:
            return  # Already created

        # Quad vertices (position + texcoord)
        # Flame rises upward, so Y goes from 0 (bottom) to height (top)
        height = self.parameters.height
        width = self.parameters.width

        self.vertices = np.array([
            # Position (x, y, z)    TexCoord (u, v)
            [-width/2, 0.0,    0.0,  0.0, 0.0],  # Bottom-left
            [ width/2, 0.0,    0.0,  1.0, 0.0],  # Bottom-right
            [ width/2, height, 0.0,  1.0, 1.0],  # Top-right
            [-width/2, height, 0.0,  0.0, 1.0],  # Top-left
        ], dtype=np.float32)

        # Create VAO and VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Position attribute (location = 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))

        # TexCoord attribute (location = 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))

        glBindVertexArray(0)

    # ========================================================================
    # EMBER PARTICLE SYSTEM
    # ========================================================================

    def _update_embers(self, delta_time: float):
        """Update ember particles (position, lifetime, spawning)."""
        # Update existing embers
        for ember in self.embers[:]:
            # Update position
            ember.position += ember.velocity * delta_time

            # Update lifetime
            ember.lifetime -= delta_time

            # Fade out near end of life
            if ember.lifetime < 0.2:
                ember.color[3] = ember.lifetime / 0.2

            # Remove dead embers
            if ember.lifetime <= 0.0:
                self.embers.remove(ember)

        # Spawn new embers
        current_time = time.time()
        spawn_rate = self.parameters.ember_count / 2.0  # Embers per second

        if spawn_rate > 0 and current_time - self.last_spawn_time > (1.0 / spawn_rate):
            self._spawn_ember()
            self.last_spawn_time = current_time

    def _spawn_ember(self):
        """Spawn a single new ember particle."""
        if len(self.embers) >= self.parameters.ember_count:
            return  # At max capacity

        # Random horizontal position near flame base
        x = (random.random() - 0.5) * self.parameters.width * 0.5
        y = random.random() * 0.2  # Near bottom of flame

        # Upward velocity with slight randomness
        vx = (random.random() - 0.5) * 0.1
        vy = self.parameters.ember_speed * (0.5 + random.random() * 0.5)
        vz = 0.0

        # Ember color (hot orange-yellow)
        r = 1.0
        g = 0.5 + random.random() * 0.5
        b = 0.0
        a = 0.8

        ember = Ember(
            position=np.array([x, y, 0.0], dtype=np.float32),
            velocity=np.array([vx, vy, vz], dtype=np.float32),
            lifetime=1.0 + random.random() * 2.0,
            size=self.parameters.ember_size,
            color=np.array([r, g, b, a], dtype=np.float32)
        )

        self.embers.append(ember)

    def _render_embers(self):
        """Render all ember particles as point sprites."""
        if not self.embers:
            return

        glDisable(GL_TEXTURE_2D)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(10.0)

        glBegin(GL_POINTS)
        for ember in self.embers:
            glColor4fv(ember.color)
            glVertex3fv(ember.position)
        glEnd()

        glDisable(GL_POINT_SMOOTH)

    # ========================================================================
    # MAIN RENDERING
    # ========================================================================

    def render(self, position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
               direction: Tuple[float, float, float] = (0.0, 1.0, 0.0),
               delta_time: float = 0.016):
        """
        Render the flame effect at the specified position.

        Args:
            position: World position (x, y, z) to render flame
            direction: Direction vector for flame orientation
            delta_time: Time since last frame (for animation)
        """
        # Compile shaders on first render
        if not self.shader_compiled:
            if not self._compile_shaders():
                # Shader compilation failed, render fallback
                self._render_fallback(position)
                return

        # Create geometry on first render
        if self.vao is None:
            self._create_flame_geometry()

        # Update embers
        self._update_embers(delta_time)

        # Enable additive blending for fire glow
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending

        # Use flame shader
        glUseProgram(self.shader_program)

        # Set uniforms
        self._set_shader_uniforms()

        # Apply position transform
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])

        # Render flame quad
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)

        # Render embers
        self._render_embers()

        glPopMatrix()

        # Restore normal blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glUseProgram(0)

    def _set_shader_uniforms(self):
        """Upload all flame parameters to shader uniforms."""
        # Time (for animation)
        elapsed_time = time.time() - self.start_time
        self._set_uniform_float('uTime', elapsed_time)

        # Colors
        self._set_uniform_vec3('uColorBottom', self.parameters.color_bottom[:3])
        self._set_uniform_vec3('uColorMiddle', self.parameters.color_middle[:3])
        self._set_uniform_vec3('uColorTop', self.parameters.color_top[:3])

        # Intensity and opacity
        self._set_uniform_float('uIntensity', self.parameters.intensity)
        self._set_uniform_float('uOpacity', self.parameters.opacity)

        # Animation
        self._set_uniform_float('uSpeed', self.parameters.speed)
        self._set_uniform_float('uTurbulence', self.parameters.turbulence)
        self._set_uniform_float('uFlickerIntensity', self.parameters.flicker_intensity)

        # Shape
        self._set_uniform_float('uNoiseScale', self.parameters.noise_scale)
        self._set_uniform_float('uDistortion', self.parameters.distortion)

    def _set_uniform_float(self, name: str, value: float):
        """Set a float uniform if it exists."""
        if name in self.uniform_locations:
            glUniform1f(self.uniform_locations[name], value)

    def _set_uniform_vec3(self, name: str, value: Tuple[float, float, float]):
        """Set a vec3 uniform if it exists."""
        if name in self.uniform_locations:
            glUniform3f(self.uniform_locations[name], value[0], value[1], value[2])

    def _render_fallback(self, position: Tuple[float, float, float]):
        """
        Render a simple fallback flame if shaders fail.
        Uses basic OpenGL without shaders.
        """
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])

        # Draw simple colored quad as fallback
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(1.0, 0.5, 0.0, 0.8)  # Orange
        glVertex3f(-0.25, 0.0, 0.0)
        glVertex3f(0.25, 0.0, 0.0)
        glColor4f(1.0, 1.0, 0.3, 0.5)  # Yellow (top, faded)
        glVertex3f(0.1, 1.0, 0.0)
        glVertex3f(-0.1, 1.0, 0.0)
        glEnd()

        glPopMatrix()

    # ========================================================================
    # PARAMETER CONTROL (For UI Sliders)
    # ========================================================================

    def set_intensity(self, value: float):
        """Set flame intensity (brightness)."""
        self.parameters.intensity = max(0.0, min(2.0, value))

    def set_speed(self, value: float):
        """Set animation speed."""
        self.parameters.speed = max(0.1, min(5.0, value))

    def set_turbulence(self, value: float):
        """Set flame turbulence (chaos)."""
        self.parameters.turbulence = max(0.0, min(2.0, value))

    def set_color_bottom(self, r: float, g: float, b: float):
        """Set bottom flame color."""
        self.parameters.color_bottom = (r, g, b, 1.0)

    def set_color_top(self, r: float, g: float, b: float):
        """Set top flame color."""
        self.parameters.color_top = (r, g, b, 0.8)

    def apply_preset(self, preset: FlamePreset):
        """Apply a predefined flame preset."""
        if preset == FlamePreset.REALISTIC_FIRE:
            self.parameters.color_bottom = (1.0, 0.3, 0.0, 1.0)
            self.parameters.color_top = (1.0, 1.0, 0.3, 0.8)
            self.parameters.turbulence = 1.0
            self.parameters.speed = 1.0

        elif preset == FlamePreset.MAGIC_FIRE:
            self.parameters.color_bottom = (0.8, 0.0, 1.0, 1.0)  # Purple
            self.parameters.color_top = (0.3, 0.8, 1.0, 0.9)     # Cyan
            self.parameters.turbulence = 1.5
            self.parameters.speed = 0.7

        elif preset == FlamePreset.PLASMA:
            self.parameters.color_bottom = (1.0, 0.0, 0.5, 1.0)
            self.parameters.color_top = (0.5, 0.5, 1.0, 1.0)
            self.parameters.turbulence = 2.0
            self.parameters.speed = 2.0

        elif preset == FlamePreset.ENERGY:
            self.parameters.color_bottom = (0.0, 1.0, 1.0, 1.0)  # Cyan
            self.parameters.color_top = (1.0, 1.0, 1.0, 1.0)     # White
            self.parameters.turbulence = 0.5
            self.parameters.speed = 1.5

        elif preset == FlamePreset.COLD_FIRE:
            self.parameters.color_bottom = (0.0, 0.5, 1.0, 1.0)  # Blue
            self.parameters.color_top = (0.8, 0.9, 1.0, 0.9)     # Light blue
            self.parameters.turbulence = 0.8
            self.parameters.speed = 1.2

    # ========================================================================
    # CLEANUP
    # ========================================================================

    def cleanup(self):
        """Free GPU resources."""
        if self.vao is not None:
            glDeleteVertexArrays(1, [self.vao])
            self.vao = None

        if self.vbo is not None:
            glDeleteBuffers(1, [self.vbo])
            self.vbo = None

        if self.shader_program is not None:
            glDeleteProgram(self.shader_program)
            self.shader_program = None

        print("✓ Flame effect resources cleaned up")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_flame_effect(preset: FlamePreset = FlamePreset.REALISTIC_FIRE) -> FlameEffect:
    """
    Create a flame effect with a specific preset.

    Args:
        preset: FlamePreset enum value

    Returns:
        Configured FlameEffect instance
    """
    effect = FlameEffect()
    effect.apply_preset(preset)
    return effect
