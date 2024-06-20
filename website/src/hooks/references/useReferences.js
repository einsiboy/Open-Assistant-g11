import useSWR from 'swr';
import { get } from 'src/lib/api';  // Import get from your API utilities
import { useCurrentLocale } from 'src/hooks/locale/useCurrentLocale';

export function useReferences(query) {
  const locale = useCurrentLocale();

  // TODO move url to routes.ts
  const { data, error, isValidating, mutate } = useSWR(query ? `/api/references?query=${query}&lang=${locale}` : null, get, { shouldRetryOnError: false });

  console.log("using useReferences, query is: ", query);
  
  return {
    references: data,
    isLoading: isValidating,
    isError: error,
    refreshReferences: mutate,  // Allows manual revalidation
  };
}
