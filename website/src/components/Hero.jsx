import Container from "./Container";
function Hero() {
  return (
    <section className="relative min-h-screen pt-32 px-6 lg:px-10 xl:px-16 bg-[#0B1120] overflow-hidden text-white flex items-center">

      {/* Background Glow */}
      <div className="absolute w-[700px] h-[700px] bg-blue-600/20 blur-[180px] rounded-full -top-40 -left-40"></div>

      <div className="absolute w-[500px] h-[500px] bg-cyan-400/10 blur-[160px] rounded-full bottom-0 right-0"></div>

        <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-16 items-center">

        <div className="max-w-2xl">

          <p className="text-blue-400 font-semibold tracking-widest uppercase">
            AI Powered Cyber Security
          </p>

          <h1 className="text-4xl lg:text-5xl font-extrabold leading-tight mt-5">

             Protect Your <span className="text-white">Devices</span>

            <br />

            With <span className="text-blue-500">RansomGuard XDR</span>

          </h1>

          <p className="mt-6 text-lg text-gray-300 leading-8 max-w-xl">

            AI-powered ransomware detection with real-time monitoring,
            behavioral analysis and enterprise-grade protection.

          </p>

          <div className="flex flex-wrap gap-5 mt-10">

            <button className="bg-blue-600 hover:bg-blue-700 duration-300 hover:scale-105 shadow-xl px-9 py-4 rounded-xl font-bold text-lg">

                ⬇ Download Windows

            </button>

           
          </div>

        </div>

        <div className="flex justify-center">

          <img

            src="/images/shield.png"

            className="w-[420px] lg:w-[470px] drop-shadow-[0_0_60px_rgba(59,130,246,.8)] floating"
          />

        </div>

      </div>

    </section>
  );
}

export default Hero;