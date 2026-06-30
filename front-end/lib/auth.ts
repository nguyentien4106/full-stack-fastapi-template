import { cache } from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { TOKEN_COOKIE } from "@/lib/api";
import { OpenAPI } from "@/lib/client";
import { request as apiRequest } from "@/lib/client/core/request";
import type { UserPublic } from "@/lib/client";

export type UserRole = "user" | "company" | "admin";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  initials: string;
  plan: string;
}

export const roles: UserRole[] = ["user", "company", "admin"];

export function isRole(value: string | undefined): value is UserRole {
  return !!value && (roles as string[]).includes(value);
}

function initialsOf(name: string): string {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]!.toUpperCase())
      .join("") || "?"
  );
}

/** Maps the backend user_type onto the front-end role. */
function roleOf(user: UserPublic): UserRole {
  if (user.user_type === "admin" || user.is_superuser) return "admin";
  if (user.user_type === "company") return "company";
  return "user";
}

const PLANS: Record<UserRole, string> = {
  admin: "Platform Admin",
  company: "Business",
  user: "Pay as you go",
};

/** Maps the backend user onto the shape the shells/views render. */
export function toAuthUser(user: UserPublic): AuthUser {
  const name = user.full_name?.trim() || user.email.split("@")[0];
  const role = roleOf(user);
  return {
    id: user.id,
    name,
    email: user.email,
    role,
    initials: initialsOf(name),
    plan: PLANS[role],
  };
}

/**
 * Resolves the session from the auth cookie by asking the API for the current
 * user. Returns null when signed out or the token is no longer valid.
 *
 * Wrapped in React cache() so the layout guard and the page guard share a
 * single /users/me round-trip per request instead of fetching twice.
 */
export const getSession = cache(async (): Promise<AuthUser | null> => {
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_COOKIE)?.value;
  if (!token) return null;

  // Mirrors UsersService.readUserMe() but injects this request's token: the
  // global OpenAPI.TOKEN resolver reads document.cookie and is browser-only, and
  // mutating it would race across concurrent server requests.
  const request = apiRequest<UserPublic>(
    { ...OpenAPI, TOKEN: token },
    { method: "GET", url: "/api/v1/users/me" },
  );
  const timeout = setTimeout(() => request.cancel(), 5000);
  try {
    return toAuthUser(await request);
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
});

/**
 * Guards a role-specific page: returns the session if the current role is
 * allowed, redirects to /login if signed out, or to that role's dashboard
 * if signed in with a different role.
 */
export async function requireRole(allowed: UserRole[], locale: string): Promise<AuthUser> {
  const session = await getSession();
  if (!session) redirect(`/${locale}/login`);
  if (!allowed.includes(session.role)) redirect(`/${locale}/dashboard`);
  return session;
}
