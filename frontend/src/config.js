// src/config.js
// Central config - edit these URLs if your API Gateway endpoint changes.
// DO NOT use process.env here (avoids Vite/CRA incompatibility).

export const config = {
  // Your CryptoFiat Bridge API (AWS API Gateway → Lambda)
  cryptofiatBase: "https://ysp58cr2xc.execute-api.us-east-1.amazonaws.com",

  // Friend 1: ImageCore API (image upload & transform)
  imagecoreBase: "https://n3vdm98ezc.execute-api.us-east-1.amazonaws.com",

  // Friend 2: Mazz Locale Formatting API (phone & date formatting)
  mazzBase: "https://itafimfx0h.execute-api.us-east-1.amazonaws.com",
};