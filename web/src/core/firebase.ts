import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const meta = import.meta as any;

const firebaseConfig = {
  apiKey: meta.env?.VITE_FIREBASE_API_KEY,
  authDomain: `${meta.env?.VITE_FIREBASE_PROJECT_ID || "com-webcraft-trademindai-c8f75"}.firebaseapp.com`,
  projectId: meta.env?.VITE_FIREBASE_PROJECT_ID || "com-webcraft-trademindai-c8f75",
  storageBucket: `${meta.env?.VITE_FIREBASE_PROJECT_ID || "com-webcraft-trademindai-c8f75"}.appspot.com`,
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef"
};

if (!firebaseConfig.apiKey || firebaseConfig.apiKey === "placeholder") {
    console.warn("CRITICAL: Firebase API Key is missing or invalid. Authentication will fail.");
}

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
