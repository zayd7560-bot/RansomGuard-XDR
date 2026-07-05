import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

function MainLayout({ children }) {
  return (
    <>
      <Navbar />

      <main
        style={{
          width: "100%",
          margin: 0,
          paddingTop: "80px",
          background: "#0B1120",
          minHeight: "100vh",
          overflow: "hidden",
        }}
      >
        {children}
      </main>

      <Footer />
    </>
  );
}

export default MainLayout;