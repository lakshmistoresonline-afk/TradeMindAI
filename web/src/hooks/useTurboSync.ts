import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/client';
import { db } from '../core/firebase';
import { collection, query, limit, onSnapshot, doc } from 'firebase/firestore';

export function useTurboSync() {
  const [updates, setUpdates] = useState<any[]>([]);
  const [firestoreSignals, setFirestoreSignals] = useState<any[]>([]);
  const [firestoreHistory, setFirestoreHistory] = useState<any[]>([]);
  const [marketContext, setMarketContext] = useState<any>(null);
  const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'ONLINE' | 'ERROR'>('CONNECTING');

  useEffect(() => {
    // 1. SSE Connection (Backend Authority)
    const sseUrl = `${API_BASE_URL.replace('/api/v1', '')}/api/v1/stream/signals`;
    const eventSource = new EventSource(sseUrl);

    eventSource.onopen = () => {
      setConnectionStatus('ONLINE');
      console.log("[Turbo-Sync] SSE Connection Established");
    };

    eventSource.onerror = () => {
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
    const q = query(signalsRef, limit(1000)); // Increased limit to support full NIFTY 200 universe

    const unsubscribeSignals = onSnapshot(q, (snapshot) => {
      const signals = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })).sort((a: any, b: any) => {
        // V2.3 Sorting: Use mirrored_at (server time) first, then fallback to signal creation time
        const timeA = (a.mirrored_at?.seconds || 0) * 1000 || new Date(a.created_at || 0).getTime();
        const timeB = (b.mirrored_at?.seconds || 0) * 1000 || new Date(b.created_at || 0).getTime();
        return timeB - timeA;
      });
      console.log(`[Turbo-Sync] Firestore Mirror Sync: ${signals.length} signals`);
      setFirestoreSignals(signals);
    }, (err) => {
      console.error("[Turbo-Sync] Firestore Mirror Error:", err);
    });

    // 3. Firestore History Mirror Sync (1-Year Historical Shadow Signals)
    const historyRef = collection(db, "signals_history");
    const qHist = query(historyRef, limit(1000));
    const unsubscribeHistory = onSnapshot(qHist, (snapshot) => {
      const hist = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      console.log(`[Turbo-Sync] Firestore History Sync: ${hist.length} historical signals`);
      setFirestoreHistory(hist);
    }, (err) => {
      console.warn("[Turbo-Sync] Firestore History Mirror Notice (using default benchmark metrics):", err);
    });

    // 4. Listen to Local Master Heartbeat for Market Context
    const unsubscribeMarket = onSnapshot(doc(db, "system_metrics", "local_master"), (snapshot: any) => {
      if (snapshot.exists()) {
        const data = snapshot.data();
        console.log("[Turbo-Sync] Market Context received from local master.");
        setMarketContext(data.market_context);
      }
    });

    return () => {
      eventSource.close();
      unsubscribeSignals();
      unsubscribeHistory();
      unsubscribeMarket();
      console.log("[Turbo-Sync] SSE & Firestore Connections Closed");
    };
  }, []);

  // Merge updates (SSE) and firestoreSignals (Mirror)
  // Logic: Prefer SSE if ONLINE, otherwise use Firestore.
  const mergedSignals = connectionStatus === 'ONLINE' && updates.length > 0 ? updates : firestoreSignals;

  return { updates: mergedSignals, connectionStatus, firestoreSignals, firestoreHistory, marketContext };
}
