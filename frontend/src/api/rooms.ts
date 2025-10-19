import { apiClient } from "./client";

export interface RoomDetails {
  id: string;
  name: string;
  mode: "classic" | "junior";
  owner_id: string;
  capacity: number;
  is_open: boolean;
  created_at: string;
  members: Array<{
    user_id: string;
    display_name: string;
    alias: string;
    joined_at: string;
  }>;
}

export async function createRoom(input: {
  name: string;
  mode: "classic" | "junior";
  owner_id: string;
  capacity?: number;
}): Promise<RoomDetails> {
  const { data } = await apiClient.post<RoomDetails>("/rooms", input);
  return data;
}

export async function joinRoom(roomId: string, userId: string): Promise<RoomDetails> {
  const { data } = await apiClient.post<RoomDetails>(`/rooms/${roomId}/join`, {
    user_id: userId,
  });
  return data;
}

export async function fetchRoom(roomId: string): Promise<RoomDetails> {
  const { data } = await apiClient.get<RoomDetails>(`/rooms/${roomId}`);
  return data;
}
