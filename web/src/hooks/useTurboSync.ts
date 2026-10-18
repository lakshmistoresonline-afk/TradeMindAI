import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/client';

export function useTurboSync() {
  const [signals, setSignals] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'ONLINE' | 'OFFLINE_FALLBACK' | 'ERROR'>('CONNECTING');

  useEffect(() => {
    fetch(`${API_BASE_URL}/equity/signals?limit=1000`)
      .then(res => {
        if (!res.ok) throw new Error("Backend API unavailable");
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data)) {
          setSignals(data);
          setConnectionStatus('ONLINE');
        } else {
          throw new Error("Invalid response format");
        }
      })
      .catch((err) => {
        console.warn("[Turbo-Sync] Live API unavailable, checking static offline cache:", err);
        fetch('/signals.json')
          .then(res => res.json())
          .then(fallbackData => {
            if (Array.isArray(fallbackData)) {
              setSignals(fallbackData);
              setConnectionStatus('OFFLINE_FALLBACK');
            } else {
              setConnectionStatus('ERROR');
            }
          })
          .catch(fallbackErr => {
            console.error("[Turbo-Sync] Static fallback failed:", fallbackErr);
            setConnectionStatus('ERROR');
          });
      });
  }, []);

  return { updates: signals, connectionStatus, firestoreSignals: signals, firestoreHistory: [], marketContext: null };
}
