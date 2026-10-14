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

      if (currentUser) {
        try {
          const token = await currentUser.getIdToken();
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;

          // Fetch server-side entitlements and roles
          const subRes = await apiClient.get('/user/subscription');
          setIsPremium(subRes.data?.plan_id && subRes.data.plan_id !== 'FREE');
          setIsAdmin(!!subRes.data?.isAdmin);
        } catch (e) {
          console.warn("Entitlement fetch notice:", e);
          setIsPremium(false);
          setIsAdmin(false);
        }
      } else {
        delete apiClient.defaults.headers.common['Authorization'];
        setIsPremium(false);
        setIsAdmin(false);
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
