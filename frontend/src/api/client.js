import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

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
