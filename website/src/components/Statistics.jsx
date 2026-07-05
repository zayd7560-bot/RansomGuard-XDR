import { ShieldCheck, Users, Activity, Cpu } from "lucide-react";

const stats = [
  {
    icon: <ShieldCheck size={36} />,
    value: "99.9%",
    title: "Detection Accuracy",
  },
  {
    icon: <Activity size={36} />,
    value: "25K+",
    title: "Threats Blocked",
  },
  {
    icon: <Users size={36} />,
    value: "5K+",
    title: "Protected Devices",
  },
  {
    icon: <Cpu size={36} />,
    value: "24/7",
    title: "AI Monitoring",
  },
];

function Statistics() {
  return (
    <section className="bg-[#0B1120] pt-64 pb-64 border-t border-slate-800">

      <div className="max-w-7xl mx-auto px-40">
        <div className="h-32"></div>
        <h2 className="text-5xl font-bold text-center">
          Trusted Security
        </h2>

        <p className="text-center text-gray-400 mt-5 mb-16">
          Powerful protection trusted by researchers and organizations.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">

          {stats.map((item, index) => (

            <div
              key={index}
              className="bg-[#111827] rounded-2xl p-8 text-center border border-slate-700 hover:border-blue-500 duration-300 hover:-translate-y-2"
            >

              <div className="flex justify-center text-blue-500 mb-5">
                {item.icon}
              </div>

              <h3 className="text-4xl font-bold text-blue-400">
                {item.value}
              </h3>

              <p className="mt-3 text-gray-300">
                {item.title}
              </p>

            </div>

          ))}

        </div>

      </div>

    </section>
  );
}

export default Statistics;