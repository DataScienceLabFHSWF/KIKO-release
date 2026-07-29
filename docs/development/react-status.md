# ⚛️ ReactJS Migration Status

KIKO currently uses Streamlit as the stable public frontend.

A ReactJS frontend migration is in progress. The goal of the migration is to provide a production-ready application shell with routing, authentication state management, role-based route guards, reusable UI components, internationalization, and a cleaner frontend architecture.

## ✅ Current stable frontend

```text
frontend/
```

The Streamlit frontend remains the default frontend on the `main` branch.

## 🚧 ReactJS migration status

The ReactJS implementation is under active development and is not yet the default public frontend.

Current migration focus:

- Vite + React + TypeScript foundation
- Routing
- AuthProvider
- Token storage and session restoration
- Role-based route guards
- API client
- i18n
- AppShell with sidebar and topbar
- Shared components
- Design tokens

## 🤝 Contribution guidance

For now:

- Use Streamlit for stable production-facing frontend changes.
- Use React only for migration-specific work.
- Keep React PRs small and clearly labeled.
- Do not remove Streamlit functionality until the React replacement is complete and reviewed.
- Document any feature parity gaps between Streamlit and React.

## 🎯 Target direction

The long-term goal is to make ReactJS the default frontend once the migration reaches feature parity with the current Streamlit interface and passes review.
