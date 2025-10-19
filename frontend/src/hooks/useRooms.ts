import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api/client";

export interface RoomSummary {
  id: string;
  name: string;
  mode: "classic" | "junior";
  player_count: number;
  capacity: number;
  is_open: boolean;
  created_at: string;
}

export function useRooms(mode?: string) {
  const [rooms, setRooms] = useState<RoomSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRooms = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await apiClient.get<RoomSummary[]>("/rooms", {
        params: mode ? { mode } : undefined,
      });
      setRooms(data);
    } catch (err) {
      console.error(err);
      setError("Не удалось загрузить комнаты");
    } finally {
      setLoading(false);
    }
  }, [mode]);

  useEffect(() => {
    fetchRooms();
  }, [fetchRooms]);

  return { rooms, loading, error, refresh: fetchRooms };
}
