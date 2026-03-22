// src/services/mazzApi.js
import axios from "axios";
import { config } from "../config";

const api = axios.create({ baseURL: config.cryptofiatBase });

export const mazz = {
  formatPhone: (number, locale) =>
    api.post("/proxy/format/phone", { number, locale }).then((r) => r.data),

  formatDate: (date, locale, format) =>
    api.post("/proxy/format/date", { date, locale, format }).then((r) => r.data),
};