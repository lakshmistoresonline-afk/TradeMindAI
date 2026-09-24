import { useState, useEffect } from 'react';

export function useBackendHealth(pollIntervalMs: number = 5000) {
  const [isOnline, setIsOnline] = useState<boolean>(false);
  const [backendStatus, setBackendStatus] = useState<'ONLINE' | 'OFFLINE' | 'CHECKING'>('CHECKING');

  useEffect(() => {
    let isMounted = true;

    const checkHealth = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      try {
        const response = await fetch('http://localhost:8000/api/v1/health', {
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (response.ok && isMounted) {
          setIsOnline(true);
          setBackendStatus('ONLINE');
        } else if (isMounted) {
          setIsOnline(false);
          setBackendStatus('OFFLINE');
        }
      } catch {
        clearTimeout(timeoutId);
        if (isMounted) {
          setIsOnline(false);
          setBackendStatus('OFFLINE');
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, pollIntervalMs);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [pollIntervalMs]);

  return { isOnline, backendStatus };
}
