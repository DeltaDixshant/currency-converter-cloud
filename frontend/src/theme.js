// src/theme.js
import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#00d4ff", dark: "#0099bb", contrastText: "#000" },
    secondary: { main: "#f7931a", contrastText: "#000" },
    success: { main: "#00e676" },
    error: { main: "#ff5252" },
    background: {
      default: "#060d1a",
      paper: "#0b1628",
    },
    text: {
      primary: "#e8f4fd",
      secondary: "#7fa8c9",
    },
    divider: "rgba(0,212,255,0.12)",
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: `"IBM Plex Mono", "Courier New", monospace`,
    h4: { fontWeight: 700, letterSpacing: "-0.02em" },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 600 },
    button: { textTransform: "none", fontWeight: 600, letterSpacing: "0.04em" },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: `
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { background: #060d1a; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0b1628; }
        ::-webkit-scrollbar-thumb { background: #1a3a5c; border-radius: 4px; }
      `,
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: "rgba(6,13,26,0.9)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid rgba(0,212,255,0.15)",
          boxShadow: "none",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: "1px solid rgba(0,212,255,0.1)",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        contained: {
          boxShadow: "0 0 20px rgba(0,212,255,0.25)",
          "&:hover": { boxShadow: "0 0 30px rgba(0,212,255,0.45)" },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            "& fieldset": { borderColor: "rgba(0,212,255,0.2)" },
            "&:hover fieldset": { borderColor: "rgba(0,212,255,0.5)" },
            "&.Mui-focused fieldset": { borderColor: "#00d4ff" },
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontFamily: `"IBM Plex Mono", monospace`,
          fontSize: "0.78rem",
          minWidth: 100,
        },
      },
    },
  },
});