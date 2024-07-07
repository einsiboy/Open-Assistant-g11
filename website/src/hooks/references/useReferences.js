import { useState, useCallback } from 'react';
import { get } from 'src/lib/api';
import { useCurrentLocale } from 'src/hooks/locale/useCurrentLocale';
import { API_ROUTES } from 'src/lib/routes';

export function useReferences() {
  const [references, setReferences] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const locale = useCurrentLocale();

  const fetchReferences = useCallback(async (query) => {
    if (!query) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await get(API_ROUTES.GET_REFERENCES(query, locale));
      setReferences(data);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [locale]);

  return {
    references,
    isLoading,
    error,
    fetchReferences,
  };
}