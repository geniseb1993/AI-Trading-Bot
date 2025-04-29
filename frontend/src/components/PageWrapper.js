import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useData } from '../contexts/DataContext';

/**
 * PageWrapper component ensures data isolation between pages
 * by performing cleanup of specified data domains when unmounting
 */
const PageWrapper = ({ 
  children,                       // Page content to render
  domains = [],                   // Data domains to clear when navigating away
  resetOnUnmount = true,          // Whether to reset domains when component unmounts
  title = null,                   // Page title (optional)
  preserveScrollPosition = false  // Whether to preserve scroll position when navigating
}) => {
  const location = useLocation();
  const { clearDomainData } = useData();
  
  // Set document title if provided
  useEffect(() => {
    if (title) {
      const previousTitle = document.title;
      document.title = `${title} | AI Trading Bot`;
      
      return () => {
        document.title = previousTitle;
      };
    }
  }, [title]);
  
  // Reset domains data when unmounting if resetOnUnmount is true
  useEffect(() => {
    return () => {
      if (resetOnUnmount && domains.length > 0) {
        domains.forEach(domain => {
          clearDomainData(domain);
        });
        
        console.log(`[PageWrapper] Cleared state for domains: ${domains.join(', ')}`);
      }
    };
  }, [resetOnUnmount, domains, clearDomainData]);
  
  // Reset scroll position when navigating if preserveScrollPosition is false
  useEffect(() => {
    if (!preserveScrollPosition) {
      window.scrollTo(0, 0);
    }
  }, [location.pathname, preserveScrollPosition]);
  
  return (
    <div className="page-wrapper">
      {children}
    </div>
  );
};

export default PageWrapper; 