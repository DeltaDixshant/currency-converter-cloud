import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import AppShell from "./components/AppShell";

// import your pages (adjust paths as per your project)
import CryptoFiat from "./pages/CryptoFiat";
import PartnersImageCore from "./pages/PartnersImageCore";
import PartnersLocaleFormat from "./pages/PartnersLocaleFormat";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/cryptofiat" replace />} />
        <Route path="/cryptofiat" element={<CryptoFiat />} />
        <Route path="/partners/imagecore" element={<PartnersImageCore />} />
        <Route path="/partners/locale-format" element={<PartnersLocaleFormat />} />
      </Routes>
    </AppShell>
  );
}