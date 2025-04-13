/**
 * Scroll Indicator Finder Utility
 * 
 * This utility helps identify scrollable elements in the application that might
 * benefit from scroll indicators by highlighting them with a colored border
 * and providing information about their scrollable status.
 * 
 * Usage:
 * 1. Import this file in your development environment
 * 2. Call enableScrollDebugger() in your browser console
 * 3. Scroll areas that could benefit from indicators will be highlighted
 * 4. Call disableScrollDebugger() to remove the highlights
 */

// Find all scrollable elements in the application
const findScrollableElements = () => {
  const allElements = document.querySelectorAll('*');
  const scrollableElements = [];
  
  allElements.forEach(el => {
    // Check if element has scrollable content
    const hasVerticalScroll = el.scrollHeight > el.clientHeight;
    const hasHorizontalScroll = el.scrollWidth > el.clientWidth;
    const computedStyle = window.getComputedStyle(el);
    const overflowY = computedStyle.getPropertyValue('overflow-y');
    const overflowX = computedStyle.getPropertyValue('overflow-x');
    
    // Is element scrollable with visible scrollbar?
    if (
      (hasVerticalScroll && ['auto', 'scroll', 'overlay'].includes(overflowY)) ||
      (hasHorizontalScroll && ['auto', 'scroll', 'overlay'].includes(overflowX))
    ) {
      scrollableElements.push({
        element: el,
        hasVerticalScroll,
        hasHorizontalScroll,
        scrollHeight: el.scrollHeight,
        clientHeight: el.clientHeight,
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        overflowY,
        overflowX
      });
    }
  });
  
  return scrollableElements;
};

// Highlight scrollable elements
const highlightScrollableElements = (scrollableElements) => {
  scrollableElements.forEach((info, index) => {
    const { element, hasVerticalScroll, hasHorizontalScroll } = info;
    
    // Create a unique ID for this element
    const id = `scroll-debug-${index}`;
    element.setAttribute('data-scroll-debug-id', id);
    
    // Add debug information overlay
    const infoElement = document.createElement('div');
    infoElement.id = `scroll-debug-info-${index}`;
    infoElement.style.position = 'absolute';
    infoElement.style.top = '0';
    infoElement.style.right = '0';
    infoElement.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    infoElement.style.color = 'white';
    infoElement.style.padding = '5px';
    infoElement.style.fontSize = '10px';
    infoElement.style.zIndex = '9999';
    infoElement.style.pointerEvents = 'none';
    
    // Display info about scrollability
    infoElement.innerHTML = `
      <div>Scroll Debug #${index}</div>
      <div>V-Scroll: ${hasVerticalScroll ? '✅' : '❌'}</div>
      <div>H-Scroll: ${hasHorizontalScroll ? '✅' : '❌'}</div>
      <div>Content: ${Math.round(info.scrollHeight)}px</div>
      <div>Visible: ${Math.round(info.clientHeight)}px</div>
    `;
    
    // Store original style
    element.setAttribute('data-original-style', element.getAttribute('style') || '');
    
    // Add highlight style
    element.style.border = hasVerticalScroll ? '2px solid #00aaff' : '2px solid #ff00aa';
    element.style.position = 'relative';
    
    // Append info element if not already there
    if (!document.getElementById(`scroll-debug-info-${index}`)) {
      element.appendChild(infoElement);
    }
  });
};

// Remove highlights from elements
const removeHighlights = () => {
  // Find all highlighted elements
  const highlightedElements = document.querySelectorAll('[data-scroll-debug-id]');
  
  highlightedElements.forEach(el => {
    // Restore original style
    const originalStyle = el.getAttribute('data-original-style');
    if (originalStyle) {
      el.setAttribute('style', originalStyle);
    } else {
      el.removeAttribute('style');
    }
    
    // Remove debug attributes
    el.removeAttribute('data-scroll-debug-id');
    el.removeAttribute('data-original-style');
    
    // Remove info overlays
    const infoElements = el.querySelectorAll('[id^="scroll-debug-info-"]');
    infoElements.forEach(infoEl => infoEl.remove());
  });
};

// Enable scroll debugger
export const enableScrollDebugger = () => {
  console.log('🔍 Scroll Indicator Finder: Enabled');
  const scrollableElements = findScrollableElements();
  console.log(`Found ${scrollableElements.length} scrollable elements`);
  highlightScrollableElements(scrollableElements);
  
  console.log('Elements that might benefit from scroll indicators:');
  scrollableElements.forEach((info, index) => {
    console.log(`${index}:`, {
      element: info.element,
      scrollHeight: info.scrollHeight,
      clientHeight: info.clientHeight,
      overflowY: info.overflowY
    });
  });
  
  return scrollableElements;
};

// Disable scroll debugger
export const disableScrollDebugger = () => {
  console.log('🔍 Scroll Indicator Finder: Disabled');
  removeHighlights();
};

// Auto-refresh on window resize (for development purposes)
export const enableAutoRefresh = () => {
  window.addEventListener('resize', () => {
    disableScrollDebugger();
    setTimeout(enableScrollDebugger, 500);
  });
  console.log('Auto-refresh enabled for scroll debugger');
};

export default {
  enableScrollDebugger,
  disableScrollDebugger,
  enableAutoRefresh
}; 