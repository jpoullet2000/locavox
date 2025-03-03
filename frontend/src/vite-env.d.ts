/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string;
    readonly VITE_ENABLE_NOTIFICATIONS: string;
    readonly VITE_ENABLE_GEOLOCATION: string;
    readonly VITE_LOG_LEVEL: string;
    // more env variables...
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
