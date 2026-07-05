import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import api from "../services/api";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const res = await api.post("/auth/login", {
        username: formData.username,
        password: formData.password,
      });

      console.log(res.data);

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("username", formData.username);

      navigate("/dashboard");
    } catch (err) {
      console.log(err.response?.data);

      setError(
        err.response?.data?.detail ||
          "Invalid username or password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="min-h-screen bg-[#0B1120] flex items-center justify-center px-6">

        <form
          onSubmit={handleSubmit}
          className="w-full max-w-xl bg-[#111827] border border-slate-700 rounded-3xl p-10"
        >
          <h1 className="text-5xl font-bold text-center mb-3 text-white">
            Login
          </h1>

          <p className="text-center text-gray-400 mb-8">
            Welcome back to RansomGuard XDR
          </p>

          {error && (
            <div className="mb-5 rounded-lg border border-red-500 bg-red-500/10 p-3 text-red-400 text-center">
              {error}
            </div>
          )}

          <div className="mb-5">
            <label className="block mb-2 text-gray-300">
              Username
            </label>

            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Enter your username"
              className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 text-white outline-none focus:border-blue-500"
            />
          </div>

          <div className="mb-7">
            <label className="block mb-2 text-gray-300">
              Password
            </label>

            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
                className="w-full h-14 rounded-xl bg-[#1E293B] border border-slate-700 px-5 pr-14 text-white outline-none focus:border-blue-500"
              />

              <button
                type="button"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
                className="absolute right-5 top-1/2 -translate-y-1/2 text-gray-400"
              >
                {showPassword ? (
                  <EyeOff size={20} />
                ) : (
                  <Eye size={20} />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-14 rounded-xl bg-blue-600 hover:bg-blue-700 font-semibold transition"
          >
            {loading ? "Signing In..." : "Login"}
          </button>
        </form>
      </div>
    </MainLayout>
  );
}

export default Login;