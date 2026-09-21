import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// AUTHORITATIVE PRODUCTION FIREBASE CONFIG (Hardened 4.2)
const firebaseConfig = {
  apiKey: "AIzaSyAV2mVlSuVSvM-FXVZtTsn06VsSP_mTr4k",
  authDomain: "com-webcraft-trademindai-c8f75.firebaseapp.com",
  projectId: "com-webcraft-trademindai-c8f75",
  storageBucket: "com-webcraft-trademindai-c8f75.firebasestorage.app",
  messagingSenderId: "595902577601",
  appId: "1:595902577601:web:583597c42cd8b544583c4b" // Optimized V2.3 Canonical ID
};

console.log("[Firebase] Initializing production node...");

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
