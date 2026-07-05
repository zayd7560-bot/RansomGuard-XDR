import { Shield, Menu } from "lucide-react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
function Navbar() {
  const navigate = useNavigate();

const isLoggedIn = localStorage.getItem("token");

const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  navigate("/login");
};
  return (
    <nav className="fixed top-0 left-0 w-full bg-[#111827]/90 backdrop-blur-md border-b border-slate-800 z-50">

      <div className="max-w-7xl mx-auto px-6 lg:px-12 h-20 flex items-center justify-between">

        {/* Logo */}

          <Link to="/" className="flex items-center gap-3">

           <Shield size={30} className="text-white" />

            <span className="text-2xl font-bold text-blue-500 hover:text-blue-400 duration-300 cursor-pointer">
             RansomGuard XDR
            </span>

           </Link> 

        {/* Desktop Menu */}
        <ul className="hidden lg:flex items-center gap-10 text-white font-medium">

          <li><a href="#" className="hover:text-blue-500 duration-300">Home</a></li>

          <li><a href="#features" className="hover:text-blue-500 duration-300">Features</a></li>

          <li><a href="#download" className="hover:text-blue-500 duration-300">Download</a></li>

          <li>
            <Link
               to={isLoggedIn ? "/dashboard" : "/login"}
               className="hover:text-blue-500 duration-300"
             >
             Dashboard
            </Link>
         </li>

          <li><a href="#contact" className="hover:text-blue-500 duration-300">Contact</a></li>

        </ul>

        {/* Right Side */}
        <div className="flex items-center gap-4">

         {!isLoggedIn ? (
  <>
    <Link to="/register">
      <button className="hidden md:block bg-blue-600 hover:bg-blue-700 px-10 py-4 rounded-xl font-semibold duration-300">
        Register
      </button>
    </Link>

    <Link to="/login">
      <button className="hidden md:block border border-blue-500 text-blue-400 hover:bg-blue-600 hover:text-white px-10 py-4 rounded-xl font-semibold duration-300">
        Login
      </button>
    </Link>
  </>
) : (
  <>
    <Link
      to="/profile"
      className="text-white hover:text-blue-400 transition font-semibold"
    >
      Profile
    </Link>

    <button
      onClick={logout}
      className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-xl font-semibold transition"
    >
      Logout
    </button>
  </>
)}
          <button className="lg:hidden">

            <Menu size={30} />

          </button>

        </div>

      </div>

    </nav>
  );
}

export default Navbar;