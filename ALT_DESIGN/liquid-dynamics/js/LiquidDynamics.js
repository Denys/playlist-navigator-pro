/**
 * LiquidDynamics - Main Orchestrator for the Liquid Dynamics Design System
 * Playlist Navigator Pro - Glassmorphism Transformation
 * 
 * @version 1.0.0
 * @author Playlist Navigator Pro Team
 * @license MIT
 * 
 * This is the main entry point for the Liquid Dynamics system.
 * It coordinates all subsystems: Spring physics, Parallax, Stagger animations,
 * Backdrop management, and feature detection.
 */

// Import dependencies (will work with module bundlers)
// For vanilla JS, ensure these scripts are loaded before this one
if (typeof LiquidSpring === 'undefined') {
  console.warn('[LiquidDynamics] LiquidSpring not loaded. Some features may not work.');
}
if (typeof LiquidParallax === 'undefined') {
  console.warn('[LiquidDynamics] LiquidParallax not loaded. Some features may not work.');
}
if (typeof LiquidStagger === 'undefined') {
  console.warn('[LiquidDynamics] LiquidStagger not loaded. Some features may not work.');
}
if (typeof LiquidBackdropManager === 'undefined') {
  console.warn('[LiquidDynamics] LiquidBackdropManager not loaded. Some features may not work.');
}

class LiquidDynamics {
  /**
   * Creates a new LiquidDynamics instance
   * 
   * @param {Object} config - Global configuration
   * @param {boolean} config.autoInit - Auto-initialize on creation (default: true)
   * @param {boolean} config.debug - Enable debug logging (default: false)
   * @param {Object} config.features - Feature flags to enable/disable
   */
  constructor(config = {}) {
    /** @type {string} Version of the Liquid Dynamics system */
    this.version = '1.0.0';
    
    /** @type {boolean} Enable debug logging */
    this.debug = config.debug ?? false;
    
    /** @type {boolean} Whether system is initialized */
    this.initialized = false;
    
    /** @type {Object} Feature configuration */
    this.features = {
      spring: config.features?.spring ?? true,
      parallax: config.features?.parallax ?? true,
      stagger: config.features?.stagger ?? true,
      backdropManager: config.features?.backdropManager ?? true,
      autoApplyClasses: config.features?.autoApplyClasses ?? true
    };
    
    /** @type {Object} Subsystem instances */
    this.subsystems = {
      spring: null,
      parallax: null,
      backdropManager: null
    };
    
    /** @type {Array<LiquidStagger>} Active stagger animations */
    this.staggers = [];
    
    /** @type {Object} Feature detection results */
    this.featuresDetected = {};
    
    /** @type {Object} Configuration for each subsystem */
    this.config = {
      spring: config.spring ?? {},
      parallax: config.parallax ?? {},
      backdropManager: config.backdropManager ?? {}
    };
    
    /** @type {Map<string, Function>} Registered event callbacks */
    this.eventListeners = new Map();
    
    // Auto-initialize if not disabled
    if (config.autoInit !== false) {
      this.init();
    }
  }

  /**
   * Initialize the Liquid Dynamics system
   * @returns {LiquidDynamics} this for chaining
   */
  init() {
    if (this.initialized) {
      this._log('Already initialized');
      return this;
    }
    
    this._log(`Initializing Liquid Dynamics v${this.version}`);
    
    // Detect browser features
    this._detectFeatures();
    
    // Apply fallback classes if needed
    this._applyFallbacks();
    
    // Initialize subsystems
    this._initSubsystems();
    
    // Auto-apply classes if enabled
    if (this.features.autoApplyClasses) {
      this._autoApplyClasses();
    }
    
    // Set up global event listeners
    this._setupEventListeners();
    
    this.initialized = true;
    this._emit('init', { version: this.version, features: this.featuresDetected });
    this._log('Initialization complete');
    
    return this;
  }

  /**
   * Detect browser features and capabilities
   * @private
   */
  _detectFeatures() {
    this.featuresDetected = {
      backdropFilter: CSS.supports('backdrop-filter', 'blur(10px)'),
      webkitBackdropFilter: CSS.supports('-webkit-backdrop-filter', 'blur(10px)'),
      containerQueries: CSS.supports('container-type', 'inline-size'),
      cssProperties: CSS.supports('(--custom: property)'),
      focusVisible: CSS.supports('selector(:focus-visible)'),
      contentVisibility: CSS.supports('content-visibility', 'auto'),
      intersectionObserver: 'IntersectionObserver' in window,
      mutationObserver: 'MutationObserver' in window,
      requestAnimationFrame: 'requestAnimationFrame' in window,
      resizeObserver: 'ResizeObserver' in window,
      matchMedia: 'matchMedia' in window,
      webGL: (() => {
        try {
          const canvas = document.createElement('canvas');
          return !!(window.WebGLRenderingContext && 
            (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        } catch (e) {
          return false;
        }
      })(),
      prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      touchDevice: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
      highDPI: window.devicePixelRatio > 1
    };
    
    this._log('Features detected:', this.featuresDetected);
  }

  /**
   * Apply fallback classes based on feature detection
   * @private
   */
  _applyFallbacks() {
    const body = document.body;
    
    // Backdrop filter fallback
    if (!this.featuresDetected.backdropFilter && !this.featuresDetected.webkitBackdropFilter) {
      body.classList.add('no-backdrop-filter');
      this._log('Applied no-backdrop-filter fallback');
    }
    
    // Reduced motion
    if (this.featuresDetected.prefersReducedMotion) {
      body.classList.add('prefers-reduced-motion');
      this._log('Applied reduced motion preference');
    }
    
    // Touch device optimizations
    if (this.featuresDetected.touchDevice) {
      body.classList.add('touch-device');
      this._log('Applied touch device optimizations');
    }
    
    // High DPI
    if (this.featuresDetected.highDPI) {
      body.classList.add('high-dpi');
    }
  }

  /**
   * Initialize subsystems
   * @private
   */
  _initSubsystems() {
    // Initialize Spring physics
    if (this.features.spring && typeof LiquidSpring !== 'undefined') {
      this.subsystems.spring = new LiquidSpring(this.config.spring);
      this._log('Spring physics initialized');
    }
    
    // Initialize Parallax (delayed to avoid scroll jank during page load)
    if (this.features.parallax && typeof LiquidParallax !== 'undefined') {
      // Defer parallax initialization
      setTimeout(() => {
        this.subsystems.parallax = new LiquidParallax({
          ...this.config.parallax,
          manualInit: true
        });
        
        // Only init if not on mobile with disableOnMobile
        if (!this.subsystems.parallax.isMobile || !this.subsystems.parallax.disableOnMobile) {
          this.subsystems.parallax.init();
          this._log('Parallax system initialized');
        }
      }, 100);
    }
    
    // Initialize Backdrop Manager
    if (this.features.backdropManager && typeof LiquidBackdropManager !== 'undefined') {
      this.subsystems.backdropManager = new LiquidBackdropManager({
        ...this.config.backdropManager,
        autoInit: true
      });
      this._log('Backdrop manager initialized');
    }
  }

  /**
   * Auto-apply Liquid Dynamics classes to existing elements
   * @private
   */
  _autoApplyClasses() {
    // Apply glass classes based on data attributes
    document.querySelectorAll('[data-liquid-glass]').forEach((el) => {
      const level = el.dataset.liquidGlass || '2';
      el.classList.add(`liquid-glass-${level}`);
    });
    
    // Apply parallax to elements with data-parallax
    document.querySelectorAll('[data-parallax]').forEach((el) => {
      if (this.subsystems.parallax && !this.subsystems.parallax.hasElement(el)) {
        this.subsystems.parallax.addElement(el, {
          speed: parseFloat(el.dataset.parallax) || 0.5
        });
      }
    });
    
    // Register backdrop elements
    document.querySelectorAll('.liquid-glass-1, .liquid-glass-2, .liquid-glass-3, .liquid-glass-4').forEach((el) => {
      if (this.subsystems.backdropManager) {
        el.setAttribute('data-backdrop', '');
        this.subsystems.backdropManager.register(el);
      }
    });
  }

  /**
   * Set up global event listeners
   * @private
   */
  _setupEventListeners() {
    // Visibility change - pause/resume animations
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pause();
        this._emit('pause', { reason: 'visibility' });
      } else {
        this.resume();
        this._emit('resume', { reason: 'visibility' });
      }
    });
    
    // Reduced motion preference change
    if (this.featuresDetected.matchMedia) {
      const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      motionQuery.addEventListener('change', (e) => {
        this.featuresDetected.prefersReducedMotion = e.matches;
        
        if (e.matches) {
          document.body.classList.add('prefers-reduced-motion');
          this._emit('reducedMotion', { enabled: true });
        } else {
          document.body.classList.remove('prefers-reduced-motion');
          this._emit('reducedMotion', { enabled: false });
        }
      });
    }
  }

  /**
   * Create a spring animation
   * @param {number} from - Starting value
   * @param {number} to - Target value
   * @param {Function} callback - Animation callback
   * @param {Object} options - Animation options
   * @returns {string|null} Animation ID
   */
  spring(from, to, callback, options = {}) {
    if (!this.subsystems.spring) {
      this._warn('Spring physics not available');
      return null;
    }
    
    return this.subsystems.spring.animate(from, to, callback, options);
  }

  /**
   * Create a stagger animation
   * @param {string|NodeList|Array} elements - Elements to animate
   * @param {Object} options - Stagger options
   * @returns {LiquidStagger|null}
   */
  stagger(elements, options = {}) {
    if (!this.features.stagger || typeof LiquidStagger === 'undefined') {
      this._warn('Stagger animations not available');
      return null;
    }
    
    let elementList;
    if (typeof elements === 'string') {
      elementList = document.querySelectorAll(elements);
    } else {
      elementList = elements;
    }
    
    const stagger = new LiquidStagger(elementList, options);
    this.staggers.push(stagger);
    
    // Clean up completed staggers
    setTimeout(() => {
      this.staggers = this.staggers.filter(s => s !== stagger);
    }, (options.duration || 400) + (options.maxDelay || 500) + 100);
    
    return stagger;
  }

  /**
   * Animate elements in with stagger
   * @param {string|NodeList|Array} elements - Elements to animate
   * @param {Object} options - Animation options
   * @returns {Promise}
   */
  animateIn(elements, options = {}) {
    const stagger = this.stagger(elements, options);
    return stagger ? stagger.animateIn() : Promise.resolve();
  }

  /**
   * Animate elements out with stagger
   * @param {string|NodeList|Array} elements - Elements to animate
   * @param {Object} options - Animation options
   * @returns {Promise}
   */
  animateOut(elements, options = {}) {
    const stagger = this.stagger(elements, { ...options, reverse: true });
    return stagger ? stagger.animateOut() : Promise.resolve();
  }

  /**
   * Add parallax to an element
   * @param {HTMLElement} element - Element to add parallax to
   * @param {Object} options - Parallax options
   * @returns {LiquidDynamics} this for chaining
   */
  parallax(element, options = {}) {
    if (this.subsystems.parallax) {
      this.subsystems.parallax.addElement(element, options);
    }
    return this;
  }

  /**
   * Register an element for backdrop management
   * @param {HTMLElement} element - Element to register
   * @returns {LiquidDynamics} this for chaining
   */
  registerBackdrop(element) {
    if (this.subsystems.backdropManager) {
      this.subsystems.backdropManager.register(element);
    }
    return this;
  }

  /**
   * Apply liquid glass effect to an element
   * @param {HTMLElement} element - Target element
   * @param {number} level - Glass level 1-5
   * @returns {LiquidDynamics} this for chaining
   */
  glass(element, level = 2) {
    element.classList.add(`liquid-glass-${level}`);
    
    // Also register for backdrop management
    if (level < 5) {
      this.registerBackdrop(element);
    }
    
    return this;
  }

  /**
   * Pause all animations
   * @returns {LiquidDynamics} this for chaining
   */
  pause() {
    this.subsystems.spring?.cancelAll();
    this.subsystems.parallax?.pause();
    this._emit('pause', { reason: 'manual' });
    return this;
  }

  /**
   * Resume all animations
   * @returns {LiquidDynamics} this for chaining
   */
  resume() {
    this.subsystems.parallax?.resume();
    this._emit('resume', { reason: 'manual' });
    return this;
  }

  /**
   * Refresh all subsystems (useful after DOM changes)
   * @returns {LiquidDynamics} this for chaining
   */
  refresh() {
    this.subsystems.parallax?.refreshElements();
    this.subsystems.backdropManager?.refresh();
    this._autoApplyClasses();
    this._emit('refresh');
    return this;
  }

  /**
   * Get system status and statistics
   * @returns {Object}
   */
  getStatus() {
    return {
      version: this.version,
      initialized: this.initialized,
      features: this.featuresDetected,
      subsystems: {
        spring: this.subsystems.spring?.getActiveCount?.() ?? 0,
        parallax: this.subsystems.parallax?.getElementCount?.() ?? 0,
        backdropManager: this.subsystems.backdropManager?.getStats?.() ?? null
      },
      staggers: this.staggers.length
    };
  }

  /**
   * Register an event listener
   * @param {string} event - Event name
   * @param {Function} callback - Event callback
   * @returns {LiquidDynamics} this for chaining
   */
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
    return this;
  }

  /**
   * Remove an event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback to remove
   * @returns {LiquidDynamics} this for chaining
   */
  off(event, callback) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    }
    return this;
  }

  /**
   * Emit an event
   * @private
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  _emit(event, data = null) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (e) {
          console.error(`[LiquidDynamics] Error in event listener for ${event}:`, e);
        }
      });
    }
  }

  /**
   * Log message if debug is enabled
   * @private
   * @param {...any} args
   */
  _log(...args) {
    if (this.debug) {
      console.log('[LiquidDynamics]', ...args);
    }
  }

  /**
   * Warn message
   * @private
   * @param {...any} args
   */
  _warn(...args) {
    console.warn('[LiquidDynamics]', ...args);
  }

  /**
   * Destroy the Liquid Dynamics system
   * @param {boolean} resetStyles - Whether to reset element styles
   */
  destroy(resetStyles = true) {
    this._emit('destroy');
    
    // Destroy subsystems
    this.subsystems.spring?.cancelAll();
    this.subsystems.parallax?.destroy(resetStyles);
    this.subsystems.backdropManager?.destroy(resetStyles);
    
    // Clear staggers
    this.staggers.forEach(s => s.destroy(resetStyles));
    this.staggers = [];
    
    // Remove event listeners
    this.eventListeners.clear();
    
    this.initialized = false;
    this._log('Destroyed');
  }

  /**
   * Static utility: Quick initialization
   * @param {Object} config - Configuration options
   * @returns {LiquidDynamics}
   */
  static init(config = {}) {
    return new LiquidDynamics(config);
  }

  /**
   * Static utility: Check if features are supported
   * @returns {Object}
   */
  static checkFeatures() {
    const detector = new LiquidDynamics({ autoInit: false });
    detector._detectFeatures();
    return detector.featuresDetected;
  }
}

// Auto-initialize if data attribute is present
document.addEventListener('DOMContentLoaded', () => {
  if (document.documentElement.dataset.liquidDynamics !== undefined) {
    window.liquidDynamics = new LiquidDynamics();
  }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LiquidDynamics;
}

if (typeof exports !== 'undefined') {
  exports.LiquidDynamics = LiquidDynamics;
}

// Global access
if (typeof window !== 'undefined') {
  window.LiquidDynamics = LiquidDynamics;
}
