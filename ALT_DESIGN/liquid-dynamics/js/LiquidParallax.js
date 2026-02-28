/**
 * LiquidParallax - Multi-Layer Depth Parallax System
 * Part of the Liquid Dynamics Design System
 * 
 * @version 1.0.0
 * @author Playlist Navigator Pro Team
 * @license MIT
 * 
 * Creates depth perception by moving background elements at different speeds.
 * Implements GPU-accelerated transforms for smooth 60fps performance.
 */

class LiquidParallax {
  /**
   * Creates a new LiquidParallax instance
   * 
   * @param {Object} config - Configuration options
   * @param {string} config.selector - CSS selector for parallax elements (default: '[data-parallax]')
   * @param {boolean} config.smoothScrolling - Enable smooth scroll interpolation (default: true)
   * @param {number} config.smoothFactor - Smoothing factor 0-1 (default: 0.1)
   * @param {boolean} config.horizontal - Enable horizontal parallax (default: false)
   * @param {boolean} config.disableOnMobile - Disable on mobile devices (default: true)
   * @param {number} config.mobileBreakpoint - Mobile breakpoint in px (default: 768)
   */
  constructor(config = {}) {
    /** @type {string} CSS selector for parallax elements */
    this.selector = config.selector ?? '[data-parallax]';
    
    /** @type {boolean} Enable smooth scroll interpolation */
    this.smoothScrolling = config.smoothScrolling ?? true;
    
    /** @type {number} Smoothing factor for interpolation (0-1) */
    this.smoothFactor = config.smoothFactor ?? 0.1;
    
    /** @type {boolean} Enable horizontal parallax */
    this.horizontal = config.horizontal ?? false;
    
    /** @type {boolean} Disable on mobile */
    this.disableOnMobile = config.disableOnMobile ?? true;
    
    /** @type {number} Mobile breakpoint */
    this.mobileBreakpoint = config.mobileBreakpoint ?? 768;
    
    /** @type {Array<ParallaxElement>} Registered parallax elements */
    this.elements = [];
    
    /** @type {number} Current scroll position Y */
    this.scrollY = 0;
    
    /** @type {number} Target scroll position Y (for smoothing) */
    this.targetScrollY = 0;
    
    /** @type {number} Current scroll position X */
    this.scrollX = 0;
    
    /** @type {number} Target scroll position X (for smoothing) */
    this.targetScrollX = 0;
    
    /** @type {boolean} Whether parallax is currently running */
    this.isRunning = false;
    
    /** @type {number} Animation frame ID */
    this.rafId = null;
    
    /** @type {boolean} Whether system is initialized */
    this.initialized = false;
    
    /** @type {boolean} Whether user prefers reduced motion */
    this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    /** @type {boolean} Whether currently on mobile */
    this.isMobile = window.innerWidth < this.mobileBreakpoint;
    
    /** @type {IntersectionObserver} Visibility observer */
    this.observer = null;
    
    // Bind methods
    this.handleScroll = this.handleScroll.bind(this);
    this.handleResize = this.handleResize.bind(this);
    this.tick = this.tick.bind(this);
    
    // Auto-initialize if not disabled
    if (!config.manualInit) {
      this.init();
    }
  }

  /**
   * Initialize the parallax system
   * @returns {LiquidParallax} this for chaining
   */
  init() {
    if (this.initialized) return this;
    
    // Check for reduced motion preference
    if (this.prefersReducedMotion) {
      console.log('[LiquidParallax] Reduced motion preferred, disabling parallax');
      return this;
    }
    
    // Check mobile
    if (this.disableOnMobile && this.isMobile) {
      console.log('[LiquidParallax] Mobile detected, disabling parallax');
      return this;
    }
    
    // Find and register elements
    this.refreshElements();
    
    // Set up intersection observer for performance
    this._setupObserver();
    
    // Add event listeners
    window.addEventListener('scroll', this.handleScroll, { passive: true });
    window.addEventListener('resize', this.handleResize, { passive: true });
    
    // Start animation loop
    this.isRunning = true;
    this.tick();
    
    this.initialized = true;
    console.log(`[LiquidParallax] Initialized with ${this.elements.length} elements`);
    
    return this;
  }

  /**
   * Refresh the list of parallax elements
   * Useful after DOM changes
   * @returns {LiquidParallax} this for chaining
   */
  refreshElements() {
    const domElements = document.querySelectorAll(this.selector);
    
    this.elements = Array.from(domElements).map((el, index) => {
      // Parse speed from data attribute
      const speedAttr = el.dataset.parallax;
      const speed = parseFloat(speedAttr) || 0.5;
      
      // Parse direction
      const direction = el.dataset.parallaxDirection || 'vertical';
      
      // Parse offset
      const offset = parseFloat(el.dataset.parallaxOffset) || 0;
      
      // Parse limits
      const min = parseFloat(el.dataset.parallaxMin) ?? null;
      const max = parseFloat(el.dataset.parallaxMax) ?? null;
      
      // Check if element is in viewport
      const rect = el.getBoundingClientRect();
      const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
      
      // Store initial position
      const initialTransform = window.getComputedStyle(el).transform;
      
      return {
        element: el,
        id: `parallax_${index}_${Date.now()}`,
        speed,
        direction,
        offset,
        min,
        max,
        isVisible,
        initialTransform: initialTransform === 'none' ? '' : initialTransform,
        currentY: 0,
        currentX: 0
      };
    });
    
    return this;
  }

  /**
   * Add a single element to parallax
   * @param {HTMLElement} element - Element to add
   * @param {Object} options - Parallax options
   * @returns {LiquidParallax} this for chaining
   */
  addElement(element, options = {}) {
    const speed = options.speed ?? 0.5;
    const direction = options.direction || 'vertical';
    const offset = options.offset ?? 0;
    
    const parallaxEl = {
      element,
      id: `parallax_added_${Date.now()}`,
      speed,
      direction,
      offset,
      min: options.min ?? null,
      max: options.max ?? null,
      isVisible: true,
      initialTransform: '',
      currentY: 0,
      currentX: 0
    };
    
    this.elements.push(parallaxEl);
    
    // Observe if using intersection observer
    if (this.observer) {
      this.observer.observe(element);
    }
    
    return this;
  }

  /**
   * Remove an element from parallax
   * @param {HTMLElement} element - Element to remove
   * @returns {LiquidParallax} this for chaining
   */
  removeElement(element) {
    const index = this.elements.findIndex(el => el.element === element);
    
    if (index !== -1) {
      // Reset transform
      const parallaxEl = this.elements[index];
      parallaxEl.element.style.transform = parallaxEl.initialTransform;
      
      // Remove from array
      this.elements.splice(index, 1);
      
      // Unobserve
      if (this.observer) {
        this.observer.unobserve(element);
      }
    }
    
    return this;
  }

  /**
   * Handle scroll events
   * @private
   */
  handleScroll() {
    this.targetScrollY = window.pageYOffset || document.documentElement.scrollTop;
    
    if (this.horizontal) {
      this.targetScrollX = window.pageXOffset || document.documentElement.scrollLeft;
    }
  }

  /**
   * Handle resize events
   * @private
   */
  handleResize() {
    const wasMobile = this.isMobile;
    this.isMobile = window.innerWidth < this.mobileBreakpoint;
    
    // Refresh elements on resize
    this.refreshElements();
    
    // Disable/enable based on mobile status
    if (this.disableOnMobile) {
      if (!wasMobile && this.isMobile) {
        this.pause();
        // Reset all transforms
        this.elements.forEach(el => {
          el.element.style.transform = el.initialTransform;
        });
      } else if (wasMobile && !this.isMobile && !this.isRunning) {
        this.resume();
      }
    }
  }

  /**
   * Animation loop tick
   * @private
   */
  tick() {
    if (!this.isRunning) return;
    
    // Smooth scroll interpolation
    if (this.smoothScrolling) {
      this.scrollY += (this.targetScrollY - this.scrollY) * this.smoothFactor;
      if (this.horizontal) {
        this.scrollX += (this.targetScrollX - this.scrollX) * this.smoothFactor;
      }
    } else {
      this.scrollY = this.targetScrollY;
      this.scrollX = this.targetScrollX;
    }
    
    // Update each element
    this.elements.forEach((el) => {
      if (!el.isVisible) return;
      
      let yPos = 0;
      let xPos = 0;
      
      // Calculate position based on direction
      if (el.direction === 'vertical' || el.direction === 'both') {
        yPos = -(this.scrollY * el.speed) + el.offset;
        
        // Apply limits
        if (el.min !== null) yPos = Math.max(yPos, el.min);
        if (el.max !== null) yPos = Math.min(yPos, el.max);
      }
      
      if (el.direction === 'horizontal' || el.direction === 'both') {
        xPos = -(this.scrollX * el.speed) + el.offset;
        
        // Apply limits
        if (el.min !== null) xPos = Math.max(xPos, el.min);
        if (el.max !== null) xPos = Math.min(xPos, el.max);
      }
      
      // Apply transform using translate3d for GPU acceleration
      const transform = `translate3d(${xPos}px, ${yPos}px, 0) ${el.initialTransform}`;
      el.element.style.transform = transform;
      
      // Store current position
      el.currentY = yPos;
      el.currentX = xPos;
    });
    
    // Continue loop
    this.rafId = requestAnimationFrame(this.tick);
  }

  /**
   * Set up intersection observer for performance
   * @private
   */
  _setupObserver() {
    if (!('IntersectionObserver' in window)) return;
    
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const parallaxEl = this.elements.find(el => el.element === entry.target);
          if (parallaxEl) {
            parallaxEl.isVisible = entry.isIntersecting;
          }
        });
      },
      {
        threshold: 0,
        rootMargin: '50px 0px 50px 0px'
      }
    );
    
    // Observe all elements
    this.elements.forEach((el) => {
      this.observer.observe(el.element);
    });
  }

  /**
   * Pause parallax updates
   * @returns {LiquidParallax} this for chaining
   */
  pause() {
    this.isRunning = false;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    return this;
  }

  /**
   * Resume parallax updates
   * @returns {LiquidParallax} this for chaining
   */
  resume() {
    if (!this.initialized) {
      return this.init();
    }
    
    if (!this.isRunning) {
      this.isRunning = true;
      this.tick();
    }
    return this;
  }

  /**
   * Destroy the parallax system
   * Cleans up event listeners and resets transforms
   * @param {boolean} resetTransforms - Whether to reset element transforms
   */
  destroy(resetTransforms = true) {
    // Stop animation
    this.pause();
    
    // Remove event listeners
    window.removeEventListener('scroll', this.handleScroll);
    window.removeEventListener('resize', this.handleResize);
    
    // Disconnect observer
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    
    // Reset transforms
    if (resetTransforms) {
      this.elements.forEach((el) => {
        el.element.style.transform = el.initialTransform;
      });
    }
    
    // Clear elements
    this.elements = [];
    this.initialized = false;
    
    console.log('[LiquidParallax] Destroyed');
  }

  /**
   * Get current scroll information
   * @returns {Object}
   */
  getScrollInfo() {
    return {
      y: this.scrollY,
      x: this.scrollX,
      targetY: this.targetScrollY,
      targetX: this.targetScrollX
    };
  }

  /**
   * Get element count
   * @returns {number}
   */
  getElementCount() {
    return this.elements.length;
  }

  /**
   * Check if element is registered
   * @param {HTMLElement} element
   * @returns {boolean}
   */
  hasElement(element) {
    return this.elements.some(el => el.element === element);
  }

  /**
   * Static utility: Create parallax on specific elements
   * @param {string|NodeList|Array} elements - Elements to parallax
   * @param {Object} options - Parallax options
   * @returns {LiquidParallax}
   */
  static create(elements, options = {}) {
    const instance = new LiquidParallax({ ...options, manualInit: true });
    
    let elementList;
    if (typeof elements === 'string') {
      elementList = document.querySelectorAll(elements);
    } else if (elements instanceof NodeList) {
      elementList = elements;
    } else if (Array.isArray(elements)) {
      elementList = elements;
    } else {
      elementList = [elements];
    }
    
    elementList.forEach((el) => {
      instance.addElement(el, options);
    });
    
    instance.init();
    return instance;
  }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LiquidParallax;
}

if (typeof exports !== 'undefined') {
  exports.LiquidParallax = LiquidParallax;
}
