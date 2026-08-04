import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

// Layering rule: `stores/` are the only code that imports from `api/*.js`. Views and
// components only read store state and call store actions — this keeps API calls,
// loading/error state, and data for a given resource in one place instead of
// scattered across whichever component happens to need them.

// FastAPI's error body is always {"detail": ...}, but `detail` is a plain string
// for our hand-raised HTTPExceptions and a list of {msg, loc, ...} objects for
// FastAPI's own automatic Pydantic validation errors (e.g. a malformed due_date).
// Stores use this to get one displayable string regardless of which shape hit.
export function extractErrorMessage(error) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join('; ')
  return error?.message || 'Something went wrong'
}
