import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { apiWsUrl } from "../api/client";
import { fetchRoom, joinRoom, RoomDetails } from "../api/rooms";
import { useGuestUser } from "../hooks/useGuestUser";
import { useCardCatalog } from "../hooks/useCardCatalog";

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
  const [sessionPlayers, setSessionPlayers] = useState<Array<{ user_id: string; alias: string }>>([]);
  const [turnInput, setTurnInput] = useState("play_card");
  const wsRef = useRef<WebSocket | null>(null);
  const cardCatalog = useCardCatalog(room?.mode ?? "classic");

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
    joinRoom(roomId, user.id)
      .then((details) => setRoom(details))
      .catch((error) => console.error("Failed to join room", error));
  }, [roomId, user]);

  useEffect(() => {
    if (!roomId || !user) return;

    const ws = new WebSocket(apiWsUrl(`/ws/rooms/${roomId}?user_id=${user.id}`));
    wsRef.current = ws;
    ws.onopen = () => setConnectionStatus("connected");
    ws.onclose = () => {
      setConnectionStatus("closed");
      wsRef.current = null;
    };
    ws.onerror = () => setConnectionStatus("error");
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "session_snapshot") {
          setSessionPlayers(data.players ?? []);
        } else if (data.type === "turn") {
          setMessages((prev) => [
            {
              id: data.turn_id ?? crypto.randomUUID(),
              type: "turn",
              payload: data,
              receivedAt: data.created_at ?? new Date().toISOString(),
            },
            ...prev.slice(0, 24),
          ]);
        } else {
          setMessages((prev) => [
            {
              id: crypto.randomUUID(),
              type: data.type ?? "event",
              payload: data,
              receivedAt: new Date().toISOString(),
            },
            ...prev.slice(0, 24),
          ]);
        }
      } catch (err) {
        console.error("Failed to parse message", err);
      }
    };

    return () => {
      wsRef.current = null;
      ws.close();
    };
  }, [roomId, user]);

  const members = useMemo(() => room?.members ?? [], [room]);
  const players = sessionPlayers.length > 0 ? sessionPlayers : members.map((m) => ({ user_id: m.user_id, alias: m.alias ?? m.display_name }));
  const marketCards = useMemo(() => cardCatalog.cards.slice(0, 3), [cardCatalog.cards]);

  const handleSendTurn = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(
      JSON.stringify({
        type: "turn",
        payload: {
          action: turnInput,
          timestamp: new Date().toISOString(),
        },
      })
    );
    setTurnInput("play_card");
  };

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-slate-100">Комната {room?.name ?? roomId}</h1>
        <p className="text-sm text-slate-400">
          {room?.mode === "junior" ? "Junior Mode" : "Classic Mode"} · {members.length}/{room?.capacity ?? 0} игроков · WebSocket: {connectionStatus}
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3 rounded-xl border border-slate-800 bg-slate-900/40 p-6 min-h-[420px] space-y-6">
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wide">Игроки</h2>
            <ul className="grid gap-3 md:grid-cols-2">
              {players.map((player) => (
                <li key={player.user_id} className="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-3">
                  <div className="flex items-center justify-between text-sm text-slate-200">
                    <span className="font-semibold">{player.alias}</span>
                    <span className="text-xs text-slate-500">{player.user_id.slice(0, 8)}</span>
                  </div>
                  <div className="mt-2 grid grid-cols-3 gap-2 text-xs text-slate-300">
                    <div className="rounded bg-slate-800/60 px-2 py-1">Энергия: 0</div>
                    <div className="rounded bg-slate-800/60 px-2 py-1">SLO: 0</div>
                    <div className="rounded bg-slate-800/60 px-2 py-1">Инциденты: 0</div>
                  </div>
                </li>
              ))}
              {players.length === 0 && <li className="text-xs text-slate-500">Пока никого нет</li>}
            </ul>
          </div>

          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wide">Рынок</h2>
            <div className="grid gap-3 md:grid-cols-3">
              {marketCards.map((card, idx) => (
                <div
                  key={card.id ?? `${card.name}-${idx}`}
                  className="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-3 text-xs text-slate-200"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm">{card.name}</span>
                    <span className="rounded-full bg-primary/20 px-2 py-0.5 text-primary">
                      {card.cost ?? 0}
                    </span>
                  </div>
                  {card.effect && <p className="mt-2 text-slate-400">{card.effect}</p>}
                  {card.action && <p className="mt-2 text-slate-400">{card.action}</p>}
                  {card.prerequisite && <p className="mt-1 text-slate-500">{card.prerequisite}</p>}
                  {typeof card.stars === "number" && (
                    <p className="mt-1 text-primary">⭐ Звёзды: {card.stars}</p>
                  )}
                </div>
              ))}
              {marketCards.length === 0 && <p className="text-xs text-slate-500">Карточки загружаются...</p>}
            </div>
          </div>

          <form onSubmit={handleSendTurn} className="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-3 flex items-center gap-3">
            <input
              className="flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:border-primary focus:outline-none"
              value={turnInput}
              onChange={(event) => setTurnInput(event.target.value)}
              placeholder="Например: play_card"
            />
            <button
              type="submit"
              className="rounded-md bg-primary px-4 py-2 text-xs font-semibold text-white hover:bg-primary/90"
              disabled={!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN}
            >
              Отправить ход
            </button>
          </form>
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
