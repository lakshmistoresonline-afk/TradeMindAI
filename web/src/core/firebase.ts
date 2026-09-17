import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// AUTHORITATIVE PRODUCTION FIREBASE CONFIG (Hardened 4.2)
const firebaseConfig = {
  apiKey: "AIzaSyAV2mVlSuVSvM-FXVZtTsn06VsSP_mTr4k",
  authDomain: "com-webcraft-trademindai-c8f75.firebaseapp.com",
  projectId: "com-webcraft-trademindai-c8f75",
  storageBucket: "com-webcraft-trademindai-c8f75.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef"
};

console.log("[Firebase] Initializing production node...");

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
