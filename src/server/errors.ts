export class AppError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export function isUniqueViolation(error: unknown): boolean {
  return !!error && typeof error === 'object' && (error as { code?: string }).code === '23505';
}

export function isForeignKeyViolation(error: unknown): boolean {
  return !!error && typeof error === 'object' && (error as { code?: string }).code === '23503';
}


