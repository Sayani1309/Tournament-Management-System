export function getErrorMessage(error) {
  if (!error?.response) {
    return 'Could not reach the server. Please check your connection and try again.';
  }

  const status = error.response.status;
  const data = error.response.data;

  if (status === 429) {
    return 'Too many attempts. Please wait a moment and try again.';
  }
  if (status === 401) {
    return 'Your session has expired or you are not logged in. Please log in again.';
  }
  if (status === 500) {
    return 'Something went wrong on our end. Please try again shortly.';
  }

  if (!data || !data.error) {
    return 'Something went wrong. Please try again.';
  }

  const err = data.error;
  if (typeof err === 'string') return err;

  if (typeof err === 'object') {
    const messages = [];
    for (const field in err) {
      const val = err[field];
      if (Array.isArray(val)) messages.push(...val);
      else messages.push(String(val));
    }
    return messages.join(' ');
  }
  return 'Something went wrong. Please try again.';
}