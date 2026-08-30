export function getErrorMessage(error) {
  const data = error?.response?.data;
  if (!data || !data.error) return 'Something went wrong. Please try again.';

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