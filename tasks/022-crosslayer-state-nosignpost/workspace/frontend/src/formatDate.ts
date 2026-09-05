export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString();
}
