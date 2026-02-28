/**
 * Liquid Dynamics Test Suite
 * Comprehensive unit tests for all core modules
 * 
 * @version 1.0.0
 * @author Playlist Navigator Pro Team
 * 
 * Run with: npm test (if configured) or open in browser with test runner
 */

// Mock DOM environment for Node.js testing
if (typeof window === 'undefined') {
  const { JSDOM } = require('jsdom');
  const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
    pretendToBeVisual: true,
    resources: 'usable'
  });
  global.window = dom.window;
  global.document = dom.window.document;
  global.navigator = dom.window.navigator;
  global.requestAnimationFrame = (cb) => setTimeout(cb, 16);
  global.cancelAnimationFrame = (id) => clearTimeout(id);
  global.performance = { now: () => Date.now() };
  global.CSS = {
    supports: (prop, value) => {
      const supports = {
        'backdrop-filter': true,
        '-webkit-backdrop-filter': true,
        'container-type': true,
        '(--custom: property)': true,
        'selector(:focus-visible)': true,
        'content-visibility': true,
        'clip-path': true,
        'mask-image': true
      };
      return supports[prop] || false;
    }
  };
}

// Import modules
const LiquidSpring = require('../js/LiquidSpring.js');
const LiquidParallax = require('../js/LiquidParallax.js');
const LiquidStagger = require('../js/LiquidStagger.js');
const LiquidBackdropManager = require('../js/LiquidBackdropManager.js');
const LiquidDynamics = require('../js/LiquidDynamics.js');

// Test utilities
class TestRunner {
  constructor() {
    this.tests = [];
    this.passed = 0;
    this.failed = 0;
  }

  describe(name, fn) {
    console.log(`\n📦 ${name}`);
    fn();
  }

  it(description, fn) {
    this.tests.push({ description, fn });
  }

  async run() {
    console.log('\n🧪 Running Liquid Dynamics Test Suite\n' + '='.repeat(50));
    
    for (const test of this.tests) {
      try {
        await test.fn();
        console.log(`  ✅ ${test.description}`);
        this.passed++;
      } catch (error) {
        console.log(`  ❌ ${test.description}`);
        console.log(`     Error: ${error.message}`);
        this.failed++;
      }
    }
    
    console.log('\n' + '='.repeat(50));
    console.log(`📊 Results: ${this.passed} passed, ${this.failed} failed`);
    console.log(this.failed === 0 ? '🎉 All tests passed!' : '⚠️ Some tests failed');
    
    return { passed: this.passed, failed: this.failed };
  }

  assert(condition, message) {
    if (!condition) {
      throw new Error(message || 'Assertion failed');
    }
  }

  assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(message || `Expected ${expected}, got ${actual}`);
    }
  }

  assertApprox(actual, expected, tolerance = 0.01, message) {
    if (Math.abs(actual - expected) > tolerance) {
      throw new Error(message || `Expected ~${expected}, got ${actual}`);
    }
  }

  assertThrows(fn, message) {
    let threw = false;
    try {
      fn();
    } catch (e) {
      threw = true;
    }
    if (!threw) {
      throw new Error(message || 'Expected function to throw');
    }
  }
}

const test = new TestRunner();

// ========================================
// LiquidSpring Tests
// ========================================

test.describe('LiquidSpring', () => {
  test.it('should create instance with default config', () => {
    const spring = new LiquidSpring();
    test.assertEqual(spring.stiffness, 300, 'Default stiffness should be 300');
    test.assertEqual(spring.damping, 30, 'Default damping should be 30');
    test.assertEqual(spring.mass, 1, 'Default mass should be 1');
    test.assertEqual(spring.precision, 0.01, 'Default precision should be 0.01');
  });

  test.it('should create instance with custom config', () => {
    const spring = new LiquidSpring({
      stiffness: 500,
      damping: 40,
      mass: 2,
      precision: 0.001
    });
    test.assertEqual(spring.stiffness, 500, 'Custom stiffness should be 500');
    test.assertEqual(spring.damping, 40, 'Custom damping should be 40');
    test.assertEqual(spring.mass, 2, 'Custom mass should be 2');
    test.assertEqual(spring.precision, 0.001, 'Custom precision should be 0.001');
  });

  test.it('should create preset instances', () => {
    const gentle = LiquidSpring.preset('gentle');
    test.assertEqual(gentle.stiffness, 200, 'Gentle preset stiffness should be 200');
    
    const snappy = LiquidSpring.preset('snappy');
    test.assertEqual(snappy.stiffness, 400, 'Snappy preset stiffness should be 400');
    
    const bouncy = LiquidSpring.preset('bouncy');
    test.assertEqual(bouncy.damping, 15, 'Bouncy preset damping should be 15');
  });

  test.it('should animate and call callback', (done) => {
    const spring = new LiquidSpring();
    let called = false;
    
    spring.animate(0, 100, (value) => {
      called = true;
    }, { duration: 50 });
    
    setTimeout(() => {
      test.assert(called, 'Callback should have been called');
    }, 100);
  });

  test.it('should cancel animation', () => {
    const spring = new LiquidSpring();
    let callCount = 0;
    
    const id = spring.animate(0, 100, (value) => {
      callCount++;
    });
    
    spring.cancel(id);
    
    test.assert(!spring.isActive(id), 'Animation should not be active after cancel');
  });

  test.it('should cancel all animations', () => {
    const spring = new LiquidSpring();
    
    spring.animate(0, 100, () => {});
    spring.animate(0, 200, () => {});
    spring.animate(0, 300, () => {});
    
    test.assert(spring.getActiveCount() > 0, 'Should have active animations');
    
    spring.cancelAll();
    
    test.assertEqual(spring.getActiveCount(), 0, 'Should have no active animations after cancelAll');
  });

  test.it('should animate multiple values', () => {
    const spring = new LiquidSpring();
    const values = [];
    
    spring.animateMultiple([
      { from: 0, to: 100, callback: (v) => values.push(v) },
      { from: 0, to: 200, callback: (v) => values.push(v) }
    ], { duration: 50 });
    
    test.assert(values.length > 0, 'Should have called callbacks');
  });

  test.it('should respect reduced motion preference', () => {
    // Simulate reduced motion
    const originalMatchMedia = window.matchMedia;
    window.matchMedia = () => ({ matches: true, addEventListener: () => {} });
    
    const spring = new LiquidSpring();
    let called = false;
    
    spring.animate(0, 100, (value) => {
      called = true;
      test.assertEqual(value, 100, 'Should immediately jump to end value');
    });
    
    test.assert(called, 'Should immediately call callback with reduced motion');
    
    // Restore
    window.matchMedia = originalMatchMedia;
  });
});

// ========================================
// LiquidParallax Tests
// ========================================

test.describe('LiquidParallax', () => {
  test.it('should create instance with default config', () => {
    const parallax = new LiquidParallax({ manualInit: true });
    test.assertEqual(parallax.selector, '[data-parallax]', 'Default selector should be [data-parallax]');
    test.assertEqual(parallax.smoothScrolling, true, 'Smooth scrolling should be enabled by default');
    test.assertEqual(parallax.smoothFactor, 0.1, 'Default smooth factor should be 0.1');
  });

  test.it('should create instance with custom config', () => {
    const parallax = new LiquidParallax({
      selector: '.custom-parallax',
      smoothScrolling: false,
      smoothFactor: 0.5,
      manualInit: true
    });
    test.assertEqual(parallax.selector, '.custom-parallax', 'Custom selector should be set');
    test.assertEqual(parallax.smoothScrolling, false, 'Smooth scrolling should be disabled');
    test.assertEqual(parallax.smoothFactor, 0.5, 'Custom smooth factor should be set');
  });

  test.it('should register elements', () => {
    const parallax = new LiquidParallax({ manualInit: true });
    const el = document.createElement('div');
    el.setAttribute('data-parallax', '0.5');
    
    parallax.addElement(el, { speed: 0.5 });
    
    test.assert(parallax.hasElement(el), 'Element should be registered');
    test.assertEqual(parallax.getElementCount(), 1, 'Should have 1 element');
  });

  test.it('should remove elements', () => {
    const parallax = new LiquidParallax({ manualInit: true });
    const el = document.createElement('div');
    
    parallax.addElement(el, { speed: 0.5 });
    test.assertEqual(parallax.getElementCount(), 1, 'Should have 1 element');
    
    parallax.removeElement(el);
    test.assertEqual(parallax.getElementCount(), 0, 'Should have 0 elements');
    test.assert(!parallax.hasElement(el), 'Element should not be registered');
  });

  test.it('should get scroll info', () => {
    const parallax = new LiquidParallax({ manualInit: true });
    const info = parallax.getScrollInfo();
    
    test.assert(typeof info.y === 'number', 'Scroll Y should be a number');
    test.assert(typeof info.x === 'number', 'Scroll X should be a number');
  });

  test.it('should not initialize on mobile when disableOnMobile is true', () => {
    // Mock mobile viewport
    const originalInnerWidth = window.innerWidth;
    Object.defineProperty(window, 'innerWidth', { value: 375, writable: true });
    
    const parallax = new LiquidParallax({
      disableOnMobile: true,
      mobileBreakpoint: 768,
      manualInit: false
    });
    
    test.assert(!parallax.initialized, 'Should not initialize on mobile');
    
    // Restore
    Object.defineProperty(window, 'innerWidth', { value: originalInnerWidth });
  });
});

// ========================================
// LiquidStagger Tests
// ========================================

test.describe('LiquidStagger', () => {
  test.it('should create instance with default options', () => {
    const els = [document.createElement('div')];
    const stagger = new LiquidStagger(els);
    
    test.assertEqual(stagger.baseDelay, 50, 'Default baseDelay should be 50');
    test.assertEqual(stagger.maxDelay, 500, 'Default maxDelay should be 500');
    test.assertEqual(stagger.duration, 400, 'Default duration should be 400');
    test.assertEqual(stagger.direction, 'up', 'Default direction should be up');
  });

  test.it('should create instance with custom options', () => {
    const els = [document.createElement('div')];
    const stagger = new LiquidStagger(els, {
      baseDelay: 100,
      maxDelay: 1000,
      duration: 600,
      direction: 'scale'
    });
    
    test.assertEqual(stagger.baseDelay, 100, 'Custom baseDelay should be set');
    test.assertEqual(stagger.maxDelay, 1000, 'Custom maxDelay should be set');
    test.assertEqual(stagger.duration, 600, 'Custom duration should be set');
    test.assertEqual(stagger.direction, 'scale', 'Custom direction should be set');
  });

  test.it('should get correct element count', () => {
    const els = [
      document.createElement('div'),
      document.createElement('div'),
      document.createElement('div')
    ];
    const stagger = new LiquidStagger(els);
    
    test.assertEqual(stagger.getElementCount(), 3, 'Should have 3 elements');
  });

  test.it('should calculate initial state correctly', () => {
    const el = document.createElement('div');
    
    const up = new LiquidStagger([el], { direction: 'up', distance: 20 });
    test.assert(up._getInitialState().transform.includes('translateY(20px)'), 'Up direction should translate Y positively');
    
    const down = new LiquidStagger([el], { direction: 'down', distance: 20 });
    test.assert(down._getInitialState().transform.includes('translateY(-20px)'), 'Down direction should translate Y negatively');
    
    const left = new LiquidStagger([el], { direction: 'left', distance: 20 });
    test.assert(left._getInitialState().transform.includes('translateX(20px)'), 'Left direction should translate X positively');
    
    const scale = new LiquidStagger([el], { direction: 'scale', distance: 20 });
    test.assert(scale._getInitialState().transform.includes('scale(0.8)'), 'Scale direction should scale down');
  });

  test.it('should reset elements', () => {
    const el = document.createElement('div');
    const stagger = new LiquidStagger([el]);
    
    stagger.reset();
    
    test.assertEqual(el.style.opacity, '0', 'Element should be reset to opacity 0');
    test.assert(el.style.transform !== '', 'Element should have transform applied');
  });

  test.it('should stop animations', () => {
    const el = document.createElement('div');
    const stagger = new LiquidStagger([el]);
    
    stagger.stop();
    
    test.assertEqual(stagger.isAnimating(), false, 'Should not be animating after stop');
  });
});

// ========================================
// LiquidBackdropManager Tests
// ========================================

test.describe('LiquidBackdropManager', () => {
  test.it('should create instance with default config', () => {
    const manager = new LiquidBackdropManager({ autoInit: false });
    test.assertEqual(manager.selector, '[data-backdrop]', 'Default selector should be [data-backdrop]');
    test.assertEqual(manager.threshold, 0.1, 'Default threshold should be 0.1');
    test.assertEqual(manager.maxConcurrent, 10, 'Default maxConcurrent should be 10');
  });

  test.it('should register elements', () => {
    const manager = new LiquidBackdropManager({ autoInit: false });
    const el = document.createElement('div');
    
    manager.register(el);
    
    test.assert(manager.elements.has(el), 'Element should be registered');
  });

  test.it('should unregister elements', () => {
    const manager = new LiquidBackdropManager({ autoInit: false });
    const el = document.createElement('div');
    
    manager.register(el);
    manager.unregister(el);
    
    test.assert(!manager.elements.has(el), 'Element should not be registered');
  });

  test.it('should not double-register elements', () => {
    const manager = new LiquidBackdropManager({ autoInit: false });
    const el = document.createElement('div');
    
    manager.register(el);
    manager.register(el);
    
    test.assertEqual(manager.elements.size, 1, 'Should only have 1 registered element');
  });

  test.it('should get stats', () => {
    const manager = new LiquidBackdropManager({ autoInit: false });
    const stats = manager.getStats();
    
    test.assert(typeof stats.totalElements === 'number', 'Stats should include totalElements');
    test.assert(typeof stats.activeCount === 'number', 'Stats should include activeCount');
    test.assert(typeof stats.supportsBackdropFilter === 'boolean', 'Stats should include supportsBackdropFilter');
  });

  test.it('should enable and disable all backdrops', () => {
    const manager = new LiquidBackdropManager({ autoInit: false });
    const el1 = document.createElement('div');
    const el2 = document.createElement('div');
    
    manager.register(el1);
    manager.register(el2);
    
    manager.enableAll();
    test.assertEqual(manager.activeCount, 2, 'Should have 2 active backdrops');
    
    manager.disableAll();
    test.assertEqual(manager.activeCount, 0, 'Should have 0 active backdrops');
  });

  test.it('should check backdrop-filter support', () => {
    const supported = LiquidBackdropManager.isSupported();
    test.assert(typeof supported === 'boolean', 'isSupported should return a boolean');
  });
});

// ========================================
// LiquidDynamics Tests
// ========================================

test.describe('LiquidDynamics', () => {
  test.it('should create instance with default config', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    test.assertEqual(liquid.version, '1.0.0', 'Version should be 1.0.0');
    test.assertEqual(liquid.debug, false, 'Debug should be false by default');
    test.assertEqual(liquid.initialized, false, 'Should not be initialized yet');
  });

  test.it('should detect browser features', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    liquid._detectFeatures();
    
    test.assert(typeof liquid.featuresDetected.backdropFilter === 'boolean', 'Should detect backdrop-filter support');
    test.assert(typeof liquid.featuresDetected.intersectionObserver === 'boolean', 'Should detect IntersectionObserver');
    test.assert(typeof liquid.featuresDetected.prefersReducedMotion === 'boolean', 'Should detect reduced motion preference');
  });

  test.it('should initialize subsystems', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    liquid.init();
    
    test.assertEqual(liquid.initialized, true, 'Should be initialized');
    test.assert(liquid.subsystems.spring !== undefined, 'Spring subsystem should exist');
  });

  test.it('should get status', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    liquid.init();
    
    const status = liquid.getStatus();
    test.assert(typeof status.version === 'string', 'Status should include version');
    test.assert(typeof status.initialized === 'boolean', 'Status should include initialized');
    test.assert(typeof status.features === 'object', 'Status should include features');
    test.assert(typeof status.subsystems === 'object', 'Status should include subsystems');
  });

  test.it('should register event listeners', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    let called = false;
    
    liquid.on('test', () => {
      called = true;
    });
    
    liquid._emit('test');
    
    test.assert(called, 'Event listener should have been called');
  });

  test.it('should remove event listeners', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    let callCount = 0;
    
    const handler = () => {
      callCount++;
    };
    
    liquid.on('test', handler);
    liquid.off('test', handler);
    liquid._emit('test');
    
    test.assertEqual(callCount, 0, 'Event listener should have been removed');
  });

  test.it('should apply glass effect to element', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    const el = document.createElement('div');
    
    liquid.glass(el, 2);
    
    test.assert(el.classList.contains('liquid-glass-2'), 'Element should have liquid-glass-2 class');
  });

  test.it('should check feature support statically', () => {
    const features = LiquidDynamics.checkFeatures();
    test.assert(typeof features === 'object', 'Should return features object');
    test.assert(typeof features.backdropFilter === 'boolean', 'Should include backdropFilter');
  });
});

// ========================================
// Integration Tests
// ========================================

test.describe('Integration Tests', () => {
  test.it('should coordinate spring and stagger animations', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    liquid.init();
    
    const el = document.createElement('div');
    const stagger = liquid.stagger([el], { duration: 50 });
    
    test.assert(stagger !== null, 'Should create stagger instance');
    test.assertEqual(stagger.getElementCount(), 1, 'Stagger should have 1 element');
  });

  test.it('should handle rapid init/destroy cycles', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    
    liquid.init();
    test.assert(liquid.initialized, 'Should be initialized');
    
    liquid.destroy();
    test.assert(!liquid.initialized, 'Should not be initialized after destroy');
    
    liquid.init();
    test.assert(liquid.initialized, 'Should be initialized again');
    
    liquid.destroy();
  });

  test.it('should handle DOM changes with refresh', () => {
    const liquid = new LiquidDynamics({ autoInit: false });
    liquid.init();
    
    // Add new element to DOM
    const newEl = document.createElement('div');
    newEl.setAttribute('data-parallax', '0.5');
    document.body.appendChild(newEl);
    
    // Refresh should pick up new element
    liquid.refresh();
    
    document.body.removeChild(newEl);
    liquid.destroy();
  });
});

// ========================================
// Performance Tests
// ========================================

test.describe('Performance Tests', () => {
  test.it('should handle many simultaneous spring animations', () => {
    const spring = new LiquidSpring();
    const startTime = performance.now();
    
    // Create 50 animations
    for (let i = 0; i < 50; i++) {
      spring.animate(0, 100, () => {}, { duration: 100 });
    }
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    test.assert(duration < 100, `Creating 50 animations should take <100ms, took ${duration}ms`);
    
    spring.cancelAll();
  });

  test.it('should limit active backdrop filters', () => {
    const manager = new LiquidBackdropManager({ 
      autoInit: false,
      maxConcurrent: 5 
    });
    
    // Register more elements than max
    for (let i = 0; i < 10; i++) {
      const el = document.createElement('div');
      manager.register(el);
    }
    
    manager.enableAll();
    
    test.assert(manager.activeCount <= 5, 'Active count should not exceed maxConcurrent');
  });
});

// Run all tests
test.run().then((results) => {
  if (typeof process !== 'undefined') {
    process.exit(results.failed > 0 ? 1 : 0);
  }
});

// Export for module use
if (typeof module !== 'undefined') {
  module.exports = { TestRunner };
}
