// src/pages/ImageCore.jsx
import React, { useState, useEffect } from "react";
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
  TextField,
  Typography,
} from "@mui/material";
import ImageIcon from "@mui/icons-material/Image";
import UploadIcon from "@mui/icons-material/Upload";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import { imagecore } from "../services/imagecoreApi";

const ACTIONS = [
  { value: "grayscale", label: "Grayscale", params: false },
  { value: "resize", label: "Resize", params: true, hint: '{"width": 300, "height": 200}' },
  { value: "rotate", label: "Rotate", params: true, hint: '{"degrees": 90}' },
  { value: "crop", label: "Crop", params: true, hint: '{"left": 0, "top": 0, "right": 200, "bottom": 200}' },
  { value: "thumbnail", label: "Thumbnail", params: true, hint: '{"size": [128, 128]}' },
  { value: "blur", label: "Blur", params: true, hint: '{"radius": 2}' },
  { value: "sharpen", label: "Sharpen", params: false },
  { value: "contour", label: "Contour", params: false },
  { value: "detail", label: "Detail Enhance", params: false },
  { value: "emboss", label: "Emboss", params: false },
  { value: "smooth", label: "Smooth", params: false },
  { value: "edge_enhance", label: "Edge Enhance", params: false },
  { value: "text", label: "Text Overlay", params: true, hint: '{"text": "Hello", "position": [10, 10], "font_size": 30}' },
];

export default function ImageCore() {
  const [health, setHealth] = useState(null);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploadKey, setUploadKey] = useState("");
  const [action, setAction] = useState("grayscale");
  const [paramsText, setParamsText] = useState("{}");
  const [resultUrl, setResultUrl] = useState("");
  const [error, setError] = useState("");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [transformLoading, setTransformLoading] = useState(false);

  useEffect(() => {
    imagecore
      .health()
      .then(setHealth)
      .catch(() => setHealth({ status: "unknown" }));
  }, []);

  const selectedAction = ACTIONS.find((a) => a.value === action);

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setUploadKey("");
    setResultUrl("");
    setError("");
  };

  const handleUpload = async () => {
    if (!file) { setError("Please select a file first."); return; }
    setUploadLoading(true); setError(""); setResultUrl("");
    try {
      const d = await imagecore.upload(file);
      setUploadKey(d.key || d.uri || "");
    } catch (e) {
      setError(e?.response?.data?.detail || e?.response?.data?.message || e.message || "Upload failed");
    } finally { setUploadLoading(false); }
  };

  const handleTransform = async () => {
    if (!uploadKey) { setError("Upload an image first to get a key."); return; }
    let params = {};
    try {
      params = JSON.parse(paramsText || "{}");
    } catch {
      setError("Parameters must be valid JSON. Example: {}"); return;
    }
    setTransformLoading(true); setError(""); setResultUrl("");
    try {
      const d = await imagecore.transform(uploadKey, action, params);
      setResultUrl(d.url || d.result_url || "");
    } catch (e) {
      setError(e?.response?.data?.detail || e?.response?.data?.message || e.message || "Transform failed");
    } finally { setTransformLoading(false); }
  };

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
        <ImageIcon sx={{ color: "secondary.main", fontSize: 28 }} />
        <Typography variant="h5">ImageCore API</Typography>
        <Chip label="Partner API" size="small" sx={{ bgcolor: "rgba(247,147,26,0.12)", color: "secondary.main", fontSize: "0.65rem" }} />
        {health && (
          <Chip
            label={`● ${health.message || health.status || "online"}`}
            size="small"
            sx={{ bgcolor: "rgba(0,230,118,0.1)", color: "#00e676", fontSize: "0.65rem" }}
          />
        )}
      </Box>

      <Typography variant="body2" sx={{ color: "text.secondary", mb: 3 }}>
        Upload an image to S3, then apply transformations like resize, grayscale, rotate, blur, and text overlay.
        Built by a classmate as part of the NCI Cloud Computing CA.
      </Typography>

      <Grid container spacing={3}>
        {/* Step 1: Upload */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, display: "flex", alignItems: "center", gap: 1 }}>
                <UploadIcon fontSize="small" sx={{ color: "secondary.main" }} />
                Step 1 — Upload Image
              </Typography>

              <Button
                variant="outlined"
                component="label"
                fullWidth
                sx={{ borderColor: "rgba(247,147,26,0.3)", color: "secondary.main", mb: 2, py: 2, borderStyle: "dashed" }}
              >
                {file ? file.name : "Click to select image"}
                <input type="file" hidden accept="image/*" onChange={handleFileChange} />
              </Button>

              {preview && (
                <Box sx={{ mb: 2, borderRadius: 1, overflow: "hidden", border: "1px solid rgba(247,147,26,0.2)" }}>
                  <img src={preview} alt="preview" style={{ width: "100%", maxHeight: 200, objectFit: "contain", background: "#0b1628" }} />
                </Box>
              )}

              <Button
                fullWidth
                variant="contained"
                onClick={handleUpload}
                disabled={!file || uploadLoading}
                sx={{ bgcolor: "secondary.main", color: "#000" }}
              >
                {uploadLoading ? <CircularProgress size={18} /> : "Upload to S3"}
              </Button>

              {uploadKey && (
                <Box sx={{ mt: 2, p: 1.5, borderRadius: 1, background: "rgba(0,230,118,0.05)", border: "1px solid rgba(0,230,118,0.2)" }}>
                  <Typography variant="caption" sx={{ color: "#00e676" }}>✓ Uploaded. Key:</Typography>
                  <Typography variant="body2" sx={{ fontFamily: "monospace", color: "#00e676", wordBreak: "break-all", fontSize: "0.72rem" }}>
                    {uploadKey}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Step 2: Transform */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, display: "flex", alignItems: "center", gap: 1 }}>
                <AutoFixHighIcon fontSize="small" sx={{ color: "secondary.main" }} />
                Step 2 — Transform
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    fullWidth
                    size="small"
                    label="Transformation"
                    value={action}
                    onChange={(e) => {
                      setAction(e.target.value);
                      setParamsText("{}");
                    }}
                  >
                    {ACTIONS.map((a) => (
                      <MenuItem key={a.value} value={a.value}>{a.label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    size="small"
                    label={`Parameters (JSON)${!selectedAction?.params ? " — not needed" : ""}`}
                    value={paramsText}
                    onChange={(e) => setParamsText(e.target.value)}
                    disabled={!selectedAction?.params}
                    helperText={selectedAction?.hint || "{}"}
                    InputProps={{ style: { fontFamily: "monospace" } }}
                  />
                </Grid>
              </Grid>

              <Button
                fullWidth
                variant="contained"
                onClick={handleTransform}
                disabled={!uploadKey || transformLoading}
                sx={{ mt: 2, bgcolor: "secondary.main", color: "#000" }}
              >
                {transformLoading ? <CircularProgress size={18} /> : `Apply: ${selectedAction?.label || action}`}
              </Button>

              {!uploadKey && (
                <Typography variant="caption" sx={{ color: "text.secondary", display: "block", mt: 1 }}>
                  Upload an image first to enable transform.
                </Typography>
              )}

              {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

              {resultUrl && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" sx={{ color: "#00e676" }}>✓ Transformed image:</Typography>
                  <Box sx={{ mt: 1, borderRadius: 1, overflow: "hidden", border: "1px solid rgba(247,147,26,0.2)" }}>
                    <img
                      src={resultUrl}
                      alt="transformed"
                      style={{ width: "100%", maxHeight: 300, objectFit: "contain", background: "#0b1628" }}
                    />
                  </Box>
                  <Button
                    size="small"
                    variant="outlined"
                    href={resultUrl}
                    target="_blank"
                    sx={{ mt: 1, borderColor: "rgba(247,147,26,0.3)", color: "secondary.main" }}
                  >
                    Open Full Size
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* API info */}
      <Box sx={{ mt: 3, p: 2, borderRadius: 2, background: "rgba(247,147,26,0.03)", border: "1px solid rgba(247,147,26,0.1)" }}>
        <Typography variant="caption" sx={{ color: "text.secondary", letterSpacing: "0.1em" }}>API DETAILS</Typography>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          {[
            ["Base URL", "https://n3vdm98ezc.execute-api.us-east-1.amazonaws.com"],
            ["POST /upload", "Upload image (multipart/form-data) → {key}"],
            ["POST /transform", "Transform image → presigned URL"],
            ["GET /", "Health check"],
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