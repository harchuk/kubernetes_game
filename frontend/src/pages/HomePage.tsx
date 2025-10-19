import { Link } from "react-router-dom";

const modes = [
  {
    id: "classic",
    title: "Classic Mode",
    description: "Полные правила с инфраструктурой, инцидентами и тактическими атаками.",
    badge: "Хардкор",
  },
  {
    id: "junior",
    title: "Junior Mode",
    description: "Упрощённая версия на 6+, быстрый набор звёзд, минимум саботажа.",
    badge: "6+",
  },
];

export default function HomePage() {
  return (
    <section className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-widest text-primary">Cluster Clash Online</p>
        <h1 className="text-3xl md:text-4xl font-bold text-slate-50">
          Добро пожаловать в цифровой куб-кластер
        </h1>
        <p className="text-slate-300 max-w-2xl">
          Соберите команду, создайте комнату и сыграйте партию в Kubernetes Cluster Clash прямо в браузере.
          Выберите режим, пригласите друзей и следите за каждым ходом в реальном времени.
        </p>
        <div className="flex gap-3">
          <Link
            to="/lobby"
            className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary/90"
          >
            Создать комнату
          </Link>
          <a
            href="https://github.com/harchuk/kubernetes_game"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-md border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:border-primary hover:text-primary"
          >
            Исходный код
          </a>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {modes.map((mode) => (
          <div key={mode.id} className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-lg">
            <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
              {mode.badge}
            </span>
            <h2 className="mt-4 text-2xl font-semibold text-slate-100">{mode.title}</h2>
            <p className="mt-2 text-sm text-slate-300">{mode.description}</p>
            <Link
              to={`/lobby?mode=${mode.id}`}
              className="mt-4 inline-flex items-center text-sm font-semibold text-primary hover:text-primary/80"
            >
              Выбрать режим →
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}
