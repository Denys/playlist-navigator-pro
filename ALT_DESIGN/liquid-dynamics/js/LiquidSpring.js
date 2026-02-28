/**
 * LiquidSpring - Physics-Based Spring Animation System
 * Part of the Liquid Dynamics Design System
 * 
 * @version 1.0.0
 * @author Playlist Navigator Pro Team
 * @license MIT
 * 
 * Implements Hooke's law with damping for realistic spring physics.
 * Provides smooth, organic motion for UI interactions.
 */

class LiquidSpring {
  /**
   * Creates a new LiquidSpring instance with configurable physics parameters
   * 
   * @param {Object} config - Configuration options
   * @param {number} config.stiffness - Spring stiffness (default: 300)
   * @param {number} config.damping - Damping coefficient (default: 30)
   * @param {number} config.mass - Mass of the object (default: 1)
   * @param {number} config.precision - Convergence threshold (default: 0.01)
   * @param {number} config.fps - Target frames per second (default: 60)
   */
  constructor(config = {}) {
    /** @type {number} Spring stiffness - higher values = faster oscillation */
    this.stiffness = config.stiffness ?? 300;
    
    /** @type {number} Damping coefficient - higher values = less bounce */
    this.damping = config.damping ?? 30;
    
    /** @type {number} Mass - higher values = more inertia */
    this.mass = config.mass ?? 1;
    
    /** @type {number} Precision threshold for animation completion */
    this.precision = config.precision ?? 0.01;
    
    /** @type {number} Target FPS for frame limiting */
    this.fps = config.fps ?? 60;
    
    /** @type {number} Minimum time step in seconds (for 60fps) */
    this.minDeltaTime = 1 / this.fps;
    
    /** @type {Map<string, AnimationInstance>} Active animation instances */
    this.activeAnimations = new Map();
    
    /** @type {number} Global animation frame ID */
    this.rafId = null;
    
    /** @type {boolean} Whether the spring system is running */
    this.isRunning = false;
    
    // Check for reduced motion preference
    this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Listen for changes in motion preference
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
      this.prefersReducedMotion = e.matches;
    });
  }

  /**
   * Animate a value from start to end using spring physics
   * 
   * @param {number} from - Starting value
   * @param {number} to - Target value
   * @param {Function} callback - Called on each frame with current value
   * @param {Object} options - Animation options
   * @param {number} options.duration - Maximum duration in ms (default: 1000)
   * @param {Function} options.onComplete - Called when animation completes
   * @param {string} options.id - Unique identifier for this animation
   * @returns {string} Animation ID for cancellation
   */
  animate(from, to, callback, options = {}) {
    // Skip animation if reduced motion is preferred
    if (this.prefersReducedMotion) {
      callback(to);
      options.onComplete?.();
      return null;
    }
    
    const animationId = options.id || `spring_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const maxDuration = options.duration || 1000;
    const startTime = performance.now();
    
    // Create animation instance
    const instance = {
      from,
      to,
      callback,
      onComplete: options.onComplete,
      startTime,
      maxDuration,
      velocity: 0,
      position: from,
      lastTime: startTime,
      settled: false
    };
    
    // Store and start animation
    this.activeAnimations.set(animationId, instance);
    this._startLoop();
    
    return animationId;
  }

  /**
   * Animate multiple values simultaneously
   * 
   * @param {Array<{from: number, to: number, callback: Function}>} animations
   * @param {Object} options - Shared animation options
   * @returns {string} Animation group ID
   */
  animateMultiple(animations, options = {}) {
    const groupId = `group_${Date.now()}`;
    let completedCount = 0;
    const totalCount = animations.length;
    
    const checkComplete = () => {
      completedCount++;
      if (completedCount === totalCount) {
        options.onComplete?.();
      }
    };
    
    animations.forEach((anim, index) => {
      this.animate(anim.from, anim.to, anim.callback, {
        ...options,
        id: `${groupId}_${index}`,
        onComplete: checkComplete
      });
    });
    
    return groupId;
  }

  /**
   * Create a spring animation for DOM element properties
   * 
   * @param {HTMLElement} element - Target element
   * @param {Object} properties - CSS properties to animate
   * @param {Object} options - Animation options
   * @returns {string} Animation ID
   */
  animateElement(element, properties, options = {}) {
    const animations = [];
    
    Object.entries(properties).forEach(([prop, { from, to, unit = '' }]) => {
      animations.push({
        from,
        to,
        callback: (value) => {
          element.style[prop] = `${value}${unit}`;
        }
      });
    });
    
    return this.animateMultiple(animations, {
      ...options,
      onComplete: () => {
        options.onComplete?.(element);
      }
    });
  }

  /**
   * Animate element transform with spring physics
   * 
   * @param {HTMLElement} element - Target element
   * @param {Object} transform - Transform properties (x, y, scale, rotate)
   * @param {Object} options - Animation options
   * @returns {string} Animation ID
   */
  animateTransform(element, transform, options = {}) {
    const currentTransform = this._getCurrentTransform(element);
    const animations = [];
    const transformValues = { ...currentTransform };
    
    if (transform.x !== undefined) {
      animations.push({
        from: currentTransform.x,
        to: transform.x,
        callback: (value) => {
          transformValues.x = value;
          this._applyTransform(element, transformValues);
        }
      });
    }
    
    if (transform.y !== undefined) {
      animations.push({
        from: currentTransform.y,
        to: transform.y,
        callback: (value) => {
          transformValues.y = value;
          this._applyTransform(element, transformValues);
        }
      });
    }
    
    if (transform.scale !== undefined) {
      animations.push({
        from: currentTransform.scale,
        to: transform.scale,
        callback: (value) => {
          transformValues.scale = value;
          this._applyTransform(element, transformValues);
        }
      });
    }
    
    if (transform.rotate !== undefined) {
      animations.push({
        from: currentTransform.rotate,
        to: transform.rotate,
        callback: (value) => {
          transformValues.rotate = value;
          this._applyTransform(element, transformValues);
        }
      });
    }
    
    return this.animateMultiple(animations, options);
  }

  /**
   * Cancel an active animation
   * 
   * @param {string} animationId - ID of animation to cancel
   * @param {boolean} snapToEnd - Whether to jump to final value
   */
  cancel(animationId, snapToEnd = false) {
    const animation = this.activeAnimations.get(animationId);
    
    if (animation) {
      if (snapToEnd) {
        animation.callback(animation.to);
        animation.onComplete?.();
      }
      this.activeAnimations.delete(animationId);
    }
    
    // Stop loop if no more animations
    if (this.activeAnimations.size === 0) {
      this._stopLoop();
    }
  }

  /**
   * Cancel all active animations
   * 
   * @param {boolean} snapToEnd - Whether to jump to final values
   */
  cancelAll(snapToEnd = false) {
    if (snapToEnd) {
      this.activeAnimations.forEach((animation) => {
        animation.callback(animation.to);
        animation.onComplete?.();
      });
    }
    
    this.activeAnimations.clear();
    this._stopLoop();
  }

  /**
   * Check if an animation is active
   * 
   * @param {string} animationId - Animation ID to check
   * @returns {boolean}
   */
  isActive(animationId) {
    return this.activeAnimations.has(animationId);
  }

  /**
   * Get count of active animations
   * 
   * @returns {number}
   */
  getActiveCount() {
    return this.activeAnimations.size;
  }

  /**
   * Start the animation loop
   * @private
   */
  _startLoop() {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this._tick();
  }

  /**
   * Stop the animation loop
   * @private
   */
  _stopLoop() {
    this.isRunning = false;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  /**
   * Animation loop tick
   * @private
   */
  _tick() {
    if (!this.isRunning) return;
    
    const currentTime = performance.now();
    
    this.activeAnimations.forEach((animation, id) => {
      const elapsed = currentTime - animation.startTime;
      const deltaTime = Math.min((currentTime - animation.lastTime) / 1000, this.minDeltaTime);
      
      // Check for timeout
      if (elapsed > animation.maxDuration) {
        animation.callback(animation.to);
        animation.onComplete?.();
        this.activeAnimations.delete(id);
        return;
      }
      
      // Calculate spring physics
      const displacement = animation.position - animation.to;
      const springForce = -this.stiffness * displacement;
      const dampingForce = -this.damping * animation.velocity;
      const acceleration = (springForce + dampingForce) / this.mass;
      
      // Update velocity and position
      animation.velocity += acceleration * deltaTime;
      animation.position += animation.velocity * deltaTime;
      animation.lastTime = currentTime;
      
      // Call callback with new position
      animation.callback(animation.position);
      
      // Check if settled
      const isSettled = Math.abs(displacement) < this.precision && 
                        Math.abs(animation.velocity) < this.precision;
      
      if (isSettled) {
        animation.callback(animation.to);
        animation.onComplete?.();
        this.activeAnimations.delete(id);
      }
    });
    
    // Continue or stop loop
    if (this.activeAnimations.size > 0) {
      this.rafId = requestAnimationFrame(() => this._tick());
    } else {
      this._stopLoop();
    }
  }

  /**
   * Get current transform values from element
   * @private
   * @param {HTMLElement} element
   * @returns {Object}
   */
  _getCurrentTransform(element) {
    const style = window.getComputedStyle(element);
    const matrix = new DOMMatrix(style.transform);
    
    return {
      x: matrix.m41 || 0,
      y: matrix.m42 || 0,
      scale: Math.sqrt(matrix.a * matrix.a + matrix.b * matrix.b) || 1,
      rotate: Math.atan2(matrix.b, matrix.a) * (180 / Math.PI) || 0
    };
  }

  /**
   * Apply transform to element
   * @private
   * @param {HTMLElement} element
   * @param {Object} values
   */
  _applyTransform(element, values) {
    const { x = 0, y = 0, scale = 1, rotate = 0 } = values;
    element.style.transform = `translate3d(${x}px, ${y}px, 0) scale(${scale}) rotate(${rotate}deg)`;
  }

  /**
   * Create a preset spring configuration
   * 
   * @param {string} preset - Preset name: 'gentle', 'snappy', 'bouncy', 'stiff'
   * @returns {LiquidSpring} New spring instance with preset
   */
  static preset(preset) {
    const presets = {
      gentle: { stiffness: 200, damping: 25, mass: 1 },
      snappy: { stiffness: 400, damping: 30, mass: 1 },
      bouncy: { stiffness: 300, damping: 15, mass: 1 },
      stiff: { stiffness: 500, damping: 40, mass: 1 },
      wobbly: { stiffness: 180, damping: 12, mass: 1 },
      slow: { stiffness: 150, damping: 20, mass: 2 }
    };
    
    return new LiquidSpring(presets[preset] || presets.gentle);
  }

  /**
   * Utility: Ease value with spring physics (one-shot calculation)
   * 
   * @param {number} progress - Animation progress (0-1)
   * @param {Object} config - Spring configuration
   * @returns {number} Eased value
   */
  static ease(progress, config = {}) {
    const spring = new LiquidSpring(config);
    let result = 0;
    
    spring.animate(0, 1, (value) => {
      result = value;
    }, { duration: progress * 1000 });
    
    return result;
  }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LiquidSpring;
}

// Default export for ES modules
if (typeof exports !== 'undefined') {
  exports.LiquidSpring = LiquidSpring;
}
