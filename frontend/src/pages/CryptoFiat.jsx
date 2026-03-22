// src/pages/CryptoFiat.jsx
import React, { useState, useEffect } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  MenuItem,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import CurrencyBitcoinIcon from "@mui/icons-material/CurrencyBitcoin";
import SwapHorizIcon from "@mui/icons-material/SwapHoriz";
import { cryptofiat } from "../services/cryptofiatApi";

// Common fiat currencies for dropdowns
const COMMON_FIAT = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "INR", "SGD", "HKD", "NOK", "SEK", "DKK", "NZD", "MXN", "BRL", "ZAR", "AED", "SAR", "TRY"];
const COMMON_CRYPTO = ["BTC", "ETH", "USDT", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", "MATIC", "LINK", "LTC", "BCH", "AVAX", "SHIB", "UNI", "ATOM", "TON", "TRX", "DAI"];

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ pt: 3 }}>{children}</Box> : null;
}

function ResultBox({ data }) {
  if (!data) return null;
  return (
    <Box
      sx={{
        mt: 2,
        p: 2,
        borderRadius: 2,
        background: "rgba(0,212,255,0.05)",
        border: "1px solid rgba(0,212,255,0.2)",
        fontFamily: "monospace",
        fontSize: "0.82rem",
        color: "#00d4ff",
        whiteSpace: "pre-wrap",
        wordBreak: "break-all",
      }}
    >
      {JSON.stringify(data, null, 2)}
    </Box>
  );
}

// ── Tab 0: Fiat → Fiat ────────────────────────────────────────────────────
function FiatToFiat() {
  const [from, setFrom] = useState("USD");
  const [to, setTo] = useState("EUR");
  const [amount, setAmount] = useState("1000");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await cryptofiat.convert(from, to, parseFloat(amount));
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Fiat → Fiat Conversion</Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="From" value={from} onChange={(e) => setFrom(e.target.value)}>
              {COMMON_FIAT.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={1} sx={{ textAlign: "center" }}>
            <SwapHorizIcon sx={{ color: "primary.main" }} />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="To" value={to} onChange={(e) => setTo(e.target.value)}>
              {COMMON_FIAT.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField fullWidth size="small" label="Amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button fullWidth variant="contained" onClick={run} disabled={loading}>
              {loading ? <CircularProgress size={18} /> : "Convert"}
            </Button>
          </Grid>
        </Grid>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h5" sx={{ color: "#00d4ff" }}>
              {result.converted_amount?.toLocaleString()} {result.to_currency}
            </Typography>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              Rate: 1 {result.from_currency} = {result.exchange_rate} {result.to_currency}
            </Typography>
            <ResultBox data={result} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

// ── Tab 1: Multi-Currency Compare ─────────────────────────────────────────
function MultiCompare() {
  const [base, setBase] = useState("USD");
  const [amount, setAmount] = useState("1000");
  const [targets, setTargets] = useState(["EUR", "GBP", "JPY", "INR", "AUD"]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggleTarget = (c) => {
    setTargets((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    );
  };

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await cryptofiat.compare(base, parseFloat(amount), targets);
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Multi-Currency Comparison</Typography>
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6} sm={3}>
            <TextField select fullWidth size="small" label="Base Currency" value={base} onChange={(e) => setBase(e.target.value)}>
              {COMMON_FIAT.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField fullWidth size="small" label="Amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          </Grid>
        </Grid>
        <Typography variant="caption" sx={{ color: "text.secondary" }}>Select target currencies:</Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5, mb: 2 }}>
          {COMMON_FIAT.filter((c) => c !== base).map((c) => (
            <Chip
              key={c}
              label={c}
              size="small"
              clickable
              onClick={() => toggleTarget(c)}
              sx={{
                bgcolor: targets.includes(c) ? "rgba(0,212,255,0.15)" : "rgba(255,255,255,0.04)",
                color: targets.includes(c) ? "#00d4ff" : "text.secondary",
                border: targets.includes(c) ? "1px solid rgba(0,212,255,0.4)" : "1px solid transparent",
              }}
            />
          ))}
        </Box>
        <Button variant="contained" onClick={run} disabled={loading || targets.length === 0}>
          {loading ? <CircularProgress size={18} /> : `Compare ${targets.length} currencies`}
        </Button>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ color: "secondary.main", mb: 1 }}>
              Best value: {result.best_value}
            </Typography>
            <Grid container spacing={1}>
              {(result.comparisons || []).map((c) => (
                <Grid item xs={6} sm={4} md={3} key={c.currency}>
                  <Box sx={{ p: 1.5, borderRadius: 1.5, background: "rgba(0,212,255,0.05)", border: "1px solid rgba(0,212,255,0.1)" }}>
                    <Typography variant="caption" sx={{ color: "text.secondary" }}>#{c.rank} {c.currency}</Typography>
                    <Typography variant="body2" sx={{ color: "#00d4ff", fontWeight: 700 }}>
                      {c.converted_amount?.toLocaleString()}
                    </Typography>
                    <Typography variant="caption" sx={{ color: "text.secondary" }}>rate: {c.exchange_rate}</Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

// ── Tab 2: Fiat → Crypto ──────────────────────────────────────────────────
function FiatToCrypto() {
  const [from, setFrom] = useState("USD");
  const [toCrypto, setToCrypto] = useState("BTC");
  const [amount, setAmount] = useState("1000");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await cryptofiat.fiatToCrypto(from, toCrypto, parseFloat(amount));
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Fiat → Crypto</Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="From (Fiat)" value={from} onChange={(e) => setFrom(e.target.value)}>
              {COMMON_FIAT.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={1} sx={{ textAlign: "center" }}>
            <SwapHorizIcon sx={{ color: "secondary.main" }} />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="To (Crypto)" value={toCrypto} onChange={(e) => setToCrypto(e.target.value)}>
              {COMMON_CRYPTO.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField fullWidth size="small" label="Amount (Fiat)" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button fullWidth variant="contained" onClick={run} disabled={loading} sx={{ bgcolor: "secondary.main", color: "#000" }}>
              {loading ? <CircularProgress size={18} /> : "Convert"}
            </Button>
          </Grid>
        </Grid>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h5" sx={{ color: "secondary.main" }}>
              {result.crypto_amount} {result.to_crypto}
            </Typography>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              1 {result.to_crypto} = {result.rate?.toLocaleString()} {result.from_currency}
            </Typography>
            <ResultBox data={result} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

// ── Tab 3: Crypto → Fiat ──────────────────────────────────────────────────
function CryptoToFiat() {
  const [fromCrypto, setFromCrypto] = useState("BTC");
  const [toFiat, setToFiat] = useState("USD");
  const [amount, setAmount] = useState("0.5");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await cryptofiat.cryptoToFiat(fromCrypto, toFiat, parseFloat(amount));
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Crypto → Fiat</Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="From (Crypto)" value={fromCrypto} onChange={(e) => setFromCrypto(e.target.value)}>
              {COMMON_CRYPTO.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={1} sx={{ textAlign: "center" }}>
            <SwapHorizIcon sx={{ color: "secondary.main" }} />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="To (Fiat)" value={toFiat} onChange={(e) => setToFiat(e.target.value)}>
              {COMMON_FIAT.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField fullWidth size="small" label="Amount (Crypto)" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} inputProps={{ step: "0.0001" }} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button fullWidth variant="contained" onClick={run} disabled={loading} sx={{ bgcolor: "secondary.main", color: "#000" }}>
              {loading ? <CircularProgress size={18} /> : "Convert"}
            </Button>
          </Grid>
        </Grid>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h5" sx={{ color: "secondary.main" }}>
              {result.fiat_amount?.toLocaleString()} {result.to_currency}
            </Typography>
            <ResultBox data={result} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

// ── Tab 4: Crypto → Crypto ────────────────────────────────────────────────
function CryptoToCrypto() {
  const [from, setFrom] = useState("BTC");
  const [to, setTo] = useState("ETH");
  const [amount, setAmount] = useState("1");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await cryptofiat.cryptoToCrypto(from, to, parseFloat(amount));
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Crypto → Crypto</Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="From" value={from} onChange={(e) => setFrom(e.target.value)}>
              {COMMON_CRYPTO.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={1} sx={{ textAlign: "center" }}>
            <SwapHorizIcon sx={{ color: "secondary.main" }} />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField select fullWidth size="small" label="To" value={to} onChange={(e) => setTo(e.target.value)}>
              {COMMON_CRYPTO.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField fullWidth size="small" label="Amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} inputProps={{ step: "0.0001" }} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button fullWidth variant="contained" onClick={run} disabled={loading} sx={{ bgcolor: "#9c27b0", color: "#fff" }}>
              {loading ? <CircularProgress size={18} /> : "Convert"}
            </Button>
          </Grid>
        </Grid>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h5" sx={{ color: "#ce93d8" }}>
              {result.to_amount || result.converted_amount} {result.to_crypto}
            </Typography>
            <ResultBox data={result} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

// ── Tab 5: Live Crypto Prices ─────────────────────────────────────────────
function LivePrices() {
  const [selected, setSelected] = useState(["BTC", "ETH", "SOL", "ADA", "DOGE"]);
  const [currency, setCurrency] = useState("usd");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggle = (c) =>
    setSelected((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    );

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await cryptofiat.cryptoPrices(selected.join(","), currency);
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Live Crypto Prices</Typography>
        <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap", alignItems: "center" }}>
          <TextField select size="small" label="vs Currency" value={currency} onChange={(e) => setCurrency(e.target.value)} sx={{ width: 120 }}>
            {["usd", "eur", "gbp", "jpy", "inr"].map((c) => <MenuItem key={c} value={c}>{c.toUpperCase()}</MenuItem>)}
          </TextField>
          <Typography variant="caption" sx={{ color: "text.secondary" }}>Select cryptos:</Typography>
        </Box>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 2 }}>
          {COMMON_CRYPTO.map((c) => (
            <Chip
              key={c}
              label={c}
              size="small"
              clickable
              onClick={() => toggle(c)}
              sx={{
                bgcolor: selected.includes(c) ? "rgba(247,147,26,0.15)" : "rgba(255,255,255,0.04)",
                color: selected.includes(c) ? "#f7931a" : "text.secondary",
                border: selected.includes(c) ? "1px solid rgba(247,147,26,0.4)" : "1px solid transparent",
              }}
            />
          ))}
        </Box>
        <Button variant="contained" onClick={run} disabled={loading || selected.length === 0} sx={{ bgcolor: "secondary.main", color: "#000" }}>
          {loading ? <CircularProgress size={18} /> : `Get Prices (${selected.length})`}
        </Button>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && (
          <Grid container spacing={1.5} sx={{ mt: 1 }}>
            {Object.entries(result).map(([sym, data]) => (
              <Grid item xs={6} sm={4} md={3} key={sym}>
                <Box sx={{ p: 2, borderRadius: 2, background: "rgba(247,147,26,0.05)", border: "1px solid rgba(247,147,26,0.15)" }}>
                  <Typography variant="caption" sx={{ color: "text.secondary" }}>{sym}</Typography>
                  <Typography variant="h6" sx={{ color: "#f7931a", fontFamily: "monospace" }}>
                    {typeof data === "object" ? (data.current_price || data.price || JSON.stringify(data)) : data}
                  </Typography>
                  {typeof data === "object" && data.price_change_percentage_24h != null && (
                    <Typography variant="caption" sx={{ color: data.price_change_percentage_24h >= 0 ? "#00e676" : "#ff5252" }}>
                      {data.price_change_percentage_24h >= 0 ? "▲" : "▼"} {Math.abs(data.price_change_percentage_24h).toFixed(2)}%
                    </Typography>
                  )}
                </Box>
              </Grid>
            ))}
          </Grid>
        )}
      </CardContent>
    </Card>
  );
}

// ── Tab 6: Crypto List ────────────────────────────────────────────────────
function CryptoList() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await cryptofiat.cryptoList();
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  useEffect(() => { run(); }, []);

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
          <Typography variant="h6">Supported Cryptocurrencies</Typography>
          <Button size="small" onClick={run} disabled={loading}>Refresh</Button>
        </Box>
        {loading && <CircularProgress size={24} />}
        {error && <Alert severity="error">{error}</Alert>}
        {result && (
          <>
            <Typography variant="body2" sx={{ color: "text.secondary", mb: 1.5 }}>
              {Array.isArray(result) ? result.length : (result.total || "?")} supported cryptocurrencies
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.75 }}>
              {(Array.isArray(result) ? result : (result.cryptocurrencies || [])).map((c) => (
                <Chip
                  key={typeof c === "string" ? c : c.symbol}
                  label={typeof c === "string" ? c : `${c.symbol} — ${c.name}`}
                  size="small"
                  sx={{ bgcolor: "rgba(247,147,26,0.08)", color: "#f7931a", fontFamily: "monospace" }}
                />
              ))}
            </Box>
            <ResultBox data={result} />
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────
export default function CryptoFiat() {
  const [tab, setTab] = useState(0);

  const tabs = [
    { label: "Fiat → Fiat", panel: <FiatToFiat /> },
    { label: "Multi-Compare", panel: <MultiCompare /> },
    { label: "Fiat → Crypto", panel: <FiatToCrypto /> },
    { label: "Crypto → Fiat", panel: <CryptoToFiat /> },
    { label: "Crypto → Crypto", panel: <CryptoToCrypto /> },
    { label: "Live Prices", panel: <LivePrices /> },
    { label: "Crypto List", panel: <CryptoList /> },
  ];

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
        <CurrencyBitcoinIcon sx={{ color: "primary.main", fontSize: 28 }} />
        <Typography variant="h5">CryptoFiat Bridge API</Typography>
        <Chip label="My API" size="small" sx={{ bgcolor: "rgba(0,212,255,0.12)", color: "primary.main", fontSize: "0.65rem" }} />
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 0 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          variant="scrollable"
          scrollButtons="auto"
          TabIndicatorProps={{ style: { backgroundColor: "#00d4ff" } }}
          sx={{ "& .Mui-selected": { color: "#00d4ff !important" } }}
        >
          {tabs.map((t, i) => <Tab key={i} label={t.label} />)}
        </Tabs>
      </Box>

      {tabs.map((t, i) => (
        <TabPanel key={i} value={tab} index={i}>
          {t.panel}
        </TabPanel>
      ))}
    </Box>
  );
}