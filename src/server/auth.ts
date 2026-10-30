import type { Request, Response, NextFunction } from 'express';
import { createHash, createHmac, randomBytes, timingSafeEqual } from 'node:crypto';
import bcrypt from 'bcryptjs';
import { getSqlClient } from './databaseRuntime.js';
import { isUniqueViolation } from './errors.js';

export interface AuthenticatedRequest extends Request {
  userId?: string;
  sessionHash?: string;
}

export const SESSION_SECONDS = 8 * 60 * 60;
const BCRYPT_ROUNDS = 12;
const MIN_PASSWORD_LENGTH = 14;
const MAX_PASSWORD_LENGTH = 200;
// Used only to equalise the cost of a failed lookup with a real bcrypt check.
const DUMMY_PASSWORD_HASH = '$2b$12$sYeEiM/8BErWHhrV8Q2rP.Xp.Qx/z/sSVaC.T/sUFgKV2hi4FJqsO';

const hash = (value: string) => createHash('sha256').update(value).digest('hex');

export const sessionCookieName = () => process.env.NODE_ENV === 'production' ? '__Host-judicial3_session' : 'judicial3_session';

function constantTimeEqualHex(left: string, right: string) {
  if (left.length !== right.length) return false;
  try {
    return timingSafeEqual(Buffer.from(left, 'hex'), Buffer.from(right, 'hex'));
  } catch {
    return false;
  }
}

/**
 * Legacy HMAC bearer tokens exist only for the local developer bridge.
 * Production always uses server-side cookie sessions.
 */
export function createSessionToken(userId: string, expiresInSeconds = 3600): string {
  if (process.env.NODE_ENV === 'production') throw new Error('legacy bearer tokens are disabled in production');
  const secret = process.env.JUDICIAL3_SESSION_SECRET;
  if (!secret) throw new Error('JUDICIAL3_SESSION_SECRET is required');
  const payloadPart = Buffer.from(JSON.stringify({ sub: userId, exp: Math.floor(Date.now() / 1000) + expiresInSeconds })).toString('base64url');
  const signature = createHmac('sha256', secret).update(payloadPart).digest('base64url');
  return `${payloadPart}.${signature}`;
}

function parseLegacyBearer(req: Request) {
  if (process.env.NODE_ENV === 'production') return null;
  const secret = process.env.JUDICIAL3_SESSION_SECRET;
  const authorization = req.header('authorization') || '';
  const token = authorization.startsWith('Bearer ') ? authorization.slice(7) : '';
  const parts = token.split('.');
  if (!secret || parts.length !== 2) return null;
  try {
    const [payloadPart, signaturePart] = parts;
    const expected = createHmac('sha256', secret).update(payloadPart).digest('base64url');
    if (signaturePart.length !== expected.length || !timingSafeEqual(Buffer.from(signaturePart), Buffer.from(expected))) return null;
    const payload = JSON.parse(Buffer.from(payloadPart, 'base64url').toString('utf8')) as { sub?: string; exp?: number };
    return payload.sub && payload.exp && payload.exp > Math.floor(Date.now() / 1000) ? payload.sub : null;
  } catch { return null; }
}

export async function login(username: string, password: string, request: Request) {
  const db = await getSqlClient();
  const result = await db.query<{ id: string; password_hash: string; is_active: boolean; security_stamp: string }>(
    'SELECT id, password_hash, is_active, security_stamp FROM users WHERE lower(username)=lower($1) LIMIT 1', [username],
  );
  const user = result.rows[0];
  const passwordHash = user?.password_hash || DUMMY_PASSWORD_HASH;
  let passwordMatches = false;
  try {
    passwordMatches = await bcrypt.compare(password, passwordHash);
  } catch {
    passwordMatches = false;
  }
  if (!user || !user.is_active || !passwordMatches) return null;

  const token = randomBytes(32).toString('base64url');
  const csrf = randomBytes(32).toString('base64url');
  const expiresAt = new Date(Date.now() + SESSION_SECONDS * 1000);
  await db.query('DELETE FROM user_sessions WHERE user_id=$1::UUID AND (is_revoked=TRUE OR expires_at<=clock_timestamp())', [user.id]);
  await db.query(`INSERT INTO user_sessions
    (user_id, session_token_hash, csrf_token_hash, security_stamp, ip_address, user_agent, expires_at)
    VALUES ($1::UUID, $2, $3, $4, $5, $6, $7)`, [
    user.id, hash(token), hash(csrf), user.security_stamp, request.ip || null,
    String(request.header('user-agent') || '').slice(0, 1000), expiresAt,
  ]);
  return { token, csrf, userId: user.id, expiresAt };
}

function cookieOptions(expiresAt?: Date) {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict' as const,
    path: '/',
    ...(expiresAt ? { expires: expiresAt } : {}),
  };
}

export function setSessionCookie(res: Response, token: string, expiresAt: Date) {
  res.cookie(sessionCookieName(), token, cookieOptions(expiresAt));
}

export function clearSessionCookie(res: Response) {
  res.clearCookie(sessionCookieName(), cookieOptions());
}

export async function revokeRequestSession(req: AuthenticatedRequest) {
  if (!req.sessionHash) return;
  const db = await getSqlClient();
  await db.query('UPDATE user_sessions SET is_revoked=TRUE, revoked_at=clock_timestamp() WHERE session_token_hash=$1', [req.sessionHash]);
}

export interface AuthenticatedSession {
  userId: string;
  sessionHash: string;
  csrfTokenHash: string | null;
}

export async function authenticateRequest(req: Request): Promise<AuthenticatedSession | null> {
  const raw = req.cookies?.[sessionCookieName()];
  if (typeof raw === 'string' && raw.length >= 32 && raw.length <= 256) {
    const sessionHash = hash(raw);
    const db = await getSqlClient();
    const result = await db.query<{ user_id: string; csrf_token_hash: string | null }>(`
      SELECT s.user_id, s.csrf_token_hash
      FROM user_sessions s JOIN users u ON u.id=s.user_id
      WHERE s.session_token_hash=$1 AND s.is_revoked=FALSE AND s.expires_at>clock_timestamp()
        AND u.is_active=TRUE AND s.security_stamp=u.security_stamp
      LIMIT 1`, [sessionHash]);
    if (result.rows[0]) {
      return { userId: result.rows[0].user_id, sessionHash, csrfTokenHash: result.rows[0].csrf_token_hash };
    }
  }
  const legacyUser = parseLegacyBearer(req);
  if (legacyUser) return { userId: legacyUser, sessionHash: '', csrfTokenHash: null };
  return null;
}

export async function requireApiUser(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  try {
    const session = await authenticateRequest(req);
    if (!session) return res.status(401).json({ error: 'authentication required' });
    req.userId = session.userId;
    req.sessionHash = session.sessionHash || undefined;
    (req as any).csrfTokenHash = session.csrfTokenHash;
    return next();
  } catch {
    return res.status(401).json({ error: 'authentication required' });
  }
}

export function requireCsrf(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  if (!req.sessionHash && process.env.NODE_ENV !== 'production') return next();
  const supplied = req.header('x-csrf-token') || '';
  const expected = String((req as any).csrfTokenHash || '');
  const origin = req.header('origin');
  const allowedOrigin = process.env.JUDICIAL3_PUBLIC_ORIGIN;
  const originOk = process.env.NODE_ENV !== 'production' || (!!origin && origin === allowedOrigin);
  if (!supplied || !expected || !constantTimeEqualHex(hash(supplied), expected) || !originOk) {
    return res.status(403).json({ error: 'request verification failed' });
  }
  return next();
}

export interface ProvisionUserInput {
  username: string;
  email: string;
  password: string;
  fullName: string;
  roleCode?: string;
}

function validateNewUser(input: ProvisionUserInput) {
  if (!/^[a-zA-Z0-9._-]{3,64}$/.test(input.username)) throw new Error('username must be 3-64 characters using letters, digits, dot, underscore or hyphen');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email) || input.email.length > 255) throw new Error('email is invalid');
  if (!input.fullName.trim() || input.fullName.length > 100) throw new Error('full name is required and must be at most 100 characters');
  if (input.password.length < MIN_PASSWORD_LENGTH || input.password.length > MAX_PASSWORD_LENGTH) {
    throw new Error(`password must contain ${MIN_PASSWORD_LENGTH}-${MAX_PASSWORD_LENGTH} characters`);
  }
}

export async function provisionUser(input: ProvisionUserInput) {
  validateNewUser(input);
  const db = await getSqlClient();
  const roleCode = (input.roleCode || 'LEAD_INVESTIGATOR').toUpperCase();
  const role = await db.query<{ id: string }>('SELECT id FROM user_roles WHERE role_code=$1 LIMIT 1', [roleCode]);
  if (!role.rows[0]) throw new Error('requested role does not exist');
  const passwordHash = await bcrypt.hash(input.password, BCRYPT_ROUNDS);
  try {
    const created = await db.query<{ id: string }>(`INSERT INTO users(username,email,password_hash,full_name,role_id)
      VALUES($1,$2,$3,$4,$5::UUID) RETURNING id`, [input.username, input.email, passwordHash, input.fullName.trim(), role.rows[0].id]);
    return created.rows[0].id;
  } catch (error) {
    if (isUniqueViolation(error)) throw new Error('username, email or badge number already exists');
    throw error;
  }
}

export async function suspendUser(userId: string) {
  const db = await getSqlClient();
  await db.query(`UPDATE users SET is_active=FALSE, security_stamp=gen_random_uuid()::text WHERE id=$1::UUID`, [userId]);
  await db.query(`UPDATE user_sessions SET is_revoked=TRUE, revoked_at=clock_timestamp() WHERE user_id=$1::UUID`, [userId]);
}

export async function reactivateUser(userId: string) {
  const db = await getSqlClient();
  await db.query(`UPDATE users SET is_active=TRUE, security_stamp=gen_random_uuid()::text WHERE id=$1::UUID`, [userId]);
}

export async function revokeAllUserSessions(userId: string) {
  const db = await getSqlClient();
  await db.query(`UPDATE user_sessions SET is_revoked=TRUE, revoked_at=clock_timestamp() WHERE user_id=$1::UUID AND is_revoked=FALSE`, [userId]);
}
