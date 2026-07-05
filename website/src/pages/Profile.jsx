import { useEffect, useState, useRef } from "react";
import api from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Profile() {

  const [user, setUser] = useState({});
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/auth/me")
      .then(res => setUser(res.data))
      .catch(console.error);
  }, []);
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
   const uploadPhoto = async (e) => {

    const file = e.target.files[0];

    if (!file) return;

    const formData = new FormData();

    formData.append("file", file);

    const token = localStorage.getItem("token");

    await api.post(
        "/auth/upload-photo",
        formData,
        {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "multipart/form-data",
            },
        }
    );

    const res = await api.get("/auth/me", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    setUser(res.data);

};
  return (
<div className="max-w-7xl mx-auto px-6 py-10">

    <h1 className="text-4xl font-bold mb-8">
        👤 My Profile
    </h1>
    <div className="h-10"></div>

    <div className="flex justify-end mb-6">

    <button
        onClick={() => navigate("/dashboard")}
        className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-semibold transition"
    >
        ← Back to Dashboard
    </button>

</div>
    {/* Top Card */}

    <div className="bg-[#151D33] rounded-2xl border border-slate-700 p-8 shadow-xl">

        <div className="flex flex-col md:flex-row items-center md:items-center gap-8">

            <div className="relative cursor-pointer" onClick={() => fileInputRef.current.click()}>

             <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                hidden
                onChange={uploadPhoto}
             />

             {

             user.profile_image ?

             <img
               src={`https://ransomguard-xdr-production.up.railway.app/uploads/${user.profile_image}`}
               className="w-24 h-24 rounded-full object-cover border-4 border-blue-500"
             />

               :

             <div className="w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center text-5xl font-bold">

               {user.username?.charAt(0)?.toUpperCase()}

             </div>

                 }

             <div className="absolute bottom-0 right-0 bg-blue-600 rounded-full p-2">

               📷

             </div>

            </div>

            <div>

                <h2 className="text-3xl font-bold">

                    {user.username}

                </h2>

                <p className="text-slate-400">

                    {user.email}

                </p>

                <div className="flex gap-3 mt-3">

                    <span className="bg-green-600 px-3 py-1 rounded-full text-sm">
                        🛡 Protected
                    </span>

                    <span className="bg-slate-700 px-3 py-1 rounded-full text-sm">
                        {user.role}
                    </span>

                </div>

            </div>

        </div>

    </div>
    <div className="h-10"></div>
    {/* Statistics */}

    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-12 mb-10">

        <div className="bg-[#151D33] rounded-xl p-6">

            <p className="text-slate-400">
                Devices
            </p>

            <h2 className="text-4xl font-bold mt-3">
                {stats?.total_devices ?? 0}
            </h2>

        </div>

        <div className="bg-[#151D33] rounded-xl p-6">

            <p className="text-slate-400">
                Online
            </p>

            <h2 className="text-4xl font-bold text-green-400 mt-3">
                {stats?.online_devices ?? 0}
            </h2>

        </div>

        <div className="bg-[#151D33] rounded-xl p-6">

            <p className="text-slate-400">
                Threats
            </p>

            <h2 className="text-4xl font-bold text-red-400 mt-3">
                {stats?.devices?.[0]?.threats_blocked ?? 0}
            </h2>

        </div>

        <div className="bg-[#151D33] rounded-xl p-6">

            <p className="text-slate-400">
                Protection
            </p>

            <h2 className="text-3xl font-bold text-green-400 mt-3">
                {stats?.devices?.[0]?.protection ? "Active" : "Inactive"}
            </h2>

        </div>

    </div>
    <div className="h-10"></div>
    {/* Information */}

    <div className="bg-[#151D33] rounded-2xl border border-slate-700 p-8 mt-6">

        <h2 className="text-2xl font-bold mb-6">

            Account Information

        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

            <div>

                <p className="text-slate-400">

                    Username

                </p>

                <h3 className="text-xl mt-1">

                    {user.username}

                </h3>

            </div>

            <div>

                <p className="text-slate-400">

                    Email

                </p>

                <h3 className="text-xl mt-1">

                    {user.email}

                </h3>

            </div>

            <div>

                <p className="text-slate-400">

                    Role

                </p>

                <h3 className="text-xl mt-1">

                    {user.role}

                </h3>

            </div>

            <div>

                <p className="text-slate-400">

                    Status

                </p>

                <h3 className="text-xl text-green-400 mt-1">

                    Protected

                </h3>

            </div>

        </div>

    </div>
    <div className="h-10"></div>
    {/* Registered Device */}

    {/* Registered Devices */}

<div className="bg-[#151D33] rounded-2xl border border-slate-700 p-8 mt-10">

    <h2 className="text-2xl font-bold mb-6">

        Registered Devices

    </h2>

    <div className="overflow-x-auto">

        <table className="w-full">

            <thead>

                <tr className="border-b border-slate-700 text-slate-400">

                    <th className="text-left p-3">Device</th>

                    <th className="text-left p-3">OS</th>

                    <th className="text-left p-3">Status</th>

                    <th className="text-left p-3">Protection</th>

                    <th className="text-left p-3">Threat</th>

                    <th className="text-left p-3">Last Seen</th>

                </tr>

            </thead>

            <tbody>

                {stats?.devices?.map((device) => (

                    <tr
                      key={device.device_id}
                      className={`border-b border-slate-800 hover:bg-slate-800/40 transition ${
                      device.threat_level === "DANGEROUS"
                      ? "bg-red-900/30"
                      : device.threat_level === "SUSPICIOUS"
                      ? "bg-yellow-900/20"
                      : ""
                      }`}
                    >                    

                        <td className="p-3">

                            💻 {device.device_name}

                        </td>

                        <td className="p-3">

                            {device.os} {device.version}

                        </td>

                        <td className="p-3">

                            <span
                                className={
                                    device.status === "Online"
                                        ? "text-green-400"
                                        : "text-red-400"
                                }
                            >

                                {device.status}

                            </span>

                        </td>

                        <td className="p-3">

                            {device.protection
                                ? "🟢 Enabled"
                                : "🔴 Disabled"}

                        </td>

                        <td className="p-3">

                         {
                          device.threat_level==="DANGEROUS"

                          ?

                         <span className="text-red-500 font-bold">
                          🚨 UNDER ATTACK
                         </span>

                           :

                          device.threat_level==="SUSPICIOUS"

                          ?

                         <span className="text-yellow-400 font-bold">
                           ⚠ Suspicious
                         </span>

                          :

                         <span className="text-green-400">
                          🟢 Safe
                         </span>

                         }

                        </td>

                        <td className="p-3 text-slate-400">

                            {device.last_seen
                                ? new Date(device.last_seen).toLocaleString()
                                : "-"}

                        </td>

                    </tr>

                ))}

            </tbody>

        </table>

    </div>

</div>

</div>
);
}