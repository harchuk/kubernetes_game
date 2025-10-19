import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { apiWsUrl } from "../api/client";
import { fetchRoom, joinRoom, RoomDetails } from "../api/rooms";
import { useGuestUser } from "../hooks/useGuestUser";

interface WsMessage {
  id: string;
  type: string;
  payload: unknown;
  receivedAt: string;
}

export default function TablePlaceholder() {
  const { roomId } = useParams();
  const { user } = useGuestUser();
  const [room, setRoom] = useState<RoomDetails | null>(null);
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting");

  useEffect(() => {
    let ignore = false;
    if (!roomId) return;
    fetchRoom(roomId)
      .then((details) => {
        if (!ignore) setRoom(details);
      })
      .catch((error) => console.error("Failed to load room", error));
    return () => {
      ignore = true;
    };
  }, [roomId]);

  useEffect(() => {
    if (!roomId || !user) return;
    joinRoom(roomId, user.id).catch((error) => console.error("Failed to join room", error));
  }, [roomId, user]);

  useEffect(() => {
    if (!roomId || !user) return;

    const ws = new WebSocket(apiWsUrl(`/ws/rooms/${roomId}?user_id=${user.id}`));
    ws.onopen = () => setConnectionStatus("connected");
    ws.onclose = () => setConnectionStatus("closed");
    ws.onerror = () => setConnectionStatus("error");
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prev) => [
          {
            id: crypto.randomUUID(),
            type: data.type ?? "unknown",
            payload: data,
            receivedAt: new Date().toISOString(),
          },
          ...prev.slice(0, 24),
        ]);
      } catch (err) {
        console.error("Failed to parse message", err);
      }
    };

    return () => ws.close();
  }, [roomId, user]);

  const members = useMemo(() => room?.members ?? [], [room]);

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-slate-100">Комната {room?.name ?? roomId}</h1>
        <p className="text-sm text-slate-400">
          {room?.mode === "junior" ? "Junior Mode" : "Classic Mode"} · {members.length}/{room?.capacity ?? 0} игроков · WebSocket: {connectionStatus}
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3 rounded-xl border border-slate-800 bg-slate-900/40 p-6 min-h-[420px]">
          <p className="text-slate-300 mb-4">Поле стола пока в разработке — карусель карт и realtime-эффекты появятся позже.</p>
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wide">Игроки</h2>
            <ul className="space-y-2">
              {members.map((member) => (
                <li key={member.user_id} className="rounded-md border border-slate-800 bg-slate-900/60 px-4 py-2 text-sm text-slate-200">
                  {member.display_name}
                </li>
              ))}
              {members.length === 0 && <li className="text-xs text-slate-500">Пока никого нет</li>}
            </ul>
          </div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 flex flex-col">
          <h2 className="text-sm font-semibold text-slate-200">Журнал WebSocket</h2>
          <p className="mt-2 text-xs text-slate-400">Отображает последние события. Позже заменим полноценным ходовым журналом.</p>
          <ul className="mt-4 space-y-2 text-xs text-slate-300 overflow-auto max-h-72">
            {messages.map((message) => (
              <li key={message.id} className="rounded-md border border-slate-800/60 bg-slate-900/70 px-3 py-2">
                <div className="flex justify-between">
                  <span className="font-semibold text-primary">{message.type}</span>
                  <span className="text-slate-500">{new Date(message.receivedAt).toLocaleTimeString()}</span>
                </div>
                <pre className="mt-1 whitespace-pre-wrap break-words text-slate-400">{JSON.stringify(message.payload, null, 2)}</pre>
              </li>
            ))}
            {messages.length === 0 && <li className="text-slate-500">Сообщений пока нет.</li>}
          </ul>
        </div>
      </div>
    </section>
  );
}
