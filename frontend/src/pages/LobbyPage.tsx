import { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { createRoom, joinRoom } from "../api/rooms";
import { useRooms } from "../hooks/useRooms";
import { useGuestUser } from "../hooks/useGuestUser";

const modeLabel: Record<string, string> = {
  classic: "Classic",
  junior: "Junior",
};

export default function LobbyPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const selectedMode = useMemo(() => new URLSearchParams(location.search).get("mode") ?? undefined, [location.search]);

  const { user, loading: userLoading } = useGuestUser();
  const { rooms, loading, error, refresh } = useRooms(selectedMode);
  const [creating, setCreating] = useState(false);

  const handleCreateRoom = async () => {
    if (!user) return;
    const name = window.prompt("Название комнаты", `Cluster ${Math.floor(Math.random() * 100)}`);
    if (!name) return;
    setCreating(true);
    try {
      const room = await createRoom({
        name,
        mode: (selectedMode as "classic" | "junior") ?? "classic",
        owner_id: user.id,
      });
      navigate(`/table/${room.id}`);
    } catch (err) {
      console.error(err);
      window.alert("Не удалось создать комнату");
    } finally {
      setCreating(false);
    }
  };

  const handleJoinRoom = async (roomId: string) => {
    if (!user) return;
    try {
      await joinRoom(roomId, user.id);
      navigate(`/table/${roomId}`);
    } catch (err) {
      console.error(err);
      window.alert("Не удалось присоединиться к комнате");
    }
  };

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-100">Лобби</h1>
          <p className="text-sm text-slate-400">Выберите комнату или создайте новую.</p>
        </div>
        <div className="flex gap-3">
          <button
            className="rounded-md border border-primary px-4 py-2 text-sm font-semibold text-primary hover:bg-primary/10 disabled:opacity-50"
            onClick={handleCreateRoom}
            disabled={creating || userLoading}
          >
            Создать комнату
          </button>
          <button
            className="rounded-md border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:border-primary hover:text-primary"
            onClick={refresh}
          >
            Обновить список
          </button>
        </div>
      </header>

      {error && <div className="rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

      <div className="rounded-xl border border-slate-800 bg-slate-900/40">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-900/80 text-slate-300">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Название</th>
              <th className="px-4 py-3 text-left font-medium">Режим</th>
              <th className="px-4 py-3 text-left font-medium">Игроки</th>
              <th className="px-4 py-3 text-left font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-slate-400">
                  Загрузка...
                </td>
              </tr>
            ) : rooms.length > 0 ? (
              rooms.map((room) => (
                <tr key={room.id} className="border-t border-slate-800 text-slate-200">
                  <td className="px-4 py-3">{room.name}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                      {modeLabel[room.mode]}
                    </span>
                  </td>
                  <td className="px-4 py-3">{room.player_count} / {room.capacity}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleJoinRoom(room.id)}
                      className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-xs font-semibold text-white hover:bg-primary/90"
                    >
                      Присоединиться
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-slate-400">
                  Пока нет комнат в этом режиме.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
