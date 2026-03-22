// src/services/cryptofiatApi.js
import axios from "axios";
import { config } from "../config";

const api = axios.create({ baseURL: config.cryptofiatBase });

export const cryptofiat = {
  // Health & info
  health: () => api.get("/health").then((r) => r.data),
  info: () => api.get("/info").then((r) => r.data),

  // Fiat currencies list
  currencies: () => api.get("/currencies").then((r) => r.data),

  // Fiat → Fiat conversion
  convert: (from_currency, to_currency, amount) =>
    api
      .post("/convert", { from_currency, to_currency, amount })
      .then((r) => r.data),

  // Multi-currency comparison
  compare: (base_currency, amount, target_currencies) =>
    api
      .post("/convert/compare", { base_currency, amount, target_currencies })
      .then((r) => r.data),

  // Fiat → Crypto
  fiatToCrypto: (from_currency, to_crypto, amount) =>
    api
      .post("/convert/crypto", { from_currency, to_crypto, fiat_amount: amount })
      .then((r) => r.data),

  // Crypto → Fiat
  cryptoToFiat: (from_crypto, to_currency, amount) =>
    api
      .post("/crypto/to-fiat", {
        from_crypto,
        to_currency,
        crypto_amount: amount,
      })
      .then((r) => r.data),

  // Crypto → Crypto
  cryptoToCrypto: (from_crypto, to_crypto, amount) =>
    api
      .post("/crypto/convert", {
        from_crypto,
        to_crypto,
        amount,
      })
      .then((r) => r.data),

  // Crypto list
  cryptoList: () => api.get("/crypto/list").then((r) => r.data),

  // Crypto prices (single or comma-separated)
  cryptoPrices: (symbols, vs_currency = "usd") =>
    api
      .get("/crypto/prices", { params: { symbols, vs_currency } })
      .then((r) => r.data),

  // Crypto details
  cryptoDetails: (symbol) =>
    api.get(`/crypto/details/${symbol}`).then((r) => r.data),
};