// src/pages/LocaleFormat.jsx
import React, { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  MenuItem,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import TranslateIcon from "@mui/icons-material/Translate";
import PhoneIcon from "@mui/icons-material/Phone";
import EventIcon from "@mui/icons-material/Event";
import { mazz } from "../services/mazzApi";

const LOCALES = [
  { value: "IE", label: "Ireland (IE)" },
  { value: "US", label: "United States (US)" },
  { value: "GB", label: "United Kingdom (GB)" },
  { value: "IN", label: "India (IN)" },
  { value: "DE", label: "Germany (DE)" },
  { value: "FR", label: "France (FR)" },
  { value: "AU", label: "Australia (AU)" },
  { value: "CA", label: "Canada (CA)" },
  { value: "JP", label: "Japan (JP)" },
  { value: "BR", label: "Brazil (BR)" },
  { value: "ZA", label: "South Africa (ZA)" },
  { value: "AE", label: "UAE (AE)" },
  { value: "SG", label: "Singapore (SG)" },
];

const DATE_FORMATS = [
  { value: "DD/MM/YYYY", label: "DD/MM/YYYY (European)" },
  { value: "MM/DD/YYYY", label: "MM/DD/YYYY (US)" },
  { value: "YYYY-MM-DD", label: "YYYY-MM-DD (ISO)" },
  { value: "long", label: "Long (e.g. 22 March 2026)" },
  { value: "short", label: "Short" },
  { value: "medium", label: "Medium" },
];

function ResultBox({ data }) {
  if (!data) return null;
  return (
    <Box
      sx={{
        mt: 2,
        p: 2,
        borderRadius: 2,
        background: "rgba(247,147,26,0.05)",
        border: "1px solid rgba(247,147,26,0.2)",
        fontFamily: "monospace",
        fontSize: "0.82rem",
        color: "#f7931a",
        whiteSpace: "pre-wrap",
        wordBreak: "break-all",
      }}
    >
      {JSON.stringify(data, null, 2)}
    </Box>
  );
}

// ── Phone Tab ──────────────────────────────────────────────────────────────
function PhoneFormatter() {
  const [number, setNumber] = useState("+353833456789");
  const [locale, setLocale] = useState("IE");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await mazz.formatPhone(number, locale);
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e?.response?.data?.message || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, display: "flex", alignItems: "center", gap: 1 }}>
          <PhoneIcon fontSize="small" sx={{ color: "secondary.main" }} />
          Phone Number Formatter
        </Typography>
        <Typography variant="body2" sx={{ color: "text.secondary", mb: 2 }}>
          Format a phone number in different national and international standards for any country.
        </Typography>
        <Grid container spacing={2} alignItems="flex-start">
          <Grid item xs={12} sm={5}>
            <TextField
              fullWidth
              size="small"
              label="Phone Number (E.164)"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              placeholder="+353833456789"
              helperText="Include country code with + prefix"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              select
              fullWidth
              size="small"
              label="Locale / Country"
              value={locale}
              onChange={(e) => setLocale(e.target.value)}
            >
              {LOCALES.map((l) => <MenuItem key={l.value} value={l.value}>{l.label}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button fullWidth variant="contained" onClick={run} disabled={loading} sx={{ bgcolor: "secondary.main", color: "#000" }}>
              {loading ? <CircularProgress size={18} /> : "Format"}
            </Button>
          </Grid>
        </Grid>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

        {result && (
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={1.5}>
              {Object.entries(result).filter(([k]) => !["input", "raw"].includes(k)).map(([k, v]) => (
                <Grid item xs={12} sm={6} key={k}>
                  <Box sx={{ p: 1.5, borderRadius: 1.5, background: "rgba(247,147,26,0.05)", border: "1px solid rgba(247,147,26,0.1)" }}>
                    <Typography variant="caption" sx={{ color: "text.secondary", textTransform: "capitalize" }}>{k.replace(/_/g, " ")}</Typography>
                    <Typography variant="body2" sx={{ color: "#f7931a", fontFamily: "monospace", fontWeight: 600 }}>
                      {String(v)}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
            <ResultBox data={result} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

// ── Date Tab ───────────────────────────────────────────────────────────────
function DateFormatter() {
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [locale, setLocale] = useState("IE");
  const [format, setFormat] = useState("DD/MM/YYYY");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const d = await mazz.formatDate(date, locale, format);
      setResult(d);
    } catch (e) {
      setError(e?.response?.data?.detail || e?.response?.data?.message || e.message || "Request failed");
    } finally { setLoading(false); }
  };

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, display: "flex", alignItems: "center", gap: 1 }}>
          <EventIcon fontSize="small" sx={{ color: "secondary.main" }} />
          Date Formatter
        </Typography>
        <Typography variant="body2" sx={{ color: "text.secondary", mb: 2 }}>
          Format a date according to different locale conventions (DD/MM/YYYY, MM/DD/YYYY, ISO, etc.).
        </Typography>
        <Grid container spacing={2} alignItems="flex-start">
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              size="small"
              label="Date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              size="small"
              label="Locale"
              value={locale}
              onChange={(e) => setLocale(e.target.value)}
            >
              {LOCALES.map((l) => <MenuItem key={l.value} value={l.value}>{l.label}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              size="small"
              label="Format"
              value={format}
              onChange={(e) => setFormat(e.target.value)}
            >
              {DATE_FORMATS.map((f) => <MenuItem key={f.value} value={f.value}>{f.label}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button fullWidth variant="contained" onClick={run} disabled={loading} sx={{ bgcolor: "secondary.main", color: "#000" }}>
              {loading ? <CircularProgress size={18} /> : "Format"}
            </Button>
          </Grid>
        </Grid>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

        {result && (
          <Box sx={{ mt: 2 }}>
            {typeof result === "object" && result.formatted && (
              <Typography variant="h5" sx={{ color: "#f7931a", mb: 1 }}>{result.formatted}</Typography>
            )}
            <Grid container spacing={1.5}>
              {Object.entries(result).map(([k, v]) => (
                <Grid item xs={12} sm={6} key={k}>
                  <Box sx={{ p: 1.5, borderRadius: 1.5, background: "rgba(247,147,26,0.05)", border: "1px solid rgba(247,147,26,0.1)" }}>
                    <Typography variant="caption" sx={{ color: "text.secondary", textTransform: "capitalize" }}>{k.replace(/_/g, " ")}</Typography>
                    <Typography variant="body2" sx={{ color: "#f7931a", fontFamily: "monospace" }}>{String(v)}</Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
            <ResultBox data={result} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────
export default function LocaleFormat() {
  const [tab, setTab] = useState(0);

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        <TranslateIcon sx={{ color: "secondary.main", fontSize: 28 }} />
        <Typography variant="h5">Locale Formatting API</Typography>
        <Chip label="Partner API" size="small" sx={{ bgcolor: "rgba(247,147,26,0.12)", color: "secondary.main", fontSize: "0.65rem" }} />
      </Box>
      <Typography variant="body2" sx={{ color: "text.secondary", mb: 3 }}>
        Built by Mazz — formats phone numbers and dates for any country/locale.
        Base URL: <span style={{ color: "#f7931a", fontFamily: "monospace", fontSize: "0.8rem" }}>https://itafimfx0h.execute-api.us-east-1.amazonaws.com</span>
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 0 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          TabIndicatorProps={{ style: { backgroundColor: "#f7931a" } }}
          sx={{ "& .Mui-selected": { color: "#f7931a !important" } }}
        >
          <Tab label="📞 Phone Formatter" />
          <Tab label="📅 Date Formatter" />
        </Tabs>
      </Box>

      <Box sx={{ pt: 3 }}>
        {tab === 0 && <PhoneFormatter />}
        {tab === 1 && <DateFormatter />}
      </Box>

      {/* API info */}
      <Box sx={{ mt: 3, p: 2, borderRadius: 2, background: "rgba(247,147,26,0.03)", border: "1px solid rgba(247,147,26,0.1)" }}>
        <Typography variant="caption" sx={{ color: "text.secondary", letterSpacing: "0.1em" }}>API DETAILS</Typography>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          {[
            ["Base URL", "https://itafimfx0h.execute-api.us-east-1.amazonaws.com"],
            ["POST /format/phone", "Format phone number → national, international, E.164"],
            ["POST /format/date", "Format date → locale-specific representation"],
          ].map(([k, v]) => (
            <Grid item xs={12} sm={6} key={k}>
              <Typography variant="caption" sx={{ color: "secondary.main", fontFamily: "monospace" }}>{k}</Typography>
              <Typography variant="body2" sx={{ color: "text.secondary", fontSize: "0.75rem" }}>{v}</Typography>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
}