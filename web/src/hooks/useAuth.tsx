import React, { createContext, useContext, useEffect, useState } from 'react';
import { onAuthStateChanged, User, signOut } from 'firebase/auth';
import { auth } from '../core/firebase';
import { apiClient } from '../api/client';

interface AuthContextType {
  user: User | null;
  isAdmin: boolean;
  isPremium: boolean;
  loading: boolean;
  logout: () => Promise<void>;
}

const ADMIN_EMAILS = [
  "admin@trademind.ai",
  "admin@trademindai.com",
  "lakshmistoresonline@gmail.com",
  "user@trademindai.com" // For testing admin dashboard
];

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAdmin: false,
  isPremium: false,
  loading: true,
  logout: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isPremium, setIsPremium] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      setIsAdmin(currentUser?.email ? ADMIN_EMAILS.includes(currentUser.email) : false);

      // Simulate entitlement check
      const premiumFlag = localStorage.getItem(`tm_premium_${currentUser?.uid}`);
      setIsPremium(!!premiumFlag || ADMIN_EMAILS.includes(currentUser?.email || ''));

      if (currentUser) {
        // Set Bearer token for all subsequent API calls
        const token = await currentUser.getIdToken();
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        delete apiClient.defaults.headers.common['Authorization'];
      }

      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const logout = async () => {
    await signOut(auth);
  };

  return (
    <AuthContext.Provider value={{ user, isAdmin, isPremium, loading, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
