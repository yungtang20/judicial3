import type { Request, Response, NextFunction } from 'express';
import { createHmac, timingSafeEqual } from 'crypto';

export interface AuthenticatedRequest extends Request {
  userId?: string;
}

export function createSessionToken(userId: string, expiresInSeconds = 3600): string {
  const secret = process.env.JUDICIAL3_SESSION_SECRET;
  if (!secret) throw new Error('JUDICIAL3_SESSION_SECRET is required');
  const payloadPart = Buffer.from(JSON.stringify({
    sub: userId,
    exp: Math.floor(Date.now() / 1000) + expiresInSeconds,
  })).toString('base64url');
  const signature = createHmac('sha256', secret).update(payloadPart).digest('base64url');
  return `${payloadPart}.${signature}`;
}

/**
 * HMAC session token 驗證。正式部署可替換為受控身分服務，但案件 API
 * 不再相信 request body 或 x-user-id 自稱的案件擁有者。
 */
export function requireApiUser(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const secret = process.env.JUDICIAL3_SESSION_SECRET;
  const authorization = req.header('authorization') || '';
  const token = authorization.startsWith('Bearer ') ? authorization.slice(7) : '';
  const parts = token.split('.');
  let userId = '';
  try {
    if (!secret || parts.length !== 2) throw new Error('invalid token shape');
    const [payloadPart, signaturePart] = parts;
    const expected = createHmac('sha256', secret).update(payloadPart).digest('base64url');
    if (signaturePart.length !== expected.length || !timingSafeEqual(Buffer.from(signaturePart), Buffer.from(expected))) {
      throw new Error('invalid token signature');
    }
    const payload = JSON.parse(Buffer.from(payloadPart, 'base64url').toString('utf8')) as { sub?: string; exp?: number };
    if (!payload.sub || !payload.exp || payload.exp <= Math.floor(Date.now() / 1000)) throw new Error('expired token');
    userId = payload.sub;
  } catch {
    return res.status(401).json({ error: 'authentication required' });
  }
  req.userId = userId;
  return next();
}
