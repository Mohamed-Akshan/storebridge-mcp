
function getErrorMessage(data, status) {
  const detail = data?.detail;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc)
          ? item.loc
            .filter((part) => part !== 'body')
            .join('.')
          : '';

        const message =
          item?.msg || 'Invalid input';

        return field
          ? `${field}: ${message}`
          : message;
      })
      .join('. ');
  }

  if (detail && typeof detail === 'object') {
    return (
      detail.message ||
      detail.msg ||
      detail.error ||
      `Server returned ${status}`
    );
  }

  if (typeof data?.message === 'string') {
    return data.message;
  }

  if (status === 401) {
    return 'Your session has expired. Please log in again.';
  }

  if (status === 403) {
    return 'You do not have permission to perform this action.';
  }

  if (status === 422) {
    return 'Please check the information you entered.';
  }

  if (status >= 500) {
    return 'The server encountered a problem. Please try again.';
  }

  return `Request failed (${status}).`;
}


export async function api(path, options = {}) {
  let response;

  try {
    response = await fetch(`/api${path}`, {
      ...options,

      credentials: 'include',

      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

  } catch (error) {
    console.error('API connection failed:', error);

    throw new Error(
      'Cannot connect to FastAPI. ' +
      'Please check that the backend is running on port 8000.'
    );
  }

  let data = {};

  try {
    data = await response.json();

  } catch {
    // Some server responses do not contain JSON.
  }

  if (!response.ok) {
    const message = getErrorMessage(
      data,
      response.status
    );

    console.error('API request failed:', {
      path,
      status: response.status,
      message,
    });

    throw new Error(message);
  }

  return data;
}
