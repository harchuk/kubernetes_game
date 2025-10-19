import { Link, useLocation } from "react-router-dom";
import { useMemo } from "react";

const mockRooms = [
  { id: "alpha", name: "Кластер Альфа", mode: "classic", players: 2, capacity: 4 },
  { id: "beta", name: "Junior Fun", mode: "junior", players: 3, capacity: 4 },
];

const modeLabel: Record<string, string> = {
  classic: "Classic",
  junior: "Junior",
};

export default function LobbyPage() {
  const location = useLocation();
  const selectedMode = useMemo(() => new URLSearchParams(location.search).get("mode"), [location.search]);

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-100">Лобби</h1>
          <p className="text-sm text-slate-400">Выберите комнату или создайте новую.</p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-md border border-primary px-4 py-2 text-sm font-semibold text-primary hover:bg-primary/10">
            Создать комнату
          </button>
          <button className="rounded-md border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:border-primary hover:text-primary">
            Обновить список
          </button>
        </div>
      </header>

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
            {mockRooms
              .filter((room) => (selectedMode ? room.mode === selectedMode : true))
              .map((room) => (
                <tr key={room.id} className="border-t border-slate-800 text-slate-200">
                  <td className="px-4 py-3">{room.name}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                      {modeLabel[room.mode]}
                    </span>
                  </td>
                  <td className="px-4 py-3">{room.players} / {room.capacity}</td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/table/${room.id}`}
                      className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-xs font-semibold text-white hover:bg-primary/90"
                    >
                      Присоединиться
                    </Link>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>

        {mockRooms.filter((room) => (selectedMode ? room.mode === selectedMode : true)).length === 0 && (
          <div className="px-4 py-6 text-center text-slate-400">Пока нет комнат в этом режиме.</div>
        )}
      </div>
    </section>
  );
}
