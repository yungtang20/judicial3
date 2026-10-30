import type { Request, Response } from 'express';
import { createSessionToken } from './auth.js';

function isLoopback(ip: string | undefined) {
  return ip === '127.0.0.1' || ip === '::1' || ip === '::ffff:127.0.0.1';
}

export function devSessionAllowed(req: Request, env: NodeJS.ProcessEnv = process.env) {
  return env.NODE_ENV !== 'production' && env.JUDICIAL3_ALLOW_DEV_SESSION === 'true' && isLoopback(req.ip);
}

/**
 * Local-only developer bridge. It is deliberately unreachable in production
 * and when the explicit opt-in flag is absent.
 */
export function handleDevSession(req: Request, res: Response, env: NodeJS.ProcessEnv = process.env) {
  if (!devSessionAllowed(req, env)) return res.status(404).json({ error: 'not found' });
  try {
    const userId = env.JUDICIAL3_DEV_USER_ID || '22222222-2222-2222-2222-222222222201';
    return res.json({ accessToken: createSessionToken(userId), userId, environment: 'local-only' });
  } catch {
    return res.status(503).json({ error: 'local session unavailable' });
  }
}


