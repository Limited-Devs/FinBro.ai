import { useQuery } from '@tanstack/react-query';
import { predictionAPI } from '@/services/api';

export interface MonthlyTrend {
    month: string;
    month_key: string;
    income: number;
    expenses: number;
    actual_savings: number;
    target_savings: number;
}

export interface TrendsResponse {
    monthly_data: MonthlyTrend[];
    total_months: number;
}

export const useTrendsData = (months: number = 6) => {
    return useQuery({
        queryKey: ['trendsData', months],
        queryFn: async (): Promise<TrendsResponse> => {
            const data = await predictionAPI.getTrends(months);
            return data;
        },
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 15 * 60 * 1000, // 15 minutes
        retry: 2,
        retryDelay: 1000,
    });
};
