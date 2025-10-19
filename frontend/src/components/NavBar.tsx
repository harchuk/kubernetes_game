import { Link, NavLink } from "react-router-dom";
import { Fragment } from "react";
import { Menu, Transition } from "@headlessui/react";
import { Bars3Icon } from "@heroicons/react/24/outline";

const navItems = [
  { to: "/", label: "Главная" },
  { to: "/lobby", label: "Лобби" },
];

export default function NavBar() {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-lg font-semibold text-primary">
          Kube Clash Online
        </Link>
        <nav className="hidden md:flex gap-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive ? "bg-primary/20 text-primary" : "text-slate-200 hover:text-primary"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="md:hidden">
          <Menu as="div" className="relative inline-block text-left">
            <Menu.Button className="inline-flex justify-center rounded-md bg-slate-800 px-3 py-2 text-sm font-medium text-slate-200 hover:bg-slate-700">
              <Bars3Icon className="h-5 w-5" />
            </Menu.Button>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 mt-2 w-40 origin-top-right divide-y divide-slate-700 rounded-md bg-slate-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                {navItems.map((item) => (
                  <Menu.Item key={item.to}>
                    {({ active }) => (
                      <NavLink
                        to={item.to}
                        className={`block px-4 py-2 text-sm ${active ? "bg-primary/20 text-primary" : "text-slate-200"}`}
                      >
                        {item.label}
                      </NavLink>
                    )}
                  </Menu.Item>
                ))}
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </header>
  );
}
