import { describe, it, expect } from 'vitest';
import { extractApiError } from '../utils/errorUtils';

describe('extractApiError', () => {
  it('extracts string detail from error.response.data.detail', () => {
    const error = {
      response: {
        status: 400,
        data: { detail: 'Email already exists' },
      },
    };
    expect(extractApiError(error)).toBe('Email already exists');
  });

  it('extracts error message from structured error.response.data.error.message (Priority 1)', () => {
    const error = {
      response: {
        status: 409,
        data: {
          success: false,
          error: {
            code: 'EMAIL_ALREADY_EXISTS',
            message: 'An account with this email already exists.',
          },
        },
      },
    };
    expect(extractApiError(error)).toBe('An account with this email already exists.');
  });

  it('formats single FastAPI 422 validation error array item', () => {
    const error = {
      response: {
        status: 422,
        data: {
          detail: [
            {
              loc: ['body', 'email'],
              msg: 'value is not a valid email',
            },
          ],
        },
      },
    };
    expect(extractApiError(error)).toBe('Email: value is not a valid email');
  });

  it('formats multiple FastAPI 422 validation error items with bullets', () => {
    const error = {
      response: {
        status: 422,
        data: {
          detail: [
            { loc: ['body', 'email'], msg: 'field required' },
            { loc: ['body', 'password'], msg: 'ensure this value has at least 8 characters' },
          ],
        },
      },
    };
    expect(extractApiError(error)).toBe('• Email: field required\n• Password: ensure this value has at least 8 characters');
  });

  it('extracts message from error.response.data.message (Priority 3)', () => {
    const error = {
      response: {
        status: 400,
        data: { message: 'Invalid credentials provided' },
      },
    };
    expect(extractApiError(error)).toBe('Invalid credentials provided');
  });

  it('extracts error string from error.response.data.error (Priority 4)', () => {
    const error = {
      response: {
        status: 400,
        data: { error: 'Resource locked' },
      },
    };
    expect(extractApiError(error)).toBe('Resource locked');
  });

  it('handles ERR_NETWORK error code', () => {
    const error = { code: 'ERR_NETWORK', message: 'Network Error' };
    expect(extractApiError(error)).toBe('Unable to connect to the server.');
  });

  it('handles ECONNABORTED timeout error code', () => {
    const error = { code: 'ECONNABORTED', message: 'timeout of 5000ms exceeded' };
    expect(extractApiError(error)).toBe('Server took too long to respond.');
  });

  it('handles CORS failure messages', () => {
    const error = { message: 'CORS policy blocked the request' };
    expect(extractApiError(error)).toBe('Unable to contact backend server.');
  });

  it('handles HTTP status code fallbacks when payload is empty', () => {
    expect(extractApiError({ response: { status: 401 } })).toBe('Authentication failed or session expired.');
    expect(extractApiError({ response: { status: 403 } })).toBe('You do not have permission to perform this action.');
    expect(extractApiError({ response: { status: 404 } })).toBe('Requested resource not found.');
    expect(extractApiError({ response: { status: 409 } })).toBe('Conflict detected. Resource already exists.');
    expect(extractApiError({ response: { status: 500 } })).toBe('Internal server error.');
  });

  it('handles HTML error responses safely without crashing', () => {
    const error = {
      response: {
        status: 502,
        data: '<!DOCTYPE html><html><body>502 Bad Gateway</body></html>',
      },
    };
    expect(extractApiError(error)).toBe('Server service temporarily unavailable.');
  });

  it('handles null, undefined, or malformed error objects without throwing', () => {
    expect(extractApiError(null)).toBe('Unexpected server error.');
    expect(extractApiError(undefined)).toBe('Unexpected server error.');
    expect(extractApiError({})).toBe('Unexpected server error.');
  });
});
