import { useState, useEffect } from 'react';
import { getEquitySignals } from '../api/client';

export function useTurboSync() {
  const [signals, setSignals] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'ONLINE' | 'OFFLINE_FALLBACK' | 'ERROR'>('CONNECTING');

  useEffect(() => {
    getEquitySignals({ limit: 1000 })
      .then(data => {
        if (Array.isArray(data)) {
          setSignals(data);
          setConnectionStatus('ONLINE');
        } else {
          throw new Error("Invalid response format");
        }
      })
      .catch((err) => {
        const status = err?.response?.status;
        const isQuarantined = status === 503 || (err.message && (err.message.includes("503") || err.message.includes("Quarantined")));
        if (isQuarantined) {
          console.warn("[Turbo-Sync] Quarantine active (503); suppressing offline fallback.");
          setConnectionStatus('ERROR');
          setSignals([]);
          return;
        }
        console.warn("[Turbo-Sync] Live API unavailable:", err);
        setConnectionStatus('ERROR');
        setSignals([]);
      });
  }, []);

  return { updates: signals, connectionStatus, firestoreSignals: signals, firestoreHistory: [], marketContext: null };
}
