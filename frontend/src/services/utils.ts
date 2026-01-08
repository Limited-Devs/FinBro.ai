import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Safely converts any value to a number. Returns fallback (default 0) if NaN.
 */
export function safeNumber(value: any, fallback = 0): number {
  if (value === null || value === undefined || value === '') return fallback;
  const num = Number(value);
  return isNaN(num) ? fallback : num;
}

/**
 * Formats a number to a string with locale support. Handles NaN safely.
 */
export function formatNumber(value: any, decimals = 0): string {
  const num = safeNumber(value);
  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Formats a percentage. Handles NaN safely.
 */
export function formatPercent(value: any, decimals = 1): string {
  const num = safeNumber(value);
  return `${num.toFixed(decimals)}%`;
}
