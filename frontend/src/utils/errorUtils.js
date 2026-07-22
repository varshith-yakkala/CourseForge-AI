/**
 * CourseForge AI — Universal Frontend API Error Utility
 *
 * Extracts and formats clean, human-readable backend error messages while
 * preserving exact server detail strings, FastAPI validation arrays (422),
 * network/timeout failures, and structured error responses.
 */

export function extractApiError(error) {
  // 1. Development Debug Logging (Task 7)
  if (import.meta.env.DEV) {
    try {
      console.group('API Error Debug');
      console.log('========== API ERROR ==========');
      console.log('Timestamp:', new Date().toISOString());
      console.log('HTTP Method:', error?.config?.method ? error.config.method.toUpperCase() : 'UNKNOWN');
      console.log('Request URL:', error?.config?.url || error?.config?.baseURL || 'N/A');
      console.log('HTTP Status:', error?.response?.status || 'N/A');
      console.log('Request Payload:', error?.config?.data || 'N/A');
      console.log('Response Headers:', error?.response?.headers || 'N/A');
      console.log('Response Body:', error?.response?.data || 'N/A');
      console.log('Axios Error Object:', error);
      console.log('==============================');
      console.groupEnd();
    } catch {
      // Ignore logging failures
    }
  }

  if (!error) {
    return 'Unexpected server error.';
  }

  // 2. Offline Check (Task 6)
  if (typeof navigator !== 'undefined' && navigator && navigator.onLine === false) {
    return 'No internet connection detected.';
  }

  // 3. Network, Timeout & CORS Error Handling (Task 6)
  if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
    return 'Unable to connect to the server.';
  }
  if (error.code === 'ECONNABORTED' || (typeof error.message === 'string' && error.message.toLowerCase().includes('timeout'))) {
    return 'Server took too long to respond.';
  }
  if (typeof error.message === 'string' && (error.message.includes('CORS') || error.message.includes('NetworkError'))) {
    return 'Unable to contact backend server.';
  }

  // 4. Inspect Axios Response Payload safely with try/catch (Task 8)
  try {
    const data = error.response?.data;

    if (data) {
      // If response body is HTML or non-object string (Task 8)
      if (typeof data === 'string') {
        const trimmed = data.trim();
        if (trimmed.startsWith('<!DOCTYPE') || trimmed.startsWith('<html')) {
          return getStatusFallback(error.response?.status) || 'Unexpected server response.';
        }
        if (trimmed.length > 0 && trimmed.length < 300) {
          return trimmed;
        }
      }

      if (typeof data === 'object') {
        // Priority 1: error.response.data.error.message (Task 3 & 4)
        if (data.error && typeof data.error === 'object' && typeof data.error.message === 'string' && data.error.message.trim().length > 0) {
          return data.error.message.trim();
        }

        // Priority 2: error.response.data.detail (Task 3 & 5)
        const detail = data.detail;

        // FastAPI 422 Validation Error Array (Task 5)
        if (Array.isArray(detail)) {
          const messages = detail.map((errItem) => {
            if (typeof errItem === 'string') return errItem;
            if (errItem && typeof errItem === 'object') {
              const loc = Array.isArray(errItem.loc) ? errItem.loc : [];
              const rawField = loc.length > 0 ? String(loc[loc.length - 1]) : 'field';
              const cleanField = rawField.replace(/_/g, ' ');
              const formattedField = cleanField.charAt(0).toUpperCase() + cleanField.slice(1);
              const msg = errItem.msg || 'invalid value';
              return `${formattedField}: ${msg}`;
            }
            return 'Invalid value';
          }).filter(Boolean);

          if (messages.length === 1) {
            return messages[0];
          }
          if (messages.length > 1) {
            return messages.map((m) => `• ${m}`).join('\n');
          }
        }

        // Detail string
        if (typeof detail === 'string' && detail.trim().length > 0) {
          return detail.trim();
        }

        // Detail object with msg or message
        if (typeof detail === 'object' && detail !== null) {
          if (typeof detail.msg === 'string' && detail.msg.trim().length > 0) return detail.msg.trim();
          if (typeof detail.message === 'string' && detail.message.trim().length > 0) return detail.message.trim();
        }

        // Priority 3: error.response.data.message (Task 3)
        if (typeof data.message === 'string' && data.message.trim().length > 0) {
          return data.message.trim();
        }

        // Priority 4: error.response.data.error (if string) (Task 3)
        if (typeof data.error === 'string' && data.error.trim().length > 0) {
          return data.error.trim();
        }
      }
    }
  } catch {
    // Fallback if parsing fails
  }

  // 5. HTTP Status Code Fallbacks
  const statusFallback = getStatusFallback(error.response?.status);
  if (statusFallback) {
    return statusFallback;
  }

  // Priority 5: error.message (Task 3)
  if (typeof error.message === 'string' && error.message.trim().length > 0 && !error.message.includes('Request failed with status code')) {
    return error.message.trim();
  }

  return 'Unexpected server error.';
}

/**
 * Maps HTTP status codes to friendly fallback error messages.
 */
function getStatusFallback(status) {
  if (!status) return null;
  switch (status) {
    case 400:
      return 'Invalid request parameters.';
    case 401:
      return 'Authentication failed or session expired.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'Requested resource not found.';
    case 409:
      return 'Conflict detected. Resource already exists.';
    case 422:
      return 'Validation error. Please check your inputs.';
    case 500:
      return 'Internal server error.';
    case 502:
    case 503:
    case 504:
      return 'Server service temporarily unavailable.';
    default:
      return null;
  }
}
