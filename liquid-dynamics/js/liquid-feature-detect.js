/**
 * Liquid Dynamics Feature Detection Script
 * Part of the Liquid Dynamics Design System
 * 
 * @version 1.0.0
 * @author Playlist Navigator Pro Team
 * @license MIT
 * 
 * Run this script early in the page lifecycle to detect browser capabilities
 * and apply appropriate fallback classes before rendering begins.
 * 
 * Usage:
 *   <script src="liquid-dynamics/js/liquid-feature-detect.js"></script>
 *   or
 *   <script>
 *     // Inline the detectFeatures() function in <head> for best performance
 *   </script>
 */

(function() {
  'use strict';

  /**
   * Detect all relevant browser features
   * @returns {Object} Feature detection results
   */
  function detectFeatures() {
    const features = {
      // CSS Feature Support
      backdropFilter: false,
      webkitBackdropFilter: false,
      containerQueries: false,
      cssCustomProperties: false,
      focusVisible: false,
      contentVisibility: false,
      clipPath: false,
      maskImage: false,
      
      // JavaScript APIs
      intersectionObserver: false,
      mutationObserver: false,
      resizeObserver: false,
      requestAnimationFrame: false,
      matchMedia: false,
      
      // Graphics
      webGL: false,
      canvas: false,
      
      // Device Capabilities
      touch: false,
      pointerEvents: false,
      highDPI: false,
      
      // User Preferences
      reducedMotion: false,
      highContrast: false,
      darkMode: false
    };

    // Test backdrop-filter support
    try {
      features.backdropFilter = CSS.supports('backdrop-filter', 'blur(10px)');
      features.webkitBackdropFilter = CSS.supports('-webkit-backdrop-filter', 'blur(10px)');
    } catch (e) {
      // Legacy fallback
      const el = document.createElement('div');
      features.backdropFilter = 'backdropFilter' in el.style;
      features.webkitBackdropFilter = 'webkitBackdropFilter' in el.style;
    }

    // Test other CSS features
    features.containerQueries = CSS.supports('container-type', 'inline-size');
    features.cssCustomProperties = CSS.supports('(--custom: property)');
    features.focusVisible = CSS.supports('selector(:focus-visible)');
    features.contentVisibility = CSS.supports('content-visibility', 'auto');
    features.clipPath = CSS.supports('clip-path', 'circle(50%)');
    features.maskImage = CSS.supports('mask-image', 'linear-gradient(black, transparent)');

    // Test JavaScript APIs
    features.intersectionObserver = 'IntersectionObserver' in window;
    features.mutationObserver = 'MutationObserver' in window;
    features.resizeObserver = 'ResizeObserver' in window;
    features.requestAnimationFrame = 'requestAnimationFrame' in window;
    features.matchMedia = 'matchMedia' in window;

    // Test graphics support
    features.canvas = !!document.createElement('canvas').getContext;
    try {
      const canvas = document.createElement('canvas');
      features.webGL = !!(window.WebGLRenderingContext && 
        (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      features.webGL = false;
    }

    // Device capabilities
    features.touch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    features.pointerEvents = 'PointerEvent' in window;
    features.highDPI = window.devicePixelRatio > 1;

    // User preferences
    features.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    features.highContrast = window.matchMedia('(prefers-contrast: high)').matches;
    features.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

    return features;
  }

  /**
   * Apply CSS classes based on feature detection
   * @param {Object} features - Feature detection results
   */
  function applyClasses(features) {
    const doc = document.documentElement;
    const body = document.body;
    
    // Create feature class name
    function addClass(className, condition) {
      if (condition) {
        doc.classList.add(className);
      } else {
        doc.classList.add('no-' + className);
      }
    }

    // Apply feature classes
    addClass('backdrop-filter', features.backdropFilter || features.webkitBackdropFilter);
    addClass('container-queries', features.containerQueries);
    addClass('js', true); // JavaScript is enabled (we're running!)
    
    // Apply device classes
    if (features.touch) {
      doc.classList.add('touch');
      body.classList.add('touch-device');
    } else {
      doc.classList.add('no-touch');
    }

    if (features.highDPI) {
      doc.classList.add('high-dpi');
    }

    // Apply preference classes
    if (features.reducedMotion) {
      doc.classList.add('prefers-reduced-motion');
      body.classList.add('prefers-reduced-motion');
    }

    if (features.highContrast) {
      doc.classList.add('prefers-high-contrast');
    }

    if (features.darkMode) {
      doc.classList.add('prefers-dark-mode');
    }

    // Apply fallback classes for missing features
    if (!features.backdropFilter && !features.webkitBackdropFilter) {
      body.classList.add('no-backdrop-filter');
    }

    if (!features.intersectionObserver) {
      doc.classList.add('no-intersection-observer');
    }

    if (!features.cssCustomProperties) {
      doc.classList.add('no-css-variables');
    }
  }

  /**
   * Store features in a global for later access
   * @param {Object} features - Feature detection results
   */
  function storeFeatures(features) {
    window.liquidFeatures = features;
    
    // Also store as JSON for easy inspection
    try {
      doc.setAttribute('data-liquid-features', JSON.stringify(features));
    } catch (e) {
      // Ignore JSON serialization errors
    }
  }

  /**
   * Main initialization
   */
  function init() {
    const features = detectFeatures();
    applyClasses(features);
    storeFeatures(features);
    
    // Log in debug mode
    if (window.location.search.includes('liquid-debug=true')) {
      console.log('[LiquidDynamics] Features detected:', features);
    }
  }

  // Run immediately if DOM is ready, otherwise wait
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose detection function globally
  window.detectLiquidFeatures = detectFeatures;
})();
