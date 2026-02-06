/**
 * LiquidStagger - Staggered Animation Controller
 * Part of the Liquid Dynamics Design System
 * 
 * @version 1.0.0
 * @author Playlist Navigator Pro Team
 * @license MIT
 * 
 * Provides coordinated entrance/exit animations for lists and grids
 * with configurable delays and easing curves.
 */

class LiquidStagger {
  /**
   * Creates a new LiquidStagger controller
   * 
   * @param {NodeList|Array|HTMLElement} elements - Elements to animate
   * @param {Object} options - Animation options
   * @param {number} options.baseDelay - Base delay between items in ms (default: 50)
   * @param {number} options.maxDelay - Maximum cumulative delay in ms (default: 500)
   * @param {number} options.duration - Animation duration in ms (default: 400)
   * @param {string} options.easing - CSS easing function (default: 'ease')
   * @param {string} options.direction - Animation direction: 'up', 'down', 'left', 'right', 'scale' (default: 'up')
   * @param {number} options.distance - Animation distance in px (default: 20)
   * @param {boolean} options.reverse - Reverse the stagger order (default: false)
   * @param {Function} options.onStart - Called when animation starts
   * @param {Function} options.onComplete - Called when all animations complete
   * @param {boolean} options.once - Only animate once (default: true)
   */
  constructor(elements, options = {}) {
    // Normalize elements to array
    if (elements instanceof HTMLElement) {
      this.elements = [elements];
    } else if (elements instanceof NodeList) {
      this.elements = Array.from(elements);
    } else if (Array.isArray(elements)) {
      this.elements = elements;
    } else {
      throw new Error('LiquidStagger: Invalid elements provided');
    }
    
    /** @type {number} Base delay between items in milliseconds */
    this.baseDelay = options.baseDelay ?? 50;
    
    /** @type {number} Maximum cumulative delay */
    this.maxDelay = options.maxDelay ?? 500;
    
    /** @type {number} Animation duration in milliseconds */
    this.duration = options.duration ?? 400;
    
    /** @type {string} CSS easing function */
    this.easing = options.easing ?? 'cubic-bezier(0.68, -0.55, 0.265, 1.55)';
    
    /** @type {string} Animation direction */
    this.direction = options.direction ?? 'up';
    
    /** @type {number} Animation distance in pixels */
    this.distance = options.distance ?? 20;
    
    /** @type {boolean} Reverse the stagger order */
    this.reverse = options.reverse ?? false;
    
    /** @type {Function} Called when animation starts */
    this.onStart = options.onStart ?? null;
    
    /** @type {Function} Called when all complete */
    this.onComplete = options.onComplete ?? null;
    
    /** @type {boolean} Only animate once */
    this.once = options.once ?? true;
    
    /** @type {boolean} Whether animation has been triggered */
    this.hasAnimated = false;
    
    /** @type {number} Active animation count */
    this.activeAnimations = 0;
    
    /** @type {IntersectionObserver} Visibility observer */
    this.observer = null;
    
    /** @type {boolean} Whether using intersection observer */
    this.useObserver = options.useObserver ?? false;
    
    /** @type {string} Container selector for observer */
    this.observeContainer = options.observeContainer ?? null;
    
    // Check for reduced motion
    this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Set up observer if requested
    if (this.useObserver && 'IntersectionObserver' in window) {
      this._setupObserver();
    }
  }

  /**
   * Set up intersection observer for scroll-triggered animations
   * @private
   */
  _setupObserver() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };
    
    if (this.observeContainer) {
      const container = document.querySelector(this.observeContainer);
      if (container) {
        observerOptions.root = container;
      }
    }
    
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          this.animateIn();
          
          // Unobserve if once is true
          if (this.once) {
            this.observer.unobserve(entry.target);
          }
        } else if (!this.once) {
          this.animateOut();
        }
      });
    }, observerOptions);
    
    // Observe the first element or a container
    if (this.elements.length > 0) {
      this.observer.observe(this.elements[0].parentElement || this.elements[0]);
    }
  }

  /**
   * Calculate the initial state based on direction
   * @private
   * @returns {Object}
   */
  _getInitialState() {
    switch (this.direction) {
      case 'up':
        return { opacity: 0, transform: `translateY(${this.distance}px)` };
      case 'down':
        return { opacity: 0, transform: `translateY(-${this.distance}px)` };
      case 'left':
        return { opacity: 0, transform: `translateX(${this.distance}px)` };
      case 'right':
        return { opacity: 0, transform: `translateX(-${this.distance}px)` };
      case 'scale':
        return { opacity: 0, transform: `scale(${1 - (this.distance / 100)})` };
      case 'fade':
        return { opacity: 0, transform: 'none' };
      default:
        return { opacity: 0, transform: `translateY(${this.distance}px)` };
    }
  }

  /**
   * Calculate the final state based on direction
   * @private
   * @returns {Object}
   */
  _getFinalState() {
    return { opacity: 1, transform: 'none' };
  }

  /**
   * Animate elements in (entrance)
   * @returns {Promise} Resolves when animation completes
   */
  animateIn() {
    // Skip if already animated and once is true
    if (this.once && this.hasAnimated) {
      return Promise.resolve();
    }
    
    // Skip if reduced motion
    if (this.prefersReducedMotion) {
      this.elements.forEach((el) => {
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
      this.hasAnimated = true;
      this.onComplete?.();
      return Promise.resolve();
    }
    
    this.hasAnimated = true;
    this.onStart?.();
    
    const initialState = this._getInitialState();
    const finalState = this._getFinalState();
    
    // Prepare elements
    this.elements.forEach((el) => {
      el.style.opacity = initialState.opacity;
      el.style.transform = initialState.transform;
    });
    
    // Trigger animations
    return new Promise((resolve) => {
      const orderedElements = this.reverse ? [...this.elements].reverse() : this.elements;
      let completedCount = 0;
      const totalCount = orderedElements.length;
      
      orderedElements.forEach((el, index) => {
        const delay = Math.min(index * this.baseDelay, this.maxDelay);
        
        this.activeAnimations++;
        
        setTimeout(() => {
          el.style.transition = `all ${this.duration}ms ${this.easing}`;
          el.style.opacity = finalState.opacity;
          el.style.transform = finalState.transform;
          
          // Clean up and track completion
          const onTransitionEnd = () => {
            el.removeEventListener('transitionend', onTransitionEnd);
            el.style.transition = '';
            this.activeAnimations--;
            completedCount++;
            
            if (completedCount === totalCount) {
              this.onComplete?.();
              resolve();
            }
          };
          
          el.addEventListener('transitionend', onTransitionEnd);
          
          // Fallback in case transitionend doesn't fire
          setTimeout(() => {
            if (el.style.opacity !== String(finalState.opacity)) {
              onTransitionEnd();
            }
          }, this.duration + delay + 50);
          
        }, delay);
      });
    });
  }

  /**
   * Animate elements out (exit)
   * @returns {Promise} Resolves when animation completes
   */
  animateOut() {
    if (this.prefersReducedMotion) {
      this.elements.forEach((el) => {
        el.style.opacity = '0';
      });
      return Promise.resolve();
    }
    
    const finalState = this._getInitialState();
    
    return new Promise((resolve) => {
      const orderedElements = this.reverse ? this.elements : [...this.elements].reverse();
      let completedCount = 0;
      const totalCount = orderedElements.length;
      
      orderedElements.forEach((el, index) => {
        const delay = Math.min(index * this.baseDelay, this.maxDelay);
        
        setTimeout(() => {
          el.style.transition = `all ${this.duration}ms ${this.easing}`;
          el.style.opacity = finalState.opacity;
          el.style.transform = finalState.transform;
          
          const onTransitionEnd = () => {
            el.removeEventListener('transitionend', onTransitionEnd);
            completedCount++;
            
            if (completedCount === totalCount) {
              resolve();
            }
          };
          
          el.addEventListener('transitionend', onTransitionEnd);
          
        }, delay);
      });
    });
  }

  /**
   * Stop all animations
   * @param {boolean} finish - Jump to final state
   */
  stop(finish = false) {
    this.elements.forEach((el) => {
      el.style.transition = '';
      
      if (finish) {
        el.style.opacity = '1';
        el.style.transform = 'none';
      }
    });
    
    this.activeAnimations = 0;
  }

  /**
   * Reset elements to initial state
   */
  reset() {
    this.hasAnimated = false;
    const initialState = this._getInitialState();
    
    this.elements.forEach((el) => {
      el.style.transition = '';
      el.style.opacity = initialState.opacity;
      el.style.transform = initialState.transform;
    });
  }

  /**
   * Refresh the element list (useful for dynamic content)
   * @param {NodeList|Array|HTMLElement} newElements
   */
  refresh(newElements) {
    // Update elements
    if (newElements instanceof HTMLElement) {
      this.elements = [newElements];
    } else if (newElements instanceof NodeList) {
      this.elements = Array.from(newElements);
    } else if (Array.isArray(newElements)) {
      this.elements = newElements;
    }
    
    // Reset state
    this.hasAnimated = false;
  }

  /**
   * Destroy the stagger controller
   * @param {boolean} reset - Whether to reset element styles
   */
  destroy(reset = true) {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    
    if (reset) {
      this.elements.forEach((el) => {
        el.style.transition = '';
        el.style.opacity = '';
        el.style.transform = '';
      });
    }
    
    this.elements = [];
  }

  /**
   * Check if animation is active
   * @returns {boolean}
   */
  isAnimating() {
    return this.activeAnimations > 0;
  }

  /**
   * Get element count
   * @returns {number}
   */
  getElementCount() {
    return this.elements.length;
  }

  /**
   * Static utility: Quick stagger animation
   * @param {string|NodeList|Array} elements - Elements to animate
   * @param {Object} options - Animation options
   * @returns {LiquidStagger}
   */
  static animate(elements, options = {}) {
    let elementList;
    
    if (typeof elements === 'string') {
      elementList = document.querySelectorAll(elements);
    } else if (elements instanceof NodeList || Array.isArray(elements)) {
      elementList = elements;
    } else {
      elementList = [elements];
    }
    
    const stagger = new LiquidStagger(elementList, options);
    stagger.animateIn();
    return stagger;
  }

  /**
   * Static utility: Create scroll-triggered stagger
   * @param {string} containerSelector - Container to observe
   * @param {string} itemSelector - Items to animate
   * @param {Object} options - Animation options
   * @returns {LiquidStagger}
   */
  static onScroll(containerSelector, itemSelector, options = {}) {
    const container = document.querySelector(containerSelector);
    if (!container) {
      console.warn(`[LiquidStagger] Container not found: ${containerSelector}`);
      return null;
    }
    
    const items = container.querySelectorAll(itemSelector);
    
    return new LiquidStagger(items, {
      ...options,
      useObserver: true,
      observeContainer: containerSelector,
      once: true
    });
  }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LiquidStagger;
}

if (typeof exports !== 'undefined') {
  exports.LiquidStagger = LiquidStagger;
}
