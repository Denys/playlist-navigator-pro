/**
 * Liquid Glass Integration - Playlist Navigator Pro
 * Interactive behaviors and animations for the liquid glass design system
 * 
 * @version 2.0.0
 * 
 * Features:
 * - Cursor-reactive light refraction
 * - Scroll-based header transformations
 * - Spring physics for hover states
 * - Modal management system
 * - Tab switching with smooth transitions
 * - Reduced motion detection
 */

(function() {
  'use strict';

  // ========================================
  // CONFIGURATION
  // ========================================
  
  const CONFIG = {
    // Animation settings
    spring: {
      stiffness: 300,
      damping: 30,
      mass: 1
    },
    
    // Light refraction settings
    lightRefraction: {
      throttle: 16, // 60fps
      intensity: 0.15
    },
    
    // Scroll settings
    scroll: {
      headerTransformThreshold: 50,
      throttle: 10
    },
    
    // Reduced motion detection
    prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    isTouchDevice: window.matchMedia('(pointer: coarse)').matches
  };

  // ========================================
  // UTILITY FUNCTIONS
  // ========================================
  
  const utils = {
    // Throttle function execution
    throttle(func, limit) {
      let inThrottle;
      return function(...args) {
        if (!inThrottle) {
          func.apply(this, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    },
    
    // Debounce function execution
    debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    },
    
    // Linear interpolation for smooth animations
    lerp(start, end, factor) {
      return start + (end - start) * factor;
    },
    
    // Spring physics calculation
    springPhysics(current, target, velocity, config = CONFIG.spring) {
      const springForce = (target - current) * config.stiffness;
      const dampingForce = velocity * config.damping;
      const acceleration = (springForce - dampingForce) / config.mass;
      
      return {
        position: current + velocity,
        velocity: velocity + acceleration * 0.016 // 60fps delta
      };
    },
    
    // Check if element is in viewport
    isInViewport(element, threshold = 0) {
      const rect = element.getBoundingClientRect();
      return (
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) - threshold &&
        rect.bottom >= threshold
      );
    }
  };

  // ========================================
  // LIGHT REFRACTION SYSTEM
  // ========================================
  
  class LightRefraction {
    constructor() {
      if (CONFIG.prefersReducedMotion || CONFIG.isTouchDevice) return;
      
      this.elements = document.querySelectorAll(
        '.liquid-card-float, .liquid-playlist-card, .liquid-video-card, ' +
        '.liquid-product-card, .liquid-indexer-card'
      );
      this.throttledUpdate = utils.throttle(this.update.bind(this), CONFIG.lightRefraction.throttle);
      
      this.init();
    }
    
    init() {
      document.addEventListener('mousemove', this.throttledUpdate);
      
      // Set initial light position
      document.documentElement.style.setProperty('--light-x', '50%');
      document.documentElement.style.setProperty('--light-y', '50%');
    }
    
    update(e) {
      this.elements.forEach(element => {
        if (!utils.isInViewport(element)) return;
        
        const rect = element.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        
        element.style.setProperty('--light-x', `${Math.max(0, Math.min(100, x))}%`);
        element.style.setProperty('--light-y', `${Math.max(0, Math.min(100, y))}%`);
      });
    }
  }

  // ========================================
  // HEADER SCROLL TRANSFORM
  // ========================================
  
  class HeaderTransform {
    constructor() {
      this.header = document.querySelector('.liquid-header');
      if (!this.header) return;
      
      this.lastScrollY = 0;
      this.ticking = false;
      
      this.init();
    }
    
    init() {
      window.addEventListener('scroll', () => {
        if (!this.ticking) {
          requestAnimationFrame(() => {
            this.update();
            this.ticking = false;
          });
          this.ticking = true;
        }
      }, { passive: true });
    }
    
    update() {
      const scrollY = window.scrollY;
      
      if (scrollY > CONFIG.scroll.headerTransformThreshold) {
        this.header.classList.add('liquid-header--scrolled');
      } else {
        this.header.classList.remove('liquid-header--scrolled');
      }
      
      this.lastScrollY = scrollY;
    }
  }

  // ========================================
  // TAB NAVIGATION SYSTEM
  // ========================================
  
  class TabNavigation {
    constructor() {
      this.navButtons = document.querySelectorAll('.liquid-nav-orb');
      this.tabContents = document.querySelectorAll('.liquid-tab-content');
      this.activeTab = 'indexer';
      
      this.init();
    }
    
    init() {
      this.navButtons.forEach(button => {
        button.addEventListener('click', (e) => {
          const tabId = button.dataset.tab;
          if (tabId && tabId !== this.activeTab) {
            this.switchTab(tabId);
          }
        });
      });
      
      // Handle initial hash
      const hash = window.location.hash.slice(1);
      if (hash && document.getElementById(`tab-${hash}`)) {
        this.switchTab(hash);
      }
    }
    
    switchTab(tabId) {
      // Update nav buttons
      this.navButtons.forEach(button => {
        if (button.dataset.tab === tabId) {
          button.classList.add('active');
        } else {
          button.classList.remove('active');
        }
      });
      
      // Animate tab content transition
      const currentContent = document.querySelector('.liquid-tab-content.active');
      const newContent = document.getElementById(`tab-${tabId}`);
      
      if (currentContent && newContent) {
        // Fade out current
        currentContent.style.opacity = '0';
        currentContent.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
          currentContent.classList.remove('active');
          newContent.classList.add('active');
          
          // Fade in new
          requestAnimationFrame(() => {
            newContent.style.opacity = '1';
            newContent.style.transform = 'translateY(0)';
          });
        }, 300);
      }
      
      this.activeTab = tabId;
      
      // Update URL hash without jumping
      history.pushState(null, null, `#${tabId}`);
      
      // Trigger module-specific initialization
      this.initializeModule(tabId);
    }
    
    initializeModule(tabId) {
      switch(tabId) {
        case 'mindmap':
          if (typeof loadMindMap === 'function') {
            loadMindMap();
          }
          break;
        case 'store':
          if (typeof initStore === 'function') {
            initStore();
          }
          break;
      }
    }
  }

  // ========================================
  // MODAL MANAGEMENT SYSTEM
  // ========================================
  
  class ModalManager {
    constructor() {
      this.activeModal = null;
      this.focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
      
      this.init();
    }
    
    init() {
      // Close on backdrop click
      document.addEventListener('click', (e) => {
        if (e.target.classList.contains('liquid-modal-backdrop')) {
          this.close();
        }
      });
      
      // Close on escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.activeModal) {
          this.close();
        }
      });
    }
    
    open(modalId) {
      const modal = document.getElementById(modalId);
      if (!modal) return;
      
      // Store currently focused element
      this.previousFocus = document.activeElement;
      
      // Show backdrop
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
      
      this.activeModal = modal;
      
      // Animate in
      requestAnimationFrame(() => {
        modal.querySelector('.liquid-modal').style.transform = 'scale(1) translateY(0)';
        modal.querySelector('.liquid-modal').style.opacity = '1';
      });
      
      // Trap focus
      this.trapFocus(modal);
      
      // Focus first element
      const focusable = modal.querySelectorAll(this.focusableElements);
      if (focusable.length) {
        focusable[0].focus();
      }
    }
    
    close() {
      if (!this.activeModal) return;
      
      const modalContent = this.activeModal.querySelector('.liquid-modal');
      
      // Animate out
      modalContent.style.transform = 'scale(0.95) translateY(20px)';
      modalContent.style.opacity = '0';
      
      setTimeout(() => {
        this.activeModal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Restore focus
        if (this.previousFocus) {
          this.previousFocus.focus();
        }
        
        this.activeModal = null;
      }, 300);
    }
    
    trapFocus(modal) {
      const focusable = modal.querySelectorAll(this.focusableElements);
      const firstFocusable = focusable[0];
      const lastFocusable = focusable[focusable.length - 1];
      
      modal.addEventListener('keydown', (e) => {
        if (e.key !== 'Tab') return;
        
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            lastFocusable.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastFocusable) {
            firstFocusable.focus();
            e.preventDefault();
          }
        }
      });
    }
  }

  // ========================================
  // DRAG AND DROP SYSTEM (Playlist)
  // ========================================
  
  class DragDropManager {
    constructor() {
      this.draggedElement = null;
      this.dragSource = null;
      
      this.init();
    }
    
    init() {
      const containers = document.querySelectorAll('.liquid-playlist-grid, .liquid-droppable');
      
      containers.forEach(container => {
        container.addEventListener('dragover', this.handleDragOver.bind(this));
        container.addEventListener('drop', this.handleDrop.bind(this));
        container.addEventListener('dragleave', this.handleDragLeave.bind(this));
      });
      
      const draggables = document.querySelectorAll('.liquid-draggable');
      draggables.forEach(draggable => {
        draggable.setAttribute('draggable', 'true');
        draggable.addEventListener('dragstart', this.handleDragStart.bind(this));
        draggable.addEventListener('dragend', this.handleDragEnd.bind(this));
      });
    }
    
    handleDragStart(e) {
      this.draggedElement = e.target;
      this.dragSource = e.target.parentElement;
      
      e.target.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
      
      // Set drag image
      const rect = e.target.getBoundingClientRect();
      e.dataTransfer.setDragImage(e.target, rect.width / 2, rect.height / 2);
    }
    
    handleDragOver(e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      
      const target = e.target.closest('.liquid-playlist-card, .liquid-droppable');
      if (target && target !== this.draggedElement) {
        target.classList.add('drag-over');
      }
    }
    
    handleDragLeave(e) {
      const target = e.target.closest('.liquid-playlist-card, .liquid-droppable');
      if (target) {
        target.classList.remove('drag-over');
      }
    }
    
    handleDrop(e) {
      e.preventDefault();
      
      const target = e.target.closest('.liquid-playlist-card, .liquid-droppable');
      if (target && target !== this.draggedElement) {
        target.classList.remove('drag-over');
        
        // Swap positions or move to new container
        if (target.classList.contains('liquid-droppable')) {
          target.appendChild(this.draggedElement);
        } else {
          // Swap with target
          const parent = target.parentElement;
          const nextSibling = target.nextSibling === this.draggedElement ? target : target.nextSibling;
          parent.insertBefore(this.draggedElement, nextSibling);
        }
        
        // Trigger reorder event
        this.onReorder();
      }
    }
    
    handleDragEnd(e) {
      e.target.classList.remove('dragging');
      document.querySelectorAll('.drag-over').forEach(el => {
        el.classList.remove('drag-over');
      });
      
      this.draggedElement = null;
      this.dragSource = null;
    }
    
    onReorder() {
      // Dispatch custom event for app to handle
      document.dispatchEvent(new CustomEvent('playlistReordered'));
    }
  }

  // ========================================
  // STAGGER ANIMATION SYSTEM
  // ========================================
  
  class StaggerAnimation {
    constructor() {
      this.observer = new IntersectionObserver(
        this.handleIntersection.bind(this),
        { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
      );
      
      this.init();
    }
    
    init() {
      const containers = document.querySelectorAll(
        '.liquid-playlist-grid, .liquid-gallery-grid, .liquid-store-categories'
      );
      
      containers.forEach(container => {
        const children = container.children;
        Array.from(children).forEach((child, index) => {
          child.style.opacity = '0';
          child.style.transform = 'translateY(20px)';
          child.dataset.staggerIndex = index;
          this.observer.observe(child);
        });
      });
    }
    
    handleIntersection(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target;
          const index = parseInt(element.dataset.staggerIndex) || 0;
          
          setTimeout(() => {
            element.style.transition = 'opacity 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
          }, index * 80);
          
          this.observer.unobserve(element);
        }
      });
    }
  }

  // ========================================
  // TOAST NOTIFICATION SYSTEM
  // ========================================
  
  class ToastSystem {
    constructor() {
      this.container = null;
      this.toasts = [];
      this.init();
    }
    
    init() {
      this.container = document.createElement('div');
      this.container.className = 'liquid-toast-container';
      this.container.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 12px;
      `;
      document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', duration = 4000) {
      const toast = document.createElement('div');
      toast.className = `liquid-toast liquid-toast--${type}`;
      
      const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠'
      };
      
      toast.innerHTML = `
        <span style="font-size: 1.2rem;">${icons[type] || icons.info}</span>
        <span>${message}</span>
      `;
      
      this.container.appendChild(toast);
      
      // Auto remove
      setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => {
          toast.remove();
        }, 300);
      }, duration);
    }
  }

  // ========================================
  // PERFORMANCE MONITOR
  // ========================================
  
  class PerformanceMonitor {
    constructor() {
      this.metrics = {
        fps: [],
        memory: []
      };
      
      if (process.env.NODE_ENV === 'development') {
        this.init();
      }
    }
    
    init() {
      this.measureFPS();
    }
    
    measureFPS() {
      let lastTime = performance.now();
      let frames = 0;
      
      const count = () => {
        frames++;
        const now = performance.now();
        
        if (now - lastTime >= 1000) {
          this.metrics.fps.push(frames);
          if (this.metrics.fps.length > 10) this.metrics.fps.shift();
          frames = 0;
          lastTime = now;
        }
        
        requestAnimationFrame(count);
      };
      
      requestAnimationFrame(count);
    }
    
    getAverageFPS() {
      if (this.metrics.fps.length === 0) return 60;
      return this.metrics.fps.reduce((a, b) => a + b, 0) / this.metrics.fps.length;
    }
    
    shouldReduceEffects() {
      return this.getAverageFPS() < 30;
    }
  }

  // ========================================
  // INITIALIZATION
  // ========================================
  
  // Wait for DOM ready
  function init() {
    // Initialize all systems
    const lightRefraction = new LightRefraction();
    const headerTransform = new HeaderTransform();
    const tabNavigation = new TabNavigation();
    const modalManager = new ModalManager();
    const dragDropManager = new DragDropManager();
    const staggerAnimation = new StaggerAnimation();
    const toastSystem = new ToastSystem();
    
    // Expose global API
    window.LiquidGlass = {
      modal: modalManager,
      toast: toastSystem,
      config: CONFIG,
      
      // Public methods
      openModal: (id) => modalManager.open(id),
      closeModal: () => modalManager.close(),
      showToast: (message, type, duration) => toastSystem.show(message, type, duration)
    };
    
    // Add loaded class for initial animations
    document.body.classList.add('liquid-loaded');
    
    console.log('🌊 Liquid Glass Design System initialized');
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
