function Footer() {
  return (
    <footer
      id="contact"
      className="bg-[#070D19] border-t border-slate-800 mt-32"
    >
      <div className="max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-4 gap-12">

        {/* Logo */}

        <div>
          <h2 className="text-3xl font-bold text-white">
            🛡 RansomGuard <span className="text-blue-500">XDR</span>
          </h2>

          <p className="text-gray-400 mt-6 leading-8">
            AI-powered ransomware detection and real-time protection for
            Windows and Android devices.
          </p>
        </div>

        {/* Quick Links */}

        <div>
          <h3 className="text-white text-xl font-semibold mb-6">
            Quick Links
          </h3>

          <ul className="space-y-4 text-gray-400">

            <li>
              <a href="#">Home</a>
            </li>

            <li>
              <a href="#features">Features</a>
            </li>

            <li>
              <a href="#download">Download</a>
            </li>

            <li>
              <a href="#contact">Contact</a>
            </li>

          </ul>
        </div>

        {/* Downloads */}

        <div>
          <h3 className="text-white text-xl font-semibold mb-6">
            Downloads
          </h3>

          <ul className="space-y-4 text-gray-400">

            <li>💻 Windows (.exe)</li>

            <li>📱 Android (.apk)</li>

            <li>🐧 Linux (Coming Soon)</li>

            <li>🍎 macOS (Coming Soon)</li>

          </ul>
        </div>

        {/* Contact */}

        <div>
          <h3 className="text-white text-xl font-semibold mb-6">
            Contact
          </h3>

          <div className="space-y-4 text-gray-400">

            <p>📧 support@ransomguardxdr.com</p>

            <p>🌍 www.ransomguardxdr.com</p>

            <p>💼 LinkedIn</p>

            <p>💻 GitHub</p>

          </div>
        </div>

      </div>

      <div className="border-t border-slate-800 py-6 text-center text-gray-500">

        © 2026 RansomGuard XDR. All Rights Reserved.

      </div>

    </footer>
  );
}

export default Footer;