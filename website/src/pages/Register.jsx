import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import MainLayout from "../layouts/MainLayout";
import api from "../services/api";

function Register() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const navigate = useNavigate();

const [loading, setLoading] = useState(false);

const [error, setError] = useState("");

const [success, setSuccess] = useState("");

const [formData, setFormData] = useState({
  full_name: "",
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  duress_password: "",
});
const handleChange = (e) => {
  setFormData({
    ...formData,
    [e.target.name]: e.target.value,
  });
};
const handleSubmit = async (e) => {
  e.preventDefault();

  setError("");
  setSuccess("");

  if (formData.password !== formData.confirmPassword) {
    setError("Passwords do not match.");
    return;
  }

  setLoading(true);

  try {
    const res = await api.post("/auth/register", {
  full_name: formData.full_name,
  username: formData.username,
  email: formData.email,
  password: formData.password,
  duress_password: formData.duress_password,
});

console.log("STATUS:", res.status);
console.log("DATA:", res.data);

    setSuccess(res.data.message);

    setTimeout(() => {
      navigate("/login");
    }, 1500);

  } catch (err) {
  console.log("ERROR:", err);
  console.log("STATUS:", err.response?.status);
  console.log("DATA:", err.response?.data);

  setError(
    JSON.stringify(err.response?.data || err.message)
  );
}

  setLoading(false);
};

  return (
    <MainLayout>
      <section className="min-h-screen bg-[#0B1120] flex items-center justify-center px-6 pt-40 pb-24">

        <div className="w-full max-w-xl rounded-3xl border border-slate-700 bg-[#111827]/90 backdrop-blur-xl shadow-[0_0_60px_rgba(37,99,235,0.15)] p-12">

          <h1 className="text-5xl font-bold text-center text-white">
            Create Account
          </h1>

          <p className="text-center text-gray-400 mt-4 text-lg">
            Join RansomGuard XDR and secure your devices.
          </p>

          <form
             onSubmit={handleSubmit}
             className="mt-10 space-y-6"
                  >

            {/* Full Name */}
            <div>
  <label className="block text-gray-300 mb-2">
    Full Name
  </label>

  <div className="relative">
    <input
      type="text"
      name="full_name"
      value={formData.full_name}
      onChange={handleChange}
      placeholder="Enter your full name"
      className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition duration-300"
    />
  </div>
</div>

            {/* Username */}
            <div>
              <label className="block text-gray-300 mb-2">
                Username
              </label>

              <div className="relative">

               <input
  type="text"
  name="username"
  value={formData.username}
  onChange={handleChange}
  placeholder="Choose a username"
  className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition duration-300"
/>
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-gray-300 mb-2">
                Email Address
              </label>

              <div className="relative">

                <input
  type="email"
  name="email"
  value={formData.email}
  onChange={handleChange}
  placeholder="example@email.com"
  className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition duration-300"
/>
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-gray-300 mb-2">
                Password
              </label>

              <div className="relative">

                <input
  type={showPassword ? "text" : "password"}
  name="password"
  value={formData.password}
  onChange={handleChange}
  placeholder="Create a password"
                  className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 pr-12 text-white outline-none focus:border-blue-500
                   focus:ring-2
                   focus:ring-blue-500/30
                   transition
                   duration-300"
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-gray-300 mb-2">
                Confirm Password
              </label>

              <div className="relative">

                <input
  type={showConfirm ? "text" : "password"}
  name="confirmPassword"
  value={formData.confirmPassword}
  onChange={handleChange}
  placeholder="Confirm your password"
                  className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 pr-12 text-white outline-none focus:border-blue-500
                     focus:ring-2
                     focus:ring-blue-500/30
                     transition
                     duration-300"
                />

                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showConfirm ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>
<div>
  <label className="block text-gray-300 mb-2">
    Emergency Password
  </label>

  <input
    type="password"
    name="duress_password"
    value={formData.duress_password}
    onChange={handleChange}
    placeholder="Create an emergency password"
    className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition"
  />

  <p className="text-xs text-gray-400 mt-2">
    Used to access a decoy account if you are forced to log in.
  </p>
</div>
            {/* Terms */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                className="w-5 h-5 accent-blue-600"
              />

              <span className="text-gray-300">
                I agree to the Terms & Privacy Policy
              </span>
            </div>
{error && (
  <div className="bg-red-500/10 border border-red-500 text-red-400 rounded-lg p-3 text-center">
    {error}
  </div>
)}

{success && (
  <div className="bg-green-500/10 border border-green-500 text-green-400 rounded-lg p-3 text-center">
    {success}
  </div>
)}
            {/* Button */}
           <button
  type="submit"
  disabled={loading}
  className="w-full h-14 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-60 transition-all duration-300 text-white font-bold text-lg"
>
  {loading ? "Creating Account..." : "Create Account"}
</button>

          </form>

          <p className="text-center text-gray-400 mt-8">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-blue-500 hover:underline font-semibold"
            >
              Login
            </Link>
          </p>

        </div>

      </section>
    </MainLayout>
  );
}

export default Register;