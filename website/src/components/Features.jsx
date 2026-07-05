import { ShieldCheck, Activity, BarChart3, LaptopMinimal } from "lucide-react";

function Features() {
  const features = [
    {
      icon: <ShieldCheck size={42} />,
      title: "AI Threat Detection",
      desc: "Advanced behavioral analysis to detect ransomware before encryption."
    },
    {
      icon: <Activity size={42} />,
      title: "Real-Time Protection",
      desc: "Continuous monitoring with instant response against suspicious activity."
    },
    {
      icon: <BarChart3 size={42} />,
      title: "Security Analytics",
      desc: "Interactive reports, threat history and detailed security insights."
    },
    {
      icon: <LaptopMinimal size={42} />,
      title: "Cross Platform",
      desc: "Desktop, Web and Android connected through one secure backend."
    }
  ];

  return (
      <section
  id="features"
  className="bg-[#0F172A] pt-64 pb-64 border-t border-slate-800"
>

      <div className="max-w-7xl mx-auto px-8">
        <div className="h-32"></div>

        <h2 className="text-5xl font-bold text-center text-white">
          Why Choose
          <span className="text-blue-500"> RansomGuard XDR</span>
        </h2>

        <p className="text-center text-gray-400 mt-5 max-w-3xl mx-auto text-lg">
          Built with AI-powered ransomware detection, real-time monitoring and
          enterprise-grade security to protect your digital environment.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mt-16">

          {features.map((item, index) => (

            <div
              key={index}
              className="bg-[#111827] rounded-2xl p-8 border border-slate-700 hover:border-blue-500 duration-300 hover:-translate-y-3 hover:shadow-[0_0_30px_rgba(59,130,246,.25)]"
            >

              <div className="text-blue-500 mb-6">
                {item.icon}
              </div>

              <h3 className="text-2xl font-bold text-white">
                {item.title}
              </h3>

              <p className="text-gray-400 mt-4 leading-7">
                {item.desc}
              </p>

            </div>

          ))}

        </div>

      </div>

    </section>
  );
}

export default Features;