// src/App.js
// IMPORTANT: This is App.js (not App.jsx). CRA resolves App.js first.
// Delete src/App.jsx if it exists to avoid confusion.

import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppShell from "./components/AppShell";
import Home from "./pages/Home";
import CryptoFiat from "./pages/CryptoFiat";
import ImageCore from "./pages/ImageCore";
import LocaleFormat from "./pages/LocaleFormat";

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/cryptofiat" element={<CryptoFiat />} />
          <Route path="/imagecore" element={<ImageCore />} />
          <Route path="/locale-format" element={<LocaleFormat />} />
          {/* Legacy routes from previous session - redirect handled gracefully */}
          <Route path="/partners/imagecore" element={<ImageCore />} />
          <Route path="/partners/locale-format" element={<LocaleFormat />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}