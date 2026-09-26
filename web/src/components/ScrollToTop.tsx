import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * ScrollToTop Component
 * Guarantees that whenever the route path changes (e.g. /dashboard -> /signals),
 * the window and main container automatically scroll instantly to the absolute top (y=0).
 */
export default function ScrollToTop() {
  const { pathname, search } = useLocation();

  useEffect(() => {
    // 1. Scroll window to absolute top
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'instant'
    });

    // 2. Reset scroll on document elements for browser compatibility
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;

    // 3. Reset scroll on any main layout container
    const mainContainer = document.querySelector('main');
    if (mainContainer) {
      mainContainer.scrollTop = 0;
    }
  }, [pathname, search]);

  return null;
}
