// src/services/imagecoreApi.js
import axios from "axios";
import { config } from "../config";

const api = axios.create({ baseURL: config.imagecoreBase });

export const imagecore = {
  health: () => api.get("/").then((r) => r.data),

  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api
      .post("/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  transform: (uri, action, parameters = {}) =>
    api
      .post("/transform", { uri, action, parameters })
      .then((r) => r.data),
};