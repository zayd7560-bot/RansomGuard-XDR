import MainLayout from "../layouts/MainLayout";

import Hero from "../components/Hero";
import Features from "../components/Features";
import Statistics from "../components/Statistics";
import DownloadSection from "../components/Download";

function Home() {
  return (
    <MainLayout>
      <Hero />
      <Features />
      <Statistics />
      <DownloadSection />
    </MainLayout>
  );
}

export default Home;