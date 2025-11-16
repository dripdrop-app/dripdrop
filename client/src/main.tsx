import React from "react";
import ReactDOM from "react-dom/client";
import { Helmet, HelmetProvider } from "react-helmet-async";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import { store } from "./store";

import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import "@mantine/dropzone/styles.css";
import "./main.css";
import { FooterProvider } from "./providers/FooterProvider";
import { OverlayProvider } from "./providers/OverlayProvider";
import { BackgroundPlayerProvider } from "./providers/BackgroundPlayerProvider";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <Provider store={store}>
        <HelmetProvider>
          <Helmet titleTemplate="%s | dripdrop" defaultTitle="dripdrop" />
          <OverlayProvider>
            <FooterProvider>
              <BackgroundPlayerProvider>
                <App />
              </BackgroundPlayerProvider>
            </FooterProvider>
          </OverlayProvider>
        </HelmetProvider>
      </Provider>
    </BrowserRouter>
  </React.StrictMode>
);
