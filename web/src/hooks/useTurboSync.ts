import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/client';

export function useTurboSync() {
  const [firestoreSignals, setFirestoreSignals] = useState<any[]>([]);
  const [firestoreHistory] = useState<any[]>([]);
  const [marketContext] = useState<any>(null);

  useEffect(() => {
    // 1. Load static signals.json bundle (496 Nifty 500 signals) - Zero Quota Cost
    fetch('/signals.json')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setFirestoreSignals(data);
          console.log(`[Turbo-Sync] Loaded ${data.length} static Nifty 500 signals.`);
        }
      })
      .catch(err => {
        console.warn("Static signals.json fetch notice:", err);
      });

    // 2. Fetch genuine signals from backend REST API if online
    fetch(`${API_BASE_URL}/equity/signals?limit=1000`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 50) {
          setFirestoreSignals(data);
          console.log(`[Turbo-Sync] Loaded ${data.length} genuine signals from backend API.`);
        }
      })
      .catch(err => {
        console.warn("REST API signal fetch notice:", err);
      });
  }, []);

  return { updates: firestoreSignals, connectionStatus: 'ONLINE', firestoreSignals, firestoreHistory, marketContext };
}
