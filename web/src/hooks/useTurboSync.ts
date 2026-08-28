import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/client';

export function useTurboSync() {
  const [updates, setUpdates] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'ONLINE' | 'ERROR'>('CONNECTING');

  useEffect(() => {
    // SSE requires a full URL including protocol
    const sseUrl = `${API_BASE_URL.replace('/api/v1', '')}/api/v1/stream/signals`;
    const eventSource = new EventSource(sseUrl);

    eventSource.onopen = () => {
      setConnectionStatus('ONLINE');
      console.log("[Turbo-Sync] SSE Connection Established");
    };

    eventSource.onerror = (e) => {
      setConnectionStatus('ERROR');
      console.error("[Turbo-Sync] SSE Error:", e);
      eventSource.close();
    };

    eventSource.addEventListener('opportunity_update', (event: any) => {
      try {
        const data = JSON.parse(event.data);
        setUpdates(data);
      } catch (err) {
        console.error("[Turbo-Sync] Failed to parse SSE data:", err);
      }
    });

    return () => {
      eventSource.close();
      console.log("[Turbo-Sync] SSE Connection Closed");
    };
  }, []);

  return { updates, connectionStatus };
}
