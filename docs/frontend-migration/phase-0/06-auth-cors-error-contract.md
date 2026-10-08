# Auth, JWT, CORS, and session contract

## Token storage
- React stores access token in `localStorage`.
- Token key: `kiko_access_token`.
- User object key: `kiko_user`.

## JWT expiration behavior
- On `401`, React clears token and redirects to `/login`.
- On `403`, React shows an unauthorized page or toast.
- No silent refresh unless backend provides a refresh-token endpoint.

## Login behavior
- `POST /api/authentication/login`
- Expected response:
  - `access_token`
  - `token_type`
  - `user.role`
  - `user.email`
  - `user.full_name`

## Logout behavior
- Clear local storage.
- Clear React Query cache.
- Redirect to `/login`.

## CORS
Allowed origins:
- local dev frontend origin
- deployed frontend origin

Allowed headers:
- `Authorization`
- `Content-Type`

Allowed methods:
- `GET`
- `POST`
- `PUT`
- `PATCH`
- `DELETE`