import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import Navbar from "@/components/Navbar";
import HomePage from "@/pages/HomePage";
import DetectPage from "@/pages/DetectPage";
import BatchPage from "@/pages/BatchPage";
import GalleryPage from "@/pages/GalleryPage";

function App() {
  return (
    <div className="App dark min-h-screen bg-zinc-950">
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/detect" element={<DetectPage />} />
          <Route path="/batch" element={<BatchPage />} />
          <Route path="/gallery" element={<GalleryPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </div>
  );
}

export default App;
