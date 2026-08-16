import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const meta = import.meta as any;

const firebaseConfig = {
  apiKey: meta.env?.VITE_FIREBASE_API_KEY || "placeholder",
  authDomain: `${meta.env?.VITE_FIREBASE_PROJECT_ID || "com-webcraft-trademindai-c8f75"}.firebaseapp.com`,
  projectId: meta.env?.VITE_FIREBASE_PROJECT_ID || "com-webcraft-trademindai-c8f75",
  storageBucket: `${meta.env?.VITE_FIREBASE_PROJECT_ID || "com-webcraft-trademindai-c8f75"}.appspot.com`,
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
