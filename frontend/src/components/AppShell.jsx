// src/components/AppShell.jsx
import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  AppBar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Tooltip,
  Chip,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import HomeIcon from "@mui/icons-material/Home";
import CurrencyBitcoinIcon from "@mui/icons-material/CurrencyBitcoin";
import ImageIcon from "@mui/icons-material/Image";
import TranslateIcon from "@mui/icons-material/Translate";
import DashboardIcon from "@mui/icons-material/Dashboard";

const DRAWER_WIDTH = 240;

const navItems = [
  { label: "Home", to: "/", icon: <DashboardIcon fontSize="small" /> },
  {
    label: "CryptoFiat API",
    to: "/cryptofiat",
    icon: <CurrencyBitcoinIcon fontSize="small" />,
    badge: "Mine",
  },
  {
    label: "ImageCore",
    to: "/imagecore",
    icon: <ImageIcon fontSize="small" />,
    badge: "Partner",
  },
  {
    label: "Locale Format",
    to: "/locale-format",
    icon: <TranslateIcon fontSize="small" />,
    badge: "Partner",
  },
];

export default function AppShell({ children }) {
  const navigate = useNavigate();

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      {/* Top AppBar */}
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
        <Toolbar sx={{ gap: 1 }}>
          {/* Back / Forward / Home */}
          <Tooltip title="Back">
            <IconButton
              size="small"
              onClick={() => navigate(-1)}
              sx={{ color: "primary.main" }}
            >
              <ArrowBackIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Forward">
            <IconButton
              size="small"
              onClick={() => navigate(1)}
              sx={{ color: "primary.main" }}
            >
              <ArrowForwardIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Home">
            <IconButton
              size="small"
              onClick={() => navigate("/")}
              sx={{ color: "primary.main" }}
            >
              <HomeIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Divider
            orientation="vertical"
            flexItem
            sx={{ borderColor: "rgba(0,212,255,0.2)", mx: 1 }}
          />

          {/* Brand */}
          <CurrencyBitcoinIcon sx={{ color: "secondary.main", mr: 0.5 }} />
          <Typography
            variant="h6"
            fontWeight={700}
            sx={{
              color: "primary.main",
              letterSpacing: "0.06em",
              fontSize: "1rem",
              flexGrow: 1,
            }}
          >
            CryptoFiat Cloud Suite
          </Typography>

          <Typography
            variant="caption"
            sx={{
              color: "text.secondary",
              display: { xs: "none", sm: "block" },
            }}
          >
            NCI MSc Cloud Computing — Dixshant Valecha
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Side Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: DRAWER_WIDTH,
            boxSizing: "border-box",
            background: "#080f1f",
            borderRight: "1px solid rgba(0,212,255,0.1)",
          },
        }}
      >
        <Toolbar />
        <Box sx={{ px: 2, pt: 2, pb: 1 }}>
          <Typography
            variant="caption"
            sx={{ color: "text.secondary", letterSpacing: "0.12em" }}
          >
            NAVIGATION
          </Typography>
        </Box>

        <List dense>
          {navItems.map((item) => (
            <ListItemButton
              key={item.to}
              component={NavLink}
              to={item.to}
              end={item.to === "/"}
              sx={{
                mx: 1,
                mb: 0.5,
                borderRadius: 2,
                "&.active": {
                  background: "rgba(0,212,255,0.1)",
                  borderLeft: "3px solid #00d4ff",
                  "& .MuiListItemText-primary": { color: "#00d4ff" },
                  "& .MuiListItemIcon-root": { color: "#00d4ff" },
                },
                "&:hover": { background: "rgba(0,212,255,0.06)" },
              }}
            >
              <ListItemIcon
                sx={{ minWidth: 32, color: "text.secondary" }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: "0.82rem",
                  fontWeight: 500,
                }}
              />
              {item.badge && (
                <Chip
                  label={item.badge}
                  size="small"
                  sx={{
                    height: 18,
                    fontSize: "0.6rem",
                    bgcolor:
                      item.badge === "Mine"
                        ? "rgba(0,212,255,0.12)"
                        : "rgba(247,147,26,0.12)",
                    color: item.badge === "Mine" ? "primary.main" : "secondary.main",
                  }}
                />
              )}
            </ListItemButton>
          ))}
        </List>

        <Divider sx={{ borderColor: "rgba(0,212,255,0.08)", mx: 2, my: 1 }} />

        <Box sx={{ px: 2 }}>
          <Typography variant="caption" sx={{ color: "text.secondary", letterSpacing: "0.1em" }}>
            LIVE APIS
          </Typography>
        </Box>
        <Box sx={{ px: 2, pt: 1 }}>
          <Typography
            variant="caption"
            sx={{ color: "rgba(0,230,118,0.7)", display: "block", mb: 0.5 }}
          >
            ● CryptoFiat Bridge
          </Typography>
          <Typography
            variant="caption"
            sx={{ color: "rgba(247,147,26,0.7)", display: "block", mb: 0.5 }}
          >
            ● ImageCore
          </Typography>
          <Typography
            variant="caption"
            sx={{ color: "rgba(247,147,26,0.7)", display: "block" }}
          >
            ● Locale Format
          </Typography>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: `${DRAWER_WIDTH}px`,
          minHeight: "100vh",
          background:
            "radial-gradient(ellipse at 20% 20%, rgba(0,212,255,0.03) 0%, transparent 60%), #060d1a",
        }}
      >
        <Toolbar />
        <Box sx={{ p: { xs: 2, md: 3 } }}>{children}</Box>
      </Box>
    </Box>
  );
}