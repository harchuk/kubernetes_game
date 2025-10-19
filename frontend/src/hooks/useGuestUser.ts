import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

export interface User {
  id: string;
  display_name: string;
  created_at: string;
}

const STORAGE_KEY = "kco_user";

export function useGuestUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function ensureUser() {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setUser(JSON.parse(stored));
        setLoading(false);
        return;
      }

      try {
        const guestName = `Guest-${crypto.randomUUID().slice(0, 5)}`;
        const response = await apiClient.post<User>("/users", {
          display_name: guestName,
        });
        localStorage.setItem(STORAGE_KEY, JSON.stringify(response.data));
        setUser(response.data);
      } catch (error) {
        console.error("Failed to create guest user", error);
      } finally {
        setLoading(false);
      }
    }

    ensureUser();
  }, []);

  return { user, loading };
}
