import React, { useState } from "react";
import { mazz } from "../services/mazzApi";
import { config } from "../config";

export default function PartnersLocaleFormat() {
  const [phone, setPhone] = useState("+353833456789");
  const [phoneOut, setPhoneOut] = useState(null);

  const [date, setDate] = useState("2026-03-14");
  const [locale, setLocale] = useState("en_GB");
  const [format, setFormat] = useState("medium");
  const [dateOut, setDateOut] = useState(null);

  const [error, setError] = useState("");

  const formatPhone = async () => {
    setError("");
    setPhoneOut(null);
    try {
      const data = await mazz.formatPhone(phone);
      setPhoneOut(data);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Phone format failed");
    }
  };

  const formatDate = async () => {
    setError("");
    setDateOut(null);
    try {
      const data = await mazz.formatDate({ date, locale, format });
      setDateOut(data);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Date format failed");
    }
  };

  return (
    <div className="container py-4">
      <h2>Partner API: Locale Formatting (mazz-api)</h2>
      <p className="text-muted">
        Uses: <code>{config.mazzBase}</code>
      </p>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card p-3 mb-3">
        <h5>1) Phone formatting</h5>
        <label className="form-label">Phone number</label>
        <input className="form-control" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <button className="btn btn-primary mt-3" onClick={formatPhone}>
          Format phone
        </button>

        {phoneOut && <pre className="mt-3 mb-0">{JSON.stringify(phoneOut, null, 2)}</pre>}
      </div>

      <div className="card p-3">
        <h5>2) Date formatting</h5>

        <div className="row g-2">
          <div className="col-md-4">
            <label className="form-label">Date (YYYY-MM-DD)</label>
            <input className="form-control" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>

          <div className="col-md-4">
            <label className="form-label">Locale</label>
            <input className="form-control" value={locale} onChange={(e) => setLocale(e.target.value)} />
          </div>

          <div className="col-md-4">
            <label className="form-label">Format</label>
            <select className="form-select" value={format} onChange={(e) => setFormat(e.target.value)}>
              {["short", "medium", "long", "full"].map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button className="btn btn-success mt-3" onClick={formatDate}>
          Format date
        </button>

        {dateOut && <pre className="mt-3 mb-0">{JSON.stringify(dateOut, null, 2)}</pre>}
      </div>
    </div>
  );
}