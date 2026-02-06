/**
 * LiquidBackdropManager - Performance Optimization for Backdrop Filters
 * Part of the Liquid Dynamics Design System
 * 
 * @version 1.0.0
 * @author Playlist Navigator Pro Team
 * @license MIT
 * 
 * Manages backdrop-filter performance by disabling effects on off-screen elements.
 * Uses IntersectionObserver for efficient visibility detection.
 */

class LiquidBackdropManager {
  /**
   * Creates a new LiquidBackdropManager instance
   * 
   * @param {Object} config - Configuration options
   * @param {string} config.selector - CSS selector for managed elements (default: '[data-backdrop]')
   * @param {number} config.threshold - Visibility threshold 0-1 (default: 0.1)
   * @param {string} config.rootMargin - Root margin for observer (default: '50px')
   * @param {boolean} config.autoInit - Auto-initialize on creation (default: true)
   * @param {boolean} config.debug - Enable debug logging (default: false)
   */
  constructor(config = {}) {
    /** @type {string} CSS selector for managed elements */
    this.selector = config.selector ?? '[data-backdrop]';
    
    /** @type {number} Visibility threshold for intersection observer */
    this.threshold = config.threshold ?? 0.1;
    
    /** @type {string} Root margin for intersection observer */
    this.rootMargin = config.rootMargin ?? '50px';
    
    /** @type {boolean} Enable debug logging */
    this.debug = config.debug ?? false;
    
    /** @type {Set<HTMLElement>} Registered elements */
    this.elements = new Set();
    
    /** @type {Map<HTMLElement, ElementState>} Element states */
    this.states = new Map();
    
    /** @type {IntersectionObserver|null} Intersection observer instance */
    this.observer = null;
    
    /** @type {boolean} Whether system is initialized */
    this.initialized = false;
    
    /** @type {boolean} Whether browser supports backdrop-filter */
    this.supportsBackdropFilter = CSS.supports('backdrop-filter', 'blur(10px)');
    
    /** @type {number} Active backdrop filter count */
    this.activeCount = 0;
    
    /** @type {number} Maximum recommended concurrent backdrop filters */
    this.maxConcurrent = config.maxConcurrent ?? 10;
    
    // Auto-initialize if not disabled
    if (config.autoInit !== false) {
      this.init();
    }
  }

  /**
   * Initialize the backdrop manager
   * @returns {LiquidBackdropManager} this for chaining
   */
  init() {
    if (this.initialized) return this;
    
    // Check for backdrop-filter support
    if (!this.supportsBackdropFilter) {
      this._log('Backdrop filter not supported, applying fallbacks');
      this._applyFallbacks();
      return this;
    }
    
    // Set up intersection observer
    this._setupObserver();
    
    // Find and register existing elements
    this._registerExistingElements();
    
    // Watch for dynamically added elements
    this._setupMutationObserver();
    
    this.initialized = true;
    this._log(`Initialized, managing ${this.elements.size} elements`);
    
    return this;
  }

  /**
   * Set up intersection observer for visibility detection
   * @private
   */
  _setupObserver() {
    if (!('IntersectionObserver' in window)) {
      this._log('IntersectionObserver not supported, all elements will be active');
      return;
    }
    
    this.observer = new IntersectionObserver(
      (entries) => this._handleVisibilityChange(entries),
      {
        threshold: this.threshold,
        rootMargin: this.rootMargin
      }
    );
  }

  /**
   * Set up mutation observer for dynamic content
   * @private
   */
  _setupMutationObserver() {
    if (!('MutationObserver' in window)) return;
    
    const mutationObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if the added node matches our selector
            if (node.matches && node.matches(this.selector)) {
              this.register(node);
            }
            
            // Check children
            if (node.querySelectorAll) {
              node.querySelectorAll(this.selector).forEach((el) => {
                this.register(el);
              });
            }
          }
        });
      });
    });
    
    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  /**
   * Register existing elements matching the selector
   * @private
   */
  _registerExistingElements() {
    const elements = document.querySelectorAll(this.selector);
    elements.forEach((el) => this.register(el));
  }

  /**
   * Register an element for backdrop management
   * @param {HTMLElement} element - Element to register
   * @returns {LiquidBackdropManager} this for chaining
   */
  register(element) {
    if (this.elements.has(element)) return this;
    
    // Store original backdrop-filter value
    const computedStyle = window.getComputedStyle(element);
    const originalFilter = element.dataset.backdrop || computedStyle.backdropFilter;
    
    // Initialize state
    this.states.set(element, {
      originalFilter: originalFilter && originalFilter !== 'none' ? originalFilter : 'blur(16px)',
      isVisible: false,
      isActive: false
    });
    
    this.elements.add(element);
    
    // Observe if we have an observer
    if (this.observer) {
      this.observer.observe(element);
    } else {
      // No observer support, enable immediately
      this._enableBackdrop(element);
    }
    
    this._log('Registered element:', element);
    
    return this;
  }

  /**
   * Unregister an element from backdrop management
   * @param {HTMLElement} element - Element to unregister
   * @returns {LiquidBackdropManager} this for chaining
   */
  unregister(element) {
    if (!this.elements.has(element)) return this;
    
    // Restore original filter
    const state = this.states.get(element);
    if (state) {
      element.style.backdropFilter = '';
      element.style.webkitBackdropFilter = '';
    }
    
    // Unobserve
    if (this.observer) {
      this.observer.unobserve(element);
    }
    
    // Remove from collections
    this.states.delete(element);
    this.elements.delete(element);
    
    this._log('Unregistered element:', element);
    
    return this;
  }

  /**
   * Handle visibility changes from intersection observer
   * @private
   * @param {Array<IntersectionObserverEntry>} entries
   */
  _handleVisibilityChange(entries) {
    entries.forEach((entry) => {
      const element = entry.target;
      const state = this.states.get(element);
      
      if (!state) return;
      
      const isVisible = entry.isIntersecting;
      state.isVisible = isVisible;
      
      if (isVisible) {
        this._enableBackdrop(element);
      } else {
        this._disableBackdrop(element);
      }
    });
  }

  /**
   * Enable backdrop-filter on an element
   * @private
   * @param {HTMLElement} element
   */
  _enableBackdrop(element) {
    const state = this.states.get(element);
    if (!state || state.isActive) return;
    
    // Check if we're at the limit
    if (this.activeCount >= this.maxConcurrent) {
      this._log('Max concurrent backdrop filters reached, queuing element');
      return;
    }
    
    // Apply the backdrop filter
    element.style.backdropFilter = state.originalFilter;
    element.style.webkitBackdropFilter = state.originalFilter;
    
    state.isActive = true;
    this.activeCount++;
    
    this._log('Enabled backdrop on element, active count:', this.activeCount);
  }

  /**
   * Disable backdrop-filter on an element
   * @private
   * @param {HTMLElement} element
   */
  _disableBackdrop(element) {
    const state = this.states.get(element);
    if (!state || !state.isActive) return;
    
    // Remove the backdrop filter
    element.style.backdropFilter = 'none';
    element.style.webkitBackdropFilter = 'none';
    
    state.isActive = false;
    this.activeCount--;
    
    this._log('Disabled backdrop on element, active count:', this.activeCount);
  }

  /**
   * Apply fallback styles for browsers without backdrop-filter support
   * @private
   */
  _applyFallbacks() {
    document.body.classList.add('no-backdrop-filter');
  }

  /**
   * Force enable all backdrops (useful for screenshots/printing)
   * @returns {LiquidBackdropManager} this for chaining
   */
  enableAll() {
    this.elements.forEach((element) => {
      this._enableBackdrop(element);
    });
    return this;
  }

  /**
   * Force disable all backdrops
   * @returns {LiquidBackdropManager} this for chaining
   */
  disableAll() {
    this.elements.forEach((element) => {
      this._disableBackdrop(element);
    });
    return this;
  }

  /**
   * Refresh all elements (re-check visibility)
   * @returns {LiquidBackdropManager} this for chaining
   */
  refresh() {
    if (!this.observer) return this;
    
    this.elements.forEach((element) => {
      this.observer.unobserve(element);
      this.observer.observe(element);
    });
    
    return this;
  }

  /**
   * Get current statistics
   * @returns {Object}
   */
  getStats() {
    return {
      totalElements: this.elements.size,
      activeCount: this.activeCount,
      maxConcurrent: this.maxConcurrent,
      supportsBackdropFilter: this.supportsBackdropFilter,
      initialized: this.initialized
    };
  }

  /**
   * Pause management (keep current states)
   * @returns {LiquidBackdropManager} this for chaining
   */
  pause() {
    if (this.observer) {
      this.observer.disconnect();
    }
    return this;
  }

  /**
   * Resume management
   * @returns {LiquidBackdropManager} this for chaining
   */
  resume() {
    if (this.observer) {
      this.elements.forEach((element) => {
        this.observer.observe(element);
      });
    }
    return this;
  }

  /**
   * Destroy the manager and clean up
   * @param {boolean} restoreFilters - Whether to restore original filters
   */
  destroy(restoreFilters = true) {
    // Disconnect observers
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    
    // Restore or clear all filters
    this.elements.forEach((element) => {
      const state = this.states.get(element);
      
      if (restoreFilters && state) {
        element.style.backdropFilter = state.originalFilter;
        element.style.webkitBackdropFilter = state.originalFilter;
      } else {
        element.style.backdropFilter = '';
        element.style.webkitBackdropFilter = '';
      }
    });
    
    // Clear collections
    this.elements.clear();
    this.states.clear();
    this.activeCount = 0;
    this.initialized = false;
    
    this._log('Destroyed');
  }

  /**
   * Log message if debug is enabled
   * @private
   * @param {...any} args
   */
  _log(...args) {
    if (this.debug) {
      console.log('[LiquidBackdropManager]', ...args);
    }
  }

  /**
   * Static utility: Check backdrop-filter support
   * @returns {boolean}
   */
  static isSupported() {
    return CSS.supports('backdrop-filter', 'blur(10px)');
  }

  /**
   * Static utility: Quick initialization
   * @param {string} selector - CSS selector for elements
   * @param {Object} options - Configuration options
   * @returns {LiquidBackdropManager}
   */
  static init(selector, options = {}) {
    return new LiquidBackdropManager({
      selector,
      ...options,
      autoInit: true
    });
  }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LiquidBackdropManager;
}

if (typeof exports !== 'undefined') {
  exports.LiquidBackdropManager = LiquidBackdropManager;
}
