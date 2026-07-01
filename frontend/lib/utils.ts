import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(value?: string | null) {
  if (!value) return "—"
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}

export function formatCurrency(value?: number | null, currency = "PKR") {
  if (value === null || value === undefined) return "—"
  return `${currency} ${new Intl.NumberFormat().format(value)}`
}

export function formatDuration(minutes?: number | null) {
  if (minutes === null || minutes === undefined) return "—"
  const hours = Math.floor(minutes / 60)
  const remaining = minutes % 60
  return hours ? `${hours}h ${remaining}m` : `${remaining}m`
}
