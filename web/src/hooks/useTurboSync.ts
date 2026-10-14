import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/client';

export function useTurboSync() {
  const [signals, setSignals] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'ONLINE' | 'ERROR'>('CONNECTING');

  useEffect(() => {
    fetch(`${API_BASE_URL}/equity/signals?limit=500`)
      .then(res => {
        if (!res.ok) throw new Error("Backend unavailable");
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data)) {
          setSignals(data);
          setConnectionStatus('ONLINE');
        } else {
          setConnectionStatus('ERROR');
        }
      })
      .catch(err => {
        console.warn("[Turbo-Sync] Backend API connectivity notice:", err);
        setConnectionStatus('ERROR');
      });
  }, []);

  return { updates: signals, connectionStatus, firestoreSignals: signals, firestoreHistory: [], marketContext: null };
}
