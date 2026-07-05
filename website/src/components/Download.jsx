import {
  Download,
  Monitor,
  Smartphone,
  Laptop,
  Apple,
} from "lucide-react";

const downloads = [
  {
    icon: <Monitor size={42} />,
    title: "Windows",
    version: "v1.0.0",
    size: "68 MB",
    status: "Available",
    button: "Download EXE",
    active: true,
  },
  {
    icon: <Smartphone size={42} />,
    title: "Android",
    version: "-",
    size: "-",
    status: "Coming Soon",
    button: "Coming Soon",
    active: false,
  },
  {
    icon: <Laptop size={42} />,
    title: "Linux",
    version: "-",
    size: "-",
    status: "Coming Soon",
    button: "Coming Soon",
    active: false,
  },
  {
    icon: <Apple size={42} />,
    title: "macOS",
    version: "-",
    size: "-",
    status: "Coming Soon",
    button: "Coming Soon",
    active: false,
  },
];

function DownloadSection() {
  return (
    <section
     id="download"
      className="bg-[#111827] pt-64 pb-64 border-t border-slate-800"
      >
      <div className="max-w-7xl mx-auto px-6">
      <div className="h-32"></div>
        <h2 className="text-center text-5xl font-bold">
          Download <span className="text-blue-500">RansomGuard XDR</span>
        </h2>

        <p className="text-center text-gray-400 mt-5 mb-16">
          Choose your platform and start protecting your devices today.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">

          {downloads.map((item, index) => (

            <div
              key={index}
              className="bg-[#111827] rounded-2xl border border-slate-700 hover:border-blue-500 duration-300 hover:-translate-y-2 p-8"
            >

              <div className="text-blue-500 mb-6">
                {item.icon}
              </div>

              <h3 className="text-3xl font-bold">
                {item.title}
              </h3>

              <p className="text-gray-400 mt-3">
                Version : {item.version}
              </p>

              <p className="text-gray-400">
                Size : {item.size}
              </p>

              <span
                className={`inline-block mt-5 px-3 py-1 rounded-full text-sm ${
                  item.active
                    ? "bg-green-500/20 text-green-400"
                    : "bg-yellow-500/20 text-yellow-400"
                }`}
              >
                {item.status}
              </span>

              <button
                disabled={!item.active}
                className={`w-full mt-8 py-4 rounded-xl font-bold flex justify-center items-center gap-2 duration-300 ${
                  item.active
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-gray-700 cursor-not-allowed"
                }`}
              >
                <Download size={20} />
                {item.button}
              </button>

            </div>

          ))}

        </div>

      </div>
    </section>
  );
}

export default DownloadSection;