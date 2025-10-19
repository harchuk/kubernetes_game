import { useParams } from "react-router-dom";

export default function TablePlaceholder() {
  const { roomId } = useParams();
  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-slate-100">Комната {roomId}</h1>
        <p className="text-sm text-slate-400">
          Здесь появится интерактивное игровое поле с реальным временем, карточками и журналом.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3 rounded-xl border border-slate-800 bg-slate-900/40 p-6 min-h-[400px]">
          <p className="text-slate-300">Поле стола (в разработке).</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6">
          <h2 className="text-sm font-semibold text-slate-200">Журнал действий</h2>
          <p className="mt-2 text-xs text-slate-400">
            Пока заглушка — в будущем сюда будут приходить события из WebSocket.
          </p>
        </div>
      </div>
    </section>
  );
}
