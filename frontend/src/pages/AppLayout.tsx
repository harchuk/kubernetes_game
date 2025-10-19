import { Outlet } from "react-router-dom";
import NavBar from "../components/NavBar";

export default function AppLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1 container mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="py-4 text-center text-sm text-slate-400 border-t border-slate-800">
        Kubernetes Cluster Clash Online &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}
