import MainLayout from "../layouts/MainLayout";
import {
  ShieldCheck,
  ShieldAlert,
  Activity,
  Download,
  User,
  FileSearch,
} from "lucide-react";
import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard() {
  const username = localStorage.getItem("username") || "User";
  const [stats, setStats] = useState(null);

useEffect(() => {

  const load = () => {

    const token = localStorage.getItem("token");

    api.get("/dashboard/stats", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    .then((res) => setStats(res.data))
    .catch(console.error);

  };

  load();

  const interval = setInterval(load, 5000);

  return () => clearInterval(interval);

}, []);

  const cards = [
  {
    title: "Protection",
    value: stats?.devices?.[0]?.protection ? "Active" : "Inactive",
    color: "text-green-400",
    icon: ShieldCheck,
  },
  {
    title: "Threats Blocked",
    value: stats?.devices?.[0]?.threats_blocked ?? 0,
    color: "text-red-400",
    icon: ShieldAlert,
  },
  {
    title: "Files Scanned",
    value: stats?.devices?.[0]?.files_scanned ?? 0,
    color: "text-blue-400",
    icon: FileSearch,
  },
  {
    title: "Realtime Monitor",
    value: stats?.devices?.[0]?.realtime ? "Running" : "Stopped",
    color: "text-yellow-400",
    icon: Activity,
  },
];
  return (
    <MainLayout>
      <section className="w-full bg-[#0B1120] min-h-screen py-10">
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Header */}

          <div className="mb-8">
            <h1 className="text-3xl lg:text-4xl font-bold text-white">
              Welcome back, {username} 👋
            </h1>

            <p className="text-slate-400 mt-1">
              RansomGuard XDR Dashboard
            </p>
          </div>

          {/* Stats */}

          <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4 mb-12">

            {cards.map((card, index) => {
              const Icon = card.icon;

              return (
                <div
                  key={index}
                  className="rounded-2xl border border-slate-700 bg-slate-900 p-6 min-h-[180px] flex flex-col justify-center"
                >
                  <Icon
                    size={42}
                    className={`${card.color} mb-5`}
                  />

                  <h3 className="text-slate-300 text-lg font-medium">
                    {card.title}
                  </h3>

                  <p className={`text-4xl font-bold mt-3 ${card.color}`}>
                    {card.value}
                  </p>
                </div>
              );
            })}

          </div>
          <div className="h-32"></div>
          {/* Bottom */}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Activity */}

            <div className="lg:col-span-2 rounded-2xl border border-slate-700 bg-slate-900 p-6">

              <h2 className="text-2xl font-bold text-white mb-6">
                Recent Activity
              </h2>

             <div className="space-y-3">
  {stats?.recent_activity?.map((item, index) => (
    <div
      key={index}
      className="rounded-xl bg-slate-800 p-3 border border-slate-700"
    >
      ✅ {item}
    </div>
  ))}
</div>

            </div>

            {/* User */}

            <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 flex flex-col justify-between">

              <div>

                <div className="flex items-center gap-3 mb-6">

                  <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center">
                    <User size={24} />
                  </div>

                  <div>
                    <p className="text-slate-400 text-sm">
                      Logged in as
                    </p>

                    <h3 className="text-xl font-bold">
                      {username}
                    </h3>
                  </div>

                </div>

                <div className="mb-6">

                  <p className="text-slate-400 text-sm">
                    Application Version
                  </p>

                  <p className="text-3xl font-bold mt-1">
                    v{stats?.client_version}
                  </p>

                  <span className="text-green-400 text-sm">
                    Latest Version
                  </span>

                </div>

              </div>

              <a
  href="http://127.0.0.1:8000/download/windows"
  className="
  w-full
  h-12
  rounded-xl
  bg-blue-600
  hover:bg-blue-700
  transition
  flex
  items-center
  justify-center
  gap-3
  font-semibold
  text-lg
  "
>
                <Download size={22} />
                Download Windows Client
              </a>

            </div>

          </div>

        </div>
      </section>
    </MainLayout>
  );
}