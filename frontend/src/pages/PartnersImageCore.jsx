import React, { useEffect, useState } from "react";
import { imagecore } from "../services/imagecoreApi";
import { config } from "../config";

const ACTIONS = [
  "grayscale",
  "resize",
  "rotate",
  "crop",
  "thumbnail",
  "blur",
  "sharpen",
  "contour",
  "detail",
  "emboss",
  "smooth",
  "edge_enhance",
  "text",
];

export default function PartnersImageCore() {
  const [health, setHealth] = useState(null);

  const [file, setFile] = useState(null);
  const [uploadKey, setUploadKey] = useState("");

  const [action, setAction] = useState("grayscale");
  const [paramsText, setParamsText] = useState("{}");

  const [resultUrl, setResultUrl] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    imagecore.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  const upload = async () => {
    setError("");
    setResultUrl("");
    setUploadKey("");

    if (!file) {
      setError("Please choose an image first (max 2MB).");
      return;
    }

    try {
      const data = await imagecore.upload(file);
      setUploadKey(data.key);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Upload failed");
    }
  };

  const transform = async () => {
    setError("");
    setResultUrl("");

    if (!uploadKey) {
      setError("Upload an image first to get the uri/key.");
      return;
    }

    let parameters = {};
    try {
      parameters = JSON.parse(paramsText || "{}");
    } catch {
      setError("Parameters must be valid JSON (example: {}).");
      return;
    }

    try {
      const data = await imagecore.transform({ uri: uploadKey, action, parameters });
      setResultUrl(data.url);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Transform failed");
    }
  };

  return (
    <div className="container py-4">
      <h2>Partner API: ImageCore</h2>
      <p className="text-muted">
        Uses: <code>{config.imagecoreBase}</code>
      </p>

      <p className="text-muted">
        Health: {health ? JSON.stringify(health) : "Not loaded / not available"}
      </p>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card p-3 mb-3">
        <h5>1) Upload image</h5>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button className="btn btn-primary mt-2" onClick={upload}>
          Upload
        </button>

        {uploadKey && (
          <div className="mt-2">
            <b>Uploaded key (uri):</b> <code>{uploadKey}</code>
          </div>
        )}
      </div>

      <div className="card p-3 mb-3">
        <h5>2) Transform</h5>

        <label className="form-label">Action</label>
        <select className="form-select" value={action} onChange={(e) => setAction(e.target.value)}>
          {ACTIONS.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>

        <label className="form-label mt-3">Parameters (JSON)</label>
        <textarea
          className="form-control"
          rows={6}
          value={paramsText}
          onChange={(e) => setParamsText(e.target.value)}
          placeholder={`Examples:
{}
{"width": 400, "height": 300}
{"angle": 90}
{"thumbnail_size":"medium"}
{"text":"Hello","font_size":32,"font_color":"(255,255,255,255)","text_x":20,"text_y":40}
`}
        />

        <button className="btn btn-success mt-3" onClick={transform}>
          Run transform
        </button>
      </div>

      {resultUrl && (
        <div className="card p-3">
          <div>
            <b>Result URL:</b>{" "}
            <a href={resultUrl} target="_blank" rel="noreferrer">
              Open
            </a>
          </div>
          <img alt="result" src={resultUrl} className="img-fluid mt-3" />
        </div>
      )}
    </div>
  );
}