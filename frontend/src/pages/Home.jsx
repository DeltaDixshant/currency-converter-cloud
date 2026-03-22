// src/pages/Home.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Typography,
} from "@mui/material";
import CurrencyBitcoinIcon from "@mui/icons-material/CurrencyBitcoin";
import ImageIcon from "@mui/icons-material/Image";
import TranslateIcon from "@mui/icons-material/Translate";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { cryptofiat } from "../services/cryptofiatApi";

const apiCards = [
  {
    title: "CryptoFiat Bridge",
    subtitle: "My API",
    description:
      "Convert between 160+ fiat currencies and 20+ cryptocurrencies. Compare rates, track prices, and perform crypto↔fiat conversions in real-time.",
    to: "/cryptofiat",
    icon: <CurrencyBitcoinIcon sx={{ fontSize: 40, color: "#00d4ff" }} />,
    color: "#00d4ff",
    features: [
      "Fiat → Fiat",
      "Fiat → Crypto",
      "Crypto → Fiat",
      "Crypto → Crypto",
      "Multi-compare",
      "Live prices",
    ],
    docs: "https://ysp58cr2xc.execute-api.us-east-1.amazonaws.com/docs",
  },
  {
    title: "ImageCore",
    subtitle: "Partner API",
    description:
      "Upload images to S3 and apply transformations — resize, rotate, grayscale, blur, text overlay, and more. Built by a classmate.",
    to: "/imagecore",
    icon: <ImageIcon sx={{ fontSize: 40, color: "#f7931a" }} />,
    color: "#f7931a",
    features: [
      "Upload to S3",
      "Resize",
      "Grayscale",
      "Rotate",
      "Blur/Sharpen",
      "Text Overlay",
    ],
    docs: "http://image-core-cloud.s3-website-us-east-1.amazonaws.com/",
  },
  {
    title: "Locale Formatter",
    subtitle: "Partner API",
    description:
      "Format phone numbers and dates for different countries and locales. Returns national, international, E.164, and more. Built by Mazz.",
    to: "/locale-format",
    icon: <TranslateIcon sx={{ fontSize: 40, color: "#f7931a" }} />,
    color: "#f7931a",
    features: [
      "Phone formatting",
      "Date formatting",
      "E.164 standard",
      "International",
      "National",
      "Multi-locale",
    ],
  },
];

export default function Home() {
  const navigate = useNavigate();
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    cryptofiat
      .health()
      .then((d) => setApiStatus(d?.status || "healthy"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <Box>
      {/* Hero */}
      <Box sx={{ mb: 5, mt: 1 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1 }}>
          <CurrencyBitcoinIcon sx={{ fontSize: 36, color: "#00d4ff" }} />
          <Typography variant="h4" sx={{ color: "#e8f4fd" }}>
            CryptoFiat Cloud Suite
          </Typography>
          {apiStatus && (
            <Chip
              label={apiStatus === "healthy" ? "● API Online" : "● API Error"}
              size="small"
              sx={{
                bgcolor:
                  apiStatus === "healthy"
                    ? "rgba(0,230,118,0.12)"
                    : "rgba(255,82,82,0.12)",
                color: apiStatus === "healthy" ? "#00e676" : "#ff5252",
                fontSize: "0.72rem",
              }}
            />
          )}
        </Box>
        <Typography variant="body1" sx={{ color: "text.secondary", maxWidth: 620 }}>
          A scalable microservices project — NCI MSc Cloud Computing, Scalable Cloud
          Programming CA. Integrates three live serverless APIs deployed on AWS Lambda.
        </Typography>
      </Box>

      {/* API Cards */}
      <Grid container spacing={3}>
        {apiCards.map((card) => (
          <Grid item xs={12} md={4} key={card.title}>
            <Card
              sx={{
                height: "100%",
                cursor: "pointer",
                transition: "transform 0.2s, box-shadow 0.2s",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: `0 8px 40px ${card.color}22`,
                  borderColor: `${card.color}44`,
                },
              }}
              onClick={() => navigate(card.to)}
            >
              <CardContent sx={{ p: 3, height: "100%" }}>
                <Box sx={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", mb: 2 }}>
                  {card.icon}
                  <Chip
                    label={card.subtitle}
                    size="small"
                    sx={{
                      bgcolor:
                        card.subtitle === "My API"
                          ? "rgba(0,212,255,0.12)"
                          : "rgba(247,147,26,0.12)",
                      color:
                        card.subtitle === "My API" ? "#00d4ff" : "#f7931a",
                      fontSize: "0.65rem",
                      fontWeight: 700,
                    }}
                  />
                </Box>

                <Typography variant="h6" sx={{ mb: 0.5, color: "#e8f4fd" }}>
                  {card.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ color: "text.secondary", mb: 2, lineHeight: 1.6 }}
                >
                  {card.description}
                </Typography>

                {/* Feature chips */}
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 3 }}>
                  {card.features.map((f) => (
                    <Chip
                      key={f}
                      label={f}
                      size="small"
                      sx={{
                        bgcolor: "rgba(255,255,255,0.04)",
                        color: "text.secondary",
                        fontSize: "0.65rem",
                      }}
                    />
                  ))}
                </Box>

                <Box sx={{ display: "flex", gap: 1 }}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(card.to);
                    }}
                    sx={{ bgcolor: card.color, color: "#000", flex: 1 }}
                  >
                    Open Tool
                  </Button>
                  {card.docs && (
                    <Button
                      variant="outlined"
                      size="small"
                      endIcon={<OpenInNewIcon fontSize="small" />}
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(card.docs, "_blank");
                      }}
                      sx={{ borderColor: `${card.color}44`, color: card.color }}
                    >
                      Docs
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Project info */}
      <Box
        sx={{
          mt: 5,
          p: 3,
          borderRadius: 2,
          background: "rgba(0,212,255,0.03)",
          border: "1px solid rgba(0,212,255,0.1)",
        }}
      >
        <Typography variant="caption" sx={{ color: "text.secondary", display: "block", mb: 1, letterSpacing: "0.1em" }}>
          PROJECT DETAILS
        </Typography>
        <Grid container spacing={3}>
          {[
            ["Developer", "Dixshant Valecha"],
            ["Module", "Scalable Cloud Programming"],
            ["College", "NCI Dublin"],
            ["Deployment", "AWS Lambda + API Gateway"],
            [
              "GitHub",
              "DeltaDixshant/currency-converter-cloud",
            ],
            ["API Docs", "Swagger UI (FastAPI)"],
          ].map(([k, v]) => (
            <Grid item xs={12} sm={6} md={4} key={k}>
              <Typography variant="caption" sx={{ color: "text.secondary" }}>
                {k}
              </Typography>
              <Typography variant="body2" sx={{ color: "#00d4ff", fontFamily: "monospace" }}>
                {v}
              </Typography>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
}