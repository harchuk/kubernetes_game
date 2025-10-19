import "./styles.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { createRoot } from "react-dom/client";
import AppLayout from "./pages/AppLayout";
import HomePage from "./pages/HomePage";
import LobbyPage from "./pages/LobbyPage";
import TablePlaceholder from "./pages/TablePlaceholder";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "lobby", element: <LobbyPage /> },
      { path: "table/:roomId", element: <TablePlaceholder /> },
    ],
  },
]);

createRoot(document.getElementById("root") as HTMLElement).render(
  <RouterProvider router={router} />
);
