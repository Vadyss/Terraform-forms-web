import { useQuery } from '@tanstack/react-query';
import type { GetOptions } from '../types';

async function fetchOptions(): Promise<GetOptions> {
    const res = await fetch(`/api/options`);
    if (!res.ok) {
        throw new Error('Failed to fetch options');
    }
    return res.json();
}

export function useOptions() {
    const { data: options, isLoading, isError } = useQuery ({
        queryKey: ['options'],
        queryFn: fetchOptions,
        staleTime: Infinity,
    });

    return { options, isLoading, isError };
}