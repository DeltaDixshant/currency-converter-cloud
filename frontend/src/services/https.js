import axios from "axios";
import { config } from "../config";

export const http = axios.create({
  baseURL: config.cryptofiatBase, // for your own API (CryptoFiat)
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});