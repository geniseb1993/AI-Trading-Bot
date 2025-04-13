// Prevent ResizeObserver loop limit exceeded error
const debounce = (fn, ms) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      timer = null;
      fn.apply(this, args);
    }, ms);
  };
};

export const installResizeObserverPolyfill = () => {
  if (typeof window === 'undefined' || !window.ResizeObserver) {
    return;
  }

  const observer = window.ResizeObserver;
  window.ResizeObserver = class ResizeObserver extends observer {
    constructor(callback) {
      callback = debounce(callback, 20);
      super(callback);
    }
  };
}; 