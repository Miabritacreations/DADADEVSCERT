## Dada Devs Certificate Platform – Architecture

```
┌─────────────────────────┐
│        Browser          │
│  - Admin Dashboard      │
│  - Verification page    │
└────────────┬────────────┘
             │ HTTPS (Flask)
┌────────────▼────────────┐
│      Flask App          │
│  Blueprints             │
│   / (web)               │
│   /admin                │
│   /api/v1               │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ Certificate Service     │
│  - Ed25519 signatures   │
│  - PDF + QR generator   │
│  - IPFS publisher       │
│  - OTS timestamping     │
│  - JSON persistence     │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  Data + Key Stores      │
│  backend/data/certs.json│
│  backend/keys/*.pem     │
│  backend/data/ots/*.ots │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ External services       │
│  - OpenTimestamps       │
│  - IPFS/Pinata (opt)    │
│  - LinkedIn share url   │
└─────────────────────────┘
```

