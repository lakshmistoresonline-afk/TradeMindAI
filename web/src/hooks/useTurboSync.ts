import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/client';
import { db } from '../core/firebase';
import { collection, query, limit, onSnapshot, orderBy } from 'firebase/firestore';

export function useTurboSync() {
  const [updates, setUpdates] = useState<any[]>([]);
  const [firestoreSignals, setFirestoreSignals] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'ONLINE' | 'ERROR'>('CONNECTING');

  useEffect(() => {
    // 1. SSE Connection (Backend Authority)
    const sseUrl = `${API_BASE_URL.replace('/api/v1', '')}/api/v1/stream/signals`;
    const eventSource = new EventSource(sseUrl);

    eventSource.onopen = () => {
      setConnectionStatus('ONLINE');
      console.log("[Turbo-Sync] SSE Connection Established");
    };

    eventSource.onerror = (e) => {
      setConnectionStatus('ERROR');
      console.warn("[Turbo-Sync] SSE Unavailable. Using Firestore Mirror fallback.");
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

    // 2. Firestore Mirror Fallback (V2.3 Hybrid Support)
    // This ensures local signals mirrored to Firestore are visible even if Render is down.
    const signalsRef = collection(db, "signals");
    const q = query(signalsRef, orderBy("mirrored_at", "desc"), limit(20));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const signals = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      console.log(`[Turbo-Sync] Firestore Mirror Sync: ${signals.length} signals`);
      setFirestoreSignals(signals);
    }, (err) => {
      console.error("[Turbo-Sync] Firestore Mirror Error:", err);
    });

    return () => {
      eventSource.close();
      unsubscribe();
      console.log("[Turbo-Sync] SSE & Firestore Connections Closed");
    };
  }, []);

  // Merge updates (SSE) and firestoreSignals (Mirror)
  // Logic: Prefer SSE if ONLINE, otherwise use Firestore.
  const mergedSignals = connectionStatus === 'ONLINE' && updates.length > 0 ? updates : firestoreSignals;

  return { updates: mergedSignals, connectionStatus, firestoreSignals };
}
